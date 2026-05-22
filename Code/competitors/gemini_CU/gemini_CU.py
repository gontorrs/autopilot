import os
import sys
import time
import pyautogui as py
from datetime import datetime
from dotenv import load_dotenv
import io
from google import genai
from google.genai import types

load_dotenv()

LOG_DIR = "./logs/copy_paste/v2"

# Logging
class Tee:
    def __init__(self, *streams):
        self.streams = streams
    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()
    def flush(self):
        for s in self.streams:
            s.flush()

def take_screenshot() -> bytes:
    screenshot = py.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    return buffer.getvalue()

def parse_coordinates(coords):
    screen_w, screen_h = py.size()
    if coords:
        return int(coords[0] / 1000 * screen_w), int(coords[1] / 1000 * screen_h)
    return None

def setup(task: str) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = open(os.path.join(LOG_DIR, f"{timestamp}.log"), "w", encoding="utf-8")
    sys.stdout = Tee(sys.stdout, log_file)
    sys.stderr = Tee(sys.stderr, log_file)

def save_screenshot(png_bytes: bytes, step: int) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(LOG_DIR, f"step_{step:02d}_{timestamp}.png")
    with open(path, "wb") as f:
        f.write(png_bytes)
    print(f"[SCREENSHOT] Saved: step_{step:02d}_{timestamp}.png")

MODEL = "gemini-3-flash-preview"
#MODEL = "gemini-3.1-pro-preview"
py.FAILSAFE = True

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={'timeout': 120000})

SYSTEM_PROMPT = """You are a Windows desktop automation agent.

You control the desktop by calling the available tools.
IMPORTANT: Use normalised coordinates (0-1000 range) for x and y in all tool calls.
0,0 is top-left and 1000,1000 is bottom-right. The system maps them to real pixels automatically.

Rules:
- Call ONE tool per message, then wait for the screenshot result.
- Before each tool call, print a short plain-English description of what you are doing (such as "Step 3: Double-clicking the Notepad icon").
- When the task is fully complete, call done() with a short summary.
- Never ask the user for clarification mid-task; make reasonable assumptions.
"""

# Tools in dict format
TOOLS = [
    types.Tool(function_declarations=[
        {
            "name": "left_click",
            "description": "Single left-click at (x, y).",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate (0-1000)."},
                    "y": {"type": "integer", "description": "Y coordinate (0-1000)."},
                },
                "required": ["x", "y"],
            },
        },
        {
            "name": "right_click",
            "description": "Single right-click at (x, y).",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate (0-1000)."},
                    "y": {"type": "integer", "description": "Y coordinate (0-1000)."},
                },
                "required": ["x", "y"],
            },
        },
        {
            "name": "double_click",
            "description": "Double left-click at (x, y).",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate (0-1000)."},
                    "y": {"type": "integer", "description": "Y coordinate (0-1000)."},
                },
                "required": ["x", "y"],
            },
        },
        {
            "name": "type_text",
            "description": "Type a string of text at the current cursor position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type."},
                },
                "required": ["text"],
            },
        },
        {
            "name": "hotkey",
            "description": "Press a keyboard shortcut, e.g. 'ctrl+s', 'alt+f4', 'win+d'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {"type": "string", "description": "Key combo as a plus-separated string, e.g. 'ctrl+c'."},
                },
                "required": ["keys"],
            },
        },
        {
            "name": "take_screenshot",
            "description": "Capture the current state of the screen. Call this when you need to see what is currently on the desktop before deciding the next action.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "done",
            "description": "Call this when the task is fully complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Short summary of what was accomplished."},
                },
                "required": ["summary"],
            },
        },
    ])
]

