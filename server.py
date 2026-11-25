"""BudgieOS AI local web server. Supports Ollama and OpenAI-compatible chat APIs."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path
import json
import os

ROOT = Path(__file__).resolve().parent
HOST = os.getenv("BUDGIE_HOST", "127.0.0.1")
PORT = int(os.getenv("BUDGIE_PORT", "8765"))
PROVIDER = os.getenv("BUDGIE_PROVIDER", "ollama").lower()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            self.send_json(200, {"available": self.provider_configured(), "provider": PROVIDER})
            return
        path = "/index.html" if self.path == "/" else self.path.split("?", 1)[0]
        target = (ROOT / path.lstrip("/")).resolve()
        if ROOT not in target.parents or not target.is_file():
            self.send_error(404)
            return
        content_type = "text/html; charset=utf-8" if target.suffix == ".html" else "text/css; charset=utf-8" if target.suffix == ".css" else "application/javascript; charset=utf-8" if target.suffix == ".js" else "application/octet-stream"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def provider_configured(self):
        if PROVIDER == "ollama":
            return True
        return bool(AI_API_KEY)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 1_000_000:
                self.send_json(400, {"error": "Request size is invalid."})
                return
            payload = json.loads(self.rfile.read(length))
            messages = payload.get("messages", [])
            if not isinstance(messages, list) or not messages:
                self.send_json(400, {"error": "Please enter a message."})
                return
            safe_messages = []
            for item in messages[-30:]:
                role = item.get("role")
                content = item.get("content")
                if role in ("user", "assistant") and isinstance(content, str):
                    safe_messages.append({"role": role, "content": content[:12000]})
            if PROVIDER == "ollama":
                model = str(payload.get("model", "llama3.2"))[:80]
                request_data = {"model": model, "messages": safe_messages, "stream": False}
                url = OLLAMA_URL.rstrip("/") + "/api/chat"
                headers = {"Content-Type": "application/json"}
            elif PROVIDER == "openai":
                if not AI_API_KEY:
                    self.send_json(503, {"error": "AI_API_KEY is not configured on the server."})
                    return
                request_data = {"model": AI_MODEL, "messages": safe_messages, "stream": False}
                url = AI_BASE_URL.rstrip("/") + "/chat/completions"
                headers = {"Content-Type": "application/json", "Authorization": "Bearer " + AI_API_KEY}
            else:
                self.send_json(500, {"error": "Unknown BUDGIE_PROVIDER. Use ollama or openai."})
                return
            req = Request(url, data=json.dumps(request_data).encode("utf-8"), headers=headers, method="POST")
            with urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
            if PROVIDER == "ollama":
                reply = result.get("message", {}).get("content", "")
            else:
                reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            self.send_json(200, {"reply": reply})
        except HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:1000]
            self.send_json(502, {"error": "AI provider returned an error: " + detail})
        except (URLError, TimeoutError) as error:
            self.send_json(503, {"error": "Could not reach the AI provider. Check that it is running and configured."})
        except (ValueError, KeyError, TypeError):
            self.send_json(400, {"error": "Invalid request or provider response."})

    def log_message(self, fmt, *args):
        print("[BudgieOS AI] " + (fmt % args))

if __name__ == "__main__":
    print(f"BudgieOS AI is running at http://{HOST}:{PORT}")
    print(f"Provider: {PROVIDER}. Press Ctrl+C to stop.")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
