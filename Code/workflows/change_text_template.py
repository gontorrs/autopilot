import pyautogui as py
import time
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from router import verify, check_item, get_coord, verify_formatting

class Change_Agent(TypedDict):
    prompt: str
    app_name: str
    file_name: str
    content: str
    style: str
    status: str
    vlm_model: str
    planner_model: str
    attempts: int

def node_launch_word(state: Change_Agent):
    print("Workflow: Change Text")
    print(f"1. Launching text editor: {state['app_name']}")
    item = check_item(state["vlm_model"], state['app_name'], type='application')
    if not item:
        py.hotkey('win')
        time.sleep(1)
        py.write(state['app_name'], interval=0.05)
        time.sleep(1)
        py.press('enter')
        print(f"Launched without coordinates")
        return {"status": "launched without coordinates"}
    else:
        coord = get_coord(state["vlm_model"], state['app_name'])
        x, y = coord['x'], coord['y']
        print(f"Moving mouse: {x}, {y}")
        py.moveTo(x, y, duration=1)
        py.click()
        return {"status": "launched with coordinates"}

def node_open_document(state: Change_Agent):
    print(f"Opening: {state['file_name']}")
    time.sleep(1)
    item = check_item(state["vlm_model"], state['file_name'], type='file')
    if not item:
        search_box = "Click in the search box in the Word application."
        coord = get_coord(state["vlm_model"], search_box)
        x, y = coord['x'], coord['y']
        print(f"Moving mouse: {x}, {y}")
        py.moveTo(x, y, duration=1)
        py.click()
        py.write(state['file_name'], interval=0.05)
        time.sleep(1)
        py.press('enter')
        print(f"Launched without coordinates")
        return {"status": "opened document without coordinates"}
    else:
        coord = get_coord(state["vlm_model"], state['file_name'])
        x, y = coord['x'], coord['y']
        print(f"Moving mouse: {x}, {y}")
        py.moveTo(x, y, duration=1)
        py.click()
        return {"status": "opened document with coordinates"}

def node_find_content(state: Change_Agent):
    print(f"Checking: {state['content']}")
    time.sleep(1)
    item = check_item(state["vlm_model"], state['content'], type='text_content')
    if not item:
        py.hotkey('ctrl','f')
        time.sleep(1)
        py.write(state['content'], interval=0.05)
        time.sleep(1)
        py.press('enter')
        time.sleep(1)
        py.press('esc')
        return {"status": "texted found and selected text"}
    else:
        start_coord = f"Give me the coordinate for the start of the sentence {state['content']}."
        end_coord = f"Give me the coordinate for the end of the sentence {state['content']}."
        coord_start = get_coord(state["vlm_model"], start_coord)
        coord_end = get_coord(state["vlm_model"], end_coord)
        start_x, start_y = coord_start['x'], coord_start['y']
        end_x, end_y = coord_end['x'], coord_end['y']
        print(f"Doing a selection of {state['content']}")
        py.moveTo(start_x, start_y)
        py.mouseDown()
        py.moveTo(end_x, end_y, duration=0.3)
        py.mouseUp()
        return {"status": "texted found and selected text with drag"}
    
def node_format(state: Change_Agent):
    time.sleep(1)
    if 'bold' in state['style']:
        py.hotkey('ctrl', 'b')
    elif 'italic' in state['style']:
        py.hotkey('ctrl', 'i')
    elif 'under' in state['style']:
        py.hotkey('ctrl', 'u')
    else:
        print("No style recognised")
    py.press('left')
    return {"status": "text formatted"}

def node_verify(state: Change_Agent):
    time.sleep(1)
    print(f"4. Verifying action...")
    if verify_formatting(state["vlm_model"], state['content'], state['style']):
        print("Action verified successfully.")
        return {"status": "verified"}
    else:
        attempts = state["attempts"]
        print("Action verification failed.")
        return {"status": "failed",
                "attempts": attempts + 1}
    
workflow = StateGraph(Change_Agent)
workflow.add_node('launch', node_launch_word)
workflow.add_node('open', node_open_document)
workflow.add_node('find', node_find_content)
workflow.add_node('format', node_format)
workflow.add_node('verify', node_verify)

workflow.set_entry_point("launch")
workflow.add_edge("launch", "open")
workflow.add_edge("open", "find")
workflow.add_edge("find", "format")
workflow.add_edge("format", "verify")

#Si falla pues intentamos otra vez, un máximo de 2 intentos.
def verify_edge(state):
    if state["status"] == "verified" or state['attempts'] >= 2:
        return END
    else:
        return "launch"

workflow.add_conditional_edges("verify", verify_edge)
change_text = workflow.compile()