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
                'coordinate': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'description': 'Coordinate [x, y] in 0-1000 scale. If action is wait, return [-1, -1].'
                }
            },
            'required': ['coordinate']
        }
    }
}

icons = {
    "notepad": "It's the Windows 11 Notepad a small blue and white notepad icon with horizontal lines.",
    "word": "Dark blue square icon with a large white 'W'.",
    "powerpoint": "Orange square icon with a large white 'P'.",
    "outlook": "Blue icon with a white 'O' sitting on top of an envelope image.",
    "file_explorer": "Yellow folder icon, looks like a physical file cabinet folder."
}

applications = {
    "notepad": "It's a simple and modern text editor with File/Edit/View menu toolbar. It has a .txt files opened or an 'Untitled' tab",
    "word": "Blue-themed interface. Look for a large 'W' icon. Includes a 'Ribbon' toolbar at the top with many formatting options. Displays a white rectangular area resembling a physical sheet of paper.",
    "powerpoint": "Orange or reddish-brown themed interface. Look for a 'P' icon. Features a sidebar on the left with small slide thumbnails and a large central area for the current slide.",
    "outlook": "Professional blue interface with an 'O' or envelope icon. Divided into three main sections: a narrow navigation rail on the far left, a folder/inbox list, and a large reading pane for emails.",
    "file_explorer": "Yellow folder icons, navigation pane on the left, search bar top right."
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
    if type == 'open':
        print('app')
        description = applications.get(item.lower(), "")
        return (
            f"You are looking for {item} which has this description {icons}"
            f"Is the application '{item}' present "
            "either as an open window OR as its icon in the taskbar? "
            "If you see its icon in the taskbar opened, minimised or closed with only the icon, answer 'YES'. "
            "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
        )
    elif type == 'application':
        description = applications.get(item.lower(), "")
        print('app')
        return (
            f"You are looking for an application with this description: {description}"
            f"Is the application present as an open window? "
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