import pyautogui as py
import time

from crew.crew import execute_gui_task, verify

def open_app(app_name, planner_model, vlm_model):
    print(f"1. Opening app: {app_name}...")
    result = execute_gui_task(
        target_item=app_name, 
        item_type='application', 
        action_intent='open', 
        planner_model=planner_model, 
        vlm_model=vlm_model
    )
    return {"status": result}

def navigate_path(path, planner_model, vlm_model, file_name=None):
    time.sleep(0.7)
    path = path[1:]  # Remove 'Default' from the path

    if path:
        print(f"2. Navigating path: {path}")
        for folder in path:
            print(f"Navigating to folder: {folder}")
            execute_gui_task(
                target_item=folder, 
                item_type='folder', 
                action_intent='open', 
                planner_model=planner_model, 
                vlm_model=vlm_model
            )
            time.sleep(1)
            
    if file_name:
        print(f"Looking for final file: {file_name}")
        result = execute_gui_task(
            target_item=file_name, 
            item_type='file', 
            action_intent='open', 
            planner_model=planner_model, 
            vlm_model=vlm_model
        )
        return {"status": result}
    return {"status": "success"}

def find_content(content, planner_model, vlm_model):
    print(f"Checking for content: {content}")
    time.sleep(3)
    result = execute_gui_task(
        target_item=content, 
        item_type='text_content', 
        action_intent='select', 
        planner_model=planner_model, 
        vlm_model=vlm_model
    )
    return {"status": result}

def format_text(style):
    time.sleep(1)
    if 'bold' in style:
        py.hotkey('ctrl', 'b')
    elif 'italic' in style:
        py.hotkey('ctrl', 'i')
    elif 'under' in style:
        py.hotkey('ctrl', 'u')
    else:
        print("No style recognized")
    py.press('left')
    return {"status": "text formatted"}

def type_text(app_name, content, planner_model, vlm_model):
    content_extended = f"Is there any written content in the open document, regardless of this: {content}?"
    if "notepad" not in app_name.lower():
        time.sleep(1)
        py.press('enter')
    time.sleep(1)
    print("Writing content...")
    
    if "notepad" not in app_name.lower() and not verify(content_extended, planner_model, vlm_model):
        py.hotkey('ctrl', 't')
        print("Executed CTRL + T")
        time.sleep(0.3)
        py.write(content, interval=0.05)
    else:
        py.write(content, interval=0.05)
    return {"status": "content written"}
