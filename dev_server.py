#!/usr/bin/env python3
"""Local development server for Pierogi Pick'em.

Serves:
- / and /index.html: html/2026_2027/nfl_pickem.html (standings)
- /pick.html: pick.html (mobile picking interface)
- /api/api.py: runs api/api.py with proper environment variables
- /images2/ and /images/: static team logo assets
"""

import http.server
import os
import socketserver
import subprocess
import sys
import urllib.parse

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class PierogiDevHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean_path = path.split("?")[0].split("#")[0]
        if clean_path in ("/", "/index.html"):
            return os.path.join(BASE_DIR, "html", "2026_2027", "nfl_pickem.html")
        elif clean_path == "/pick.html":
            return os.path.join(BASE_DIR, "pick.html")
        return os.path.join(BASE_DIR, clean_path.lstrip("/"))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/api.py":
            self.handle_api("GET", parsed.query, b"")
            return
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/api.py":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length > 0 else b""
            self.handle_api("POST", parsed.query, body)
            return
        self.send_error(404, "Not Found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def handle_api(self, method: str, query_string: str, body: bytes):
        env = dict(os.environ)
        env["REQUEST_METHOD"] = method
        env["QUERY_STRING"] = query_string
        env["CONTENT_LENGTH"] = str(len(body))
        env["REMOTE_ADDR"] = self.client_address[0]
        env["PIEROGI_PROJ_DIR"] = BASE_DIR

        api_script = os.path.join(BASE_DIR, "api", "api.py")
        proc = subprocess.Popen(
            [sys.executable, api_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=BASE_DIR,
        )
        stdout, stderr = proc.communicate(input=body)

        if stderr:
            sys.stderr.write(stderr.decode("utf-8", errors="replace"))

        try:
            parts = stdout.split(b"\n\n", 1)
            header_lines = parts[0].decode("utf-8").split("\n")
            response_body = parts[1] if len(parts) > 1 else b""
            status_code = 200
            headers_to_send = []
            for line in header_lines:
                line = line.strip()
                if not line:
                    continue
                if line.lower().startswith("status:"):
                    try:
                        status_code = int(line.split(":")[1].strip().split(" ")[0])
                    except Exception:
                        pass
                elif ":" in line:
                    k, v = line.split(":", 1)
                    headers_to_send.append((k.strip(), v.strip()))

            self.send_response(status_code)
            for k, v in headers_to_send:
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)
        except Exception as e:
            self.send_error(500, f"CGI Execution error: {e}")

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PierogiDevHandler) as httpd:
        print(f"🚀 Pierogi Pick'em local dev server running on http://localhost:{PORT}")
        print(f"   - Standings page:  http://localhost:{PORT}/")
        print(f"   - Mobile pick UI:  http://localhost:{PORT}/pick.html?u=smb&k=K95eLBPagmEelFkOrVGZyQ")
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    run()
