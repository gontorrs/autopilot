from utils.router import get_tool
from utils.metrics import start_monitoring, end_monitoring, append_metric
import json
from pathlib import Path
import time
import subprocess

planner_models = {
    'gemma4e4b': 'gemma4:e4b',
    'qwen8k': 'qwen3:8b-q4_K_M'
}

user_inputs = [
    "Thsi is just for initialisation to see how much it consumes."
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