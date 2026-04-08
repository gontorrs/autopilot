import json
import requests
from crewai import BaseLLM
from typing import Any, Dict, List, Optional, Union


class ManagerAgent(BaseLLM):

    def __init__(self, model: str, base_url: str = "http://localhost:11434", think: bool = True):
        super().__init__(model=model, temperature=0.0)
        self.base_url = base_url.rstrip("/")
        self.think = think

    def call(self, messages, tools=None, callbacks=None, available_functions=None, **kwargs):
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        # Clean messages: keep only what Ollama understands
        clean = []
        for m in messages:
            entry = {"role": m.get("role", "user"), "content": m.get("content") or ""}
            if m.get("tool_calls"):
                entry["tool_calls"] = m["tool_calls"]
            if m.get("images"):
                entry["images"] = m["images"]
            clean.append(entry)

        payload = {
            "model": self.model,
            "messages": clean,
            "stream": False,
            "think": self.think,
        }
        if tools:
            payload["tools"] = tools
        if self.stop:
            payload["options"] = {"stop": self.stop}

        # Call Ollama
        resp = requests.post(f"{self.base_url}/api/chat", json=payload)
        data = resp.json()
        print(f"[DEBUG OLLAMA RAW] {data}")
        msg = data.get("message", {})

        # Tool loop: call tool -> feed result back -> repeat until text response
        rounds = 0
        while msg.get("tool_calls") and available_functions and rounds < 15:
            rounds += 1

            clean.append({"role": "assistant", "content": "", "tool_calls": msg["tool_calls"]})

            for tc in msg["tool_calls"]:
                fn_name = tc["function"]["name"]
                fn_args = tc["function"].get("arguments", {})
                if isinstance(fn_args, str):
                    fn_args = json.loads(fn_args)

                print(f"[ManagerAgent] {fn_name}({fn_args})")

                if fn_name in available_functions:
                    try:
                        result = available_functions[fn_name](**fn_args)
                    except Exception as e:
                        result = f"ERROR: {e}"
                else:
                    result = f"ERROR: Unknown function '{fn_name}'"

                clean.append({"role": "tool", "content": str(result)})

            payload["messages"] = clean
            resp = requests.post(f"{self.base_url}/api/chat", json=payload)
            data = resp.json()
            print(f"[DEBUG OLLAMA RAW] {data}")
            msg = data.get("message", {})

        # Gemma 4 sometimes puts the Action inside thinking instead of content
        content = msg.get("content", "")
        if not content.strip() and msg.get("thinking"):
            thinking = msg.get("thinking", "")
            if "Action:" in thinking:
                lines = thinking.split("\n")
                extracted = []
                capturing = False
                for line in lines:
                    if line.strip().startswith("Thought:") or line.strip().startswith("Action:"):
                        capturing = True
                    if capturing:
                        extracted.append(line)
                content = "\n".join(extracted)

        return content if content.strip() else msg.get("thinking", "")

    def supports_function_calling(self):
        return True

    def supports_stop_words(self):
        return True