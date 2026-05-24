import subprocess
import sys
from pathlib import Path


root = Path(__file__).resolve().parent
code = root / "Code"
env = {
    **dict(__import__("os").environ),
    "PYTHONPATH": str(code),
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "PLANNER_URL": "http://localhost:8000",
}
env.pop("WHISPER_URL", None)

try:
    subprocess.run(["docker", "compose", "up", "--build", "-d", "--remove-orphans", "ollama", "planner"], cwd=root, check=True)
    subprocess.run([sys.executable, "-u", "main.py"], cwd=code, env=env)
except KeyboardInterrupt:
    pass
finally:
    subprocess.run(["docker", "compose", "down", "--remove-orphans"], cwd=root)