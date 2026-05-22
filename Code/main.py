import gradio as gr
from crewai import Crew, Process, Task
from crew.agents import create_agents
from tools.tools import create_manager_tools, start_timing
from voice.whisper import listen
import os
import glob

model_dict = {
    'e4bk': 'gemma4:e4b-it-q4_K_M',
    'qwen2k-vl': 'qwen3-vl:2b-instruct-q4_K_M',
}

planner_model = model_dict['e4bk']
vlm_model = model_dict['qwen2k-vl']
intention_model = model_dict['e4bk']


def run_pipeline(user_input: str):
    agents = create_agents(planner_model, vlm_model, intention_model)
    config = {
        "user_input": user_input,
        "vlm_model": vlm_model,
        "planner_model": planner_model,
        "intention_model": intention_model,
    }
    manager_tools = create_manager_tools(agents, config)
    agents["manager"].tools = manager_tools

    task = Task(
        description=f"Complete this GUI automation request: '{user_input}'",
        expected_output="Final result: YES (success) or NO (failure) from verification.",
        agent=agents["manager"],
    )

    crew = Crew(
        agents=[agents["manager"]],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    start_timing()
    result = crew.kickoff()

    plan_files = glob.glob("pddl/results/*_plan.txt")
    pddl_plan = ""
    if plan_files:
        latest = max(plan_files, key=os.path.getmtime)
        with open(latest, "r") as f:
            pddl_plan = f.read()

    return result.raw, pddl_plan


def loop():
    while True:
        yield "Listening...", "", "", ""

        transcription = listen()
        if not transcription.strip():
            continue

        if "exit" in transcription.strip().lower():
            yield "Session ended by user.", "", "", ""
            break

        yield f"Transcribed: {transcription}", transcription, "", ""
        yield "Running workflow...", transcription, "", ""

        try:
            final_result, pddl_plan = run_pipeline(transcription)
            yield "Done. Listening...", transcription, pddl_plan, final_result
        except Exception as e:
            yield f"Error: {str(e)}", transcription, "", ""


with gr.Blocks(title="Autopilot") as demo:
    gr.Markdown("# Autopilot\nHands-free desktop automation. Speak your command, say \"Exit\" to end the session.")

    status_box = gr.Textbox(
        label="Status",
        interactive=False,
        lines=1,
        value="Press Start to begin.",
    )

    with gr.Row():
        transcription_box = gr.Textbox(
            label="Transcription",
            interactive=False,
            lines=2,
        )

    with gr.Row():
        pddl_box = gr.Textbox(
            label="PDDL Plan",
            interactive=False,
            lines=10,
        )

    with gr.Row():
        result_box = gr.Textbox(
            label="Result",
            interactive=False,
            lines=2,
        )

    demo.load(
        fn=loop,
        inputs=[],
        outputs=[status_box, transcription_box, pddl_box, result_box],
    )

if __name__ == "__main__":
    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
        inbrowser=os.getenv("GRADIO_INBROWSER", "true").lower() == "true",
    )
