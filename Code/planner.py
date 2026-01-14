from utils.router import get_tool
from utils.metrics import start_monitoring, end_monitoring, append_metric
import json
from pathlib import Path
import time
import subprocess

planner_models = {
    'gemma3n': 'gemma3n:e2b',
    'gemma4k': 'gemma3:4b-it-qat',
    'functiongemma': 'functiongemma:latest',
    'llama3k': 'llama3.2:3b-instruct-q4_K_M',
    'llama3': 'llama3.2:3b',
    'ministral3': 'ministral-3:3b',
    'ministral3k': 'ministral-3:3b-instruct-2512-q4_K_M',
    'qwen4k': 'qwen3:4b-instruct-2507-q4_K_M',
    'qwen4instruct': 'qwen3:4b-instruct'
}

user_inputs = [
    "Thsi is just for initialisation to see how much it consumes."
    "Open Gonzalo_Anteproyecto.pdf which is in a folder Docs, which is in TFG folder, which is in Documents folder.",
    "Take a quick note saying that I have a meeting tommorrow at 3 pm in Tokyo please.",
    "Open my Entrevista_Reli.odt and make the text Gonzalo Torras Serrano in bold."
]

Path('data').mkdir(exist_ok=True)

total_planners = len(planner_models)
current = 0

for planner_name, planner_model in planner_models.items():
    current += 1
    print(f"\n{'='*60}")
    print(f"Testing PLANNER {current}/{total_planners}: {planner_name}")
    print(f"{'='*60}\n")
    
    for user_input in user_inputs:
        print(f"Query: {user_input}.")
        
        start_monitoring()
        
        start_time = time.time()
        intent_name, intent_args, inference_time = get_tool(planner_model, user_input)
        
        metrics = end_monitoring()
        
        result = {
            'model': planner_name,
            'user_input': user_input,
            'intent_name': intent_name,
            'intent_args': intent_args,
            'inference_time': inference_time
        }
        
        json_path = Path('data') / f'{planner_name}_planner.json'
        with open(json_path, 'a') as f:
            f.write(json.dumps(result) + '\n')
        
        append_metric(planner_name, 
                      user_input=user_input,
                      inference_time=inference_time,
                      intent_name=intent_name,
                      **metrics)
        subprocess.run(['ollama', 'stop', planner_model], capture_output=True)
        time.sleep(2)

print(f"\n{'='*60}")
print("All planners tested. Check data/ folder for results.")
print(f"{'='*60}")