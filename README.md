# Autopilot — AI-Powered GUI Automation System

> **⚠️ Windows Only:** This system is currently only guaranteed to work on Windows. It relies on Windows-specific GUI elements (taskbar, Start menu, File Explorer), keyboard shortcuts (Win key search), and PyAutoGUI behaviors that may not translate to macOS or Linux desktop environments.

Autopilot is a fully local, multi-agent desktop automation system that translates natural language instructions into real GUI actions. It combines classical AI planning (PDDL + Fast Downward) with vision-language models and a manager agent that orchestrates the entire pipeline — from understanding user intent to clicking buttons on screen.

Built as a Final Degree Project (FDP) in Computer Engineering.

> **This branch introduces modular state detection.** Before planning, a VLM analyzes the current screen state (open apps, active folder, file status) and injects it into the PDDL init, allowing the planner to skip steps that are already completed (e.g., if Notepad is already open, skip the open action). Each intent template (navigate, write, create, change, delete, search, copy/paste) uses a tailored VLM prompt to detect only what it needs.

## How It Works

A single **Manager Agent** sits at the top and orchestrates every other agent through tool-calling. It never executes GUI actions itself — it delegates to specialized agents:

```
                         ┌──────────────────────┐
                         │    MANAGER AGENT      │
                         │  (Gemma 4, Ollama)    │
                         │                       │
                         │  Orchestrates all      │
                         │  agents via tools      │
                         └──┬──┬──┬──┬──┬──┬──┬──┘
                            │  │  │  │  │  │  │
          ┌─────────────────┘  │  │  │  │  │  └─────────────────┐
          ▼                    ▼  │  │  │  ▼                    ▼
   ┌─────────────┐   ┌──────────┐│  │  ││──────────┐   ┌─────────────┐
   │  Intention   │   │  PDDL    ││  │  ││  PDDL    │   │     QA      │
   │  Agent       │   │  Planner ││  │  ││Translator│   │  Verifier   │
   │  (LLM)       │   │  (Fast   ││  │  ││(Determ.) │   │  (VLM)      │
   │              │   │ Downward)││  │  ││          │   │             │
   └─────────────┘   └──────────┘│  │  │└──────────┘   └─────────────┘
                                  │  │  │
                    ┌─────────────┘  │  └─────────────┐
                    ▼                ▼                 ▼
             ┌─────────────┐ ┌─────────────┐  ┌─────────────┐
             │    Scout     │ │   Vision    │  │  Executor   │
             │   Agent      │ │   Agent     │  │   Agent     │
             │  (VLM)       │ │  (VLM)      │  │ (Determ.)   │
             │ "Is it       │ │ "Where is   │  │  Clicks,    │
             │  visible?"   │ │  it?"        │  │  types,     │
             │              │ │              │  │  shortcuts   │
             └─────────────┘ └─────────────┘  └─────────────┘
```

The manager calls 7 tools in sequence:

1. **classify_intent** → Intention Agent classifies the user request into a structured intent (navigate, write, format, create, delete, search, copy/paste).
2. **generate_plan** → PDDL Planner Agent generates a classical plan using Fast Downward.
3. **translate_plan** → Translator Agent converts the PDDL plan into executable GUI steps.
4. **check_visibility** → Scout Agent takes a screenshot and checks if a UI element is visible.
5. **find_coordinates** → Vision Agent takes a screenshot and returns pixel coordinates of the element.
6. **execute_action** → Executor Agent performs the actual GUI interaction (click, type, shortcut).
7. **verify_result** → QA Agent takes a final screenshot to confirm the task was completed.

## Supported Tasks

| Task | Example |
|------|---------|
| Navigate & open files | *"Open report.pdf in Documents/TFG/Docs"* |
| Write text | *"Take a note saying I have a meeting at 3pm"* |
| Format text | *"Open my file.odt and make 'Hello' bold"* |
| Create files/folders | *"Create a folder named 'Projects' in Documents"* |
| Delete text | *"Open my file and delete 'old paragraph'"* |
| Search text | *"Open my file and search for 'Introduction'"* |
| Copy/paste files | *"Copy report.docx from Downloads to Documents"* |

## Project Structure

```
├── run.py                     # Main entry point — starts Docker services and launches the app
├── docker-compose.yaml        # Docker services (Ollama + Fast Downward planner)
├── docker/
│   └── planner/               # Dockerfile for the Fast Downward planner service
└── Code/
    ├── main.py                # Core app logic (called by run.py)
    ├── competitors/           # Evidence for the execution of all templates, for the different competitors.
    ├── crew/
    │   ├── agents.py          # Agent factory (manager, intention, VLM agents, etc.)
    │   ├── manager_agent.py   # Custom BaseLLM for Ollama with CrewAI 1.14+ support
    │   ├── executor_agent.py  # Deterministic GUI executor (clicks, typing, shortcuts)
    │   ├── planner_agent.py   # PDDL problem generator + Fast Downward runner
    │   ├── pddl_translator.py # Converts PDDL plans to executable step dicts
    │   └── vlm_agents.py      # Scout, Vision, and QA agents (Ollama VLM wrappers)
    ├── logs/
    │   └── crew-ai-plain      # Logs for all the tests done, with the base version.
    ├── tools/
    │   ├── tools.py           # All CrewAI tools (orchestration + execution + intent tools)
    │   └── vlm_prompts.py     # Prompt templates for VLM agents
    ├── pddl/
    │   ├── gui_domain.pddl    # PDDL domain definition for GUI actions
    │   └── *.pddl             # Example problem files
    └── requirements.txt
```

