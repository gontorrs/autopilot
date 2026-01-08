from router import get_tool
from workflows.files_template import file_explorer
from workflows.text_template import write_text
from workflows.open_application import open_application
from router import verify

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

user_input = "Take a quick note saying that I have a meeting tommorrow at 3 pm in Tokyo please."
refined_prompt = f"Original Goal: {user_input}. Based on the history of actions provided in the system context, what is the NEXT step? Do not repeat completed steps."
default_system_info = "History of actions: \n Step 0: No application is opened."
over = False;
i = 0
while over != True:
    #Paso número uno, abrimos la o las aplicaciones.
    intent_name, intent_args = get_tool(planner_model, refined_prompt, default_system_info)
    
    if intent_name == 'open_application':
        i+=1
        print(f"Intent: {intent_name}")
        print(f"Arguments: {intent_args}")
        initial_state ={
            "prompt": user_input, 
            "app_name": intent_args.get('app_name', ''),
            "vlm_model": vlm_model,
            "planner_model": planner_model, 
            "status": "start"
        }
        result = open_application.invoke(initial_state)
        default_system_info += f"\n Step {i}: {result.get('status')}"

    elif intent_name == 'navigate_explorer':
        i+=1
        print(f"Intent: {intent_name}")
        print(f"Arguments: {intent_args}")
        initial_state ={
            "prompt": user_input,
            "file_name": intent_args.get('file_name', ''),
            "path": intent_args.get('path', ''),
            "vlm_model": vlm_model,
            "planner_model": planner_model,
            "status": "start"
        }
        result = file_explorer.invoke(initial_state)
        default_system_info += f"\n Step {i}: {result.get('status')}"

    elif intent_name == 'type_text':
        i+=1
        print(f"Intent: {intent_name}")
        print(f"Arguments: {intent_args}")
        initial_state ={
            "prompt": user_input, 
            "app_name": intent_args.get('app_name', ''),
            "content": intent_args.get('text', ''),
            "vlm_model": vlm_model,
            "planner_model": planner_model, 
            "status": "start"
        }
        result = write_text.invoke(initial_state)
        default_system_info += f"\n Step {i}: {result.get('status')}"

    elif intent_name == 'verify_screen':
        i+=1
        print(f"Intent: {intent_name}")
        print(f"Arguments: {intent_args}")
        result = verify(vlm_model, user_query=user_input)
        default_system_info += f"\n Step {i}: The entire workflow was verified with a result of {result}"
        over = True
    
    elif intent_name:
        i+=1
        print(f"Intent not classified.")
    else:
        i+=1
        print("Fallo curioso.")
    print(default_system_info)