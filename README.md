# Autopilot

> **Natural language → PDDL planning → GUI execution — fully local, fully private.**

Autopilot is a multi-agent desktop automation system that lets you control your Windows PC using plain English. Unlike cloud-based competitors, Autopilot runs entirely on your machine using small quantized models (2–4B parameters, ≤4 GB VRAM), with zero data ever leaving your device.

**Status:** Beta — core pipelines implemented and functional.

---

> **This branch introduces PDDL-based formal planning as the core execution backbone, using Fast Downward as the solver across three task templates.**
>
> This design represents the architectural sweet spot reached after two earlier approaches:
>
> - **Static workflow templates** (previous branch): fully deterministic and reliable, but rigid — recurring sub-steps like opening an application were duplicated across every template, making the system hard to extend.
> - **LLM-driven modular execution** (previous branch): flexible in theory, but the model consistently failed to manage the full sequence of steps — repeating tools, losing track of the goal, and never converging reliably.
>
> PDDL planning takes the best of both worlds: it inherits the **modularity** of the LLM approach (reusable actions, composable steps) while remaining **fully deterministic and verifiable**, like the static templates. Fast Downward generates an optimal plan from a domain and problem file, so the agent always follows a structured, auditable sequence — not a guess.
>
> The three supported task templates are encoded as PDDL domains and problems, and the planner resolves them in milliseconds, making the pipeline significantly faster than any LLM-based orchestration approach.

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
│   ├── bin/
│   ├── pddl/
│   │   └── templates/
│   │       ├── change_problem.pddl
│   │       ├── file_problem.pddl
│   │       ├── gui_domain.pddl
│   │       ├── navigate_problem.pddl
│   │       └── text_problem.pddl
│   ├── tools/
│   │   ├── planner_tools.py
│   │   └── vlm_tools.py
│   ├── utils/
│   │   ├── actions.py
│   │   ├── parser.py
│   │   ├── pddl.py
│   │   └── router.py
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
