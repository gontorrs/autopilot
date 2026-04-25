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
Code/
├── main.py                    # Entry point
├── competitors/               # Evidence for the execution of all templates, for the different competitors.
├── crew/
│   ├── agents.py              # Agent factory (manager, intention, VLM agents, etc.)
│   ├── manager_agent.py       # Custom BaseLLM for Ollama with CrewAI 1.14+ support
│   ├── executor_agent.py      # Deterministic GUI executor (clicks, typing, shortcuts)
│   ├── planner_agent.py       # PDDL problem generator + Fast Downward runner
│   ├── pddl_translator.py     # Converts PDDL plans to executable step dicts
│   └── vlm_agents.py          # Scout, Vision, and QA agents (Ollama VLM wrappers)
├── logs/
│   └── crew-ai-plain          # Logs for all the tests done, with the base version. 
|
├── tools/
│   ├── tools.py               # All CrewAI tools (orchestration + execution + intent tools)
│   └── vlm_prompts.py         # Prompt templates for VLM agents
├── pddl/
│   ├── gui_domain.pddl        # PDDL domain definition for GUI actions
│   └── *.pddl                 # Example problem files
└── requirements.txt
```

## Prerequisites

- **Python** 3.10+
- **Ollama** — running locally at `http://localhost:11434`
- **Fast Downward** — classical AI planner (compiled from source)
- **Windows desktop environment** — the system controls the actual GUI via PyAutoGUI

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
cd TFG/Code
```

### 2. Create a Python environment

Using conda (recommended):
```bash
conda create -n autopilot python=3.12
conda activate autopilot
```

Or using venv:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and start Ollama

**Windows/macOS:** Download from [ollama.com](https://ollama.com) and install.

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Start Ollama and pull the required models:
```bash
ollama serve  # if not running as a service

ollama pull gemma4:e4b-it-q4_K_M
ollama pull qwen3:4b-instruct
ollama pull qwen3-vl:2b-instruct-q4_K_M
```

### 5. Install Fast Downward

Fast Downward requires a C++ compiler and CMake to build from source.

#### Windows

1. Install [Visual Studio Community](https://visualstudio.microsoft.com/vs/community/) with the **"Desktop development with C++"** workload (this includes CMake).
2. Install [Python](https://www.python.org/downloads/) if not already installed.
3. Download the [Fast Downward source tarball](https://www.fast-downward.org/latest/releases/) and extract it.
4. Open **Developer PowerShell for VS** and run:

```powershell
cd fast-downward-24.06.1
py build.py
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt install cmake g++ make python3
git clone https://github.com/aibasel/downward.git
cd downward
python3 build.py
```

#### macOS

```bash
brew install cmake
git clone https://github.com/aibasel/downward.git
cd downward
python3 build.py
```

### 6. Configure the Fast Downward path

In `crew/planner_agent.py`, update the path to your Fast Downward installation:

```python
# Change this line to match your system:
fd = "C:\\Users\\gonza\\fastdownward\\fast-downward.py"

# Linux/macOS example:
# fd = "/home/user/downward/fast-downward.py"
```

## Usage

Edit `main.py` to set your desired user input, then run:

```bash
cd Code/
python main.py
```

**Important:** Minimize your terminal after launching. The system controls your mouse and keyboard directly — do not interact with the desktop while Autopilot is running.

Example inputs (uncomment one in `main.py`):

```python
user_input = "Open the file report.pdf which is in Documents, then TFG folder and then Docs folder."
user_input = "Take a quick note saying that I have a meeting tomorrow at 3 pm."
user_input = "Open my file.odt in MyFolder and make the text 'Hello World' in italic."
user_input = 'Create a folder named "Projects" in the Documents folder.'
user_input = 'Copy my document.docx in my Downloads folder and paste it in my Documents folder.'
```

The manager agent will orchestrate the full pipeline automatically, performing real GUI actions on your screen.

## Configuration

Models can be changed in `main.py` via the `model_dict`:

```python
planner_model = model_dict['e4bk']       # Manager LLM
vlm_model = model_dict['qwen2k-vl']      # Vision-language model
intention_model = model_dict['qwen4k']    # Intention classifier
```

See `main.py` for the full list of available model aliases.

## Tech Stack

- **CrewAI 1.14+** — multi-agent orchestration framework
- **Ollama** — local LLM/VLM inference
- **Fast Downward** — classical AI planner (PDDL)
- **PyAutoGUI** — GUI automation (mouse/keyboard control)
- **Gemma 4 / Qwen 3** — language models for reasoning and tool-calling
- **Qwen3-VL** — vision-language model for screenshot analysis

## License

Part of a Final Degree Project (FDP) at Universidad Francisco de Vitoria, Madrid.