import json
from crewai import Crew, Process, Task
from crew.agents import create_agents
from crew.tasks import create_gui_tasks, create_qa_task

def get_intent(user_query: str, planner_model: str, vlm_model: str) -> tuple[str, dict]:
    agents = create_agents(planner_model, vlm_model)
    task = Task(
        description=f"Analyze this query using intention_tool: '{user_query}'",
        expected_output="A valid JSON string with 'intent' and 'args' keys.",
        agent=agents["intention"]
    )
    crew = Crew(agents=[agents["intention"]], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    try:
        clean_json = result.raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        return data.get("intent"), data.get("args", {})
    except Exception as e:
        print(f"Failed to parse Intent: {e}")
        return None, {}

def execute_gui_task(target_item: str, item_type: str, action_intent: str, planner_model: str, vlm_model: str) -> str:
    agents = create_agents(planner_model, vlm_model)
    tasks_list = create_gui_tasks(target_item, item_type, action_intent, agents)
    crew = Crew(
        agents=[agents["scout"], agents["vision"], agents["executor"]],
        tasks=tasks_list,
        process=Process.sequential,
        verbose=True
    )
    return str(crew.kickoff())

def verify(goal: str, planner_model: str, vlm_model: str) -> bool:
    agents = create_agents(planner_model, vlm_model)
    qa_task = create_qa_task(goal, agents)
    crew = Crew(agents=[agents["qa"]], tasks=[qa_task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    return "YES" in str(result).upper()
