from crewai import Agent, LLM
from utils.tools import create_tools
from crew.vlm_agents import ScoutAgent, VisionAgent, QAAgent
from crew.executor_agent import ExecutorAgent
from crew.pddl_translator import PDDLTranslatorAgent
from crew.planner_agent import PDDLPlannerAgent
from crew.manager_agent import ManagerAgent

def create_agents(planner_model: str, vlm_model: str, intention_model: str) -> dict:
    
    planner_llm = ManagerAgent(
        model=planner_model,
        think=True,
    )

    intention_llm = LLM(
        model=f"ollama/{intention_model}",
        base_url="http://localhost:11434"
    )

    tools_dict = create_tools()

    intention_agent = Agent(
        role="GUI Task Planner",
        goal="Analyze the user's intention and determine which PDDL template to use and with what arguments.",
        backstory="You are a direct intent classifier, you just classify the end goal, you do not plan any steps in between. You translate natural language into structured intents.",
        tools=[tools_dict["navigate_tool"], tools_dict["write_tool"], tools_dict["change_tool"], tools_dict["create_tool"], tools_dict["delete_tool"], tools_dict["search_tool"], tools_dict["copy_paste_tool"]],
        llm=intention_llm,
        verbose=True,
        max_iter=1
    )

    manager_agent = Agent(
            role="Manager",
            goal="Coordinate all agents to complete the user's GUI automation task using the available tools.",
            backstory=(
                "You are a GUI automation manager. You complete tasks by calling tools in sequence.\n\n"
                "TOOLS:\n"
                "1. check_visibility(target, item_type) — Takes a screenshot and checks if a UI element is visible.\n"
                "   Returns YES or NO.\n"
                "   item_type: 'application', 'folder', 'file', 'button', 'menu_option', 'text_content'\n\n"
                "2. find_coordinates(target) — Takes a screenshot and returns the exact {x, y} pixel coordinates of the element.\n"
                "   Only use AFTER check_visibility returns YES.\n\n"
                "3. execute_action(intent, target, scout_result, coordinates) — Performs the actual GUI interaction.\n"
                "   VISUAL INTENTS (require scout_result and coordinates):\n"
                "     - open: Open an application icon to launch it.\n"
                "     - navigate: Double-click on a folder to enter it.\n"
                "     - open_file: Double-click on a file to open it.\n"
                "     - click_new: Single-click on a button in order to open a menu to create a file/folder.\n"
                "     - select_type: Single-click on the menu option such as a file or folder.\n"
                "     - copy: Single-click on a file to select it, then Ctrl+C or Ctrl+X, this one works for cut too.\n"
                "   KEYBOARD INTENTS (no coordinates needed, pass scout_result='' and coordinates=''):\n"
                "     - paste: Presses Ctrl+V.\n"
                "     - navigate_back: Presses Alt+Left to go back one folder.\n"
                "     - type: Types text content into the active application.\n"
                "     - type_name: Types a name and presses Enter to confirm (e.g., naming a new file/folder).\n"
                "     - search_text: Opens Ctrl+F and types the search query.\n"
                "     - change_text: Applies formatting to selected text. The target MUST be the style name ('bold', 'italic', or 'underline'), NOT the text content.\n"
                "     - delete_text: Presses Backspace to delete selected text.\n\n"
                "WORKFLOW:\n"
                "  Visual steps: check_visibility -> find_coordinates (if YES) -> execute_action\n"
                "  Keyboard steps: execute_action directly\n\n"
                "CRITICAL RULES:\n"
                "- If check_visibility returns NO, you MUST still call execute_action with the same intent and target. "
                "Pass scout_result='NO' and coordinates=''. The executor has a fallback that searches for the item.\n"
                "- Each task requires exactly ONE sequence of tool calls. Do NOT repeat tools unnecessarily.\n"
                "- After execute_action returns SUCCESS, respond with Final Answer: SUCCESS."
            ),
            llm=planner_llm,
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
        "planner": planner_agent
    }