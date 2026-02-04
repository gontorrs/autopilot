from utils.router import get_tool
from utils.pddl import to_goal
from utils.parser import parse_plan
from utils.index import init_indexer, search_files

search_engine = init_indexer()

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
user_input = "Take a quick note saying that I have a meeting tommorrow at 3 pm in Tokyo please."
#user_input = "Open my Entrevista_Reli.odt in Gonzalo - UFV and make the text Gonzalo Torras Serrano in bold."
intent_name, intent_args = get_tool(planner_model, user_input)

def main():

    if intent_name == 'navigate_tool':
        print(f"Intent: {intent_name}")
        print(f"Arguments: {intent_args}")
        goal = "(open_file)"
        path = search_files
        
        initial_state = {
            "prompt": user_input,
        "file_name": intent_args.get('file_name', ''),
        "app_name": intent_args.get('app_name', ''),
        "path": path,
        "vlm_model": vlm_model,
        "planner_model": planner_model,
        "status": "start",
        "goal": goal,
        "attempts": 0
        }
        print(initial_state)
        print("\nFlow Starting")
        plan = to_goal('pddl/templates/navigate_template.pddl', initial_state, "navigate_problem.pddl")
        parse_plan(plan, initial_state)
        print(plan)

    elif intent_name == 'write_tool':
        print(f"Intent: {intent_name}")
        print(f"Arguments: {intent_args}")
        goal = "(typed_text)"
        
        initial_state = {
            "prompt": user_input,
        "app_name": intent_args.get('application', 'notepad'),
        "content": intent_args.get('text', ''),
        "vlm_model": vlm_model,
        "planner_model": planner_model,
        "status": "start",
        "goal": goal,
        "attempts": 0
        }
        print(initial_state)
        print("\nFlow Starting")
        plan = to_goal('pddl/templates/text_template.pddl', initial_state, "text_problem.pddl")
        parse_plan(plan, initial_state)
        print(plan)

    elif intent_name == 'change_tool':
        print(f"Intent: {intent_name}")
        print(f"Arguments: {intent_args}")
        goal = "(changed_text)"
        path = intent_args.get('path', [])
        path = ["Default"] + path
        
        initial_state = {
            "prompt": user_input,
            "app_name": intent_args.get('application'),
            "file_name": intent_args.get('file_name', ''),
            "content": intent_args.get('content', ''),
            "style": intent_args.get('style', ''),
            "path": path,
            "goal": goal,
            "vlm_model": vlm_model,
            "planner_model": planner_model,
            "status": "start",
            "attempts": 0
        }
        print(initial_state)
        print("\nFlow Starting")
        plan = to_goal('pddl/templates/change_template.pddl', initial_state, "change_problem.pddl")
        parse_plan(plan, initial_state)
        print(plan)
            
    elif intent_name:
        print(f"Intent not classified.")
    else:
        print("Fallo curioso.")
    
if __name__ == "__main__":
    main()