import pyautogui as py
import time
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from router import verify

class Write_Agent(TypedDict):
    prompt: str
    app_name: str
    content: str
    status: str
    vlm_model: str
    planner_model: str
    attempts: 0

def node_write_content(state: Write_Agent):
    app_name = state['app_name']
    if isinstance(app_name, list):
        app_name = app_name[0]
    if "notepad" not in app_name.lower():
        time.sleep(1)
        py.press('enter')
    time.sleep(1)
    print(f"2. Writing content...")
    content = state['content']
    if isinstance(content, list):
        content = content[0]
    py.write(content, interval=0.05)
    return {"status": "Content written."}

def node_verify(state: Write_Agent):
    print(f"4. Verifying action...")
    attempts = state.get('attempts', 0)
    app_name = state['app_name']
    if isinstance(app_name, list):
        app_name = app_name[0]
    content = state["content"]
    verify_prompt = f"Is the text '{content}' visible in the {app_name} window?"
    if verify(state["vlm_model"], verify_prompt):
        print("Action verified successfully.")
        return {"status": "Verified that the text was written."}
    else:
        print("Action verification failed.")
        return {"status": f"The text was not written correctly in {app_name}.",
                "attempts": attempts + 1}

workflow = StateGraph(Write_Agent)
workflow.add_node('write', node_write_content)
workflow.add_node('verify', node_verify)

workflow.set_entry_point("write")
workflow.add_edge("write", "verify")

#Si falla pues intentamos otra vez, un máximo de 2 intentos.
def verify_edge(state):
    status = state.get("status", "")
    attempts = state.get("attempts", 0)
    
    if "Verified that the text" in status or attempts >= 2:
        return END
    else:
        return "write"

workflow.add_conditional_edges("verify", verify_edge)
write_text = workflow.compile()