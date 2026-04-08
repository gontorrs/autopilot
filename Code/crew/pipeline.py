import json
import re
from crewai import Crew, Process, Task
from crewai.flow.flow import Flow, listen, start
from crew.agents import create_agents
from utils.tasks import create_intent_task, create_planner_task


class PipelineFlow(Flow):

    def __init__(self, user_input: str, planner_model: str, vlm_model: str, intention_model: str):
        super().__init__()
        self.state["user_input"] = user_input
        self.state["planner_model"] = planner_model
        self.state["vlm_model"] = vlm_model
        self.state["intention_model"] = intention_model
        self._agents = create_agents(planner_model, vlm_model, intention_model)

    @start()
    def classify_intent(self):
        task = create_intent_task(self.state["user_input"], self._agents["intention"])
        crew = Crew(
            agents=[self._agents["intention"]],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff()

        # Parsear resultado
        data = None
        for match in re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result.raw):
            try:
                candidate = json.loads(match.group(0).replace("'", '"'))
                if "intent" in candidate:
                    data = candidate
                    break
            except (json.JSONDecodeError, ValueError):
                continue

        if not data:
            raise ValueError(f"No JSON with 'intent' key found in: {result.raw}")

        self.state["intent_name"] = data.get("intent")
        if self.state["intent_name"] and not self.state["intent_name"].endswith("_tool"):
            self.state["intent_name"] += "_tool"
        self.state["intent_args"] = data.get("args", {})

        print(f"[Flow] Intent: {self.state['intent_name']}")
        return self.state["intent_name"]

    @listen(classify_intent)
    def build_state(self):
        intent_name = self.state["intent_name"]
        args = self.state["intent_args"]
        sanitize = self._agents["planner"].sanitize

        if intent_name == 'navigate_tool':
            path = ["Default"] + args.get('path', [])
            self.state["task_state"] = {
                "prompt": self.state["user_input"],
                "file_name": args.get('file_name', ''),
                "app_name": args.get('app_name', ''),
                "path": path,
                "vlm_model": self.state["vlm_model"],
                "planner_model": self.state["planner_model"],
                "status": "start",
                "goal": "(open_file " + sanitize(args.get('file_name', '')) + ")",
                "attempts": 0,
            }

        elif intent_name == 'write_tool':
            self.state["task_state"] = {
                "prompt": self.state["user_input"],
                "app_name": args.get('application', 'notepad'),
                "content": args.get('text', ''),
                "vlm_model": self.state["vlm_model"],
                "planner_model": self.state["planner_model"],
                "status": "start",
                "goal": "(typed_text " + sanitize(args.get('text', '')) + ")",
                "attempts": 0,
            }

        elif intent_name == 'change_tool':
            path = ["Default"] + args.get('path', [])
            self.state["task_state"] = {
                "prompt": self.state["user_input"],
                "app_name": args.get('application'),
                "file_name": args.get('file_name', ''),
                "content": args.get('content', ''),
                "style": args.get('style', ''),
                "path": path,
                "goal": "(changed_text " + sanitize(args.get('style', '')) + ")",
                "vlm_model": self.state["vlm_model"],
                "planner_model": self.state["planner_model"],
                "status": "start",
                "attempts": 0,
            }

        elif intent_name == 'create_tool':
            item_type = args.get('item_type', 'folder')
            name_raw = args.get('name', '')
            path = ["Default"] + args.get('path', [])
            self.state["task_state"] = {
                "prompt": self.state["user_input"],
                "app_name": args.get('application'),
                "file_name_new": name_raw if item_type == "file" else None,
                "folder_name": name_raw if item_type == "folder" else None,
                "name": name_raw,
                "path": path,
                "goal": f"(created {sanitize(name_raw)}_name)",
                "vlm_model": self.state["vlm_model"],
                "planner_model": self.state["planner_model"],
                "status": "start",
                "attempts": 0,
            }

        elif intent_name == 'delete_tool':
            path = ["Default"] + args.get('path', [])
            self.state["task_state"] = {
                "prompt": self.state["user_input"],
                "app_name": args.get('application'),
                "file_name": args.get('file_name', ''),
                "content": args.get('content', ''),
                "path": path,
                "goal": f"(delete_text {sanitize(args.get('content', ''))})",
                "vlm_model": self.state["vlm_model"],
                "planner_model": self.state["planner_model"],
                "status": "start",
                "attempts": 0,
            }

        elif intent_name == 'search_tool':
            path = ["Default"] + args.get('path', [])
            self.state["task_state"] = {
                "prompt": self.state["user_input"],
                "app_name": args.get('application'),
                "file_name": args.get('file_name', ''),
                "content": args.get('content', ''),
                "path": path,
                "goal": f"(text_searched {sanitize(args.get('content', ''))})",
                "vlm_model": self.state["vlm_model"],
                "planner_model": self.state["planner_model"],
                "status": "start",
                "attempts": 0,
            }

        elif intent_name == 'copy_paste_tool':
            path_copy = ["Default"] + args.get('path_to_copy', [])
            path_paste = ["Default"] + args.get('path_to_paste', [])
            self.state["task_state"] = {
                "prompt": self.state["user_input"],
                "app_name": args.get('application', 'file explorer'),
                "file_name": args.get('file_name', ''),
                "path_to_copy": path_copy,
                "path_to_paste": path_paste,
                "cut": args.get('operation', 'copy') == 'cut',
                "vlm_model": self.state["vlm_model"],
                "planner_model": self.state["planner_model"],
                "status": "start",
                "goal": f"(pasted {sanitize(args.get('file_name', ''))} {sanitize(args.get('path_to_paste', [''])[-1])})",
                "attempts": 0,
            }

        else:
            print(f"[Flow] Intent not classified: {intent_name}")
            self.state["task_state"] = None
            return None

        print(f"[Flow] State built for intent: {intent_name}")
        return self.state["task_state"]

    @listen(build_state)
    def generate_plan(self):
        if not self.state.get("task_state"):
            return None

        task_state = self.state["task_state"]
        planner = self._agents["planner"]

        task = create_planner_task(task_state, planner, "navigate_problem.pddl")
        result = planner.execute_task(
            task=task,
            state_dict=task_state,
            output_filename="navigate_problem.pddl",
        )

        if not result or "Planner failed" in str(result):
            print("[Flow] Planner failed.")
            return None

        self.state["plan_result"] = result
        print("[Flow] Plan generated.")
        return result
    

    @listen(generate_plan)
    def translate_plan(self):
        if not self.state.get("plan_result"):
            return None

        plan_result = self.state["plan_result"]
        task_state = self.state["task_state"]

        # El translator necesita plan + mapping + state
        payload = json.dumps({
            "plan": plan_result["plan"],
            "mapping": plan_result["mapping"],
            "state": task_state,
        })

        translator_task = Task(
            description=payload,
            expected_output="List of executable Tasks.",
            agent=self._agents["translator"],
        )

        execution_tasks = self._agents["translator"].execute_task(translator_task)
        self.state["execution_tasks"] = execution_tasks

        print(f"[Flow] {len(execution_tasks)} execution tasks created.")
        return execution_tasks


    @listen(translate_plan)
    def execute_steps(self):
        if not self.state.get("execution_tasks"):
            return None

        execution_tasks = self.state["execution_tasks"]
        task_state = self.state["task_state"]

        print(f"\n[Flow] ========== EXECUTION ==========")
        print(f"[Flow] {len(execution_tasks)} tasks to execute")

        # Extract unique intents from the plan for the manager tools
        from utils.tools import create_manager_tools
        plan_intents = []
        for t in execution_tasks:
            cfg = getattr(t, "config", None) or {}
            action = cfg.get("action", "")
            if action and action != "final":
                plan_intents.append(action)
        plan_intents = list(set(plan_intents))
        print(f"[Flow] Plan intents extracted: {plan_intents}")
        for t in execution_tasks:
            cfg = getattr(t, "config", None) or {}
            print(f"[DEBUG] task config: {cfg}")
        manager_tools = create_manager_tools(self._agents, task_state, plan_intents)
        self._agents["manager"].tools = manager_tools

        # Assign manager to each task from the translator
        for task in execution_tasks:
            task.agent = self._agents["manager"]

        crew = Crew(
            agents=[self._agents["manager"]],
            tasks=execution_tasks,
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()

        # QA final — ejecutado por código, no por el LLM
        from tools.vlm_tools import (
            verification_prompt_file,
            verification_prompt_formatting,
            verification_prompt_delete,
            verification_prompt_copy_paste,
        )

        goal = task_state.get("goal", "")
        style = task_state.get("style", "")

        if "changed_text" in goal:
            prompt = verification_prompt_formatting(goal, style)
        elif "delete_text" in goal:
            prompt = verification_prompt_delete(goal)
        elif "pasted" in goal:
            dest = task_state.get("path_to_paste", [""])[-1] if task_state.get("path_to_paste") else ""
            prompt = verification_prompt_copy_paste(goal, dest)
        else:
            prompt = verification_prompt_file(goal)

        qa_task = Task(
            description=prompt,
            expected_output="YES or NO",
            agent=self._agents["qa"],
        )
        qa_result = self._agents["qa"].execute_task(qa_task)
        print(f"\n[Flow] QA final: {qa_result}")

        self.state["final_result"] = qa_result
        print(f"[Flow] Pipeline finished. Result: {qa_result}")
        return qa_result