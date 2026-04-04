import json
from crewai import Crew, Process
from crew.agents import create_agents
from utils.tasks import create_planner_task
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
    'qwen2-vl': 'qwen3-vl:2b-instruct',
    'gemma4:e2b': 'gemma4:e2b',
    'gemma4:e4b': 'gemma4:e4b'
}

planner_model = model_dict['qwen4k']
vlm_model = model_dict['qwen2k-vl']

agents_dict = create_agents(planner_model, vlm_model)
pddl_agent = agents_dict["planner"]

def sanitize(text):
    return pddl_agent.sanitize(text)

def run_pddl_agent(state_dict, output_filename="navigate_problem.pddl"):
    task = create_planner_task(state_dict, pddl_agent, output_filename)
    
    result_raw = pddl_agent.execute_task(
        task=task,
        state_dict=state_dict,
        output_filename=output_filename
    )
    return result_raw

initial_state = None

#user_input = "Open the file Gonzalo_Anteproyecto.pdf which is in Documents, then TFG folder and then Docs folder."
#user_input = "Take a quick note saying that I have a meeting tommorrow at 3 pm in Tokyo please."
#user_input = "Open my Entrevista_Reli.odt in Gonzalo - UFV and make the text Gonzalo Torras Serrano in italic."
#user_input = 'Create a folder named "GTS" in the Documents folder.'
#user_input = 'Open my Entrevista_Reli.odt in Gonzalo - UFV and delete the text Gonzalo Torras Serrano.'
#user_input = 'Open my Entrevista_Reli.odt in Gonzalo - UFV and search for the text Gonzalo Torras Serrano.'
user_input = 'Copy my claude.docx in my Downloads folder and paste it in my Documents folder.'
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

elif intent_name == 'delete_tool':
    goal = f"(delete_text {sanitize(intent_args.get('content', ''))})"
    path = intent_args.get('path', [])
    path = ["Default"] + path

    initial_state = {
        "prompt": user_input,
        "app_name": intent_args.get('application'),
        "file_name": intent_args.get('file_name', ''),
        "content": intent_args.get('content', ''),
        "path": path,
        "goal": goal,
        "vlm_model": vlm_model,
        "planner_model": planner_model,
        "status": "start",
        "attempts": 0
    }

elif intent_name == 'search_tool':
    goal = f"(text_searched {sanitize(intent_args.get('content', ''))})"
    path = intent_args.get('path', [])
    path = ["Default"] + path

    initial_state = {
        "prompt": user_input,
        "app_name": intent_args.get('application'),
        "file_name": intent_args.get('file_name', ''),
        "content": intent_args.get('content', ''),
        "path": path,
        "goal": goal,
        "vlm_model": vlm_model,
        "planner_model": planner_model,
        "status": "start",
        "attempts": 0
    }

elif intent_name == 'copy_paste_tool':
    path_copy = ["Default"] + intent_args.get('path_to_copy', [])
    path_paste = ["Default"] + intent_args.get('path_to_paste', [])
    
    initial_state = {
        "prompt": user_input,
        "app_name": intent_args.get('application', 'file explorer'),
        "file_name": intent_args.get('file_name', ''),
        "path_to_copy": path_copy,
        "path_to_paste": path_paste,
        "cut": intent_args.get('operation', 'copy') == 'cut',
        "vlm_model": vlm_model,
        "planner_model": planner_model,
        "status": "start",
        "goal": f"(pasted {sanitize(intent_args.get('file_name', ''))} {sanitize(intent_args.get('path_to_paste', [''])[-1])})",
        "qa_goal": f"Is the file {sanitize(intent_args.get('file_name', ''))} present in the Documents folder?",
        "attempts": 0
    }
        
elif intent_name:
    print(f"Intent not classified.")
else:
    print("Fallo curioso.")

if initial_state:
    print(initial_state)
    print("\nFlow Starting using CrewAI PDDL Agent")
    
    # Usamos la función helper de CrewAI en lugar del antiguo to_goal
    plan = run_pddl_agent(initial_state, "navigate_problem.pddl")
    
    if plan and "Planner failed" not in plan:
        with open("pddl/results/mapping.json", "r") as f:
            name_map = json.load(f)
            
        orchestrator = Orchestrator(state=initial_state, name_map=name_map)
        orchestrator.run(plan)
        print(plan)
    else:
        print("El planner no supo hacer un plan.")