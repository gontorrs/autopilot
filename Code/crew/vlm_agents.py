import json
import re
import ollama
import time
from crewai import Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import Optional, Any
from crew.tools import take_screenshot, parse_coordinates
from tools.vlm_tools import get_coordinates_prompt, verification_prompt_file, check_item_prompt, vlm_tools, verification_prompt_formatting

class VLMBaseAgent(BaseAgent):
    vlm_model_name: str
    function_calling_llm: Optional[Any] = None
    step_callback: Optional[Any] = None
    last_messages: list = []

    def __init__(self, vlm_model_name: str, **kwargs):
        super().__init__(
            vlm_model_name=vlm_model_name,
            tools=[],
            **kwargs
        )

    def _call_ollama(self, prompt: str, img: bytes) -> dict:
        response = ollama.chat(
            model=self.vlm_model_name,
            messages=[{"role": "user", "content": prompt, "images": [img]}],
        )
        return response

    def _call_ollama_tools(self, prompt: str, img: bytes) -> dict:
        response = ollama.chat(
            model=self.vlm_model_name,
            messages=[{"role": "user", "content": prompt, "images": [img]}],
            tools=vlm_tools,
            options={"temperature": 0.1},
        )
        return response

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[list] = None) -> str:
        raise NotImplementedError

    def create_agent_executor(self, tools=None):
        self.agent_executor = self
        return self

    def invoke(self, inputs: dict, config=None) -> dict:
        task = inputs.get("task") or inputs.get("input", "")
        result = self.execute_task(task)
        return {"output": result, "messages": []}

    def _execute_core_task(self, *args, **kwargs) -> str:
        return ""

    def get_delegation_tools(self, agents=None):
        return []

    def get_mcp_tools(self):
        return []

    def get_platform_tools(self):
        return []

    @staticmethod
    def _parse_target(description: str) -> str:
        match = re.search(r"'([^']+)'", description)
        return match.group(1) if match else ""

    @staticmethod
    def _parse_item_type(description: str) -> str:
        match = re.search(r"\(type:\s*([^)]+)\)", description)
        return match.group(1).strip() if match else ""


class ScoutAgent(VLMBaseAgent):
    def __init__(self, vlm_model_name: str):
        super().__init__(
            vlm_model_name=vlm_model_name,
            role="Screen Scout",
            goal="Verify that the required elements are visible on screen before any action is taken.",
            backstory="You are a vision agent specialized in confirming the presence of UI elements. You always check before acting.",
        )

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[list] = None) -> str:
        img = take_screenshot()
        target = self._parse_target(task.description)
        item_type = self._parse_item_type(task.description)
        print(f"scout target: '{target}' ; type: '{item_type}'")
        prompt = check_item_prompt(target, item_type)
        response = self._call_ollama(prompt, img)
        print(f"response: {response['message']['content'].strip()}")
        return response["message"]["content"].strip()


class VisionAgent(VLMBaseAgent):
    def __init__(self, vlm_model_name: str):
        super().__init__(
            vlm_model_name=vlm_model_name,
            role="Vision Coordinate Finder",
            goal="Observe the screenshot and identify where to click. It can be a folder, file, application, button or area.",
            backstory="You are a computer vision expert at locating elements in GUIs and returning their coordinates.",
        )

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[list] = None) -> str:
        img = take_screenshot()
        target = self._parse_target(task.description)
        print(f"vision target: '{target}'")
        prompt = get_coordinates_prompt(target)
        response = self._call_ollama_tools(prompt, img)
        if response["message"].get("tool_calls"):
            raw_coords = response["message"]["tool_calls"][0]["function"]["arguments"].get("coordinate")
            coords = parse_coordinates(raw_coords)
            if coords:
                return json.dumps({"x": coords[0], "y": coords[1]})
        return json.dumps({"x": None, "y": None})


class QAAgent(VLMBaseAgent):
    def __init__(self, vlm_model_name: str):
        super().__init__(
            vlm_model_name=vlm_model_name,
            role="QA Verifier",
            goal="Verify that the executed actions have fulfilled the user's original objective.",
            backstory="You are a strict QA agent. You take screenshots to confirm the screen reflects the requested goal.",
        )

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[list] = None) -> str:
        time.sleep(2)
        img = take_screenshot()
        target = self._parse_target(task.description)
        print(f"qa goal: '{target}'")
        qa_type = (task.config or {}).get("qa_type", "default")
        style = (task.config or {}).get("style", "bold")
        if qa_type == "formatting":
            prompt = verification_prompt_formatting(target, style)
        else:
            prompt = verification_prompt_file(target)
        response = self._call_ollama(prompt, img)
        return response["message"]["content"].strip()