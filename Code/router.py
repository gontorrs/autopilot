import ollama
from tools.planner_tools import planner_tools
from tools.vlm_tools import verification_prompt_file, get_coordinates_prompt, vlm_tools, check_item_prompt, applications
import pyautogui
import re
import io
import json
import time

def get_tool(model, user_query, system_context):
    print(f"Checking planner with {model}")
    
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': user_query}, {'role': 'system', 'content': system_context}], tools=planner_tools)
    answer = response['message']['content'].strip()
    print(f"LLM Thinking: {answer}")
    if response['message'].get('tool_calls'):
        tool_call = response['message']['tool_calls'][0]
        func_name = tool_call['function']['name']
        arguments = tool_call['function']['arguments']
        return func_name, arguments
    else:
        print("no tool")

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
                "y": good_coords[1],
            }
    print("no tool used.")
    return None