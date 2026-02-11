import json
import os
from utils.actions import open_app, navigate_path, find_content, format, type_text, final_verify

# Direct Action Mapping
ACTIONS = {
    'open': open_app,
    'navigate': navigate_path,
    'open_file': navigate_path,
    'type': type_text,
    'search_text': find_content,
    'change_text': format
}

def load_name_mapping():
    try:
        with open('pddl/results/mapping.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def parse_plan(plan_text, state):
    name_map = load_name_mapping()
    
    for attempt in range(3):
        state['attempts'] = attempt
        state['path_tracking'] = ['Default']
        
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
            
            # Execute mapped action
            if action_name == 'open':
                ACTIONS['open'](state['app_name'], state['vlm_model'])
                
            elif action_name == 'navigate':
                target = real_params[-1]
                state['path_tracking'].append(target)
                
            elif action_name == 'open_file':
                target_file = real_params[-1]
                ACTIONS['open_file'](state['path_tracking'], state['vlm_model'], target_file)
                
            elif action_name == 'type':
                ACTIONS['type'](state['app_name'], state.get('content', ''), state['vlm_model'])
                
            elif action_name == 'search_text':
                ACTIONS['search_text'](state.get('content', ''), state['vlm_model'])
                
            elif action_name == 'change_text':
                ACTIONS['change_text'](state.get('style', ''))
                
            else:
                print(f"Action not recognized: {action_name}")
        
        # Final Verification
        if state.get('goal') == '(changed_text)':
            verify_result = final_verify(state['attempts'], state['vlm_model'], state['prompt'], 
                                         goal=state['goal'], content=state.get('content'), style=state.get('style'))
        else:
            verify_result = final_verify(state['attempts'], state['vlm_model'], state['prompt'])
        
        state.update(verify_result)
        
        if state['status'] == 'verified':
            break
    
    return state