import json
from utils.pddl import to_goal, sanitize
from crew.crew import get_intent
from crew.orchestrator import Orchestrator
import langchain
langchain.debug = True

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
vlm_model = model_dict['qwen2k-vl']

#user_input = "Open the file Gonzalo_Anteproyecto.pdf which is in Documents, then TFG folder and then Docs folder."
#user_input = "Take a quick note saying that I have a meeting tommorrow at 3 pm in Tokyo please."
user_input = "Open my Entrevista_Reli.odt in Gonzalo - UFV and make the text Gonzalo Torras Serrano in bold."
#user_input = 'Create a folder named "GTS" in the Documents folder.'
intent_name, intent_args = get_intent(user_input, planner_model, vlm_model)
print(f"DEBUG intent_name: '{intent_name}'")
print(f"DEBUG intent_args: {intent_args}")
    
if intent_name == 'navigate_tool':
    goal = "(open_file " + sanitize(intent_args.get('file_name', '')) + ")"
    path = intent_args.get('path', '')
    path = ["Default"] + path
      
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
    plan = to_goal(initial_state, "navigate_problem.pddl")
    if plan:
        with open("pddl/results/mapping.json", "r") as f:
            name_map = json.load(f)
        orchestrator = Orchestrator(state=initial_state, name_map=name_map)
        orchestrator.run(plan)
    print(plan)

elif intent_name == 'write_tool':
    goal = "(typed_text " + sanitize(intent_args.get('text', '')) + ")"
      
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
    plan = to_goal(initial_state, "navigate_problem.pddl")
    if plan:
        with open("pddl/results/mapping.json", "r") as f:
            name_map = json.load(f)
        orchestrator = Orchestrator(state=initial_state, name_map=name_map)
        orchestrator.run(plan)
    print(plan)

elif intent_name == 'change_tool':
    goal = "(changed_text " + sanitize(intent_args.get('style', '')) + ")"
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
    plan = to_goal(initial_state, "navigate_problem.pddl")
    if plan:
        with open("pddl/results/mapping.json", "r") as f:
            name_map = json.load(f)
        orchestrator = Orchestrator(state=initial_state, name_map=name_map)
        orchestrator.run(plan)
    print(plan)

elif intent_name == 'create_tool':
    item_type = intent_args.get('item_type', 'folder')
    name_raw = intent_args.get('name', '')
    goal = f"(created {sanitize(name_raw)}_name)"
    path = intent_args.get('path', [])
    path = ["Default"] + path

    initial_state = {
        "prompt": user_input,
        "app_name": intent_args.get('application'),
        "file_name_new": name_raw if item_type == "file" else None,
        "folder_name": name_raw if item_type == "folder" else None,
        "name": name_raw,
        "path": path,
        "goal": goal,
        "vlm_model": vlm_model,
        "planner_model": planner_model,
        "status": "start",
        "attempts": 0
    }

    print(initial_state)
    print("\nFlow Starting")
    plan = to_goal(initial_state, "navigate_problem.pddl")
    if plan:
        with open("pddl/results/mapping.json", "r") as f:
            name_map = json.load(f)
        orchestrator = Orchestrator(state=initial_state, name_map=name_map)
        orchestrator.run(plan)
    print(plan)
        
elif intent_name:
    print(f"Intent not classified.")
else:
    print("Fallo curioso.")