# planner_tools.py
open_app = {
    'type': 'function',
    'function': {
        'Operating System': 'Windows',
        'name': 'open_application',
        'description': (
            'Opens a desktop application. '
            'RULES: If user wants to write text and no app is named, select "notepad". '
            'If user wants to find/open a file or folder and no app is named, select "file_explorer".'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'app_name': {
                    'type': 'list',
                    'enum': ['notepad', 'word', 'powerpoint', 'file_explorer'],
                    'description': 'The application to launch. e.g. ["notepad"], ["file_explorer", "notepad"]'
                }
            },
            'required': ['app_name']
        }
    }
}

task_complete = {
    'type': 'function',
    'function': {
        'name': 'task_complete',
        'description': 'Call this function ONLY when the user goal has been fully achieved and verified. This stops the agent.',
        'parameters': {
            'type': 'object',
            'properties': {
                'reason': {
                    'type': 'string',
                    'description': 'Short explanation of why the task is considered done.'
                }
            },
            'required': ['reason']
        }
    }
}

navigate = {
    'type': 'function',
    'function': {
        'Operating System': 'Windows',
        'name': 'navigate_explorer',
        'description': 'Navigate to a specific file or folder in Windows File Explorer. Use this ONLY after opening Windows File Explorer.',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Optional ordered list of folders to navigate: ["downloads", "masters"]. Omit if path is unknown.'
                },
                'file_name': {
                    'type': 'string',
                    'description': 'Name of the final file or folder to search/open. Always required.'
                }
            },
            'required': ['file_name']
        }
    }
}

type_text = {
    'type': 'function',
    'Operating System': 'Windows',
    'function': {
        'name': 'type_text',
        'description': 'Types text into the currently active window. Use this ONLY after opening an application.',
        'parameters': {
            'type': 'object',
            'properties': {
                'text': {
                    'type': 'string',
                    'description': 'The text content to type.'
                }
            },
            'required': ['text']
        }
    }
}

verify = {
    'type': 'function',
    'Operating System': 'Windows',
    'function': {
        'name': 'verify_screen',
        'description': 'Looks at the screen to check if the entire user goal is done. This is the last tool to be used in the entire flow.',
        'parameters': {
            'type': 'object',
            'properties': {},
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

planner_tools = _collect_tools()