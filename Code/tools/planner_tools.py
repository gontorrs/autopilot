explorer_tool = {
    'type': 'function',
    'function': {
        'Operating System': 'Windows',
        'name': 'navigate_tool',
        'description': 'Open Windows File Explorer and navigate to a specific file or folder.',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Ordered list of folders to navigate: ["downloads", "masters"]. Omit if path is unknown.'
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
        "name": "write_tool",
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

change_text_tool = {
    "type": "function",
    "function": {
        "Operating System": "Windows",
        "name": "change_tool",
        "description": "Open a specific file in a text editor application and apply formatting (bold, italic, underlined) to a specific text segment.",
        "parameters": {
            "type": "object",
            "properties": {
                "application": {
                    "type": "string",
                    "enum": ["Notepad", "Microsoft Word", "Microsoft Power Point", "File Explorer", "Microsoft Outlook"],
                    "description": "The name of the Windows application to open to acces that file. If the user does not specify an application, this must default to 'File Explorer'."
                },
                "file_name": {
                    "type": "string",
                    "description": "The name of the file to open to format the text."
                },
                "content": {
                    "type": "string",
                    "description": "The specific text content inside the document that needs to be formatted."
                },
                "style": {
                    "type": "string",
                    "enum": ["bold", "italic", "underlined"],
                    "description": "The style to apply to the text content."
                }
            },
            "required": ["application", "file_name", "content", "style"]
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