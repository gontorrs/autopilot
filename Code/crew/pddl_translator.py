from crewai import Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import Optional


class PDDLTranslatorAgent(BaseAgent):

    role: str = "PDDL Translator"
    goal: str = "Parse a PDDL plan text into a structured list of action steps."
    backstory: str = "A deterministic parser that converts PDDL plan text into Python dicts."

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[list] = None) -> str:
        import json
        steps = self._parse(task.description)
        return json.dumps(steps)

    def _parse(self, plan_text: str) -> list[dict]:
        steps = []

        for line in plan_text.strip().split("\n"):
            line = line.strip()

            # Skip comments, empty lines and Fast Downward cost line
            if not line.startswith("(") or line.startswith(";") or "cost" in line.lower():
                continue

            parts = line.replace("(", "").replace(")", "").split()
            if not parts:
                continue

            action = parts[0]
            # quito Default del path.
            params = [p for p in parts[1:] if p.lower() != "default"]

            steps.append({"action": action, "params": params})

        # Always append the final QA step
        steps.append({"action": "final", "params": []})

        return steps

    def create_agent_executor(self, tools=None) -> None:
        pass

    def _execute_core_task(self, *args, **kwargs) -> str:
        return ""
    
    def get_delegation_tools(self, agents=None):
        return []

    def get_mcp_tools(self):
        return []

    def get_platform_tools(self):
        return []