# Autopilot

> **Natural language → PDDL planning → GUI execution — fully local, fully private.**

Autopilot is a multi-agent desktop automation system that lets you control your Windows PC using plain English. Unlike cloud-based competitors, Autopilot runs entirely on your machine using small quantized models (2–4B parameters, ≤4 GB VRAM), with zero data ever leaving your device.

**Status:** Beta — core pipelines implemented and functional.

---

> **This branch implements the three core task templates as static Python workflows — and also includes a LangGraph-based version of the same approach.**
>
> Each template (open a file, write a note, apply text formatting) is hardcoded as a fixed sequence of steps in Python, with no shared actions between them. Sub-steps that appear across multiple templates — such as opening an application — are duplicated in each workflow rather than reused, making the system rigid and hard to scale. Adding a new task type requires writing a completely new workflow from scratch.
>
> A LangGraph-based version of these static templates was also implemented in this branch, exploring whether a graph-based state machine could bring some structure to the execution flow. However, the fundamental limitation remains the same: the templates are still static and deterministic by design, with no modularity between them.
>
> This rigidity was the main motivation for moving towards PDDL-based planning in later branches, where actions are reusable and the planner composes them automatically.

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
│   ├── pddl/
│   │   ├── change_problem.pddl
│   │   ├── file_problem.pddl
│   │   ├── gui_domain.pddl
│   │   ├── navigate_problem.pddl
│   │   └── text_problem.pddl
│   ├── py_workflows/
│   │   ├── change_text_template.py
│   │   ├── files_template.py
│   │   ├── files_template_easy.py
│   │   └── text_template.py
│   ├── tools/
│   │   ├── planner_tools.py
│   │   └── vlm_tools.py
│   ├── utils/
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
