"""A scripted OpenAI-compatible /v1/chat/completions server so the pipeline can be tested without an API key."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


def make_server(first_turn_calls: list[tuple[str, dict]]):
    """First reply = the given tool calls (all in ONE message); after tool results arrive, reply with text."""
    seen: list[dict] = []

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):  # silence
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            seen.append(body)
            msgs = body["messages"]
            tool_msgs = [m for m in msgs if m["role"] == "tool"]
            if not tool_msgs:
                message = {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {"id": f"call_{i}", "type": "function", "function": {"name": n, "arguments": json.dumps(a)}}
                        for i, (n, a) in enumerate(first_turn_calls)
                    ],
                }
                finish = "tool_calls"
            else:
                message = {"role": "assistant", "content": "RESULTS: " + " || ".join(m["content"].replace("\n", " ") for m in tool_msgs)}
                finish = "stop"
            payload = {
                "id": "chatcmpl-fake", "object": "chat.completion", "created": 0, "model": body.get("model", "fake"),
                "choices": [{"index": 0, "message": message, "finish_reason": finish}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            }
            data = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, seen
