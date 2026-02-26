# utils/agents.py

from crewai import Agent, LLM
from crew.tools import create_tools

def create_agents(planner_model: str, vlm_model: str) -> dict:
    """Creates agents dynamically using the provided model strings."""
    
    # 1. Configurar los modelos apuntando explícitamente a Ollama local
    # Asegúrate de que el puerto 11434 es donde corre tu Ollama (es el por defecto)
    planner_llm = LLM(
        model=f"ollama/{planner_model}",
        base_url="http://localhost:11434"
    )
    
    vlm_llm = LLM(
        model=f"ollama/{vlm_model}",
        base_url="http://localhost:11434"
    )

    # 2. Inyectamos los modelos en las tools
    tools_dict = create_tools(planner_model, vlm_model)

    # 3. Crear los agentes usando los objetos LLM en lugar de strings
    intention_agent  = Agent(
        role="GUI Task Planner",
        goal="Analyze the user's intention and determine which PDDL template to use and with what arguments.",
        backstory="You are an expert planner for Windows GUI automation. You translate natural language into structured intents.",
        tools=[tools_dict["intention_tool"]],
        llm=planner_llm,
        verbose=True,
        max_iter=3
    )

    scout_agent = Agent(
        role="Screen Scout",
        goal="Verify that the required elements are visible on screen before any action is taken.",
        backstory="You are a vision agent specialized in confirming the presence of elements. You always check first.",
        tools=[tools_dict["scout_tool"]],
        llm=vlm_llm,
        verbose=True,
        max_iter=3
    )

    vision_agent = Agent(
        role="Vision Coordinate Finder",
        goal="Obtain the exact pixel coordinates of a visible element on screen.",
        backstory="You are a computer vision model expert at locating elements in GUIs and returning coordinates.",
        tools=[tools_dict["vision_tool"]],
        llm=vlm_llm,
        verbose=True,
        max_iter=3
    )

    qa_agent = Agent(
        role="QA Verifier",
        goal="Verify that the executed action has fulfilled the user's original objective.",
        backstory="You are a strict QA agent. You take screenshots to confirm that the screen state reflects the requested goal.",
        tools=[tools_dict["qa_tool"]],
        llm=vlm_llm,
        verbose=True,
        max_iter=3
    )

    executor_agent = Agent(
        role="GUI Action Executor",
        goal="Execute GUI actions using the available tools based on the context.",
        backstory="You decide: if coordinates exist, click; otherwise, search.",
        tools=[tools_dict["click_tool"], tools_dict["search_tool"]],
        llm=planner_llm,
        verbose=True,
        max_iter=1
    )

    return {
        "intention": intention_agent,
        "scout": scout_agent,
        "vision": vision_agent,
        "qa": qa_agent,
        "executor": executor_agent
    }