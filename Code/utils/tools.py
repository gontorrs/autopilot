# utils/crew_tools.py
import json
import pyautogui as py
import io
import time
from crewai.tools import tool
from typing import Any, List

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

def click(x: int, y: int, intent: str = "") -> str:
    py.moveTo(x, y, duration=1)
    if intent in ("navigate", "open_file"):
        py.doubleClick()
    else:
        py.click()
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

def create_manager_tools(agents: dict, task_state: dict, plan_intents: list = None) -> list:
    """
    Creates custom tools for the Manager agent that internally call
    the specialized agents with the afinado prompts from vlm_tools.py.
    """
    from crewai import Task
    from tools.vlm_tools import (
        check_item_prompt,
        get_coordinates_prompt,
        verification_prompt_file,
        verification_prompt_formatting,
        verification_prompt_delete,
        verification_prompt_copy_paste,
    )

    @tool("check_visibility")
    def check_visibility(target: str, item_type: str = "item") -> str:
        """
        Check if a UI element is visible on screen. Returns YES or NO.
        Use this FIRST before trying to find coordinates.

        Args:
            target: The name of the element to find (e.g., 'Downloads', 'file explorer', 'claude.docx').
            item_type: The type of element: 'application', 'folder', 'file', 'button', 'menu_option', or 'text_content'.
        """
        prompt = check_item_prompt(target, item_type)
        scout_task = Task(
            description=prompt,
            expected_output="YES or NO",
            agent=agents["scout"],
        )
        result = agents["scout"].execute_task(scout_task)
        return result

    @tool("find_coordinates")
    def find_coordinates(target: str) -> str:
        """
        Find the exact screen coordinates of a visible UI element.
        Only use this AFTER check_visibility returned YES.

        Args:
            target: The name of the element to locate (e.g., 'Downloads', 'file explorer', 'claude.docx').
        """
        prompt = get_coordinates_prompt(target)
        vision_task = Task(
            description=prompt,
            expected_output="JSON with x and y coordinates.",
            agent=agents["vision"],
        )
        result = agents["vision"].execute_task(vision_task)
        return result

    intent_list = ', '.join(plan_intents) if plan_intents else 'open, navigate, open_file, click_new, select_type, copy, paste, navigate_back, type, type_name, search_text, change_text, delete_text'
    print(f"[Manager Tools] Available intents: {intent_list}")

    @tool("execute_action")
    def execute_action(intent: str, target: str = "", scout_result: str = "", coordinates: Any = "") -> str:
        """
        Execute a GUI action (click, type, shortcut, etc).
        For visual actions, pass the scout_result and coordinates from previous tools.
        For keyboard actions, coordinates are not needed.

        Args:
            intent: The action to perform. Use ONLY the intent specified in the task.
            target: The target of the action (e.g., file name, folder name, text to type, style to apply).
            scout_result: The result from check_visibility ('YES' or 'NO'). Pass empty string for keyboard actions.
            coordinates: JSON string with x,y from find_coordinates (e.g., '{"x": 500, "y": 300}'). Pass empty string for keyboard actions.
        """
        import pyautogui as py
        import time

        # Parse coordinates — handle dict, JSON string, or single-quote string
        coords = None
        if coordinates:
            coord_data = None
            if isinstance(coordinates, dict):
                coord_data = coordinates
            elif isinstance(coordinates, str):
                try:
                    coord_data = json.loads(coordinates.replace("'", '"'))
                except (json.JSONDecodeError, TypeError):
                    # Try "x,y" format
                    parts = coordinates.split(",")
                    if len(parts) == 2:
                        try:
                            coord_data = {"x": int(parts[0].strip()), "y": int(parts[1].strip())}
                        except ValueError:
                            pass
            if coord_data:
                x, y = coord_data.get("x"), coord_data.get("y")
                if x is not None and y is not None:
                    coords = (int(x), int(y))

        scout_found = "YES" in (scout_result or "").upper()

        print(f"[execute_action] intent='{intent}' target='{target}' coords={coords} scout_found={scout_found}")

        if intent in ("open", "navigate", "open_file", "click_new", "select_type"):
            if coords and scout_found:
                return click(coords[0], coords[1], intent=intent)
            if intent in ("open", "navigate", "open_file"):
                file_name = target or task_state.get("file_name") or task_state.get("folder_name") or ""
                fallback_search_tool(file_name, intent=intent)
                return "FALLBACK_SKIP" if intent == "open_file" else "FALLBACK_SUCCESS"
            return f"FAILED: Could not find '{target}' on screen."

        elif intent == "search_text":
            return fallback_search_tool(target, intent="search_text")

        elif intent == "change_text":
            return str(format_text(target))

        elif intent == "type":
            return str(type_text(task_state.get("app_name", ""), target))

        elif intent == "navigate_back":
            time.sleep(1)
            py.hotkey("alt", "left")
            return "SUCCESS: Navigated back."

        elif intent == "delete_text":
            py.press("backspace")
            return "SUCCESS: Pressed delete key."

        elif intent == "copy":
            if coords and scout_found:
                click(coords[0], coords[1], intent="copy")
            time.sleep(0.2)
            if task_state.get("cut", False):
                py.hotkey("ctrl", "x")
            else:
                py.hotkey("ctrl", "c")
            return "SUCCESS: Cut/Copied to clipboard."

        elif intent == "paste":
            time.sleep(1)
            py.hotkey("ctrl", "v")
            return "SUCCESS: Pasted."

        elif intent == "type_name":
            time.sleep(0.5)
            py.write(target, interval=0.05)
            time.sleep(0.3)
            py.press("enter")
            time.sleep(1)
            return "SUCCESS: Typed name and confirmed."

        return f"FAILED: Unknown intent '{intent}'."

    @tool("verify_entire_workflow")
    def verify_entire_workflow(qa_type: str = "default", goal: str = "", style: str = "") -> str:
        """
        Verify that a task was completed by taking a screenshot and checking.
        Use this as the LAST step to confirm the overall task succeeded.

        Args:
            qa_type: Type of verification. One of: 'default', 'formatting', 'delete', 'copy_paste'.
            goal: What to verify (e.g., the text content, file name, or user prompt).
            style: For formatting verification, the style applied ('bold', 'italic', 'underlined'). For copy_paste, the destination folder name.
        """
        if qa_type == "formatting":
            prompt = verification_prompt_formatting(goal, style)
        elif qa_type == "delete":
            prompt = verification_prompt_delete(goal)
        elif qa_type == "copy_paste":
            prompt = verification_prompt_copy_paste(goal, style)
        else:
            prompt = verification_prompt_file(goal)

        qa_task = Task(
            description=prompt,
            expected_output="YES or NO",
            agent=agents["qa"],
            config={"qa_type": qa_type, "style": style},
        )
        result = agents["qa"].execute_task(qa_task)
        return result

    # Override execute_action description with dynamic intent list
    execute_action.description = (
        "Execute a GUI action. "
        f"The intent MUST be one of: {intent_list}. "
        "For visual actions, pass scout_result and coordinates from previous tools. "
        "For keyboard actions (paste, navigate_back, type, type_name, search_text, change_text, delete_text), coordinates are not needed."
    )

    return [check_visibility, find_coordinates, execute_action]


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
    
    @tool("create_tool")
    def create_tool(application: str, name: str, item_type: str = "text document", path: List[str] = []) -> str:
        """
        Use this tool when the user explicitly asks to create a file or folder.
        Args:
            application: The application required to START this process if File Explorer.
            name: The name of the new file or folder to be created.
            item_type: Whether to create a "file" or a "folder". Default is "folder".
            path: An ordered list of folders to navigate, for example: ["downloads", "masters"]. If not provided return [].
        """
        folder_name = name if item_type == "folder" else None
        file_name = name if item_type == "file" else None

        result = {
            "intent": "create_tool",
            "args": {
                "application": application,
                "file_name": file_name,
                "folder_name": folder_name,
                "name": name,
                "path": path
            }
        }
        return f"SUCCESS. DO NOT USE ANY MORE TOOLS. Final Answer: {json.dumps(result)}"
    
    @tool("delete_tool")
    def delete_tool(application: str, content: str, file_name: str, path: List[str] = []) -> str:
        """
        Use this tool when the user asks to open a file and delete specific text inside it.
        This tool handles the full workflow: navigating to the file, opening it, and deleting the text.
        ONLY use this when the user explicitly asks to delete or remove text from a document.
        
        Args:
            application: The application required to START this process. Must be 'file explorer' if the file needs to be located through folders.
            content: The specific text content to be deleted from the document.
            file_name: Name of the file containing the text to delete.
            path: An ordered list of folders to navigate, for example: ["downloads", "masters"]. If not provided return [].
        """

        result = {
            "intent": "delete_tool",
            "args": {
                "application": application,
                "content": content,
                "file_name": file_name,
                "path": path
            }
        }
        return f"SUCCESS. DO NOT USE ANY MORE TOOLS. Final Answer: {json.dumps(result)}"
    
    @tool("search_tool")
    def search_tool(application: str, content: str, file_name: str, path: List[str] = []) -> str:
        """
        Use this tool when the user asks to open a file and find a specific text inside it.
        This tool handles the full workflow: navigating to the file, opening it, and searching for the text.
        ONLY use this when the user explicitly asks to search for text in a document.

        Args:
            application: The application required to START this process. Must be 'file explorer' if the file needs to be located through folders.
            content: The specific text content to be searched for in the document.
            file_name: Name of the file containing the text to search.
            path: An ordered list of folders to navigate, for example: ["downloads", "masters"]. If not provided return [].
        """

        result = {
            "intent": "search_tool",
            "args": {
                "application": application,
                "content": content,
                "file_name": file_name,
                "path": path
            }
        }
        return f"SUCCESS. DO NOT USE ANY MORE TOOLS. Final Answer: {json.dumps(result)}"

    @tool("copy_paste_tool")
    def copy_paste_tool(application: str, file_name: str, operation: str = "copy", path_to_copy: List[str] = [], path_to_paste: List[str] = []) -> str:
        """
         Use this tool when the user asks to copy or cut and paste a file.

        Args:
            application: The application required to START this process. Must be 'file explorer' if the file needs to be located through folders.
            file_name: Name of the file to copy and paste.
            operation: Whether to 'copy' or 'cut' the file. Default is 'copy'.
            path_to_copy: An ordered list of folders to navigate to the source location, for example: ["downloads", "masters"]. If not provided return [].
            path_to_paste: An ordered list of folders to navigate to the destination location, for example: ["downloads", "masters"]. If not provided return [].
        """

        result = {
            "intent": "copy_paste_tool",
            "args": {
                "application": application,
                "file_name": file_name,
                "operation": operation,
                "path_to_copy": path_to_copy,
                "path_to_paste": path_to_paste
            }
        }
        return f"SUCCESS. DO NOT USE ANY MORE TOOLS. Final Answer: {json.dumps(result)}"

    return {
        "navigate_tool": navigate_tool,
        "write_tool": write_tool,
        "change_tool": change_tool,
        "create_tool": create_tool,
        "delete_tool": delete_tool,
        "search_tool": search_tool,
        "copy_paste_tool": copy_paste_tool
    }