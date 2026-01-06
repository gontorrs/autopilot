import pyautogui
import time
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from router import verify, check_item, get_coord
from tools.vlm_tools import click

class Write_Agent(TypedDict):
    prompt: str
    app_name: str
    content: str
    status: str
    vlm_model: str
    planner_model: str

def node_launch_editor(state: Write_Agent):
    print(f"1. Launching text editor: {state['app_name']}")
    item = check_item(state["vlm_model"], state['app_name'])
    if not item:
        pyautogui.hotkey('win')
        time.sleep(1)
        pyautogui.write(state['app_name'])
        time.sleep(1)
        pyautogui.press('enter')
        print(f"Launched without coordinates")
    else:
        coord = get_coord(state["vlm_model"], state['app_name'])
        x, y = coord['x'], coord['y']
        print(f"Moving mouse: {x}, {y}")
        pyautogui.moveTo(x, y, duration=1)
        click(coord)
        return {"status": "launched with coordinates"}

def node_write_content(state: Write_Agent):
    if "notepad" not in state["app_name"].lower():
        time.sleep(1)
        pyautogui.press('enter')
    time.sleep(1)
    print(f"2. Writing content...")
    pyautogui.write(state['content'], interval=0.05)
    return {"status": "content written"}

def node_verify(state: Write_Agent):
    print(f"4. Verifying action...")
    if verify(state["vlm_model"], state['prompt']):
        print("Action verified successfully.")
        return {"status": "verified"}
    else:
        print("Action verification failed.")
        return {"status": "failed"}

workflow = StateGraph(Write_Agent)
workflow.add_node('launch', node_launch_editor)
workflow.add_node('write', node_write_content)
workflow.add_node('verify', node_verify)

workflow.set_entry_point("launch")
workflow.add_edge("launch", "write")
workflow.add_edge("write", "verify")
workflow.add_edge("verify", END)

write_text = workflow.compile()