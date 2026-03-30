from crewai import Task

def create_intent_task(user_query: str, agent) -> Task:
    return Task(
        description=f"Analyze this query using the available intention tools: '{user_query}'",
        expected_output="A valid JSON string with 'intent' and 'args' keys.",
        agent=agent
    )

def create_scout_task(target_item: str, item_type: str, agent) -> Task:
    return Task(
        description=f"Check if '{target_item}' (type: {item_type}) is visible on screen. Reply ONLY YES or NO.",
        expected_output="YES or NO",
        agent=agent
    )

def create_vision_task(target_item: str, agent, scout_task: Task) -> Task:
    return Task(
        description=f"Find exact coordinates for '{target_item}' (type: vision).",
        expected_output="JSON string with 'x' and 'y' integer coordinates, or null if not found.",
        agent=agent,
        context=[scout_task]
    )

def create_executor_task(target_item: str, item_type: str, action_intent: str, agent, context_tasks: list[Task]) -> Task:
    return Task(
        description=f"Execute action '{action_intent}' on '{target_item}' (type: {item_type}).",
        expected_output="Confirmation string of the action executed.",
        agent=agent,
        context=context_tasks
    )

def create_qa_task(goal: str, agent, qa_type: str = "default", style: str = "") -> Task:
    return Task(
        description=f"Verify if this goal has been achieved: '{goal}'",
        expected_output="YES or NO",
        agent=agent,
        config={"qa_type": qa_type, "style": style}
    )

# En tasks.py
def create_planner_task(state_dict: dict, agent, output_filename: str = "navigate_problem.pddl") -> Task:
    return Task(
        description=f"Generate a PDDL plan based on the provided state dictionary and save it to {output_filename}.",
        expected_output="A string representing the generated plan steps, or None if planning failed.",
        agent=agent,
        config={
            "state_dict": state_dict,
            "output_filename": output_filename
        }
    )
