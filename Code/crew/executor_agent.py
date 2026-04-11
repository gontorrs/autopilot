import json
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import Optional, Any
from tools.tools import click, win_search, type_text, format_text
import pyautogui as py
import time

class ExecutorAgent(BaseAgent):

    function_calling_llm: Optional[BaseAgent] = None
    llm: Optional[BaseAgent] = None
    step_callback: Optional[Any] = None
    last_messages: list = []

    def __init__(self):
        super().__init__(
            tools=[],
            role="GUI Action Executor",
            goal="Execute the correct GUI action based on the intent and coordinates provided.",
            backstory="You are a deterministic executor. You receive an intent and act on it directly without reasoning.",
        )

    def _parse_coords(self, coordinates) -> tuple | None:
        if not coordinates:
            return None
        if isinstance(coordinates, dict):
            x, y = coordinates.get("x"), coordinates.get("y")
            if x is not None and y is not None:
                return (int(x), int(y))
        if isinstance(coordinates, str):
            try:
                d = json.loads(coordinates.replace("'", '"'))
                if d.get("x") is not None and d.get("y") is not None:
                    return (int(d["x"]), int(d["y"]))
            except (json.JSONDecodeError, TypeError):
                pass
        return None

    def execute_task(self, task, context=None, tools=None, intent="", target="", scout_result="", coordinates="", state=None, **kwargs):
        config = task.config or {}
        intent = intent or config.get("intent", "")
        target = target or config.get("target", "")
        scout_result = scout_result or config.get("scout_result", "")
        state = state or config.get("state", {})
        
        coords = self._parse_coords(coordinates or config.get("coordinates", ""))
        scout_found = "YES" in (scout_result or "").upper()

        if intent in ("open", "navigate", "open_file", "click_new", "select_type"):
            if coords and scout_found:
                return click(coords[0], coords[1], intent=intent)
            
            if intent in ("navigate", "open_file", "open"):
                file_name = target or (state or {}).get("file_name") or (state or {}).get("folder_name") or ""
                win_search(file_name)
                
                if intent == "open_file":
                    return "FALLBACK_SKIP"
                else:
                    return "FALLBACK_SUCCESS"
            
            return f"FAILED: Could not find '{target}' on screen."

        elif intent == "search_text":
            time.sleep(1)
            print(f"DEBUG executor search_text — target: '{target}'")
            time.sleep(1)
            py.keyDown('ctrlleft')
            time.sleep(0.3)
            py.press('f')
            time.sleep(0.2)
            py.keyUp('ctrlleft')
            time.sleep(1)
            py.write(target, interval=0.05)
            py.press('enter')
            time.sleep(1)
            py.press('esc')
            return "SUCCESS: Search executed."

        elif intent == "change_text":
            print(f"Changing text style to '{target}'.")
            return format_text(target)  # target is the style

        elif intent == "type":
            return type_text((state or {}).get("app_name", ""), target)
        
        elif intent == "navigate_back":
            time.sleep(1)
            return py.hotkey('alt', 'left')
        
        elif intent == "delete_text":
            py.press('backspace')
            return "SUCCESS: Pressed delete key."
        
        elif intent == "copy":
            if coords and scout_found:
                click(coords[0], coords[1], intent="copy")
            time.sleep(0.2)
            is_cut = state.get("cut", False)
            if is_cut:
                py.hotkey('ctrl', 'x')
            else:
                py.hotkey('ctrl', 'c')
            return "SUCCESS: Cut/Copied to clipboard."

        elif intent == "paste":
            time.sleep(1)
            py.hotkey('ctrl', 'v')
            return "SUCCESS: Pasted."
        
        # type_name: solo escribir el nombre y pulsar Enter (no necesita VLM)
        elif intent == "type_name":
            time.sleep(0.5)
            py.write(target, interval=0.05)
            time.sleep(0.3)
            py.press('enter')
            time.sleep(1)
            print(f"[Orchestrator] type_name escrito: '{target}'")
            return True

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
    
    async def aexecute_task(self, task, context=None, tools=None):
        return self.execute_task(task, context, tools)