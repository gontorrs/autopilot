import json
import os
from utils.actions import open_app, navigate_path, find_content, format_text, type_text

# Direct Action Mapping
ACTIONS = {
    'open': open_app,
    'navigate': navigate_path,
    'open_file': navigate_path,
    'type': type_text,
    'search_text': find_content,
    'change_text': format_text
}

def load_name_mapping():
    try:
        with open('pddl/results/mapping.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def parse_plan(plan_text, state):
    name_map = load_name_mapping()
    
    state['path_tracking'] = ['Default']
    
    state['status'] = 'verified' 
    
    for line in plan_text.strip().split('\n'):
        if not line.startswith('(') or line.startswith(';'):
            continue
            
        # Parse PDDL line
        parts = line.replace('(', '').replace(')', '').split()
        action_name = parts[0]
        pddl_params = parts[1:]
        
        # Retrieve original names
        real_params = [name_map.get(p, p) for p in pddl_params]
        
        print(f"\nEjecutando: {action_name} con {real_params}")
        
        # Guardamos el resultado de la acción ejecutada por la Crew
        result = {}
        
        # Execute mapped action
        if action_name == 'open':
            result = ACTIONS['open'](state['app_name'], state['planner_model'], state['vlm_model'])
            
        elif action_name == 'navigate':
            target = real_params[-1]
            state['path_tracking'].append(target)
            result = {"status": "success"} # Navigate solo añade al tracker, no ejecuta
            
        elif action_name == 'open_file':
            target_file = real_params[-1]
            result = ACTIONS['open_file'](state['path_tracking'], state['planner_model'], state['vlm_model'], target_file)
            
        elif action_name == 'type':
            result = ACTIONS['type'](state['app_name'], state.get('content', ''), state['planner_model'], state['vlm_model'])
            
        elif action_name == 'search_text':
            result = ACTIONS['search_text'](state.get('content', ''), state['planner_model'], state['vlm_model'])
            
        elif action_name == 'change_text':
            result = ACTIONS['change_text'](state.get('style', ''))
            
        else:
            print(f"Action not recognized: {action_name}")
            result = {"status": "failed"}

        if "failed" in result.get("status", "").lower() or "NO" in result.get("status", ""):
            print(f"La acción '{action_name}' falló o fue rechazada por el Agente QA.")
            state['status'] = 'failed'
            break

    return state