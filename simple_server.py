from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json
import os

from src.core.agent_orchestrator import run_housing_agent


HTML_FILE = os.path.join(os.path.dirname(__file__), "docs", "form.html")


class SimpleHandler(BaseHTTPRequestHandler):
    def _set_json_response(self, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        # Permissive CORS
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            try:
                with open(HTML_FILE, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                # Permissive CORS
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_response(404)
                # Permissive CORS
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b"Form not found. Place form.html in docs/")
        else:
            self.send_response(404)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

    def do_POST(self):
        if self.path != "/submit":
            self.send_response(404)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        content_type = self.headers.get("Content-Type", "")
        raw = self.rfile.read(content_length) if content_length else b""

        try:
            if "application/json" in content_type:
                payload = json.loads(raw.decode("utf-8"))
            else:
                # form data
                parsed = parse_qs(raw.decode("utf-8"))
                # parse_qs returns lists for each key
                payload = {k: v[0] for k, v in parsed.items()}

            # Accept either a single free-text `user_input` or structured fields
            if payload.get("user_input"):
                user_input = payload.get("user_input")
            else:
                # Build a prompt from structured fields
                current = payload.get("current_location", "")
                target = payload.get("target_location", "")
                workplace = payload.get("workplace_location", "")
                budget = payload.get("monthly_budget", "")
                prefs = payload.get("preferences", "")

                user_input = (
                    f"I am moving from {current}. I want to move to {target}. "
                    f"I will be working at {workplace}. My monthly budget is {budget}. "
                    f"Preferences: {prefs}"
                )

            # Call existing orchestrator
            result = run_housing_agent(user_input, [])

            self._set_json_response(200)
            self.wfile.write(json.dumps(result).encode("utf-8"))

        except Exception as e:
            self._set_json_response(500)
            err = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(err).encode("utf-8"))

    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.send_header("Access-Control-Max-Age", "3600")
        self.end_headers()


def run(server_class=HTTPServer, handler_class=SimpleHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving on http://0.0.0.0:{port} — GET / for form, POST /submit for API")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down")
        httpd.server_close()


if __name__ == "__main__":
    run()
