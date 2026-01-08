import pyautogui as py
import time
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from router import verify, check_item, get_coord

class open_app(TypedDict):
    prompt: str
    app_name: str
    status: str
    vlm_model: str
    planner_model: str
    attempts: 0

def node_launch(state: open_app):
    app_name = state['app_name']
    if isinstance(app_name, list):
        app_name = app_name[0]
    print(f"Launching {app_name}")
    item = check_item(state['vlm_model'], app_name, type='open')
    if not item:
        print("Automated application opening.")
        py.hotkey('win')
        time.sleep(1.3)
        py.write(app_name, interval=0.05)
        time.sleep(0.7)
        py.press('enter')
        time.sleep(2)
        return {"status": "App launched without coordinates"}
    else:
        coord = get_coord(state["vlm_model"], app_name)
        x, y = coord['x'], coord['y']
        print(f"Moving mouse: {x}, {y}")
        py.moveTo(x, y, duration=1)
        py.click()
        time.sleep(2)
        return {"status": "App launched with coordinates"}
    
def node_verify(state: dict):
    print(f"4. Verifying action...")
    attempts = state.get('attempts', 0)
    app_name = state['app_name']
    if isinstance(app_name, list):
        app_name = app_name[0]
    if check_item(state['vlm_model'], app_name, type='application'):
        print("Action verified successfully.")
        return {"status": f"Application {app_name} opened correctly."}
    else:
        print("Action verification failed.")
        return {"status": f"Application {app_name} did not launch.",
                "attempts": attempts + 1}
    
workflow = StateGraph(open_app)
workflow.add_node("launch", node_launch)
workflow.add_node("verify", node_verify)

workflow.set_entry_point("launch")
workflow.add_edge("launch", "verify")

#Si falla pues intentamos otra vez, un máximo de 2 intentos.
def verify_edge(state):
    status = state.get("status", "")
    attempts = state.get("attempts", 0)
    
    if "correctly" in status or attempts >= 2:
        return END
    else:
        return "launch"


workflow.add_conditional_edges("verify", verify_edge)
open_application = workflow.compile()