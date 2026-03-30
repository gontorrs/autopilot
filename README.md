# 🤖 Autopilot

> **Natural language → PDDL planning → GUI execution — fully local, fully private.**

Autopilot is a multi-agent desktop automation system that lets you control your Windows PC using plain English. Unlike cloud-based competitors, Autopilot runs entirely on your machine using small quantized models (2–4B parameters, ≤4 GB VRAM), with zero data ever leaving your device.

**Status:** Beta — core pipelines implemented and functional. Empirical benchmarking against competitors in progress.

---

## 📄 Research Paper

> **A paper based on this work is currently being written for academic publication.**

This project is the foundation of an undergraduate thesis (TFG) and an accompanying research paper exploring the integration of formal PDDL planning with multi-agent VLM-based GUI automation on consumer hardware. The paper covers architecture design, empirical evaluation against state-of-the-art competitors, and a discussion of privacy-preserving desktop automation as a research direction.

---

## ✨ What makes Autopilot different

| Feature | Autopilot | Cloud systems (Agent S2, GPT CU, Gemini CU) | Peekaboo | ScreenAgent |
|---|---|---|---|---|
| Runs fully locally | ✅ | ❌ | ✅ (macOS only) | ✅ |
| Zero data leaves device | ✅ | ❌ Screenshots sent to API | ✅ | ✅ |
| Formal planning layer (PDDL) | ✅ | ❌ Reactive LLM | ❌ | ❌ |
| Works on Windows | ✅ | ✅ | ❌ macOS 15+ only | ✅ |
| VRAM requirement | ≤ 4 GB | N/A (cloud) | N/A (cloud) | 8–16 GB |
| Verifiable, auditable plans | ✅ | ❌ | ❌ | ❌ |
| QA self-verification step | ✅ | ❌ | ❌ | ❌ |

---

## 🏗️ Architecture

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
│   Orchestrator    │  Iterates over plan steps, dispatches agents
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
| `Orchestrator` | LLM | CrewAI Agent *(planned)* | Dispatches plan steps to the right agents |
| `ScoutAgent` | VLM | Custom BaseAgent (Ollama embedded) | Checks if target UI element is visible on screen |
| `VisionAgent` | VLM | Custom BaseAgent (Ollama embedded) | Locates exact pixel coordinates of a UI element |
| `QAAgent` | VLM | Custom BaseAgent (Ollama embedded) | Verifies the task goal was achieved |
| `ExecutorAgent` | Pure code | Custom BaseAgent | Executes GUI actions (click, type, format text) |
| `PDDLTranslatorAgent` | Pure code | Custom BaseAgent | Parses PDDL plan text into structured action steps |

---

## 🗂️ Supported Task Templates

| Template | Implemented |
|---|---|
| Search and open a file | ✅ |
| Write a note (Notepad / Word) | ✅ |
| Apply text formatting (bold, italic, underline) | ✅ |
| Create a file or folder at a given path | PDDL only |
| Send an email via Outlook | 🔲 Planned |
| Copy and paste a file | 🔲 Optional |
| Compress files/folders to ZIP | 🔲 Optional |
| Add a slide to a PowerPoint | 🔲 Planned |
| Search for specific text in a document | 🔲 Planned |
| Delete specific text in a document | 🔲 Planned |

---

## ⚙️ Requirements

- **OS:** Windows 10 / 11
- **GPU:** NVIDIA GPU with ≥ 4 GB VRAM (tested on RTX 3060)
- **RAM:** ≥ 8 GB
- **Python:** 3.11+
- **Ollama:** running locally at `http://localhost:11434`
- **Fast Downward:** installed and accessible from PATH

### Recommended models

| Role | Model | Size |
|---|---|---|
| LLM planner / intent | `qwen3:4b-instruct` | ~2.5 GB |
| VLM (scout / vision / QA) | `qwen3-vl:2b-instruct` | ~1.5 GB |

---

## 🚀 Installation

```bash
# 1. Clone the repo
git clone https://github.com/TBD/autopilot.git
cd autopilot

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Pull the required Ollama models
ollama pull qwen3:4b-instruct-2507-q4_K_M
ollama pull qwen3-vl:2b-instruct-q4_K_M

# 4. Make sure Fast Downward is installed and in PATH
# https://www.fast-downward.org/

# 5. Run
python main.py
```

---

## 💬 Usage examples

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

## 🔬 Competitors & context

Autopilot was designed and evaluated against the following systems:

- **Agent S2** — state-of-the-art cloud-based desktop agent (GUI Odyssey benchmark leader)
- **ScreenAgent** — first VLM grounding paper, local but resource-heavy
- **Peekaboo** — macOS-only, uses accessibility tree + optional Ollama
- **Claude Cowork / GPT Computer Use / Gemini Computer Use** — high-capability cloud agents
- **Windows Voice Access** — rule-based speech-to-action, not a model
- **WarmWind** — Linux-only remote automation

The key distinction of Autopilot is **formal planning + local-first + Windows** — a combination no existing system currently offers.

---

## 📁 Project structure

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

---

## 📜 License

This project is part of an undergraduate thesis (TFG) at Universidad Francisco de Vitoria. Academic use only.

---

## 👤 About

**Author:** Gonzalo Torras Serrano  
**Supervisor:** Moisés Martínez Muñoz  
**Institution:** Universidad Francisco de Vitoria (UFV), Madrid  
**Degree:** Computer Science — Final Degree Project (TFG)  
**Year:** 2025

---

*Built with [CrewAI](https://crewai.com), [Ollama](https://ollama.com), and [Fast Downward](https://www.fast-downward.org/).*

---

<sub>© 2025 Gonzalo Torras Serrano — Universidad Francisco de Vitoria. All rights reserved. This project and its associated research paper are the original work of the author, developed under the supervision of Moisés Martínez Muñoz.</sub>
