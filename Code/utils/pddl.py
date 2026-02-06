import os
import shutil
import subprocess
import json

# Global mapping for PDDL sanitization
OBJECT_MAPPING = {}

def sanitize(text):
    if not text:
        return text
    
    clean_text = text.lower().replace(' ', '_').replace('.', '_').replace('-', '_')
    OBJECT_MAPPING[clean_text] = text
    return clean_text

def objects(state_dict):
    parts = ["(:objects"]
    
    # App
    if 'app_name' in state_dict:
        app = sanitize(state_dict['app_name'])
        parts.append(f"    {app} - app")
    
    # Folders
    if 'path' in state_dict and state_dict['path']:
        folders = [sanitize(f) for f in state_dict['path']]
        parts.append(f"{' '.join(folders)} - folder")
    
    # File
    if 'file_name' in state_dict and state_dict['file_name']:
        file_name = sanitize(state_dict['file_name'])
        parts.append(f"{file_name} - file")
    
    # Text
    if 'content' in state_dict and state_dict['content']:
        text = sanitize(state_dict['content'])
        parts.append(f"{text} - text")
    
    # Style
    if 'style' in state_dict and state_dict['style']:
        style = sanitize(state_dict['style'])
        parts.append(f"{style} - style")
    
    parts.append(")")
    return '\n'.join(parts)

def state(state_dict):
    goal = state_dict.get('goal', '')
    predicates = ['(empty)']
    
    # Handle paths and hierarchy
    if 'path' in state_dict and state_dict['path']:
        folders = [sanitize(f) for f in state_dict['path']]
        
        # Ensure Default is mapped
        default_safe = sanitize("Default")
        predicates.append(f'(current {default_safe})')
        
        if len(folders) > 1:
            predicates.append(f'(inside {folders[1]} {default_safe})')
            for i in range(1, len(folders) - 1):
                predicates.append(f'(inside {folders[i+1]} {folders[i]})')
        
        if 'file_name' in state_dict and state_dict['file_name']:
            file_name = sanitize(state_dict['file_name'])
            predicates.append(f'(file_to {file_name} {folders[-1]})')
    
    return '\n'.join(predicates)

def clear_results():
    results_dir = 'pddl/results'
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    os.makedirs(results_dir, exist_ok=True)

def generate_problem(template_path, state_dict, output_filename):
    with open(template_path, 'r') as f:
        template = f.read()
    
    objects_str = objects(state_dict)
    state_str = state(state_dict)
    
    problem = template.replace('{OBJECTS}', objects_str)
    problem = problem.replace('{INIT_PREDICATES}', state_str)
    
    results_dir = 'pddl/results'
    os.makedirs(results_dir, exist_ok=True)
    
    output_path = os.path.join(results_dir, output_filename)
    with open(output_path, 'w') as f:
        f.write(problem)
    
    return output_path

def to_goal(template_path, state_dict, output_filename):
    OBJECT_MAPPING.clear()
    sanitize("Default")
    
    clear_results()
    
    problem_path = generate_problem(template_path, state_dict, output_filename)
    
    # Save mapping to JSON
    mapping_path = os.path.join('pddl/results', 'mapping.json')
    with open(mapping_path, 'w') as f:
        json.dump(OBJECT_MAPPING, f, indent=4)
    
    domain_path = 'pddl/gui_domain.pddl'
    results_dir = 'pddl/results'
    plan_filename = output_filename.replace('.pddl', '_plan.txt')
    plan_path = os.path.join(results_dir, plan_filename)

    fd = "C:\\Users\\gonza\\fastdownward\\fast-downward.py"
    
    cmd = ['python', fd, domain_path, problem_path, '--search', 'astar(lmcut())']
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Plan executed")
        if os.path.exists('sas_plan'):
            shutil.move('sas_plan', plan_path)
            with open(plan_path, 'r') as f:
                plan_content = f.read()
                print(plan_content)
            return plan_content
    else:
        print("Planner failed.")
        print(result.stderr)
        return None