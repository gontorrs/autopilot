from crewai import Agent, LLM
from utils.tools import create_tools
from crew.vlm_agents import ScoutAgent, VisionAgent, QAAgent
from crew.executor_agent import ExecutorAgent
from crew.pddl_translator import PDDLTranslatorAgent
from crew.planner_agent import PDDLPlannerAgent

def create_agents(planner_model: str, vlm_model: str) -> dict:
    """Creates agents dynamically using the provided model strings."""
    
    # 1. Configurar los modelos apuntando explícitamente a Ollama local
    planner_llm = LLM(
        model=f"ollama/{planner_model}",
        base_url="http://localhost:11434"
    )
    
    vlm_llm = LLM(
        model=f"ollama/{vlm_model}",
        base_url="http://localhost:11434"
    )

    # 2. Inyectamos los modelos en las tools
    tools_dict = create_tools()

    # 3. Crear los agentes usando los objetos LLM en lugar de strings
    intention_agent  = Agent(
        role="GUI Task Planner",
        goal="Analyze the user's intention and determine which PDDL template to use and with what arguments.",
        backstory="You are a direct intent classifier, you just classify the end goal, you do not plan any steps in between. You translate natural language into structured intents.",
        tools=[tools_dict["navigate_tool"], tools_dict["write_tool"], tools_dict["change_tool"], tools_dict["create_tool"], tools_dict["delete_tool"], tools_dict["search_tool"], tools_dict["copy_paste_tool"]],
        llm=planner_llm,
        verbose=True,
        max_iter=1
    )

    #Importamos todos los agentes de visión custom pero metidos en el loop de crewai.
    scout_agent = ScoutAgent(vlm_model_name=vlm_model)
    vision_agent = VisionAgent(vlm_model_name=vlm_model)
    qa_agent = QAAgent(vlm_model_name=vlm_model)

    #Importamos el agente execturo de código puro, sin LLM.
    executor_agent = ExecutorAgent()

    #Creamos el agente traductor de PDDL a python.
    translator_agent = PDDLTranslatorAgent()

    #agente PDDL planificacor
    planner_agent = PDDLPlannerAgent()

    return {
        "intention": intention_agent,
        "scout": scout_agent,
        "vision": vision_agent,
        "qa": qa_agent, 
        "executor": executor_agent,
        "translator": translator_agent, 
        "planner": planner_agent
    }