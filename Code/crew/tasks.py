# utils/tasks.py
from crewai import Task

def create_gui_tasks(target_item: str, item_type: str, action_intent: str, agents_dict: dict) -> list[Task]:
    
    # 1. Scout Agent: Checks if the target is visible on the screen.
    task_scout = Task(
        description=f"Use scout_tool to check if '{target_item}' (type: {item_type}) is visible. Reply ONLY YES or NO.",
        expected_output="YES or NO",
        agent=agents_dict["scout"]
    )

    # 2. Vision Agent: Finds the pixel coordinates if Scout said YES.
    task_vision = Task(
        description=f"If Scout says YES, use vision_tool to find exact coordinates for '{target_item}'. If NO, return exactly: {{\"x\": null, \"y\": null}}",
        expected_output="JSON string with 'x' and 'y' integer coordinates.",
        agent=agents_dict["vision"],
        context=[task_scout]
    )

    # 3. Executor Agent: Decides which action tool to use based on the Vision coordinates.
    task_execute = Task(
        description=f"""
        Target: '{target_item}'
        Type: '{item_type}'
        Intent: '{action_intent}'
        
        Analyze the coordinates from the Vision agent:
        - If coordinates are VALID numbers: Use click_tool on those coordinates.
        - If coordinates are NULL or Vision says NO/Not visible: Use fallback_search_tool with Target and Type.
        
        CRITICAL INSTRUCTION: Once you have used a tool and received a SUCCESS message, DO NOT use it again. IMMEDIATELY output the result as your Final Answer and stop.
        """,
        expected_output="Confirmation string of the action executed and tool used.",
        agent=agents_dict["executor"],
        context=[task_vision]
    )

    return [task_scout, task_vision, task_execute]

# Mantengo también la de QA aparte por si la necesitas suelta
def create_qa_task(goal: str, agents_dict: dict) -> Task:
    return Task(
        description=f"Use qa_tool to verify if this goal is achieved on screen: '{goal}'",
        expected_output="YES or NO",
        agent=agents_dict["qa"]
    )