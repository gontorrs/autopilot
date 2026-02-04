explorer_tool = {
    'type': 'function',
    'function': {
        'Operating System': 'Windows',
        'name': 'navigate_tool',
        'description': 'Open Windows File Explorer and navigate to a specific file or folder. Nothing more, only use to navigate or/and open the app.',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'An ordered list of folders to navigate, for example : ["downloads", "masters"]. If path is not provided return [].'
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
        "description": "Open a specific file and apply formatting (bold, italic, underlined) to a specific text segment.",
        "parameters": {
            "type": "object",
            "properties": {
                "application": {
                    "type": "string",
                    "enum": ["Notepad", "Microsoft Word", "Microsoft Power Point", "File Explorer", "Microsoft Outlook"],
                    "description": "The application required to START the process. IMPORTANT: If the user asks to open/find a specific file (e.g., 'Open file.docx'), you MUST return 'File Explorer' so the agent can navigate to it. Only return 'Microsoft Word' or 'Notepad' if the user asks to open the application purely to create a new file from scratch."
                },
                'path': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'An ordered list of folders to navigate, for example : ["downloads", "masters"]. If path is not provided return [].'
                },
                'file_name': {
                    'type': 'string',
                    'description': 'Name of the final file to search/open. Always required.'
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