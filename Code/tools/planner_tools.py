explorer_tool = {
    'type': 'function',
    'function': {
        'Operating System': 'Windows',
        'name': 'open_template',
        'description': 'Open Windows File Explorer and navigate to a specific file or folder.',
        'parameters': {
            'type': 'object',
            'properties': {
                'operation': {
                    'name': 'open',
                    'type': 'string',
                    'description': 'Action to perform: open a folder view or open a specific file.'
                },
                'file_name': {
                    'type': 'string',
                    'description': 'Name of the final file or folder to open if aplicable, state if it is a folder or a file.'
                },
                'app_name': {
                    'type': 'string',
                    'description': 'Name of the application to use to open the file or folder.'
                }
            },
            'required': ['operation', 'file_name']
        }
    }
}

tool_text = {
    "type": "function",
    "function": {
        "name": "write_text",
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