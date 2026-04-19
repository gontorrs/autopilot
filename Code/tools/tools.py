# utils/tools.py
import json
import re
import pyautogui as py
import io
import time
from crewai.tools import tool
from crewai import Task
from typing import Any, List
from tools.vlm_prompts import check_item_prompt, get_coordinates_prompt, verification_prompt_file, verification_prompt_formatting, verification_prompt_delete, verification_prompt_copy_paste, verification_prompt_search
from functools import wraps

_last_tool_end = {"t": None}

def start_timing():
    _last_tool_end["t"] = time.perf_counter()

def timed(phase_name: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if _last_tool_end["t"] is not None:
                thinking = time.perf_counter() - _last_tool_end["t"]
                print(f"[TIMING] manager_thinking → {phase_name}: {thinking:.2f}s")

            start = time.perf_counter()
            result = fn(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"[TIMING] {phase_name}: {elapsed:.2f}s")

            _last_tool_end["t"] = time.perf_counter()
            return result
        return wrapper
    return decorator

def take_screenshot() -> bytes:
    screenshot = py.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    return buffer.getvalue()

def correct_coord(x: int, y: int, offset_x: int = 25) -> tuple[int, int]:
    return (x + offset_x, y)

def parse_coordinates(coords):
    screen_w, screen_h = py.size()
    if coords:
        return int(coords[0] / 1000 * screen_w), int(coords[1] / 1000 * screen_h)
    return None


def win_search(target: str):
    """Open Windows search, type target, press Enter."""
    py.press('win')
    time.sleep(1)
    py.write(target, interval=0.05)
    time.sleep(1)
    py.press('enter')
    time.sleep(1)

def click(x: int, y: int, intent: str = "") -> str:
    py.moveTo(x, y, duration=1)
    if intent in ("navigate", "open_file"):
        py.doubleClick()
    else:
        py.click()
    time.sleep(1)
    return f"SUCCESS: Clicked at ({x}, {y})."


def type_text(app_name, content):
    if "notepad" not in app_name.lower():
        time.sleep(1)
        py.press('enter')
    time.sleep(1)
    py.write(content, interval=0.05)
    return "SUCCESS: Content written."


def format_text(style: str) -> str:
    time.sleep(2)
    shortcuts = {'bold': 'b', 'italic': 'i', 'under': 'u'}
    for key, char in shortcuts.items():
        if key in style:
            py.hotkey('ctrl', char)
            break
    py.press('left')
    time.sleep(3)
    return "SUCCESS: Text formatted."

def build_task_state(intent_name, intent_args, user_input, sanitize_fn):
    args = intent_args
    common = {"prompt": user_input, "status": "start", "attempts": 0}

    if intent_name == 'navigate_tool':
        path = ["Default"] + args.get('path', [])
        return {**common, "file_name": args.get('file_name', ''), "app_name": args.get('app_name', ''),
                "path": path, "goal": f"(open_file {sanitize_fn(args.get('file_name', ''))})"}

    if intent_name == 'write_tool':
        return {**common, "app_name": args.get('application', 'notepad'), "content": args.get('text', ''),
                "goal": f"(typed_text {sanitize_fn(args.get('text', ''))})"}

    if intent_name == 'change_tool':
        path = ["Default"] + args.get('path', [])
        return {**common, "app_name": args.get('application'), "file_name": args.get('file_name', ''),
                "content": args.get('content', ''), "style": args.get('style', ''), "path": path,
                "goal": f"(changed_text {sanitize_fn(args.get('style', ''))})"}

    if intent_name == 'create_tool':
        item_type = args.get('item_type', 'folder')
        name_raw = args.get('name', '')
        path = ["Default"] + args.get('path', [])
        return {**common, "app_name": args.get('application'),
                "file_name_new": name_raw if item_type == "file" else None,
                "folder_name": name_raw if item_type == "folder" else None,
                "name": name_raw, "path": path,
                "goal": f"(created {sanitize_fn(name_raw)}_name)"}

    if intent_name == 'delete_tool':
        path = ["Default"] + args.get('path', [])
        return {**common, "app_name": args.get('application'), "file_name": args.get('file_name', ''),
                "content": args.get('content', ''), "path": path,
                "goal": f"(delete_text {sanitize_fn(args.get('content', ''))})"}

    if intent_name == 'search_tool':
        path = ["Default"] + args.get('path', [])
        return {**common, "app_name": args.get('application'), "file_name": args.get('file_name', ''),
                "content": args.get('content', ''), "path": path,
                "goal": f"(text_searched {sanitize_fn(args.get('content', ''))})"}

    if intent_name == 'copy_paste_tool':
        path_copy = ["Default"] + args.get('path_to_copy', [])
        path_paste = ["Default"] + args.get('path_to_paste', [])
        return {**common, "app_name": args.get('application', 'file explorer'),
                "file_name": args.get('file_name', ''), "path_to_copy": path_copy, "path_to_paste": path_paste,
                "cut": args.get('operation', 'copy') == 'cut',
                "goal": f"(pasted {sanitize_fn(args.get('file_name', ''))} {sanitize_fn(args.get('path_to_paste', [''])[-1])})"}

    return None


# ================================================================== #
#  Intent JSON parser                                                 #
# ================================================================== #

def parse_intent_json(raw_text: str) -> dict | None:
    """Extract intent JSON from LLM output. Handles 'intent' or 'tool_name' keys."""
    for match in re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_text):
        try:
            candidate = json.loads(match.group(0).replace("'", '"'))
            # Accept either "intent" or "tool_name" as the key
            if "intent" in candidate or "tool_name" in candidate or "tool" in candidate:
                if "tool_name" in candidate and "intent" not in candidate:
                    candidate["intent"] = candidate.pop("tool_name")
                elif "tool" in candidate and "intent" not in candidate:
                    candidate["intent"] = candidate.pop("tool")
                return candidate
        except (json.JSONDecodeError, ValueError):
            continue
    return None


