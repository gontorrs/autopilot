from utils.actions import open_app, navigate_path, find_content, format, type, final_verify


# Mapping directo de acciones PDDL a funciones Python
# p = parámetros del plan PDDL
# s = state que viene de main.py (contiene vlm_model, planner_model, etc.)
ACTION_MAP = {
    'open': lambda p, s: open_app(s['app_name'], s['vlm_model']),
    'navigate': lambda p, s: s['path_tracking'].append(p[2]),
    'open_file': lambda p, s: navigate_path(s['path_tracking'], s['vlm_model'], s['file_name']),
    'type': lambda p, s: type(s['app_name'], s.get('content', ''), s['vlm_model']),
    'search_text': lambda p, s: find_content(s.get('content', ''), s['vlm_model']),
    'change_text': lambda p, s: format(s.get('style', ''))
}


def parse_plan(plan_text, state):
    for attempt in range(3):
        state['attempts'] = attempt
        #Estado inicial de donde se encuentra
        state['path_tracking'] = ['Default']
        
        for line in plan_text.strip().split('\n'):
            # Ignora comentarios y líneas vacías
            if not line.startswith('(') or line.startswith(';'):
                continue
                
            # Extraemos acción y parámetros del plan PDDL
            action_parts = line.strip('()').split()
            action_name = action_parts[0]
            params = action_parts[1:]
            
            # Usamos el mapping de las funciones anónimas.
            if action_name in ACTION_MAP:
                print(f"\nEjecutando: {action_name} {params}")
                ACTION_MAP[action_name](params, state)
            else:
                print(f"Absolutely no cluee (revisa esto): {action_name}")
        
        #Maximum of 3 attempts if failed
        if state.get('goal') == '(changed_text)':
            verify_result = final_verify(state['attempts'], state['vlm_model'], state['prompt'], 
                                         goal=state['goal'], content=state.get('content'), style=state.get('style'))
        else:
            verify_result = final_verify(state['attempts'], state['vlm_model'], state['prompt'])
        
        state.update(verify_result)
        
        if state['status'] == 'verified':
            break
    
    return state
