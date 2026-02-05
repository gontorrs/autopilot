import pyautogui as py
import time
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from utils.router import verify, get_coord, check_item, verify_formatting
from tools.vlm_tools import ctrl_find, scroll_back

def final_verify(attempts, vlm_model, prompt, goal=None, content=None, style=None):
    print(f"4. Verifying action...")
    attempts = attempts
    time.sleep(1.5)
    if goal:
        if verify_formatting(vlm_model, content, style):
            print("Action verified successfully.")
            return {"status": "verified"}
        else:
            print("Action verification failed.")
            return {"status": "failed",
                    "attempts": attempts + 1}
    else:
        if verify(vlm_model, prompt):
            print("Action verified successfully.")
            return {"status": "verified"}
        else:
            print("Action verification failed.")
            return {"status": "failed",
                    "attempts": attempts + 1}

def open_app(app, vlm_model):
    print(f"1. Opening app...")
    item = check_item(vlm_model, app, type='application')
    if not item:
        ctrl_find(app)
        print(f"Launched without coordinates")
        return {"status": "launched without coordinates"}
    else:
        coord = get_coord(vlm_model, app)
        x, y = coord['x'], coord['y']
        print(f"Moving mouse: {x}, {y}")
        py.moveTo(x, y, duration=1)
        py.click()
        time.sleep(2)
        return {"status": "launched with coordinates"}
    
def navigate_path(path, vlm_model, file_name):
    time.sleep(0.7)
    path = path[1:]  # Remove Default from the path
    navigation_failed = False

    if path:
        print(f"2. Navigating path: {path}")
        for folder in path:
            item = check_item(vlm_model, folder, type='folder')
            #Primero comprobamos que la carpeta está en pantalla.
            if item:
                #Como si que está entonces cogemos coordenadas.
                coord = get_coord(vlm_model, folder)
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
        print(f"Looking for final file: {file_name}")
        item = check_item(vlm_model, file_name, type='file')
        
        if item:
            coord = get_coord(vlm_model, file_name)
            if coord:
                x, y = coord['x'], coord['y']
                print(f"Opening file '{file_name}' at {x}, {y}")
                py.moveTo(x, y, duration=1)
                py.doubleClick()
                return {"status": "opened_with_coordinates"}
    
    #útlimo fallback total en caso de que todo falle.
    print("Using ctrl + f")
    ctrl_find(file_name)
    
    return {"status": "opened_with_search"}

def find_content(content, vlm_model):
    print(f"Checking: {content}")
    time.sleep(3)
    print("Esperando 3 segundos")
    item = check_item(vlm_model, content, type='text_content')
    if not item:
        py.hotkey('ctrl','f')
        time.sleep(1)
        py.write(content, interval=0.05)
        time.sleep(1)
        py.press('enter')
        time.sleep(1)
        py.press('esc')
        return {"status": "texted found and selected text"}
    else:
        start_coord = f"Give me the coordinate for the start of the sentence {content}."
        end_coord = f"Give me the coordinate for the end of the sentence {content}."
        coord_start = get_coord(vlm_model, start_coord)
        coord_end = get_coord(vlm_model, end_coord)
        start_x, start_y = coord_start['x'], coord_start['y']
        end_x, end_y = coord_end['x'], coord_end['y']
        print(f"Doing a selection of {content}")
        py.moveTo(start_x, start_y)
        py.mouseDown()
        py.moveTo(end_x, end_y, duration=0.3)
        py.mouseUp()
        return {"status": "texted found and selected text with drag"}

def format(style):
    time.sleep(1)
    if 'bold' in style:
        py.hotkey('ctrl', 'b')
    elif 'italic' in style:
        py.hotkey('ctrl', 'i')
    elif 'under' in style:
        py.hotkey('ctrl', 'u')
    else:
        print("No style recognised")
    py.press('left')
    return {"status": "text formatted"}

def type_text(app_name, content, vlm_model):
    content_extended = f"Is there any written content in the open document, regardless of this: {content}?"
    if "notepad" not in app_name.lower():
        time.sleep(1)
        py.press('enter')
    time.sleep(1)
    print(f"2. Writing content...")
    if "notepad" is app_name.lower() and not verify(vlm_model, content_extended):
        py.hotkey('ctrl', 't')
        print("CTRL + T")
        time.sleep(0.3)
        py.write(content, interval=0.05)
    else:
        py.write(content, interval=0.05)
    return {"status": "content written"}