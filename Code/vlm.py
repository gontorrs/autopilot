from utils.router import get_tool, verify, check_item, verify_formatting
from utils.metrics import start_monitoring, end_monitoring, append_metric
import json
from pathlib import Path
import time
import traceback
import ollama

# Importamos los workflows para poder ejecutarlos
from workflows.files_template import file_explorer
from workflows.text_template import write_text
from workflows.change_text_template import change_text 

planner_model = 'qwen3:4b-instruct-2507-q4_K_M'

# vlm_models = {
#     'qwen2k-vl': 'qwen3-vl:2b-instruct-q4_K_M',
#     'gemma4k': 'gemma3:4b-it-qat',
#     'ministral3': 'ministral-3:3b',
#     'ministral3k': 'ministral-3:3b-instruct-2512-q4_K_M',
#     'qwen4k-vl': 'qwen3-vl:4b-instruct-q4_K_M',
#     'qwen4-vl': 'qwen3-vl:4b',
#     'qwen2-vl': 'qwen3-vl:2b-instruct',
#     'phi3': 'llava-phi3:3.8b'
# }

user_inputs = [
    "This is just for initialisation to see how much it consumes.",
    "Open Gonzalo_Anteproyecto.pdf which is in a folder Docs, which is in TFG folder, which is in Documents folder.",
    "Take a quick note saying that I have a meeting tommorrow at 3 pm in Tokyo please.",
    "Open my Entrevista_Reli.odt and make the text Gonzalo Torras Serrano in bold."
]

Path('data').mkdir(exist_ok=True)

total_vlms = len(vlm_models)
current = 0

for vlm_name, vlm_model in vlm_models.items():
    current += 1
    print(f"\n{'='*60}")
    print(f"Testing VLM {current}/{total_vlms}: {vlm_name}")
    print(f"{'='*60}\n")
    
    for user_input in user_inputs:
        try:
            print(f"Query: {user_input[:50]}...")
            ollama.chat(model=planner_model, keep_alive=0)
            ollama.chat(model=vlm_model, keep_alive=0)
            
            intent_name, intent_args, _ = get_tool(planner_model, user_input)
            
            if not intent_name:
                print("Planner failed, skipping VLM test")
                continue
            
            # Preparamos el estado inicial segun el intent
            initial_state = {
                "prompt": user_input,
                "vlm_model": vlm_model,
                "planner_model": planner_model,
                "status": "start",
                "attempts": 0
            }
            ollama.chat(model=planner_model, keep_alive=0)
            workflow = None
            if intent_name == 'navigate_tool':
                initial_state.update({
                    "file_name": intent_args.get('file_name', ''),
                    "app_name": intent_args.get('app_name', ''),
                    "path": intent_args.get('path', '')
                })
                workflow = file_explorer
            elif intent_name == 'write_tool':
                initial_state.update({
                    "app_name": intent_args.get('application', 'notepad'),
                    "content": intent_args.get('text', '')
                })
                workflow = write_text
            elif intent_name == 'change_tool':
                initial_state.update({
                    "app_name": intent_args.get('application', 'word'),
                    "file_name": intent_args.get('file_name', ''),
                    "content": intent_args.get('content', ''),
                    "style": intent_args.get('style', '')
                })
                workflow = change_text
            
            start_monitoring()
            
            start_time = time.time()
            
            # Ejecutamos el workflow real en lugar de solo verify
            if workflow:
                final_state = workflow.invoke(initial_state)
                vlm_result = final_state.get("status", "unknown")
            else:
                # Fallback por si acaso
                vlm_result = verify(vlm_model, user_input)

            inference_time = time.time() - start_time
            
            metrics = end_monitoring()
            
            result = {
                'model': vlm_name,
                'user_input': user_input,
                'intent_name': intent_name,
                'vlm_result': vlm_result,
                'inference_time': inference_time
            }
            
            json_path = Path('data') / f'{vlm_name}_vlm.json'
            with open(json_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
            
            print(f"VLM result: {vlm_result}")
            print(f"Inference time: {inference_time:.3f}s")
            print(f"CPU avg: {metrics.get('cpu_avg', 0):.1f}%, peak: {metrics.get('cpu_peak', 0):.1f}%")
            print(f"RAM avg: {metrics.get('ram_avg_mb', 0):.1f} MB, peak: {metrics.get('ram_peak_mb', 0):.1f} MB")
            if 'vram_avg_mb' in metrics:
                print(f"VRAM avg: {metrics.get('vram_avg_mb', 0):.1f} MB, peak: {metrics.get('vram_peak_mb', 0):.1f} MB")
            
            append_metric(vlm_name, 
                          user_input=user_input, 
                          inference_time=inference_time, 
                          intent_name=intent_name, 
                          vlm_result=vlm_result, 
                          **metrics)
                          
        except Exception as e:
            print(f"Error executing model {vlm_name}: {e}")
            # Guardamos el error para no perder el dato
            error_json_path = Path('data') / f'{vlm_name}_error.json'
            with open(error_json_path, 'a', encoding='utf-8') as f:
                 f.write(json.dumps({'model': vlm_name, 'error': str(e)}, ensure_ascii=False) + '\n')
            traceback.print_exc() 
        
        finally:
             ollama.chat(model=vlm_model, keep_alive=0)
             print("Esperando 20 segundos para limpieza manual...")
             time.sleep(20)


print(f"\n{'='*60}")
print("All VLMs tested. Check data/ folder for results.")
print(f"{'='*60}")