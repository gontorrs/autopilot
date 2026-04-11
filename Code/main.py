from crewai import Crew, Process, Task
from crew.agents import create_agents
from tools.tools import create_manager_tools

model_dict = {
    'gemma4k': 'gemma3:4b-it-qat',
    'functiongemma': 'functiongemma:latest',
    'qwen2k-vl': 'qwen3-vl:2b-instruct-q4_K_M',
    'qwen4k-vl': 'qwen3-vl:4b-instruct-q4_K_M',
    'llama3k': 'llama3.2:3b-instruct-q4_K_M',
    'llama3': 'llama3.2:3b',
    'ministral3': 'ministral-3:3b',
    'ministral3k': 'ministral-3:3b-instruct-2512-q4_K_M',
    'qwen4k': 'qwen3:4b-instruct-2507-q4_K_M',
    'qwen4instruct': 'qwen3:4b-instruct',
    'qwen4-vl': 'qwen3-vl:4b',
    'qwen2-vl': 'qwen3-vl:2b-instruct',
    'e2b': 'gemma4:e2b',
    'e4b': 'gemma4:e4b',
    'e4bk': 'gemma4:e4b-it-q4_K_M ',
    'e2bk': 'gemma4:e2b-it-q4_K_M',
    'qwen3.52b': 'qwen3.5:2b',
    'qwen3.54b': 'qwen3.5:4b',
    'qwen3.52bk': 'qwen3.5:2b-q4_K_M',
    'qwen3.54bk': 'qwen3.5:4b-q4_K_M',
    'qwen8k': 'qwen3:8b-q4_K_M'
}

planner_model = model_dict['e4bk']
vlm_model = model_dict['qwen2k-vl']
intention_model = model_dict['e4bk']

#user_input = "Open the file Gonzalo_Anteproyecto.pdf which is in Documents, then TFG folder and then Docs folder."
#user_input = "Take a quick note saying that I have a meeting tommorrow at 3 pm in Tokyo please."
#user_input = "Open my Entrevista_Reli.odt in Desktop folder and make the text Gonzalo Torras Serrano in italic."
#user_input = 'Create a folder named "GTS" in the Documents folder.'
#user_input = 'Open my Entrevista_Reli.odt in Desktop and delete the text Gonzalo Torras Serrano.'
#user_input = 'Open my Entrevista_Reli.odt in Desktop and search for the text Gonzalo Torras Serrano.'
user_input = 'Copy my claude.docx in my Downloads folder and paste it in my Documents folder.'

# 1. Create all agents
agents = create_agents(planner_model, vlm_model, intention_model)

# 2. Create manager tools (orchestration + execution + verification)
config = {
    "user_input": user_input,
    "vlm_model": vlm_model,
    "planner_model": planner_model,
    "intention_model": intention_model,
}
manager_tools = create_manager_tools(agents, config)
agents["manager"].tools = manager_tools

# 3. Single task: the manager orchestrates everything
task = Task(
    description=f"Complete this GUI automation request: '{user_input}'",
    expected_output="Final result: YES (success) or NO (failure) from verification.",
    agent=agents["manager"],
)

# 4. Run
crew = Crew(
    agents=[agents["manager"]],
    tasks=[task],
    process=Process.sequential,
    verbose=True,
)

result = crew.kickoff()
print(f"\n{'='*50}")
print(f"FINAL RESULT: {result.raw}")
print(f"{'='*50}")