# Actions to pyautogui function mapping
def execute(fn_name: str, args: dict):
    if fn_name == "left_click":
        x, y = parse_coordinates([args["x"], args["y"]])
        py.click(x, y)
        return f"Left-clicked at ({x}, {y})"

    elif fn_name == "right_click":
        x, y = parse_coordinates([args["x"], args["y"]])
        py.rightClick(x, y)
        return f"Right-clicked at ({x}, {y})"

    elif fn_name == "double_click":
        x, y = parse_coordinates([args["x"], args["y"]])
        py.doubleClick(x, y)
        return f"Double-clicked at ({x}, {y})"

    elif fn_name == "type_text":
        text = args["text"]
        py.write(text, interval=0.05)
        return f"Typed: {text}"

    elif fn_name == "hotkey":
        keys = args["keys"].split("+")
        py.hotkey(*keys)
        return f"Pressed hotkey: {args['keys']}"

    elif fn_name == "take_screenshot":
        screenshot = take_screenshot()
        return screenshot

    elif fn_name == "done":
        return f"DONE: {args['summary']}"

    return f"Unknown function: {fn_name}"

# Main Loop
def run_agent(task: str):
    setup(task)

    print(f"\n{'='*60}")
    print(f"TASK: {task}")
    print(f"LOGS: {LOG_DIR}")
    print(f"{'='*60}\n")

    step = 0
    total_start = time.perf_counter()
    history = []

    history.append(
        types.Content(role="user", parts=[
            types.Part(text=task),
        ])
    )

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
    )

    while True:
        t_think_start = time.perf_counter()

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=history,
                config=config,
            )
        except Exception as e:
            thinking_time = time.perf_counter() - t_think_start
            print(f"\n[ERROR] API call failed after {thinking_time:.2f}s: {e}")
            break

        thinking_time = time.perf_counter() - t_think_start

        candidate = response.candidates[0]
        history.append(candidate.content)

        for part in candidate.content.parts:
            if part.text:
                print(part.text)

        fn_call = next(
            (p.function_call for p in candidate.content.parts if p.function_call),
            None
        )

        if fn_call is None:
            print("\n[Agent finished - no further tool calls.]")
            break

        fn_name = fn_call.name
        args = dict(fn_call.args)

        step += 1
        print(f"[TIMING] thinking -> {fn_name}: {thinking_time:.2f}s")

        t_exec_start = time.perf_counter()
        result = execute(fn_name, args)
        exec_time = time.perf_counter() - t_exec_start

        # Caso especial: Si Gemini pide screenshot, lo guardamos y enviamos la imagen
        if fn_name == "take_screenshot":
            save_screenshot(result, step)
            print(f"  -> Screenshot taken")
            print(f"[TIMING] {fn_name} execution: {exec_time:.2f}s")
            history.append(
                types.Content(role="user", parts=[
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=fn_name,
                            id=fn_call.id,
                            response={"result": "Screenshot captured."},
                        )
                    ),
                ])
            )
            history.append(
                types.Content(role="user", parts=[
                    types.Part.from_bytes(data=result, mime_type="image/png"),
                ])
            )
            continue

        print(f"  -> {result}")
        print(f"[TIMING] {fn_name} execution: {exec_time:.2f}s")

        if fn_name == "done":
            break

        history.append(
            types.Content(role="user", parts=[
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fn_name,
                        id=fn_call.id,
                        response={"result": result},
                    )
                ),
            ])
        )

    total_time = time.perf_counter() - total_start
    print(f"\n{'='*60}")
    print(f"Total steps executed: {step}")
    print(f"[TIMING] Total end-to-end: {total_time:.2f}s")
    print(f"{'='*60}")

#TASK = "Take a quick note in Notepad saying that I have a meeting tommorrow at 8 pm in Tokyo please." #write
#TASK = 'Create a text file named "GTS" in the Documents folder.' #create
#TASK = "Open the file Entrevista_Reli.pdf which is in Documents > INCO > Prueba." #open
#TASK = 'Open my Entrevista_Reli.odt in Desktop and search for the text Gonzalo Torras Serrano.' #search
#TASK = 'Open my Entrevista_Reli.odt in Desktop and delete the text Gonzalo Torras Serrano.' #delete
#TASK = "Open my Entrevista_Reli.odt in Desktop folder and make the text Gonzalo Torras Serrano in italic." #format
TASK = 'Copy my prueba.txt in my Downloads folder and paste it in my Documents folder.' #copy

if __name__ == "__main__":
    run_agent(TASK)