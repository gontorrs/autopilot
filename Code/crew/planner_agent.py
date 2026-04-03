import os
import shutil
import subprocess
import json
from typing import Optional, Any
from crewai.agents.agent_builder.base_agent import BaseAgent

class PDDLPlannerAgent(BaseAgent):

    object_mapping: dict = {}

    function_calling_llm: Optional[BaseAgent] = None
    llm: Optional[BaseAgent] = None
    step_callback: Optional[Any] = None
    last_messages: list = []

    def __init__(self):
        super().__init__(
            tools=[],
            role="PDDL Task Planner",
            goal="Generate a PDDL problem from the state dict and execute Fast Downward to obtain a structured plan.",
            backstory="You are a deterministic logic planner. You receive structured intents and generate classical step-by-step PDDL plans without LLM reasoning.",
        )

    def sanitize(self, text):
        if not text:
            return text
        clean_text = text.lower().replace(' ', '_').replace('.', '_').replace('-', '_')
        self.object_mapping[clean_text] = text
        return clean_text

    def _objects(self, state_dict):
        parts = ["(:objects"]
        
        if 'app_name' in state_dict:
            app = self.sanitize(state_dict['app_name'])
            parts.append(f" {app} - app")
            
        if 'path' in state_dict and state_dict['path']:
            folders = [self.sanitize(f) for f in state_dict['path']]
            parts.append(f"{' '.join(folders)} - folder")
            
        if 'file_name' in state_dict and state_dict['file_name']:
            file_name = self.sanitize(state_dict['file_name'])
            parts.append(f"{file_name} - file")
            
        if 'content' in state_dict and state_dict['content']:
            text = self.sanitize(state_dict['content'])
            parts.append(f"{text} - text")
            
        if 'style' in state_dict and state_dict['style']:
            style = self.sanitize(state_dict['style'])
            parts.append(f"{style} - style")
            
        if 'folder_name' in state_dict and state_dict['folder_name']:
            folder_name = self.sanitize(state_dict['folder_name'])
            parts.append(f"{folder_name}_name - text")
            
        if 'file_name_new' in state_dict and state_dict['file_name_new']:
            file_name_new = self.sanitize(state_dict['file_name_new'])
            parts.append(f"{file_name_new}_name - text")

        if 'path_to_copy' in state_dict and 'path_to_paste' in state_dict:
            all_folders = list(dict.fromkeys(
                state_dict['path_to_copy'] + state_dict['path_to_paste']
            ))
            folders = [self.sanitize(f) for f in all_folders]
            parts.append(f"{' '.join(folders)} - folder")
            
        parts.append(")")
        return '\n'.join(parts)

    def _state(self, state_dict):
        predicates = ['(empty)']
        
        if 'path_to_copy' in state_dict and 'path_to_paste' in state_dict:
            default_safe = self.sanitize("Default")
            predicates.append(f'(current {default_safe})')

            seen = set()
            for path in [state_dict['path_to_copy'], state_dict['path_to_paste']]:
                sanitized_path = [self.sanitize(f) for f in path]
                for i in range(1, len(sanitized_path)):
                    predicate = f'(inside {sanitized_path[i]} {sanitized_path[i-1]})'
                    if predicate not in seen:
                        seen.add(predicate)
                        predicates.append(predicate)

            if 'file_name' in state_dict and state_dict['file_name']:
                file_name = self.sanitize(state_dict['file_name'])
                origin = self.sanitize(state_dict['path_to_copy'][-1])
                predicates.append(f'(file_to {file_name} {origin})')

        elif 'path' in state_dict and state_dict['path']:
            folders = [self.sanitize(f) for f in state_dict['path']]
            
            default_safe = self.sanitize("Default")
            predicates.append(f'(current {default_safe})')
            
            if len(folders) > 1:
                predicates.append(f'(inside {folders[1]} {default_safe})')
                for i in range(1, len(folders) - 1):
                    predicates.append(f'(inside {folders[i+1]} {folders[i]})')
                    
            if 'file_name' in state_dict and state_dict['file_name']:
                file_name = self.sanitize(state_dict['file_name'])
                predicates.append(f'(file_to {file_name} {folders[-1]})')
                
            if state_dict.get('folder_name') or state_dict.get('file_name_new'):
                last_folder = self.sanitize(state_dict['path'][-1])
                predicates.append(f'(can_create_files {last_folder})')
                
        return '\n'.join(predicates)

    def clear_results(self):
        results_dir = 'pddl/results'
        if os.path.exists(results_dir):
            shutil.rmtree(results_dir)
        os.makedirs(results_dir, exist_ok=True)

    def generate_problem(self, state_dict, output_filename):
        domain_name = "gui"
        problem_name = output_filename.replace('.pddl', '')
        
        objects_str = self._objects(state_dict)
        init_str = self._state(state_dict)
        goal_str = state_dict.get('goal', '(empty)')
        
        problem = f"""(define (problem {problem_name})
  (:domain {domain_name})
  {objects_str}
  (:init
    {init_str}
  )
  (:goal {goal_str})
)"""
        
        results_dir = 'pddl/results'
        os.makedirs(results_dir, exist_ok=True)
        output_path = os.path.join(results_dir, output_filename)
        print(problem)
        with open(output_path, 'w') as f:
            f.write(problem)
        return output_path

    def to_goal(self, state_dict, output_filename):
        self.object_mapping.clear()
        self.sanitize("Default")
        self.clear_results()
        problem_path = self.generate_problem(state_dict, output_filename)
        
        mapping_path = os.path.join('pddl/results', 'mapping.json')
        with open(mapping_path, 'w') as f:
            json.dump(self.object_mapping, f, indent=4)
            
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
            print(result.stdout)
            print(result.stderr)
            return None

    def execute_task(self, task, state_dict=None, output_filename="problem.pddl", **kwargs) -> str:
        if state_dict is None:
            state_dict = (task.config or {}).get("state_dict", {})

        return self.to_goal(state_dict, output_filename)

    # Requerimientos base de BaseAgent para agentes deterministas puros:
    def create_agent_executor(self, tools=None) -> None:
        pass

    def _execute_core_task(self, *args, **kwargs) -> str:
        return ""

    def get_delegation_tools(self, agents=None):
        return []

    def get_mcp_tools(self):
        return []

    def get_platform_tools(self):
        return []