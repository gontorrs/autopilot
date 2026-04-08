import json
from crewai import Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import Optional


class PDDLTranslatorAgent(BaseAgent):

    role: str = "PDDL Translator"
    goal: str = "Parse a PDDL plan text into a structured list of CrewAI Tasks."
    backstory: str = "A deterministic parser that converts PDDL plan text into executable CrewAI Tasks."

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[list] = None) -> list[Task]:
        payload = json.loads(task.description)
        plan_text = payload["plan"]
        mapping = payload["mapping"]
        state = payload.get("state", {})
        return self._parse(plan_text, mapping, state)

    def _resolve(self, pddl_id: str, mapping: dict) -> str:
        return mapping.get(pddl_id, pddl_id)

    def _parse(self, plan_text: str, mapping: dict, state: dict) -> list[Task]:
        tasks = []
        for line in plan_text.strip().split("\n"):
            line = line.strip()
            if not line.startswith("(") or line.startswith(";") or "cost" in line.lower():
                continue
            parts = line.replace("(", "").replace(")", "").split()
            if not parts:
                continue
            action = parts[0]
            params = parts[1:]
            task = self._build_task(action, params, mapping, state)
            if task:
                tasks.append(task)

        #tasks.append(self._build_qa_task(state))
        return tasks

    def _build_task(self, action, params, mapping, state):

        if action == "navigate":
            target = self._resolve(params[-1], mapping)
            return Task(
                description=f"Navigate to the folder '{target}' in File Explorer. Find it visually on screen and double-click it.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": target, "item_type": "folder"},
            )

        if action == "open":
            target = self._resolve(params[0], mapping)
            return Task(
                description=f"Open the application '{target}'. Find it on the taskbar, desktop or start menu and click it.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": target, "item_type": "application"},
            )

        if action == "open_file":
            target = self._resolve(params[2], mapping)
            return Task(
                description=f"Open the file '{target}'. Find it visually on screen and double-click it.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": target, "item_type": "file"},
            )

        if action == "copy":
            target = self._resolve(params[1], mapping)
            return Task(
                description=f"Select and copy the file '{target}'. Find it on screen and use Ctrl+C.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": target, "item_type": "file"},
            )

        if action == "paste":
            return Task(
                description="Paste the copied file using Ctrl+V. This is a keyboard action.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": "", "item_type": "keyboard_action"},
            )

        if action == "navigate_back":
            return Task(
                description="Go back to the previous folder using Alt+Left. This is a keyboard action.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": "", "item_type": "keyboard_action"},
            )

        if action == "type":
            content = self._resolve(params[1], mapping)
            return Task(
                description=f"Type the following text: '{content}'. This is a keyboard action.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": content, "item_type": "text_content"},
            )

        if action == "type_name":
            raw = self._resolve(params[1], mapping)
            base = raw.replace("_name", "") if raw.endswith("_name") else raw
            real = mapping.get(base, state.get("folder_name") or state.get("name", raw))
            return Task(
                description=f"Type the name '{real}' and press Enter. This is a keyboard action.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": real, "item_type": "text_content"},
            )

        if action == "search_text":
            content = self._resolve(params[1], mapping)
            return Task(
                description=f"Search for the text '{content}' using Ctrl+F. This is a keyboard action.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": content, "item_type": "text_content"},
            )

        if action == "change_text":
            content = self._resolve(params[1], mapping)
            style = self._resolve(params[2], mapping)
            return Task(
                description=f"Apply '{style}' formatting to the text '{content}'. This is a keyboard action.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": style, "item_type": "text_content"},
            )

        if action == "delete_text":
            content = self._resolve(params[1], mapping)
            return Task(
                description=f"Delete the text '{content}' from the document. This is a keyboard action.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": content, "item_type": "text_content"},
            )

        if action == "click_new":
            return Task(
                description="Click the 'New' button in File Explorer. Find it visually on screen.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": "New", "item_type": "button"},
            )

        if action == "create_file" or action == "create_folder":
            return Task(
                description="Click the 'New' button in File Explorer. Find it visually on screen.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": "New", "item_type": "button"},
            )

        if action == "select_type":
            if state.get("folder_name"):
                real_target = "Folder"
            else:
                real_target = state.get("item_type", "Text Document")
            return Task(
                description=f"Select '{real_target}' from the menu. Find it visually on screen.",
                expected_output="SUCCESS or FAILED",
                config={"action": action, "target": real_target, "item_type": "menu_option"},
            )

        return None

    def _build_qa_task(self, state):
        goal = state.get("goal", "")
        if "changed_text" in goal:
            qa_type, desc = "formatting", "Verify that the text formatting was applied correctly."
        elif "delete_text" in goal:
            qa_type, desc = "delete", "Verify that the text was deleted from the document."
        elif "pasted" in goal:
            qa_type, desc = "copy_paste", "Verify that the file was pasted in the destination folder."
        elif "typed_text" in goal:
            qa_type, desc = "default", "Verify that the text was typed correctly."
        elif "open_file" in goal:
            qa_type, desc = "default", "Verify that the file was opened successfully."
        elif "created" in goal:
            qa_type, desc = "default", "Verify that the file or folder was created."
        else:
            qa_type, desc = "default", "Verify that the user's request was completed."

        return Task(
            description=desc,
            expected_output="YES or NO",
            config={"action": "final", "qa_type": qa_type, "state": state},
        )

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