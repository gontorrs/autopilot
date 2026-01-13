from router import get_tool
from workflows.files_template import file_explorer
from workflows.text_template import write_text
from workflows.change_text_template import change_text

model_dict = {
    'gemma4k': 'gemma3:4b-it-qat',
    'functiongemma': 'functiongemma:latest',
    'qwen2k-vl': 'qwen3-vl:2b-instruct-q4_K_M',
    'qwen4k-vl': 'qwen3-vl:4b-instruct-q4_K_M',
    'llama3k': 'llama3.2:3b-instruct-q4_K_M',
    'llama3': 'llama3.2:3b',
    'ministral3': 'ministral-3:3b',
    'ministral3k': 'ministral-3:3b-instruct-2512-q4_K_M',
    'qwen4k': 'qwen3:4b-instruct-2507-q4_K_M',
    'qwen4instruct': 'qwen3:4b-instruct',
    'qwen4-vl': 'qwen3-vl:4b',
    'qwen2-vl': 'qwen3-vl:2b-instruct'
}

planner_model = model_dict['qwen4k']
vlm_model = model_dict['qwen4k-vl']

#user_input = "Open Gonzalo_Anteproyecto.pdf which is in a folder Docs, which is in TFG folder, which is in Documents folder."
#user_input = "Take a quick note saying that I have a meeting tommorrow at 3 pm in Tokyo please."
user_input = "Open my Entrevista_Reli.odt and make the text Gonzalo Torras Serrano in bold."
intent_name, intent_args = get_tool(planner_model, user_input)
    
if intent_name == 'navigate_tool':
    print(f"Intent: {intent_name}")
    print(f"Arguments: {intent_args}")
      
    initial_state = {
        "prompt": user_input,
       "file_name": intent_args.get('file_name', ''),
       "app_name": intent_args.get('app_name', ''),
       "path": intent_args.get('path', ''),
       "vlm_model": vlm_model,
       "planner_model": planner_model,
       "status": "start",
       "attempts": 0
    }
    print(initial_state)
    print("\nFlow Starting")
    file_explorer.invoke(initial_state)

elif intent_name == 'write_tool':
    print(f"Intent: {intent_name}")
    print(f"Arguments: {intent_args}")
      
    initial_state = {
        "prompt": user_input,
       "app_name": intent_args.get('application', 'notepad'),
       "content": intent_args.get('text', ''),
       "vlm_model": vlm_model,
       "planner_model": planner_model,
       "status": "start",
       "attempts": 0
    }
    print(initial_state)
    print("\nFlow Starting")
    write_text.invoke(initial_state)

elif intent_name == 'change_tool':
    print(f"Intent: {intent_name}")
    print(f"Arguments: {intent_args}")
      
    initial_state = {
        "prompt": user_input,
        "app_name": intent_args.get('application', 'word'),
        "file_name": intent_args.get('file_name', ''),
        "content": intent_args.get('content', ''),
        "style": intent_args.get('style', ''),
        "vlm_model": vlm_model,
        "planner_model": planner_model,
        "status": "start",
        "attempts": 0
    }
    print(initial_state)
    print("\nFlow Starting")
    change_text.invoke(initial_state)
        
elif intent_name:
    print(f"Intent not classified.")
else:
    print("Fallo curioso.")