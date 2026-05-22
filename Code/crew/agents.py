from crewai import Agent, LLM
from tools.tools import create_tools
from crew.vlm_agents import ScoutAgent, VisionAgent, QAAgent
from crew.executor_agent import ExecutorAgent
from crew.pddl_translator import PDDLTranslatorAgent
from crew.planner_agent import PDDLPlannerAgent
import os


def create_agents(planner_model: str, vlm_model: str, intention_model: str) -> dict:

    # planner_llm = ManagerAgent(
    #     model=planner_model,
    #     think=False,
    # )

    intention_llm = LLM(
        model=f"ollama/{intention_model}",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )

    tools_dict = create_tools()

    intention_agent = Agent(
        role="Intention Agent",
        goal="Analyze the user's intention and determine which PDDL template to use and with what arguments.",
        backstory="You are a direct intent classifier, you just classify the end goal, you do not plan any steps in between. You translate natural language into structured intents.",
        tools=[tools_dict["navigate_tool"], tools_dict["write_tool"], tools_dict["change_tool"],
               tools_dict["create_tool"], tools_dict["delete_tool"], tools_dict["search_tool"],
               tools_dict["copy_paste_tool"]],
        llm=intention_llm,
        verbose=True,
        max_iter=1
    )

    manager_agent = Agent(
        role="Manager",
        goal="Complete the user's GUI automation task by calling tools in the correct sequence.",
        backstory=(
            "You are a GUI automation manager. You MUST call tools to complete tasks - never simulate or imagine tool results.\n\n"
            "MANDATORY WORKFLOW — call tools in this exact order:\n"
            "1. classify_intent(user_query) — always call this first.\n"
            "1.5. detect_current_state(intent_name) — call with the intent name from step 1 (e.g., 'navigate_tool').\n"
            "2. generate_plan() — call after classify_intent succeeds.\n"
            "3. translate_plan() — call after generate_plan succeeds. It returns the execution steps.\n"
            "4. Execute each step from translate_plan IN ORDER using check_visibility, find_coordinates, and execute_action. Unless check_visibility returns NO, do NOT call find_coordinates, but still call execute_action with scout_result='NO' and coordinates=''.\n"
            "5. verify_result() — call ONCE after ALL execution steps are done. Never call it mid-workflow.\n\n"
            "RULES:\n"
            "- You MUST actually call each tool. Do NOT write fake Observations or invent results.\n"
            "- If check_visibility returns NO, do NOT call find_coordinates, but still call execute_action with scout_result='NO' and coordinates=''.\n"
            "- After verify_result returns, respond with Final Answer."
        ),
        llm=intention_llm,
        tools=[],
        allow_delegation=False,
        verbose=True,
    )

    scout_agent = ScoutAgent(vlm_model_name=vlm_model)
    vision_agent = VisionAgent(vlm_model_name=vlm_model)
    qa_agent = QAAgent(vlm_model_name=vlm_model)
    executor_agent = ExecutorAgent()
    translator_agent = PDDLTranslatorAgent()
    planner_agent = PDDLPlannerAgent()

    return {
        "intention": intention_agent,
        "manager": manager_agent,
        "scout": scout_agent,
        "vision": vision_agent,
        "qa": qa_agent,
        "executor": executor_agent,
        "translator": translator_agent,
        "planner": planner_agent,
    }
