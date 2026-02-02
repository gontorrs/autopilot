import pyautogui as py
import time
import pyperclip
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from utils.router import verify, check_item, get_coord
py.FAILSAFE = False 


class Write_Agent(TypedDict):
    prompt: str
    app_name: str
    content: str
    status: str
    vlm_model: str
    planner_model: str
    attempts: int


def node_launch_editor(state: Write_Agent):
    print(f"1. Launching text editor: {state['app_name']}")
    item = check_item(state["vlm_model"], state['app_name'], type='application')
    if not item:
        py.hotkey('win')
        time.sleep(1)
        #py.write(state['app_name'], interval=0.05)
        pyperclip.copy(state['app_name'])
        py.hotkey('ctrl', 'v')
        time.sleep(1)
        py.press('enter')
        return {"status": "launched without coordinates"}
    else:
        coord = get_coord(state["vlm_model"], state['app_name'])
        x, y = coord['x'], coord['y']
        print(f"Moving mouse: {x}, {y}")
        py.moveTo(x, y, duration=1)
        py.click()
        return {"status": "launched with coordinates"}


def node_write_content(state: Write_Agent):
    if "notepad" not in state["app_name"].lower():
        time.sleep(1)
        py.press('enter')
    time.sleep(1)
    print(f"2. Writing content...")
    #py.write(state['content'], interval=0.05)
    pyperclip.copy(state['content'])
    py.hotkey('ctrl', 'v')
    return {"status": "content written"}


def node_verify(state: Write_Agent):
    print(f"4. Verifying action...")
    if verify(state["vlm_model"], state['prompt']):
        print("Action verified successfully.")
        return {"status": "verified"}
    else:
        attempts = state["attempts"]
        print("Action verification failed.")
        return {"status": "failed",
                "attempts": attempts + 1}


workflow = StateGraph(Write_Agent)
workflow.add_node('launch', node_launch_editor)
workflow.add_node('write', node_write_content)
workflow.add_node('verify', node_verify)


workflow.set_entry_point("launch")
workflow.add_edge("launch", "write")
workflow.add_edge("write", "verify")


#Si falla pues intentamos otra vez, un máximo de 2 intentos.
def verify_edge(state):
    if state["status"] == "verified" or state['attempts'] >= 2:
        return END
    else:
        return "launch"


workflow.add_conditional_edges("verify", verify_edge)
write_text = workflow.compile()