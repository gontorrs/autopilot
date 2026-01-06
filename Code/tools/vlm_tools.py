# vlm_tools.py
import pyautogui
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
        f"Observe the screenshot and identify where to click to: '{goal}'. "
        "Use the tool_click tool to specify the action and normalized coordinates (0-1000 scale)."
    )

def verification_prompt_file(goal):
    return (
        f"Observe the screenshot. Task: {goal}. "
        "Has the objective been achieved? Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )

def check_item_prompt(item):
    return (
        f"Observe the screenshot. Is '{item}' present on the screen? "
        "Not anything related to the item, jus it this item is present, if it's an application icon, a folder, a file, etc."
        "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )

def click(coord: dict):
    if(coord['action'] == 'double_click'):
        pyautogui.doubleClick()
        return f"Left click: ({coord['x']}, {coord['y']})."
    elif(coord['action'] == 'right_click'):
        pyautogui.rightClick()
        return f"Right click: ({coord['x']}, {coord['y']})."
    else:
        pyautogui.click()
        return f"Left click: ({coord['x']}, {coord['y']})."
    
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