import pyautogui
import time
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from router import verify, get_coord, check_item
from tools.vlm_tools import click

class Explore_Agent(TypedDict):
    prompt: str
    operation: str
    file_name: str
    app_name: str
    status: str
    vlm_model: str
    planner_model: str

def node_launch_explorer(state: Explore_Agent):
    print(f"1. File explorer open")
    item = check_item(state["vlm_model"], state['app_name'])
    if not item:
        pyautogui.hotkey('win', 'e')
        print(f"Launched without coordinates")
        return {"status": "launched without coordinates"}
    else:
        coord = get_coord(state["vlm_model"], state['app_name'])
        x, y = coord['x'], coord['y']
        print(f"Moving mouse: {x}, {y}")
        pyautogui.moveTo(x, y, duration=1)
        click(coord)
        return {"status": "launched with coordinates"}


def node_navigate(state: Explore_Agent):
    time.sleep(1)
    coord = get_coord(state["vlm_model"], state['file_name'])
    print(f"2. Navigating to...")
    if not coord:
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(2)
        pyautogui.write(state['file_name'])
        time.sleep(2)
        print(f"3. Opening file...")
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(2)
        pyautogui.press('space')
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(2)
        return {"status": "navigated without coordinates"}
    else:
        x, y = coord['x'], coord['y']
        print(f"Moving mouse: {x}, {y}")
        pyautogui.moveTo(x, y, duration=1)
        click(coord)
        return {"status": "launched with coordinates"}

def node_verify(state: Explore_Agent):
    print(f"4. Verifying action...")
    if verify(state["vlm_model"], state['prompt']):
        print("Action verified successfully.")
        return {"status": "verified"}
    else:
        print("Action verification failed.")
        return {"status": "failed"}
    

#Compilamos el workflow.
workflow = StateGraph(Explore_Agent)
workflow.add_node("launch", node_launch_explorer)
workflow.add_node("navigate", node_navigate)
workflow.add_node("verify", node_verify)

workflow.set_entry_point("launch")
workflow.add_edge("launch", "navigate")
workflow.add_edge("navigate", "verify")
workflow.add_edge("verify", END)

file_explorer = workflow.compile()