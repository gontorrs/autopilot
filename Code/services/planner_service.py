import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from crew.planner_agent import PDDLPlannerAgent


class PlannerHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/plan":
            self._send_json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        state_dict = payload.get("state_dict", {})
        output_filename = payload.get("output_filename", "problem.pddl")

        print(f"[planner-service] planning {output_filename}", flush=True)
        result = PDDLPlannerAgent().to_goal(state_dict, output_filename)
        self._send_json(200, {"result": result})


def main():
    host = os.getenv("PLANNER_HOST", "0.0.0.0")
    port = int(os.getenv("PLANNER_PORT", "8000"))
    print(f"[planner-service] listening on {host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), PlannerHandler).serve_forever()


if __name__ == "__main__":
    main()
