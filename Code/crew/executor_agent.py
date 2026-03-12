import json
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import Optional
from crew.tools import click, fallback_search_tool, type_text, format_text

class ExecutorAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            tools=[],
            role="GUI Action Executor",
            goal="Execute the correct GUI action based on the intent and coordinates provided.",
            backstory="You are a deterministic executor. You receive an intent and act on it directly without reasoning.",
        )

    def execute_task(self, task, context=None, tools=None, intent="", target="", item_type="", scout_result="", state=None) -> str:
        intent = (task.config or {}).get("intent", intent)
        target = (task.config or {}).get("target", target)
        item_type = (task.config or {}).get("item_type", item_type)
        
        coords = self._extract_coords(context)
        scout_found = "YES" in scout_result.upper()

        if intent in ("open", "navigate", "open_file"):
            if coords and scout_found:
                return click(coords[0], coords[1])
            file_name = (state or {}).get("file_name", target)
            fallback_search_tool(file_name, intent=intent)
            return "FALLBACK_SKIP"

        elif intent == "search_text":
            print(f"DEBUG executor search_text — target: '{target}'")
            return fallback_search_tool(target, intent="search_text")

        elif intent == "change_text":
            print(f"Changing text style to '{target}'.")
            return format_text(target)  # target is the style

        elif intent == "type":
            return type_text((state or {}).get("app_name", ""), target)

        return f"FAILED: Unknown intent '{intent}'."

    def _extract_coords(self, context: Optional[str]) -> Optional[tuple]:
        if not context:
            return None
        data = json.loads(context)
        x, y = data.get("x"), data.get("y")
        if x is not None and y is not None:
            return (x, y)
        return None
    

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