# Autopilot

> **Natural language → PDDL planning → GUI execution — fully local, fully private.**

Autopilot is a multi-agent desktop automation system that lets you control your Windows PC using plain English. Unlike cloud-based competitors, Autopilot runs entirely on your machine using small quantized models (2–4B parameters, ≤4 GB VRAM), with zero data ever leaving your device.

**Status:** Beta — core pipelines implemented and functional.

> **This branch is where CrewAI was first integrated into the project.**

---

## This branch's architecture

Autopilot uses a **three-layer pipeline**: intent classification → formal planning → multi-agent execution.

```
User prompt (natural language)
        │
        ▼
┌───────────────────┐
│  IntentionAgent   │  LLM (CrewAI) — classifies intent, extracts args
└────────┬──────────┘
         │ intent + args
         ▼
┌───────────────────┐
│   PDDL Planner    │  Fast Downward — generates optimal, verifiable plan
│  (Fast Downward)  │
└────────┬──────────┘
         │ plan steps
         ▼
┌───────────────────┐
│   Orchestrator    │  Code — iterates over plan steps, dispatches agents
└────────┬──────────┘
         │
    ┌────┴─────────────────────────┐
    │                              │
    ▼                              ▼
┌──────────┐  ┌──────────┐    ┌──────────┐
│  Scout   │→ │  Vision  │ →  │ Executor │  Per step: VLM pipeline or pure code
│  Agent   │  │  Agent   │    │  Agent   │
└──────────┘  └──────────┘    └──────────┘
    VLM           VLM           Pure code
    YES/NO      {x, y}        pyautogui
         │
         ▼
┌───────────────────┐
│     QA Agent      │  VLM — verifies goal was achieved (YES / NO)
└───────────────────┘
```

### Agents

| Agent | Type | Framework | Role |
|---|---|---|---|
| `IntentionAgent` | LLM | CrewAI Agent | Classifies user input into a PDDL template |
| `Orchestrator` | Code | Custom code | Dispatches plan steps to the right agents |
| `ScoutAgent` | VLM | Custom BaseAgent (Ollama embedded) | Checks if target UI element is visible on screen |
| `VisionAgent` | VLM | Custom BaseAgent (Ollama embedded) | Locates exact pixel coordinates of a UI element |
| `QAAgent` | VLM | Custom BaseAgent (Ollama embedded) | Verifies the task goal was achieved |
| `ExecutorAgent` | Code | Custom BaseAgent | Executes GUI actions (click, type, format text) |
| `PDDLTranslatorAgent` | Code | Custom BaseAgent | Parses PDDL plan text into structured action steps |

---

## Supported Task Templates

| Template | Implemented |
|---|---|
| Search and open a file | Yes |
| Write a note (Notepad / Word) | Yes |
| Apply text formatting (bold, italic, underline) | Yes |
| Create a file or folder at a given path | PDDL only |
| Send an email via Outlook | Planned |
| Copy and paste a file | Optional |
| Compress files/folders to ZIP | Optional |
| Add a slide to a PowerPoint | Planned |
| Search for specific text in a document | Planned |
| Delete specific text in a document | Planned |

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
├── main.py                  # Entry point
├── crew/
│   ├── agents.py            # Agent definitions
│   ├── crew.py              # Intent extraction crew
│   ├── orchestrator.py      # Plan execution orchestrator
│   ├── tasks.py             # CrewAI task definitions
│   ├── tools.py             # pyautogui tools
│   ├── vlm_agents.py        # Scout, Vision, QA agents
│   ├── executor_agent.py    # Pure-code executor
│   ├── pddl_translator.py   # PDDL plan parser
│   └── registry.py          # Action registry
├── pddl/
│   ├── templates/           # PDDL domain + problem templates
│   └── results/             # Generated plans + name mappings
└── utils/
    └── pddl.py              # PDDL problem builder
```
