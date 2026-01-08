explorer_tool = {
    'type': 'function',
    'function': {
        'Operating System': 'Windows',
        'name': 'navigate_template',
        'description': 'Open Windows File Explorer and navigate to a specific file or folder.',
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
                    'description': 'Name of the final file to search/open. Always required.'
                },
                'app_name': {
                    'type': 'string',
                    'description': 'Application to use (e.g., "Windows File Explorer").'
                }
            },
            'required': ['operation', 'file_name']
        }
    }
}

tool_text = {
    "type": "function",
    "function": {
        'Operating System': 'Windows',
        "name": "write_template",
        "description": "Open a text editor application and type specific content into it.",
        "parameters": {
            "type": "object",
            "properties": {
                "application": {
                    "type": "string",
                    "enum": ["notepad", "word", "power point"],
                    "description": "The name of the Windows application to open (e.g., 'notepad' or 'word'). If application is not stated, default to notepad."
                },
                "text": {
                    "type": "string",
                    "description": "The content text that needs to be written inside the application."
                }
            },
            "required": ["application", "text"]
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