import os
import shutil
import subprocess

def objects(state_dict):

    parts = ["(:objects"]
    
    # App
    if 'app_name' in state_dict:
        app = state_dict['app_name'].replace(' ', '_')
        parts.append(f"    {app} - app")
    
    # Folders
    if 'path' in state_dict and state_dict['path']:
        folders = [f.replace(' ', '_') for f in state_dict['path']]
        parts.append(f"{' '.join(folders)} - folder")
    
    # File
    if 'file_name' in state_dict and state_dict['file_name']:
        file_name = state_dict['file_name'].replace('.', '_').replace(' ', '_')
        parts.append(f"{file_name} - file")
    
    # Text
    if 'content' in state_dict and state_dict['content']:
        text = state_dict['content'].replace(' ', '_')
        parts.append(f"{text} - text")
    
    # Style
    if 'style' in state_dict and state_dict['style']:
        style = state_dict['style']
        parts.append(f"{style} - style")
    
    parts.append(")")
    return '\n'.join(parts)


def state(state_dict):

    goal = state_dict.get('goal', '')
    predicates = ['(empty)']
    
    # Para goals que necesitan path (navigate, change)
    if 'path' in state_dict and state_dict['path']:
        folders = [f.replace(' ', '_') for f in state_dict['path']]
        
        #Default ese el estado inicial de file explorer
        predicates.append('(current Default)')
        
        #Relacionamos carpetas
        if len(folders) > 1:
            predicates.append(f'(inside {folders[1]} Default)')
            for i in range(1, len(folders) - 1):
                predicates.append(f'(inside {folders[i+1]} {folders[i]})')
        
        # Archivo dentro de la útlima carpeta siempre.
        if 'file_name' in state_dict and state_dict['file_name']:
            file_name = state_dict['file_name'].replace('.', '_').replace(' ', '_')
            predicates.append(f'(file_to {file_name} {folders[-1]})')
    
    return '\n'.join(predicates)


def clear_results():
    results_dir = 'pddl/results'
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    os.makedirs(results_dir, exist_ok=True)


def generate_problem(template_path, state_dict, output_filename):

    # Leer template
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Generar problema
    objects_str = objects(state_dict)
    state_str = state(state_dict)
    
    problem = template.replace('{OBJECTS}', objects_str)
    problem = problem.replace('{INIT_PREDICATES}', state_str)
    
    # Guardar en results
    results_dir = 'pddl/results'
    os.makedirs(results_dir, exist_ok=True)
    
    output_path = os.path.join(results_dir, output_filename)
    with open(output_path, 'w') as f:
        f.write(problem)
    
    return output_path

def to_goal(template_path, state_dict, output_filename):
    clear_results()
    #We generate PDDL problem
    problem_path = generate_problem(template_path, state_dict, output_filename)
    
    domain_path = 'pddl/gui_domain.pddl'
    results_dir = 'pddl/results'
    plan_filename = output_filename.replace('.pddl', '_plan.txt')
    plan_path = os.path.join(results_dir, plan_filename)

    fd = "C:\\Users\\gonza\\fastdownward\\fast-downward.py"
    
    cmd = ['python', fd, domain_path, problem_path, '--search', 'astar(lmcut())']
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Plan executed")
        shutil.move('sas_plan', plan_path)
        with open(plan_path, 'r') as f:
            plan_content = f.read()
        print(result.stdout)
        return plan_content
    else:
        print("How about you take a rest.")
        print(result.stderr)
        return None