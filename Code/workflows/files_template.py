import pyautogui
import time
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from router import verify, get_coord, check_item
from tools.vlm_tools import click, ctrl_find, scroll_back

class Explore_Agent(TypedDict):
    prompt: str
    file_name: str
    app_name: str
    status: str
    path: List[str]
    vlm_model: str
    planner_model: str
    attempts: int

def node_launch_explorer(state: Explore_Agent):
    print(f"1. File explorer open")
    #item = check_item(state["vlm_model"], state['app_name'], type='application')
    item = 1
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
                    pyautogui.moveTo(x, y, duration=1)
                    coord['action'] = 'double_click'
                    click(coord)
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
                pyautogui.moveTo(x, y, duration=1)
                coord['action'] = 'double_click'
                click(coord)
                return {"status": "opened_with_coordinates"}
    
    #útlimo fallback total en caso de que todo falle.
    print("Using ctrl + f")
    ctrl_find(state)
    
    return {"status": "opened_with_search"}

def node_verify(state: Explore_Agent):
    print(f"4. Verifying action...")
    time.sleep(0.7)
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

#Si falla pues intentamos otra vez, un máximo de 2 intentos.
def verify_edge(state, result):
    state['attempts'] += 1
    if result.get("status") == "verified" or state['attempts'] >= 2:
        return END
    else:
        return "launch"

workflow.add_conditional_edges("verify", verify_edge)

file_explorer = workflow.compile()