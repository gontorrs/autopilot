import ollama
from tools.planner_tools import planner_tools
from tools.vlm_tools import verification_prompt_file, get_coordinates_prompt, vlm_tools, check_item_prompt, verification_prompt_formatting
import pyautogui
import io
import time
import json

def get_tool(model, user_query):
    if "gemma" in model and "function" not in model:
        gemma_prompt = f"""You are a function calling assistant. Analyze the user query and determine which function to call with the appropriate parameters.

Available functions:
{json.dumps(planner_tools, indent=2)}

User query: {user_query}

Respond ONLY with a JSON object in this exact format:
{{
  "function_name": "navigate_tool" or "write_tool" or "change_tool",
  "arguments": {{
    "param1": "value1",
    "param2": "value2"
  }}
}}

Do not include any explanation, only the JSON object."""
        start_time = time.time()

        response = ollama.chat(model=model, messages=[{'role': 'user', 'content': gemma_prompt}])

        end_time = time.time() - start_time
        
        answer = response['message']['content'].strip()
        print(f"LLM answer: {answer}")
        
        if '```json' in answer:
            answer = answer.split('```json')[1].split('```')[0].strip()
        elif '```' in answer:
            answer = answer.split('```')[1].split('```')[0].strip()

        parsed = json.loads(answer)
        func_name = parsed.get('function_name')
        arguments = parsed.get('arguments', {})
        return func_name, arguments, end_time
    
    else:
        print(f"Checking planner with {model}")
        start_time = time.time()

        response = ollama.chat(model=model, messages=[{'role': 'user', 'content': user_query}], tools=planner_tools)

        end_time = time.time() - start_time
        answer = response['message']['content'].strip()

        print(f"LLM answer for item check: {answer}")
        if response['message'].get('tool_calls'):
            tool_call = response['message']['tool_calls'][0]
            func_name = tool_call['function']['name']
            arguments = tool_call['function']['arguments']
            return func_name, arguments, end_time
        else:
            print("no tool")
            return None, None, end_time

def take_screenshot():
    screenshot = pyautogui.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    return img_bytes

def verify_formatting(model, text, style):
    print(f"Verifying: '{text}' should be {style}")
    img_bytes = take_screenshot()
    response = ollama.chat(model=model, messages=[{'role':'user', 'content': verification_prompt_formatting(text, style), 'images': [img_bytes]}])
    answer = response['message']['content'].strip()
    print(f"VLM answer: {answer}")
    return "YES" in answer.upper()

def verify(model, user_query):
    print(f"Checking VLM with {model}")
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

    response = ollama.chat(model=model, messages=[{'role':'user', 'content': get_coordinates_prompt(user_query), 'images': [img_bytes]}], tools=vlm_tools, options={"temperature": 0.1})
    
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