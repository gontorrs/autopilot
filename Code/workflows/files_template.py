import pyautogui as py
import time
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from router import verify, get_coord, check_item
from tools.vlm_tools import ctrl_find, scroll_back

class Explore_Agent(TypedDict):
    prompt: str
    file_name: str
    status: str
    path: List[str]
    vlm_model: str
    planner_model: str
    attempts: 0

def node_navigate(state: Explore_Agent):
    time.sleep(0.7)
    path = state.get('path', [])
    navigation_failed = False

    if path:
        print(f"2. Navigating path: {path}")
        for folder in path:
            item = check_item(state["vlm_model"], folder, type='folder')
            #Primero comprobamos que la carpeta está en pantalla.
            if item:
                #Como si que está entonces cogemos coordenadas.
                coord = get_coord(state["vlm_model"], folder)
                if coord:
                    x, y = coord['x'], coord['y']
                    print(f"Opening folder '{folder}' at {x}, {y}")
                    py.moveTo(x, y, duration=1)
                    py.doubleClick()
                    time.sleep(0.7)
                    #scroll_back(-150)
                #En caso de que este vlm diga que no hay coords, pues hacemos ctrl + f.
                else:
                    print(f"Folder '{folder}' found but no coords.")
                    navigation_failed = True
                    break
            #no encontró la carpeta del path, hacemos ctrl  + f.
            else:
                print(f"Folder '{folder}' not found.")
                navigation_failed = True
                break
    #una vez el path a terminado buscamos el archivo final.
    if not navigation_failed:
        print(f"Looking for final file: {state['file_name']}")
        item = check_item(state["vlm_model"], state['file_name'], type='file')
        
        if item:
            coord = get_coord(state["vlm_model"], state['file_name'])
            if coord:
                x, y = coord['x'], coord['y']
                print(f"Opening file '{state['file_name']}' at {x}, {y}")
                py.moveTo(x, y, duration=1)
                py.doubleClick()
                return {"status": "Item opened with coordinates.'"}
    
    #útlimo fallback total en caso de que todo falle.
    print("Using ctrl + f")
    ctrl_find(state)
    
    return {"status": "Item opened using search functions."}

def node_verify(state: Explore_Agent):
    print(f"4. Verifying action...")
    attempts = state.get('attempts', 0)
    path = state['path']
    file_name = state['path']
    verify_prompt = f"Is the file or folder '{file_name}' visible and open on the screen?"
    time.sleep(0.7)
    if verify(state["vlm_model"], verify_prompt):
        print("Action verified successfully.")
        if state['path']:
            return {"status": f"Navigated to {path} and opened {file_name} was verified."}
        else:
            return {"status": f"Opened {file_name} was verified."}
    else:
        print("Action verification failed.")
        if state['path']:
            return {"status": f"Failed to navigated to {path} and opened {file_name}.",
                    "attempts": attempts + 1}
        else:
            return {"status": f"Failed to opened {file_name}.",
                    "attempts": attempts + 1}
    

#Compilamos el workflow.
workflow = StateGraph(Explore_Agent)
workflow.add_node("navigate", node_navigate)
workflow.add_node("verify", node_verify)

workflow.set_entry_point("navigate")
workflow.add_edge("navigate", "verify")

#Si falla pues intentamos otra vez, un máximo de 2 intentos.
def verify_edge(state):
    status = state.get("status", "")
    attempts = state.get("attempts", 0)
    
    if "verified" in status or attempts >= 2:
        return END
    else:
        state['attempts'] = attempts + 1
        return "navigate"

workflow.add_conditional_edges("verify", verify_edge)

file_explorer = workflow.compile()