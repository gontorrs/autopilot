import ollama
from tools.planner_tools import planner_tools
from tools.vlm_tools import verification_prompt_file, get_coordinates_prompt, vlm_tools, check_item_prompt
import pyautogui
import re
import io
import json
import time

def get_tool(model, user_query, system_context):

    if ("gemma" in model and "function" not in model) or ("ministral" in model):
        print("Usando modo JSON manual.")
        
        manual_prompt = f"""You are a function calling assistant. Analyze the user query and execution history to determine the NEXT function call.

System History:
{system_context}

User Goal: {user_query}

Available functions:
{json.dumps(planner_tools, indent=2)}

Respond ONLY with a valid JSON object matching one of the functions. Do not write explanations.
Format example:
{{
  "function_name": "open_application",
  "arguments": {{
    "app_name": ["notepad"]
  }}
}}
"""
        start_time = time.time()
        response = ollama.chat(model=model, messages=[{'role': 'user', 'content': manual_prompt}])
        end_time = time.time() - start_time
        
        answer = response['message']['content']
        # Nos aseguramos de que sea string antes de hacer strip
        if answer:
             answer = str(answer).strip()
        else:
             answer = ""
             
        print(f"LLM Manual JSON Answer: {answer}")

        try:
            # Usamos Regex para extraer el bloque JSON de forma segura, ignorando texto extra
            import re
            json_match = re.search(r'\{.*\}', answer, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                func_name = parsed.get('function_name')
                arguments = parsed.get('arguments', {})
                return func_name, arguments
            else:
                # Fallback por si no encuentra llaves, intentamos parsear directo si es un JSON limpio
                parsed = json.loads(answer)
                func_name = parsed.get('function_name')
                arguments = parsed.get('arguments', {})
                return func_name, arguments
            
        except Exception as e:
            print(f"Error parseando JSON de {model}: {e}")
            return None, None

    else:
        print(f"Checking planner with {model} (Native Tool Mode)")
        response = ollama.chat(
            model=model, 
            messages=[
                {'role': 'user', 'content': user_query}, 
                {'role': 'system', 'content': system_context}
            ], 
            tools=planner_tools
        )
        
        # Obtenemos content de forma segura
        answer = response['message'].get('content', '')
        if answer:
            answer = str(answer).strip()
            print(f"LLM Thinking: {answer}")

        if response['message'].get('tool_calls'):
            tool_call = response['message']['tool_calls'][0]
            func_name = tool_call['function']['name']
            arguments = tool_call['function']['arguments']
            return func_name, arguments
        else:
            print("No tool call detected.")
            return None, None

def take_screenshot():
    screenshot = pyautogui.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    return img_bytes

def verify(model, user_query):
    print(f"Checking VLM with {model}")
    time.sleep(2)
    img_bytes = take_screenshot()
    response = ollama.chat(model=model, messages=[{'role':'user', 'content': verification_prompt_file(user_query), 'images': [img_bytes]}])
    answer = response['message']['content'].strip()
    print(f"VLM answer: {answer}")
    return "YES" in answer.upper()

def check_item(model, item, type='item'):
    print(f"Item to check: {item}")
    img_bytes = take_screenshot()
    response = ollama.chat(model=model, messages=[{'role':'user', 'content': check_item_prompt(item, type), 'images': [img_bytes]}])
    answer = response['message']['content'].strip()
    print(f"VLM answer for item check: {answer}")
    return "YES" in answer.upper()

def parse_coordinates(coords):
    print("Answer: ", coords)
    screen_w, screen_h = pyautogui.size()
    if coords:
        real_x = int((coords[0] / 1000) * screen_w)
        real_y = int((coords[1] / 1000) * screen_h)
        return real_x, real_y
    print("No coordinates found.")
    return None

def get_coord(model, user_query):
    print(f"Getting coordinates with {model}")
    img_bytes = take_screenshot()
    
    response = ollama.chat(
        model=model, 
        messages=[{'role':'user', 'content': get_coordinates_prompt(user_query), 'images': [img_bytes]}], 
        tools=vlm_tools, 
        options={"temperature": 0.1}
    )
    
    print(f"DEBUG - Full response: {response.model_dump_json(indent=2)}")
    answer = response['message']['content'].strip()
    print(f"VLM answer for coordinates: {answer}")
    
    if response['message'].get('tool_calls'):
        tool_call = response['message']['tool_calls'][0]
        arguments = tool_call['function']['arguments']
        bad_coords = arguments.get('coordinate')
        if bad_coords:
            good_coords = parse_coordinates(bad_coords)
            return {
                "x": good_coords[0],
                "y": good_coords[1]
            }
    
    print("no tool used.")
    return None