import json
from crewai import Crew, Process, Task
from utils.registry import ACTION_REGISTRY
from crew.agents import create_agents
from utils.tasks import (
    create_scout_task,
    create_vision_task,
    create_executor_task,
    create_qa_task,
)
import ollama


class Orchestrator:

    def __init__(self, state: dict, name_map: dict):
        self.state = state
        self.name_map = name_map
        self.state.setdefault("path_tracking", ["Default"])
        self.state.setdefault("skip_until", None)
        self._agents = create_agents(state["planner_model"], state["vlm_model"])

    def _unload_models(self):
        ollama.chat(
            model=self.state["vlm_model"],
            messages=[{"role": "user", "content": ""}],
            keep_alive=0
        )

    def run(self, plan_text: str) -> dict:
        steps = self._translate(plan_text)

        for step in steps:
            action_name = step["action"]
            pddl_params = step["params"]

            skip_until = self.state.get("skip_until")
            if skip_until:
                if action_name != skip_until:
                    print(f"Saltando '{action_name}' por fallback.")
                    continue
                else:
                    del self.state["skip_until"]

            if action_name not in ACTION_REGISTRY:
                print(f"action no se sabe '{action_name}', saltamos.")
                continue

            config = ACTION_REGISTRY[action_name]
            print(f"\nAcción: {action_name} ; agents: {config.agents} ; params: {pddl_params}")

            success = self._execute_step(action_name, config, pddl_params)

            if "FALLBACK_SKIP" in str(success):
                file_name = self.state.get("file_name", "")
                pddl_id = None
                for k, v in self.name_map.items():
                    if v == file_name:
                        pddl_id = k
                        break
                for j, s in enumerate(steps):
                    if pddl_id in s["params"] and j+1 < len(steps):
                        self.state["skip_until"] = steps[j+1]["action"]
                        print(f"Fallback: saltando hasta '{self.state['skip_until']}'")
                        break

            if not success:
                print(f"Action '{action_name}' fracasado, abortamos misión.")
                self.state["status"] = "failed"
                break

        self._unload_models()
        return self.state

    def _translate(self, plan_text: str) -> list[dict]:

        task = Task(
            description=plan_text,
            expected_output="JSON list of action steps.",
            agent=self._agents["translator"]
        )
        raw = self._agents["translator"].execute_task(task)
        return json.loads(raw)


    def _execute_step(self, action_name: str, config, pddl_params: list[str]) -> bool:

        target = self._resolve_target(action_name, config, pddl_params)

        # QA es siempre el últim paso.
        if action_name == "final":
            if "changed_text" in self.state.get("goal", ""):
                qa_type = "formatting"
                target_text = self.state.get("content", "")
            elif "delete_text" in self.state.get("goal", ""):
                qa_type = "delete"
                target_text = self.state.get("content", "") # Usar el contenido a borrar
            else:
                qa_type = "default"
                target_text = self.state.get("prompt", "")

            qa_task = create_qa_task(
                goal=target_text, # <--- Pasar el target específico
                agent=self._agents["qa"],
                qa_type=qa_type,
                style=self.state.get("style", "")
            )
            crew = Crew(
                agents=[self._agents["qa"]],
                tasks=[qa_task],
                process=Process.sequential,
                verbose=True
            )
            result = crew.kickoff()
            
            if qa_type == "delete":
                return "NO" in str(result).upper()
            else:
                return "YES" in str(result).upper()

        # Instancia de cuando necesitamos scout, vision y executor trabajando juntos.
        if set(config.agents) >= {"scout", "vision", "executor"}:
            scout_task = create_scout_task(
                target_item=target,
                item_type=config.item_type,
                agent=self._agents["scout"]
            )
            vision_task = create_vision_task(
                target_item=target,
                agent=self._agents["vision"],
                scout_task=scout_task
            )

            # Run Scout and Vision as a crew first
            scout_vision_crew = Crew(
                agents=[self._agents["scout"], self._agents["vision"]],
                tasks=[scout_task, vision_task],
                process=Process.sequential,
                verbose=True
            )
            vision_result = str(scout_vision_crew.kickoff())

            result = self._agents["executor"].execute_task(
                task=create_executor_task(
                    target_item=target,
                    item_type=config.item_type,
                    action_intent=action_name,
                    agent=self._agents["executor"],
                    context_tasks=[]
                ),
                context=vision_result,
                scout_result=str(scout_task.output.raw) if scout_task.output else "",
                intent=action_name,
                target=target,
                item_type=config.item_type or "",
                state=self.state,
            )
            if result == "FALLBACK_SKIP":
                return "FALLBACK_SKIP"
            return "failed" not in str(result).lower()

        # A veces solo el ejecutor.
        if config.agents == ["executor"]:
            result = self._agents["executor"].execute_task(
                task=create_executor_task(
                    target_item=target,
                    item_type=config.item_type,
                    action_intent=action_name,
                    agent=self._agents["executor"],
                    context_tasks=[]
                ),
                context=None,
                intent=action_name,
                target=target,
                item_type=config.item_type or "",
                state=self.state,
            )

            if result == "FALLBACK_SKIP":
                return "FALLBACK_SKIP"
            
            return "failed" not in str(result).lower()

        if any(a in config.agents for a in ["scout", "vision"]):
            self._unload_models()
        return True

    def _resolve_target(self, action_name: str, config, pddl_params: list[str]) -> str:
        #resolvemos el target para cada paso.
        if action_name == "navigate":
            raw = pddl_params[-1] if pddl_params else ""
            real = self.name_map.get(raw, raw)
            self.state["path_tracking"].append(real)
            print(f"[Orchestrator] path_tracking: {self.state['path_tracking']}")
            return real
        
        if action_name == "type_name":
            raw = pddl_params[-1] if pddl_params else ""
            base = raw.replace("_name", "") if raw.endswith("_name") else raw
            real = self.name_map.get(base, self.state.get("folder_name") or self.state.get("name", raw))
            return real

        if action_name == "click_new":
            return "New"

        if action_name == "select_type":
            if self.state.get("folder_name"):
                return "Folder"
            else:
                return self.state.get("item_type", "Text Document")

        if config.target_param:
            return self.state.get(config.target_param, "")

        return ""