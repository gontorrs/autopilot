from crew.pipeline import PipelineFlow
import langchain
langchain.debug = True

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

#user_input = "Open the file Gonzalo_Anteproyecto.pdf which is in Documents, then TFG folder and then Docs folder."
#user_input = "Take a quick note saying that I have a meeting tommorrow at 3 pm in Tokyo please."
user_input = "Open my Entrevista_Reli.odt in Gonzalo - UFV and make the text Gonzalo Torras Serrano in italic."
#user_input = 'Create a folder named "GTS" in the Documents folder.'
#user_input = 'Open my Entrevista_Reli.odt in Gonzalo - UFV and delete the text Gonzalo Torras Serrano.'
#user_input = 'Open my Entrevista_Reli.odt in Gonzalo - UFV and search for the text Gonzalo Torras Serrano.'
#user_input = 'Copy my claude.docx in my Downloads folder and paste it in my Documents folder.'

flow = PipelineFlow(user_input, planner_model, vlm_model, intention_model=model_dict['qwen4k'])
flow.kickoff()