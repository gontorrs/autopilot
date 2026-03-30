# utils/crew_tools.py
import json
import pyautogui as py
import io
import time
from crewai.tools import tool
from typing import List

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

def ctrl_find(file_name):
    py.press('win')
    time.sleep(1)
    py.write(file_name, interval=0.05)
    time.sleep(1)
    print(f"3. Opening file...")
    py.press('enter')
    time.sleep(1)

def click(x: int, y: int) -> str:
    py.moveTo(x, y, duration=1)
    py.doubleClick()
    time.sleep(1)
    return f"SUCCESS: Clicked at coordinates {x}, {y}."


def fallback_search_tool(target: str, intent: str = "") -> str:
    print(f"DEBUG fallback_search_tool called — target: '{target}' ; intent: '{intent}'")
    time.sleep(1)
    if intent == "search_text":
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
    else:
        time.sleep(1)
        ctrl_find(target)
    time.sleep(1)
    return f"SUCCESS: Fallback search executed for {target}."

def type_text(app_name, content):
    #content_extended = f"Is there any written content in the open document, regardless of this: {content}?"
    if "notepad" not in app_name.lower():
        time.sleep(1)
        py.press('enter')
    time.sleep(1)
    print("Writing content...")
    py.write(content, interval=0.05)
    print("Content written.sdafkljasdklfjasdlñkfjañslkdfjalñsdkfjlñaskdfjñlaksdjfñalskdfjañskldfjalñskdfjñaslkdfjlñasdkfjasñldkfjasdfñlkja")
    return {"status": "content written"}

def format_text(style: str) -> str:
    time.sleep(2)
    if 'bold' in style:
        py.hotkey('ctrl', 'b')
    elif 'italic' in style:
        py.hotkey('ctrl', 'i')
    elif 'under' in style:
        py.hotkey('ctrl', 'u')
    else:
        print("No style recognized")
    py.press('left')
    time.sleep(3)
    return {"status": "text formatted"}

def create_tools() -> dict:
    
    @tool("navigate_tool")
    def navigate_tool(file_name: str, path: List[str] = [], app_name: str = "File Explorer") -> str:
        """
        Use this if the user's ONLY requirement is to open a file and navigate to a specific file or folder, nothing else, only this action.
        
        Args:
            file_name: Name of the final file to search/open. Always required.
            path: An ordered list of folders to navigate, for example: ["downloads", "masters"]. If path is not provided return [].
            app_name: Application to use (e.g., "File Explorer").
        """

        result = {
            "intent": "navigate_tool",
            "args": {"file_name": file_name, "path": path, "app_name": app_name}
        }
        return f"SUCCESS. DO NOT USE ANY MORE TOOLS. Final Answer: {json.dumps(result)}"

    @tool("write_tool")
    def write_tool(text: str, application: str = "notepad") -> str:
        """
        Open a text editor application and type specific content into it.
        
        Args:
            application: The name of the Windows application to open (e.g., 'notepad' or 'word'). If application is not stated, default to notepad. (Options: "notepad", "word", "power point")
            text: The content text that needs to be written inside the application.
        """
        result = {
            "intent": "write_tool",
            "args": {"application": application, "text": text}
        }
        return f"SUCCESS. DO NOT USE ANY MORE TOOLS. Final Answer: {json.dumps(result)}"

    @tool("change_tool")
    def change_tool(application: str, file_name: str, content: str, style: str, path: List[str] = []) -> str:
        """
        If the user asks to open a file and apply formatting to specific text inside it, use this tool.
        ONLY use this when the user explicitly asks to format text (bold, italic, underlined) inside a document.
        Apply formatting to a text segment. 
        IMPORTANT: The 'application' argument MUST be 'file explorer' if the file needs 
        to be located through folders before being opened.
        Args:
            application: The application required to START this process if File Explorer.
            file_name: Name of the final file to search/open. Always required.
            content: The specific text content inside the document that needs to be formatted.
            style: The style to apply to the text content. (Options: "bold", "italic", "underlined")
            path: An ordered list of folders to navigate, for example: ["downloads", "masters"]. If path is not provided return [].
        """
        result = {
            "intent": "change_tool",
            "args": {
                "application": application, 
                "file_name": file_name, 
                "content": content, 
                "style": style, 
                "path": path
            }
        }
        return f"SUCCESS. DO NOT USE ANY MORE TOOLS. Final Answer: {json.dumps(result)}"

    return {
        "navigate_tool": navigate_tool,
        "write_tool": write_tool,
        "change_tool": change_tool
    }