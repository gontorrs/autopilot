import json
import re
from crewai import Crew, Process, Task
from crew.agents import create_agents
from crew.tasks import create_intent_task

def get_intent(user_query: str, planner_model: str, vlm_model: str) -> tuple[str, dict]:
    agents = create_agents(planner_model, vlm_model)
    task = create_intent_task(user_query, agents["intention"])
    crew = Crew(agents=[agents["intention"]], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    try:
        match = re.search(r'\{.*\}', result.raw, re.DOTALL)
        data = json.loads(match.group(0).replace("'", '"'))
        return data.get("intent"), data.get("args", {})
    except Exception as e:
        print(f"Failed to parse Intent: {e}")
        return None, {}