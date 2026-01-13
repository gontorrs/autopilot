import pyautogui
import time


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
                    'description': 'Coordinate [x, y] in 0-1000 scale.'
                }
            },
            'required': ['coordinate']
        }
    }
}


def get_coordinates_prompt(goal):
    return (
        f"Observe the screenshot and identify where to click to: '{goal}' folder, file, application, butto or area. "
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
    elif type == 'text_content':
        return (
        f"Observe the screenshot. Look ONLY at the content inside the open document window (not file names, not taskbar, not folder names). "
        f"Is the text '{item}' visible as content WITHIN the open document? "
        f"IMPORTANT: Only answer YES if you can see this exact text as part of the document content that is currently displayed and readable. "
        "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )
    return (
        f"Observe the screenshot. Is the {type} '{item}' present on the screen?"
        "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )
def verification_prompt_formatting(text, style):
    style_description = {
        'bold': 'in bold/thick font weight',
        'italic': 'in italic/slanted style', 
        'underlined': 'with an underline'
    }
    
    style_key = style.lower()
    if style_key not in style_description:
        style_key = 'bold'
    
    return (
        f"Observe the screenshot. Look at the document content and find the text '{text}'. "
        f"Is this text formatted {style_description[style_key]}? "
        f"IMPORTANT: Ignore any selection highlights (grey/blue backgrounds) - focus ONLY on the actual text formatting. "
        f"Look at the font weight/style of the letters themselves. "
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