import json
import re
import os
import ollama
import time
from crewai import Task, tools
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import Optional, Any
from tools.tools import take_screenshot, parse_coordinates, correct_coord
from tools.vlm_prompts import vlm_tools

class VLMBaseAgent(BaseAgent):
    vlm_model_name: str
    function_calling_llm: Optional[Any] = None
    step_callback: Optional[Any] = None
    last_messages: list = []
    agent_tag: str = "agent"
    step_count: int = 0

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
            #keep_alive=0
        )
        return response

    def _call_ollama_tools(self, prompt: str, img: bytes) -> dict:
        response = ollama.chat(
            model=self.vlm_model_name,
            messages=[{"role": "user", "content": prompt, "images": [img]}],
            tools=vlm_tools,
            options={"temperature": 0.1},
            #keep_alive=0
        )
        return response

    def _save_screenshot(self, img: bytes) -> None:
            self.step_count += 1
            nombre_archivo = f"logs/crew-ai-plain/search/v3/{self.agent_tag}_{self.step_count:02d}.png"
            with open(nombre_archivo, "wb") as f:
                f.write(img)
            print(f"[{self.agent_tag}] screenshot guardado en: {nombre_archivo}")

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
    
    async def aexecute_task(self, task, context=None, tools=None):
        return self.execute_task(task, context, tools)

    @staticmethod
    def _parse_target(description: str) -> str:
        match = re.search(r"'([^']+)'", description)
        return match.group(1) if match else ""

    @staticmethod
    def _parse_item_type(description: str) -> str:
        match = re.search(r"\(type:\s*([^)]+)\)", description)
        return match.group(1).strip() if match else ""


class ScoutAgent(VLMBaseAgent):
    agent_tag: str = "scout"
    def __init__(self, vlm_model_name: str):
        super().__init__(
            vlm_model_name=vlm_model_name,
            role="Screen Scout",
            goal="Verify that the required elements are visible on screen before any action is taken.",
            backstory="You are a vision agent specialized in confirming the presence of UI elements. You always check before acting.",
        )

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[list] = None) -> str:
        img = take_screenshot()
        self._save_screenshot(img)
        prompt = task.description
        response = self._call_ollama(prompt, img)
        result = response["message"]["content"].strip()
        print(f"scout response: '{result}'")
        return result


class VisionAgent(VLMBaseAgent):
    agent_tag: str = "vision"
    def __init__(self, vlm_model_name: str):
        super().__init__(
            vlm_model_name=vlm_model_name,
            role="Vision Coordinate Finder",
            goal="Observe the screenshot and identify where to click.",
            backstory="You are a computer vision expert at locating elements in GUIs and returning their coordinates.",
        )

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[list] = None) -> str:
        img = take_screenshot()
        self._save_screenshot(img)
        prompt = task.description
        response = self._call_ollama(prompt, img)
        content = response["message"]["content"].strip()
        match = re.search(r'\[(\d+),\s*(\d+)\]', content)
        if match:
            coords = [int(match.group(1)), int(match.group(2))]
            result = parse_coordinates(coords)
            if result:
                x, y = correct_coord(result[0], result[1])
                return json.dumps({"x": x, "y": y})
        return json.dumps({"x": None, "y": None})


class QAAgent(VLMBaseAgent):
    agent_tag: str = "qa"
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
        self._save_screenshot(img)
        prompt = task.description
        print(prompt)
        response = self._call_ollama(prompt, img)
        result = response["message"]["content"].strip()
        print(f"qa response: '{result}'")
        return result