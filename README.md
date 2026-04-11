# Autopilot

> **Natural language → PDDL planning → GUI execution — fully local, fully private.**

Autopilot is a multi-agent desktop automation system that lets you control your Windows PC using plain English. Unlike cloud-based competitors, Autopilot runs entirely on your machine using small quantized models (2–4B parameters, ≤4 GB VRAM), with zero data ever leaving your device.

**Status:** Beta — core pipelines implemented and functional.

---

> **This branch contains empirical benchmarking of LLM and VLM models across the three fully implemented task templates.**
>
> - **LLMs** were tested for intent classification (IntentionAgent): determining what the user wants to do and extracting structured arguments from the prompt.
> - **VLMs** were tested for two roles: locating exact pixel coordinates of UI elements on screen, and verifying that the user's request was fulfilled after execution.
>
> Each run was recorded with the following metrics: `user_input`, `inference_time`, `intent_name`, `vlm_result`, `cpu_avg`, `cpu_peak`, `ram_avg_mb`, `ram_peak_mb`, `vram_avg_mb`, `vram_peak_mb`.

---

## Models tested

### LLMs (intent classification)

| Model |
|---|
| `gemma_planner` |
| `gemma3n_planner` |
| `gemma4k_planner` |
| `llama3_planner` |
| `llama3k_planner` |
| `ministral3_planner` |
| `ministral3k_planner` |
| `qwen4instruct_planner` |
| `qwen4k_planner` |

### VLMs (coordinate grounding + goal verification)

| Model |
|---|
| `qwen2-vl` |
| `qwen2k-vl` |
| `qwen4k-vl` |
| `gemma4k` |
| `ministral3` |
| `ministral3k` |
| `phi3` |

---

## Supported Task Templates

| Template | Implemented |
|---|---|
| Search and open a file | Yes |
| Write a note (Notepad / Word) | Yes |
| Apply text formatting (bold, italic, underline) | Yes |

---

## Usage examples

```bash
# Open a file
"Open my Gonzalo_Anteproyecto.pdf which is in Documents > TFG > Docs"

# Write a note
"Take a quick note saying I have a meeting tomorrow at 3pm in Tokyo"

# Format text
"Open Entrevista_Reli.odt in Gonzalo - UFV and make the text 'Gonzalo Torras Serrano' bold"
```

When you run `main.py`, Autopilot will:
1. Classify your intent and extract structured arguments
2. Generate a PDDL problem file and solve it with Fast Downward
3. Execute the plan step by step using the agent pipeline
4. Take a final screenshot and verify the goal was achieved

---

## Project structure

```
autopilot/
├── Code/
│   ├── data/
│   │   ├── planner/
│   │   └── vlm/
│   ├── tools/
│   │   ├── planner_tools.py
│   │   └── vlm_tools.py
│   ├── utils/
│   │   ├── metrics.py
│   │   └── router.py
│   ├── workflows/
│   ├── main.py
│   ├── planner.py
│   ├── requirements.txt
│   └── vlm.py
├── Docs/
│   ├── ltx/
│   └── Gonzalo_Anteproyecto.pdf
├── Workflows/
│   ├── change_template.drawio
│   ├── navigate_template.drawio
│   ├── navigate_template_easy.drawio
│   └── write_template.drawio
└── .gitignore
```