## Prerequisites

- **Python** 3.10+ with a virtual environment (conda or venv)
- **Docker Desktop** — must be running before launching the app
- **NVIDIA GPU with CUDA** — required for local Whisper inference (`float16`)
- **Microphone** — voice is the primary input interface
- **Windows desktop environment** — the system controls the actual GUI via PyAutoGUI

> **Why not fully Dockerized?** Two components must run on the host: the main agent pipeline (`main.py`) needs direct access to the Windows GUI via PyAutoGUI, and Whisper needs direct access to the microphone — Docker cannot reliably forward audio input devices on Windows.

### Docker Services

| Service | Image / Build | Port | Purpose |
|---------|--------------|------|---------|
| `ollama` | `ollama/ollama` | 11434 | Local LLM/VLM inference |
| `planner` | Custom (Fast Downward) | 8000 | Classical AI planner as HTTP service |

### Models (pulled via Ollama)

| Role | Default Model | Purpose |
|------|--------------|---------|
| Manager (planner LLM) | `gemma4:e4b-it-q4_K_M` | Orchestrates the pipeline via tool-calling |
| Intention classifier | `gemma4:e4b-it-q4_K_M` | Classifies user intent |
| VLM (scout/vision/QA) | `qwen3-vl:2b-instruct-q4_K_M` | Screenshot analysis and coordinate detection |

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd proyecto-fin-de-grado-2026-gontorrs
```

### 2. Create and activate a Python environment

Using conda (recommended):
```bash
conda create -n autopilot python=3.12
conda activate autopilot
```

Or using venv:
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r Code/requirements.txt
```

### 4. Install and start Docker Desktop

Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/). Make sure it is running before the next step.

### 5. Pull the required Ollama models

**This step is required.** Unlike Whisper, Ollama models are **not downloaded automatically** — if you skip this, the app will fail when it tries to use the models.

```bash
docker compose up -d ollama
docker exec -it ollama ollama pull gemma4:e4b-it-q4_K_M
docker exec -it ollama ollama pull qwen3-vl:2b-instruct-q4_K_M
```

The models are stored in a persistent Docker volume (`ollama_models`), so you only need to do this once.

### 6. Whisper model (auto-downloaded on first run)

Whisper runs **locally on the host** (not in Docker) because Docker cannot reliably forward microphone input on Windows. It uses the `faster-whisper` library, which is already included in `requirements.txt`.

The `small` model (~460 MB) **downloads automatically the first time you run `python run.py`**, so no manual step is needed. If you prefer to download it in advance to avoid waiting on the first launch:

```python
# Run once from the Code/ directory with the environment activated
from faster_whisper import WhisperModel
WhisperModel("small", device="cuda", compute_type="float16", download_root="./models/whisper")
```

Or equivalently from the shell:

```bash
cd Code
python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cuda', compute_type='float16', download_root='./models/whisper')"
```

> **Note:** Whisper requires an NVIDIA GPU. If CUDA is not available you can change `device="cuda"` to `device="cpu"` and `compute_type="float16"` to `compute_type="int8"` in `Code/voice/whisper.py`, at the cost of slower transcription.

## Usage

Make sure your Python environment is activated, then run from the project root:

```bash
# Activate environment first (if not already active)
conda activate autopilot   # or: .venv\Scripts\activate

# Launch everything
python run.py
```

`run.py` will automatically:
1. Build and start the **Ollama** and **Fast Downward planner** Docker containers in the background.
2. Launch `main.py` on the host to control the Windows GUI.
3. Shut down all containers cleanly when the app exits (or you press `Ctrl+C`).

**Important:** Minimize your terminal after launching. The system controls your mouse and keyboard directly — do not interact with the desktop while Autopilot is running.

### Customising the task

Edit `Code/main.py` to set your desired user input before running:

```python
user_input = "Open the file report.pdf which is in Documents, then TFG folder and then Docs folder."
user_input = "Take a quick note saying that I have a meeting tomorrow at 3 pm."
user_input = "Open my file.odt in MyFolder and make the text 'Hello World' in italic."
user_input = 'Create a folder named "Projects" in the Documents folder.'
user_input = 'Copy my document.docx in my Downloads folder and paste it in my Documents folder.'
```

## Configuration

Models can be changed in `Code/main.py` via the `model_dict`:

```python
planner_model = model_dict['e4bk']       # Manager LLM
vlm_model = model_dict['qwen2k-vl']      # Vision-language model
intention_model = model_dict['qwen4k']    # Intention classifier
```

See `Code/main.py` for the full list of available model aliases.

## Tech Stack

- **CrewAI 1.14+** — multi-agent orchestration framework
- **Docker** — containerised Ollama and Fast Downward services
- **Ollama** — local LLM/VLM inference
- **Fast Downward** — classical AI planner (PDDL), running as a Docker service
- **PyAutoGUI** — GUI automation (mouse/keyboard control)
- **Gemma 4 / Qwen 3** — language models for reasoning and tool-calling
- **Qwen3-VL** — vision-language model for screenshot analysis

## License

Part of a Final Degree Project (FDP) at Universidad Francisco de Vitoria, Madrid.
