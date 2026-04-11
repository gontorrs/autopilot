# Autopilot

> **Natural language → PDDL planning → GUI execution — fully local, fully private.**

Autopilot is a multi-agent desktop automation system that lets you control your Windows PC using plain English. Unlike cloud-based competitors, Autopilot runs entirely on your machine using small quantized models (2–4B parameters, ≤4 GB VRAM), with zero data ever leaving your device.

**Status:** Beta — core pipelines implemented and functional.

---

> **This branch explores the integration of an IndexTool so the user only needs to mention the document name, without providing the full path.**
>
> The goal is to automatically resolve file paths by indexing the filesystem. Integration with [Everything](https://www.voidtools.com/) is currently being attempted as the primary backend, as the native Windows Search has been tested but proved unreliable for this use case.
>
> **This branch is a work in progress and is not finished.** Implementation will be completed if time allows within the scope of the Final Degree Project.

---

## Architecture

Autopilot uses a **three-layer pipeline**: intent classification → formal planning → multi-agent execution.

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
│   │   ├── index.py
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
