# utils/crew_tools.py
import json
import pyautogui as py
import ollama
import io
import time
from crewai.tools import tool

from tools.planner_tools import planner_tools
from tools.vlm_tools import get_coordinates_prompt, verification_prompt_file, check_item_prompt, vlm_tools, ctrl_find

def take_screenshot() -> bytes:
    screenshot = py.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    return buffer.getvalue()

def parse_coordinates(coords):
    screen_w, screen_h = py.size()
    if coords:
        real_x = int(coords[0] / 1000 * screen_w)
        real_y = int(coords[1] / 1000 * screen_h)
        return real_x, real_y
    return None

def create_tools(planner_model_name: str, vlm_model_name: str) -> dict:

    @tool("intention_tool")
    def intention_tool(user_query: str) -> str:
        """Analyzes natural language and returns the intent and arguments in JSON format.
        Args:
            user_query: The user's instruction.
        """
        response = ollama.chat(
            model=planner_model_name,
            messages=[{"role": "user", "content": user_query}],
            tools=planner_tools,
        )
        msg = response["message"]
        
        if msg.get("tool_calls"):
            tool_call = msg["tool_calls"][0]
            json_result = json.dumps({
                "intent": tool_call["function"]["name"],
                "args": tool_call["function"]["arguments"]
            })
            return f"SUCCESS. DO NOT USE ANY MORE TOOLS. Give this exact JSON as your Final Answer: {json_result}"

        return "FAILED. Intent not found."

    @tool("scout_tool")
    def scout_tool(item: str, type_item: str) -> str:
        """Checks if an element is visible on screen. Returns YES or NO.
        Args:
            item: Name of the element to look for.
            type_item: application | file | folder | textcontent
        """
        img = take_screenshot()
        response = ollama.chat(
            model=vlm_model_name,
            messages=[{"role": "user", "content": check_item_prompt(item, type_item), "images": [img]}],
        )
        return response["message"]["content"].strip()

    @tool("vision_tool")
    def vision_tool(target: str) -> str:
        """Returns exact pixel coordinates.
        Args:
            target: Description of the element.
        """
        img = take_screenshot()
        response = ollama.chat(
            model=vlm_model_name,
            messages=[{"role": "user", "content": get_coordinates_prompt(target), "images": [img]}],
            tools=vlm_tools,
            options={"temperature": 0.1},
        )
        if response["message"].get("tool_calls"):
            coords = parse_coordinates(response["message"]["tool_calls"][0]["function"]["arguments"].get("coordinate"))
            if coords:
                return json.dumps({"x": coords[0], "y": coords[1]})
        return json.dumps({"x": None, "y": None})

    @tool("qa_tool")
    def qa_tool(goal: str) -> str:
        """Verifies if the specified goal is achieved on the current screen.
        Args:
            goal: Description of the objective.
        """
        img = take_screenshot()
        response = ollama.chat(
            model=vlm_model_name,
            messages=[{"role": "user", "content": verification_prompt_file(goal), "images": [img]}],
        )
        return response["message"]["content"].strip()

    @tool("click_tool")
    def click_tool(x: int, y: int) -> str:
        """Clicks on the given screen coordinates. Use this when coordinates are found."""
        py.moveTo(x, y, duration=1)
        #Siempre doble_click()
        py.doubleClick()
        time.sleep(1)
        return f"SUCCESS: Clicked at coordinates {x}, {y}."

    @tool("search_tool")
    def fallback_search_tool(target: str, item_type: str) -> str:
        """Use this when coordinates are null or the item is not visible. It handles Ctrl+F or system search."""
        if item_type == "text_content":
            py.hotkey('ctrl', 'f')
            time.sleep(0.5)
            py.write(target)
            py.press('enter')
            py.press('esc')
        else:
            ctrl_find(target)
        return f"SUCCESS: Fallback search executed for {target}."

    return {
        "intention_tool": intention_tool,
        "scout_tool": scout_tool,
        "vision_tool": vision_tool,
        "qa_tool": qa_tool,
        "click_tool": click_tool,
        "search_tool": fallback_search_tool
    }