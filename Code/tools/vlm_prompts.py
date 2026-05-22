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

def get_coordinates_prompt(goal):
    return (
        f"Observe the screenshot and identify where to click to find: '{goal}'. If it's an app do not minimise or close the app."
        "Respond ONLY with the coordinates in this exact format: [x, y] in 0-1000 scale. Nothing else."
    )

def verification_prompt_file(goal):
    return (
        f"Observe the screenshot. Task: {goal}. "
        "Has the objective been achieved? Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )

def verification_prompt_create(goal):
    return (
        "Observe the screenshot."
        f"Is there a folder or file with the name: {goal}? Respond ONLY with 'YES' or 'NO' followed by a brief observation. If it's a file, ignore the extension."
    )

def check_item_prompt(item, type='item'):
    if type == 'application':
        print('app')
        return (
            f"Is the application '{item}' present "
            "either as an open window, or not running but visible on the desktop or taskbar? "
            "If you see its icon in the taskbar opened, minimised or closed with only the icon, answer 'YES'. "
            "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
        )
    elif type == 'file':
        print("file")
        return (
        f"Observe the screenshot. Is the {type} '{item}' present on the screen?"
        f"Note: Ignore file extensions. If you see '{item}.pdf', or just '{item}', or any other extension counts as YES."
        "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )
    elif type == 'text_content':
        print("text_content")
        return (
        f"Observe the screenshot. Look ONLY at the content inside the open document window (not file names, not taskbar, not folder names). "
        f"Is the text '{item}' visible as content WITHIN the open document? "
        f"IMPORTANT: Only answer YES if you can see this exact text as part of the document content that is currently displayed and readable. "
        "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )
    print("other")
    return (
        f"Observe the screenshot. Is the {type} '{item}' present on the screen?"
        "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )
def verification_prompt_formatting(text, style):
    style_description = {
        'bold': 'in bold/thick font weight',
        'italic': 'in italic (in other words a bit inclined compared to normal text)', 
        'underlined': 'with an underline'
    }

    style_key = style.lower()
    if style_key not in style_description:
        style_key = 'bold'
    
    return (
        f"Observe the screenshot. Find the text '{text}' in the document. "
        f"Compare its visual appearance to the surrounding text around it. "
        f"Is it formatted {style_description[style_key]}? "
        f"IMPORTANT: Base your answer PRIMARILY on the visual appearance of the text itself compared to nearby text — NOT on the toolbar state, since the toolbar only reflects formatting when the cursor is placed on that text. "
        f"Ignore any selection highlights. "
        "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )

def verification_prompt_delete(text):
    return (
        f"Observe the screenshot. Look ONLY at the content inside the open document window. "
        f"The task was to DELETE the text '{text}' from the document. "
        f"The task is successful if the text is NOT visible in the document.\n\n"
        f"You MUST format your response exactly like this:\n"
        f"OBSERVATION: [Write a detailed description of what text you see in the document]\n"
        f"DECISION: [Write only YES if the text '{text}' is NO LONGER visible (deletion succeeded), "
        f"or NO if the text is still visible (deletion failed)]"
    )

def verification_prompt_copy_paste(file_name, dest_folder):
    return (
        f"Observe the screenshot. Look at the current folder contents. "
        f"Is the file '{file_name}' visible in the screen?"
        "Respond ONLY with 'YES' or 'NO' followed by a brief observation."
    )

def verification_prompt_search(text):
    return (
        f"Observe the screenshot. Look ONLY at the content inside the open document window. "
        f"The task was to SEARCH for the text '{text}' in the document. "
        f"The search is successful if the text is visible in the document.\n\n"
        f"You MUST format your response exactly like this:\n"
        f"OBSERVATION: [Write a detailed description of what text you see in the document]\n"
        f"DECISION: [Write only YES if the text '{text}' is visible (search succeeded), "
        f"or NO if the text is not visible (search failed)]"
    )


MODULAR_PROMPTS = {
    # Group 1: navigate, create, copy_paste
    "navigate_tool": (
        "Look at this screenshot and answer ONLY in this exact JSON format, no other text:\n"
        '{"file_explorer_open": true/false, "current_folder": "<folder name or null>"}\n'
        "- file_explorer_open: is File Explorer OPEN right now?\n"
        "- current_folder: if File Explorer is open, what is the LAST folder name shown in the address bar? File Explorer MUST be OPENED for this to be valid, otherwise just answer null."
        "If you can see the desktop clean with no open windows, answer false for file_explorer_open and null for current_folder."
    ),

    # write
    "write_tool": (
        "Look at this screenshot and answer ONLY in this exact JSON format, no other text:\n"
        '{"notepad_open": true/false, "has_text": true/false}\n'
        "- notepad_open: is Notepad currently open as the active window?\n"
        "- has_text: if Notepad is open, is there any text already written in it? If not open, false."
    ),

    # Group 3: change, delete, search
    "change_tool": (
        "Look at this screenshot and answer ONLY in this exact JSON format, no other text:\n"
        '{"active_app": "<file_explorer/word/libreoffice/none>", "current_folder": "<folder name or null>"}\n'
        "- active_app: what is the active window? Answer 'file_explorer', 'word', 'libreoffice', or 'none'.\n"
        "- current_folder: if active_app is file_explorer, what is the LAST folder name in the address bar? Otherwise null."
    ),
}

# Aliases
MODULAR_PROMPTS["create_tool"] = MODULAR_PROMPTS["navigate_tool"]
MODULAR_PROMPTS["copy_paste_tool"] = MODULAR_PROMPTS["navigate_tool"]
MODULAR_PROMPTS["delete_tool"] = MODULAR_PROMPTS["change_tool"]
MODULAR_PROMPTS["search_tool"] = MODULAR_PROMPTS["change_tool"]