# ================================================================== #
#  Manager tools                                                      #
# ================================================================== #

def create_manager_tools(agents: dict, config: dict) -> list:

    shared_state = {"task_state": None, "plan_result": None}

    @tool("classify_intent")
    @timed("Intent Classification")
    def classify_intent(user_query: str) -> str:
        """
        STEP 1 of the workflow. Classify the user's natural language request into a structured intent.
        This MUST be the very first tool you call. It analyzes the user query and determines
        what type of GUI task needs to be performed (navigate, write, change formatting, create, delete, search, or copy/paste).
        After this returns SUCCESS, call generate_plan.

        Args:
            user_query: The user's original request exactly as given (e.g., 'Open my file.odt in Documents and make text bold').
        """

        t = Task(
            description=f"Analyze this query using the available intention tools: '{user_query}'",
            expected_output="A valid JSON string with 'intent' and 'args' keys.",
            agent=agents["intention"],
        )
        result = agents["intention"].execute_task(t)

        data = parse_intent_json(result)
        if not data:
            return f"FAILED: Could not parse intent from: {result}"

        intent_name = data.get("intent", "")
        if intent_name and not intent_name.endswith("_tool"):
            intent_name += "_tool"  
        intent_args = data.get("args", {})

        task_state = build_task_state(intent_name, intent_args, user_query, agents["planner"].sanitize)
        if not task_state:
            return f"FAILED: Unknown intent '{intent_name}'"

        shared_state["task_state"] = task_state
        print(f"[classify_intent] Intent: {intent_name}, Args: {intent_args}")
        return f"SUCCESS: Intent classified as '{intent_name}'. Now call generate_plan."

    # --- PHASE 2: PDDL Planning --- #

    @tool("generate_plan")
    @timed("PDDL Planning")
    def generate_plan() -> str:
        """
        STEP 2 of the workflow. Generate a PDDL plan using Fast Downward based on the classified intent.
        Call this AFTER classify_intent has returned SUCCESS.
        Takes no arguments — uses the internal state from classify_intent.
        After this returns SUCCESS, call translate_plan.
        """
        task_state = shared_state.get("task_state")
        if not task_state:
            return "FAILED: No task state available. Call classify_intent first."

        t = Task(
            description="Generate PDDL plan.",
            expected_output="Plan result or None.",
            agent=agents["planner"],
        )
        result = agents["planner"].execute_task(t, state_dict=task_state)
        if not result:
            return "FAILED: PDDL planner could not generate a plan."

        shared_state["plan_result"] = result
        return "SUCCESS: Plan generated. Now call translate_plan."

    # --- PHASE 3: Translate plan --- #

    @tool("translate_plan")
    @timed("Plan Translation")
    def translate_plan() -> str:
        """
        STEP 3 of the workflow. Translate the PDDL plan into executable GUI steps.
        Call this AFTER generate_plan has returned SUCCESS.
        Takes no arguments — uses the internal plan from generate_plan.
        Returns a numbered list of steps. Execute each step IN ORDER using the execution tools.
        VISUAL steps require: check_visibility → find_coordinates → execute_action.
        KEYBOARD steps require: execute_action directly (no coordinates needed).
        After ALL steps are done, call verify_result.
        """
        plan_result = shared_state.get("plan_result")
        task_state = shared_state.get("task_state")
        if not plan_result or not task_state:
            return "FAILED: No plan available. Call generate_plan first."

        t = Task(
            description="Translate PDDL plan to steps.",
            expected_output="List of executable steps.",
            agent=agents["translator"],
        )
        steps = agents["translator"].execute_task(t, plan_text=plan_result["plan"], mapping=plan_result["mapping"], state=task_state)

        lines = []
        for i, s in enumerate(steps, 1):
            if s["action"] in ("paste", "navigate_back", "type", "type_name", "search_text", "change_text", "delete_text"):
                lines.append(f"Step {i}: KEYBOARD — execute_action(intent='{s['action']}', target='{s['target']}')")
            else:
                lines.append(
                    f"Step {i}: VISUAL — "
                    f"(1) call check_visibility(target='{s['target']}', item_type='{s['item_type']}'). "
                    f"(2a) If it returns NO → call execute_action(intent='{s['action']}', target='{s['target']}', scout_result='NO', coordinates='') ONCE and go to next step. DO NOT call find_coordinates. "
                    f"(2b) If it returns YES → call find_coordinates(target='{s['target']}'), then execute_action(intent='{s['action']}', target='{s['target']}', scout_result='YES', coordinates=<result>) ONCE."
                )
        print(f"[translate_plan] {len(steps)} steps translated.")
        return f"SUCCESS: Execute these steps IN ORDER:\n" + "\n".join(lines) + "\nAfter ALL steps are done, call verify_result."

    # --- PHASE 4: Execution tools --- #

    @tool("check_visibility")
    @timed("Check Visibility")
    def check_visibility(target: str, item_type: str = "item") -> str:
        """
        STEP 4a — Check if a UI element is visible on screen by taking a screenshot. Returns YES or NO.
        Use this as the FIRST step for each VISUAL action before calling find_coordinates.
        If this returns NO, you must STILL call execute_action with scout_result='NO' and coordinates='' — the executor has a fallback.

        Args:
            target: The name of the element to find (e.g., 'Downloads', 'file explorer', 'claude.docx').
            item_type: The type of element: 'application', 'folder', 'file', 'button', 'menu_option', or 'text_content'.
        """
        prompt = check_item_prompt(target, item_type)
        t = Task(description=prompt, expected_output="YES or NO", agent=agents["scout"])
        return agents["scout"].execute_task(t)

    @tool("find_coordinates")
    @timed("Find Coordinates")
    def find_coordinates(target: str) -> str:
        """
        STEP 4b — Find the exact pixel coordinates of a visible UI element by taking a screenshot.
        Only call this AFTER check_visibility returned YES for the same target.
        Returns a JSON string like {"x": 500, "y": 300}. Pass this to execute_action as coordinates.

        Args:
            target: The name of the element to locate (e.g., 'Downloads', 'file explorer', 'claude.docx').
        """
        prompt = get_coordinates_prompt(target)
        t = Task(description=prompt, expected_output="JSON with x and y coordinates.", agent=agents["vision"])
        return agents["vision"].execute_task(t)

    @tool("execute_action")
    @timed("Execute Action")
    def execute_action(intent: str, target: str = "", scout_result: str = "", coordinates: Any = "") -> str:
        """
        STEP 4c — Execute a GUI action (click, type, keyboard shortcut, etc).
        For VISUAL actions (open, navigate, open_file, click_new, select_type, copy):
            Pass scout_result from check_visibility and coordinates from find_coordinates.
        For KEYBOARD actions (paste, navigate_back, type, type_name, search_text, change_text, delete_text):
            No coordinates needed. Pass scout_result='' and coordinates=''.

        Visual intents:
            open — click an application icon to launch it.
            navigate — double-click a folder to enter it.
            open_file — double-click a file to open it.
            click_new — click the 'New' button to open a creation menu.
            select_type — click a menu option (file type or folder).
            copy — click a file to select it, then Ctrl+C (or Ctrl+X for cut).
        Keyboard intents:
            paste — Ctrl+V.
            navigate_back — Alt+Left to go back one folder.
            type — type text content into the active application.
            type_name — type a name and press Enter to confirm.
            search_text — Ctrl+F and type the search query.
            change_text — apply formatting. Target MUST be the style name ('bold', 'italic', 'underline'), NOT the text.
            delete_text — press Backspace to delete selected text.

        Args:
            intent: The action to perform. Must match one of the intents listed above.
            target: The target (file name, folder name, text to type, or style to apply).
            scout_result: Result from check_visibility ('YES' or 'NO'). Empty string for keyboard actions.
            coordinates: JSON string from find_coordinates (e.g., '{"x": 500, "y": 300}'). Empty string for keyboard actions.
        """
        task_state = shared_state.get("task_state") or {}
        t = Task(
            description=f"Execute '{intent}' on '{target}'",
            expected_output="SUCCESS or FAILED",
            agent=agents["executor"],
        )
        return agents["executor"].execute_task(t, intent=intent, target=target, scout_result=scout_result, coordinates=coordinates, state=task_state)

    # --- PHASE 5: QA Verification --- #

    @tool("verify_result")
    @timed("Verify Result")
    def verify_result() -> str:
        """
        STEP 5 — Final verification. Takes a screenshot and checks if the task was completed successfully.
        Call this ONCE as the very LAST step, only after ALL execution steps from translate_plan are done.
        NEVER call this during intermediate steps.
        Takes no arguments — automatically determines what to verify based on the task.
        Returns YES if the task succeeded, NO if it failed.
        """
        task_state = shared_state.get("task_state") or {}
        goal = task_state.get("goal", "")

        if "changed_text" in goal:
            prompt = verification_prompt_formatting(task_state.get("content", ""), task_state.get("style", ""))
        elif "delete_text" in goal:
            prompt = verification_prompt_delete(task_state.get("content", ""))
        elif "pasted" in goal:
            prompt = verification_prompt_copy_paste(task_state.get("file_name", ""), task_state.get("path_to_paste", [""])[-1])
        elif "text_searched" in goal:
            prompt = verification_prompt_search(task_state.get("content", ""))
            print(f"[verify_result] Search verification prompt: {prompt}")
        else:
            prompt = verification_prompt_file(task_state.get("prompt", ""))

        t = Task(description=prompt, expected_output="YES or NO", agent=agents["qa"])
        result = agents["qa"].execute_task(t)
        print(f"[verify_result] QA result: {result}")
        return result

    return [classify_intent, generate_plan, translate_plan, check_visibility, find_coordinates, execute_action, verify_result]


