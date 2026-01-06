import pyautogui
import time
# vlm_tools.py


tool_click = {
    'type': 'function',
    'function': {
        'name': 'computer_use',
        'description': 'Use a mouse and keyboard to interact with a computer GUI. The screen resolution is normalized to 0-1000. Return coordinates in this scale 0-1000.',
        'parameters': {
            'type': 'object',
            'properties': {
                'action': {
                    'type': 'string',
                    'enum': ['left_click', 'double_click', 'right_click', 'wait'],
                    'description': 'The action to perform on the screen. left_click to open applications, double_click to open files or folders, right_click to open context menus, wait means the objective is not present.'
                },
                'coordinate': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'description': 'Coordinate [x, y] in 0-1000 scale. If action is wait, return [-1, -1].'
                }
            },
            'required': ['action', 'coordinate']
        }
    }
}


def get_coordinates_prompt(goal):
    return (
        f"Observe the screenshot and identify where to click to: '{goal}' folder, file or application. "
        "Use the tool_click tool to specify the action and normalized coordinates (0-1000 scale)."
        )

def verification_prompt_file(goal):
    return (
        f"Observe the screenshot. Task: {goal}. "
        "Has the objective been achieved? Respond ONLY with 'YES' or 'NO' followed by a brief observation. Make sure to check if it is achevied completely and not partially."
    )

def check_item_prompt(item, type='item'):
    if type == 'application':
        print('app')
        return (
            f"Is the application '{item}' present "
            "either as an open window OR as its icon in the taskbar? "
            "If you see its icon in the taskbar opened, minimised or closed with only the icon, answer 'YES'. "
            "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
        )
    elif type == 'file':
        return (
        f"Observe the screenshot. Is the {type} '{item}' present on the screen?"
        f"Note: Ignore file extensions. If you see '{item}.pdf', or just '{item}', or any other extension counts as YES."
        "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )
    return (
        f"Observe the screenshot. Is the {type} '{item}' present on the screen?"
        "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )

def click(coord: dict):
    if(coord['action'] == 'double_click'):
        pyautogui.doubleClick()
        return f"Double click: ({coord['x']}, {coord['y']})."
    elif(coord['action'] == 'right_click'):
        pyautogui.rightClick()
        return f"Right click: ({coord['x']}, {coord['y']})."
    else:
        pyautogui.click()
        return f"Left click: ({coord['x']}, {coord['y']})."
    
def ctrl_find(state: dict):
    pyautogui.press('win')
    time.sleep(1)
    pyautogui.write(state['file_name'], interval=0.05)
    time.sleep(1)
    print(f"3. Opening file...")
    pyautogui.press('enter')
    time.sleep(1)

def scroll_back(value):
    pyautogui.keyDown('ctrl')
    time.sleep(0.1)

    pyautogui.scroll(value) 
    
    time.sleep(0.1)
    pyautogui.keyUp('ctrl')
    
def _collect_tools():
    tools = []
    g = globals()
    for name, value in g.items():
        if isinstance(value, dict):
            if (value.get('type') == 'function' and 
                'function' in value and 
                isinstance(value['function'], dict)):
                tools.append(value)
    return tools

vlm_tools = _collect_tools()