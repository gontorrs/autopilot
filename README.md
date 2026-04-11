# Autopilot

> **Natural language → PDDL planning → GUI execution — fully local, fully private.**

Autopilot is a multi-agent desktop automation system that lets you control your Windows PC using plain English. Unlike cloud-based competitors, Autopilot runs entirely on your machine using small quantized models (2–4B parameters, ≤4 GB VRAM), with zero data ever leaving your device.

**Status:** Beta — core pipelines implemented and functional.

---

> **This branch tests whether an LLM alone is capable of autonomously organizing the execution steps and reaching the user's goal — without a formal planning layer.**
>
> The hypothesis was that a sufficiently capable LLM, given a set of tools, could reason about the correct sequence of actions to complete a desktop task. The results showed that this approach does not work reliably: the model tends to get confused, chaining tools one after another without a clear plan, repeating the same tools multiple times, and failing to converge on the goal.
>
> This confirms the need for the PDDL planning layer as the backbone of Autopilot's architecture, rather than relying on free-form LLM reasoning for execution control.

---

## Supported Task Templates

| Template | Implemented |
|---|---|
| Search and open a file | Yes |
| Write a note (Notepad / Word) | Yes |
| Apply text formatting (bold, italic, underline) | Yes |

---

## Models tested

### LLMs (intent classification and planning)

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
│   │   └── modular/
│   │       ├── metrics_vlm.csv
│   │       ├── functiongemma_modular_planner.json
│   │       ├── gemma3n_modular_planner.json
│   │       ├── gemma4k_modular_planner.json
│   │       ├── llama3_modular_planner.json
│   │       ├── llama3k_modular_planner.json
│   │       ├── ministral3_modular_planner.json
│   │       ├── ministral3k_modular_planner.json
│   │       ├── qwen4instruct_modular_planner.json
│   │       └── qwen4k_modular_planner.json
│   ├── test/
│   │   └── test.py
│   ├── tools/
│   │   ├── planner_tools.py
│   │   └── vlm_tools.py
│   ├── utils/
│   │   ├── metrics.py
│   │   └── router.py
│   ├── workflows/
│   │   ├── files_template.py
│   │   ├── open_application.py
│   │   └── text_template.py
│   ├── main.py
│   └── requirements.txt
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