# ================================================================== #
#  Intention tools (used by the intention agent)                      #
# ================================================================== #

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
        return json.dumps({"intent": "navigate_tool", "args": {"file_name": file_name, "path": path, "app_name": app_name}})

    @tool("write_tool")
    def write_tool(text: str, application: str = "notepad") -> str:
        """
        Open a text editor application and type specific content into it.

        Args:
            application: The name of the Windows application to open (e.g., 'notepad' or 'word'). If application is not stated, default to notepad. (Options: "notepad", "word", "power point")
            text: The content text that needs to be written inside the application.
        """
        return json.dumps({"intent": "write_tool", "args": {"application": application, "text": text}})

    @tool("change_tool")
    def change_tool(application: str, file_name: str, content: str, style: str, path: List[str] = []) -> str:
        """
        If the user asks to open a file and apply formatting to specific text inside it, use this tool.
        ONLY use this when the user explicitly asks to format text (bold, italic, underlined) inside a document.

        Args:
            application: The application required to START the process IS File Explorer.
            file_name: Name of the final file to search/open. Always required.
            content: The specific text content inside the document that needs to be formatted.
            style: The style to apply to the text content. (Options: "bold", "italic", "underlined")
            path: An ordered list of folders to navigate, for example: ["downloads", "masters"]. If path is not provided return [].
        """
        return json.dumps({"intent": "change_tool", "args": {"application": application, "file_name": file_name, "content": content, "style": style, "path": path}})

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
        return json.dumps({"intent": "create_tool", "args": {"application": application, "file_name": file_name, "folder_name": folder_name, "name": name, "path": path}})

    @tool("delete_tool")
    def delete_tool(application: str, content: str, file_name: str, path: List[str] = []) -> str:
        """
        Use this tool when the user asks to open a file and delete specific text inside it.

        Args:
            application: The application required to START this process. Must be 'file explorer' if the file needs to be located through folders.
            content: The specific text content to be deleted from the document.
            file_name: Name of the file containing the text to delete.
            path: An ordered list of folders to navigate, for example: ["downloads", "masters"]. If not provided return [].
        """
        return json.dumps({"intent": "delete_tool", "args": {"application": application, "content": content, "file_name": file_name, "path": path}})

    @tool("search_tool")
    def search_tool(application: str, content: str, file_name: str, path: List[str] = []) -> str:
        """
        Use this tool when the user asks to open a file and find a specific text inside it.

        Args:
            application: The application required to START this process. Must be 'file explorer' if the file needs to be located through folders.
            content: The specific text content to be searched for in the document.
            file_name: Name of the file containing the text to search.
            path: An ordered list of folders to navigate, for example: ["downloads", "masters"]. If not provided return [].
        """
        return json.dumps({"intent": "search_tool", "args": {"application": application, "content": content, "file_name": file_name, "path": path}})

    @tool("copy_paste_tool")
    def copy_paste_tool(application: str, file_name: str, operation: str = "copy",
                        path_to_copy: List[str] = [], path_to_paste: List[str] = []) -> str:
        """
        Use this tool when the user asks to copy or cut and paste a file.

        Args:
            application: The application required to START this process. Must be 'file explorer' if the file needs to be located through folders.
            file_name: Name of the file to copy and paste.
            operation: Whether to 'copy' or 'cut' the file. Default is 'copy'.
            path_to_copy: An ordered list of folders to navigate to the source location, for example: ["downloads", "masters"]. If not provided return [].
            path_to_paste: An ordered list of folders to navigate to the destination location, for example: ["downloads", "masters"]. If not provided return [].
        """
        return json.dumps({"intent": "copy_paste_tool", "args": {"application": application, "file_name": file_name, "operation": operation, "path_to_copy": path_to_copy, "path_to_paste": path_to_paste}})

    return {
        "navigate_tool": navigate_tool, "write_tool": write_tool, "change_tool": change_tool,
        "create_tool": create_tool, "delete_tool": delete_tool, "search_tool": search_tool,
        "copy_paste_tool": copy_paste_tool
    }