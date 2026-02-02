import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List
from utils.router import get_tool, verify
from workflows.files_template import file_explorer
from workflows.text_template import write_text
from workflows.open_application import open_application


from utils.metrics import start_monitoring, end_monitoring, append_metric


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


VLM_MODEL_NAME = 'qwen3-vl:4b-instruct-q4_K_M' 


# === PROMPTS (Copiado de tu estática) ===
user_inputs = [
    "Open Gonzalo_Anteproyecto.pdf which is in a folder Docs, which is in TFG folder, which is in Documents folder.",
    "Take a quick note saying that I have a meeting tommorrow at 3 pm in Tokyo please.",
    "Open my Entrevista_Reli.odt and make the text Gonzalo Torras Serrano in bold."
]


def run_modular_task(planner_model: str, vlm_model: str, user_input: str):
    default_system_info = "History of actions: \n Step 0: No application is opened."

    refined_prompt = f"""
Original Goal: {user_input}

History of actions:
{default_system_info}

INSTRUCTIONS:
1. Analyze the history. Has the goal been achieved?
2. If YES, you MUST call the 'verify_screen' or 'task_complete' tool immediately.
3. If NO, determine the next necessary step.
4. Do NOT repeat steps that are already marked as "verified" or "done" in the history.
"""
    
    step_trace = []
    
    over = False
    i = 0
    MAX_STEPS = 5
    
    while not over and i < MAX_STEPS:
        i += 1
        
        intent_name, intent_args = get_tool(planner_model, refined_prompt, default_system_info)
        
        step_info = {"step": i, "intent": intent_name, "args": intent_args, "status": "attempting"}
        print(f"--- Step {i}: {intent_name} ---")


        result_status = ""
        
        # 2. Router de ejecución
        if intent_name == 'open_application':
            initial_state = {
                "prompt": user_input,
                "app_name": intent_args.get('app_name', ''),
                "vlm_model": vlm_model,
                "planner_model": planner_model,
                "status": "start"
            }
            result = open_application.invoke(initial_state)
            result_status = result.get('status')
            
        elif intent_name == 'navigate_explorer':
            initial_state = {
                "prompt": user_input,
                "file_name": intent_args.get('file_name', ''),
                "path": intent_args.get('path', ''),
                "vlm_model": vlm_model,
                "planner_model": planner_model,
                "status": "start"
            }
            result = file_explorer.invoke(initial_state)
            result_status = result.get('status')


        elif intent_name == 'type_text':
            initial_state = {
                "prompt": user_input,
                "app_name": intent_args.get('app_name', ''),
                "content": intent_args.get('text', ''),
                "vlm_model": vlm_model,
                "planner_model": planner_model,
                "status": "start"
            }
            result = write_text.invoke(initial_state)
            result_status = result.get('status')


        elif intent_name == 'verify_screen':
            # Verificación final
            verified = verify(vlm_model, user_query=user_input)
            result_status = f"Verified: {verified}"
            if verified:
                over = True
            
        elif intent_name == 'task_complete':
            print(f"Agent decided to finish: {intent_args.get('reason')}")
            result_status = "Task completed by agent decision."
            over = True

        elif intent_name:
            result_status = "Intent recognized but no handler defined."
        else:
            result_status = "No intent generated (None)."
            over = True


        default_system_info += f"\n Step {i}: {result_status}"
        step_info["result"] = result_status
        step_trace.append(step_info)


    return step_trace


if __name__ == "__main__":
    Path('data').mkdir(exist_ok=True)
    
    total_planners = len(planner_models)
    current = 0


    for planner_name, planner_model in planner_models.items():
        current += 1
        print(f"\n{'='*60}")
        print(f"Testing Modular planner {current}/{total_planners}: {planner_name}")
        print(f"{'='*60}\n")


        for user_input in user_inputs:
            print(f"Query: {user_input}")
            
            # Monitoreamos
            start_monitoring()
            start_time = time.time()
            
            try:
                # Ejecutamos la tarea completa
                trace = run_modular_task(planner_model, VLM_MODEL_NAME, user_input)
                success = True
            except Exception as e:
                print(f"Error executing task: {e}")
                trace = [{"error": str(e)}]
                success = False
                
            elapsed_time = time.time() - start_time
            metrics = end_monitoring()


            # Guradamos datos
            result_data = {
                'model': planner_name,
                'user_input': user_input,
                'total_time': elapsed_time,
                'steps_count': len(trace),
                'execution_trace': trace,
                **metrics
            }


            # JSON detallado
            json_path = Path('data') / f'{planner_name}_modular_planner.json'
            with open(json_path, 'a') as f:
                f.write(json.dumps(result_data, indent=2) + '\n,')


            append_metric(planner_name,
                          user_input=user_input,
                          inference_time=elapsed_time,
                          steps=len(trace),
                          intent_name="MODULAR_FLOW",
                          **metrics)
            
            print(f"Task finished in {elapsed_time:.2f}s with {len(trace)} steps.")
            print("20 Segundos de espera para limpiar todo")
            time.sleep(20)


        # Limpieza
        subprocess.run(['ollama', 'stop', planner_model], capture_output=True)
        time.sleep(2)


    print(f"\n{'='*60}")
    print("All modular planners tested. Check data/ folder for results.")
    print(f"{'='*60}")