from crewai import Task

def create_intent_task(user_query: str, agent) -> Task:
    return Task(
        description=f"Analyze this query using the available intention tools: '{user_query}'",
        expected_output="A valid JSON string with 'intent' and 'args' keys.",
        agent=agent
    )