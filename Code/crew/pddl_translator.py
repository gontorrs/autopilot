import json
from crewai import Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import Optional


class PDDLTranslatorAgent(BaseAgent):

    role: str = "PDDL Translator"
    goal: str = "Parse a PDDL plan text into a structured list of executable steps."
    backstory: str = "A deterministic parser that converts PDDL plan text into executable step dictionaries."

    def translate_to_steps(self, plan_text: str, mapping: dict, state: dict) -> list[dict]:
        """Parse PDDL plan into a list of step dicts (no CrewAI Tasks)."""
        steps = []
        for line in plan_text.strip().split("\n"):
            line = line.strip()
            if not line.startswith("(") or line.startswith(";") or "cost" in line.lower():
                continue
            parts = line.replace("(", "").replace(")", "").split()
            if not parts:
                continue
            action = parts[0]
            params = parts[1:]
            step = self._build_step(action, params, mapping, state)
            if step:
                steps.append(step)
        return steps

    def _resolve(self, pddl_id: str, mapping: dict) -> str:
        return mapping.get(pddl_id, pddl_id)

    def _build_step(self, action, params, mapping, state) -> dict | None:

        if action == "navigate":
            target = self._resolve(params[-1], mapping)
            return {"action": "navigate", "target": target, "item_type": "folder",
                    "description": f"Navigate to folder '{target}'"}

        if action == "open":
            target = self._resolve(params[0], mapping)
            return {"action": "open", "target": target, "item_type": "application",
                    "description": f"Open application '{target}'"}

        if action == "open_file":
            target = self._resolve(params[2], mapping)
            return {"action": "open_file", "target": target, "item_type": "file",
                    "description": f"Open file '{target}'"}

        if action == "copy":
            target = self._resolve(params[1], mapping)
            return {"action": "copy", "target": target, "item_type": "file",
                    "description": f"Select and copy file '{target}'"}

        if action == "paste":
            return {"action": "paste", "target": "", "item_type": "keyboard_action",
                    "description": "Paste with Ctrl+V"}

        if action == "navigate_back":
            return {"action": "navigate_back", "target": "", "item_type": "keyboard_action",
                    "description": "Go back with Alt+Left"}

        if action == "type":
            content = self._resolve(params[1], mapping)
            return {"action": "type", "target": content, "item_type": "text_content",
                    "description": f"Type text: '{content}'"}

        if action == "type_name":
            raw = self._resolve(params[1], mapping)
            base = raw.replace("_name", "") if raw.endswith("_name") else raw
            real = mapping.get(base, state.get("folder_name") or state.get("name", raw))
            return {"action": "type_name", "target": real, "item_type": "text_content",
                    "description": f"Type name '{real}' and press Enter"}

        if action == "search_text":
            content = self._resolve(params[1], mapping)
            return {"action": "search_text", "target": content, "item_type": "text_content",
                    "description": f"Search for text '{content}' with Ctrl+F"}

        if action == "change_text":
            content = self._resolve(params[1], mapping)
            style = self._resolve(params[2], mapping)
            return {"action": "change_text", "target": style, "item_type": "text_content",
                    "description": f"Apply '{style}' formatting to '{content}'"}

        if action == "delete_text":
            content = self._resolve(params[1], mapping)
            return {"action": "delete_text", "target": content, "item_type": "text_content",
                    "description": f"Delete text '{content}'"}

        if action == "click_new":
            return {"action": "click_new", "target": "New", "item_type": "button",
                    "description": "Click the 'New' button in File Explorer"}

        if action in ("create_file", "create_folder"):
            return {"action": action, "target": "New", "item_type": "button",
                    "description": "Click the 'New' button in File Explorer"}

        if action == "select_type":
            if state.get("folder_name"):
                real_target = "Folder"
            else:
                real_target = state.get("item_type", "Text Document")
            return {"action": "select_type", "target": real_target, "item_type": "menu_option",
                    "description": f"Select '{real_target}' from the menu"}

        return None

    def create_agent_executor(self, tools=None):
        pass

    def _execute_core_task(self, *args, **kwargs):
        return ""

    def get_delegation_tools(self, agents=None):
        return []

    def get_mcp_tools(self):
        return []

    def get_platform_tools(self):
        return []
    
    async def aexecute_task(self, task, context=None, tools=None):
        return self.execute_task(task, context, tools)
    
    def execute_task(self, task, context=None, tools=None, plan_text=None, mapping=None, state=None, **kwargs):
        if plan_text is None:
            payload = json.loads(task.description)
            plan_text = payload["plan"]
            mapping = payload["mapping"]
            state = payload.get("state", {})
        return self.translate_to_steps(plan_text, mapping, state)