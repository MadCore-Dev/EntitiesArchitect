#!/usr/bin/env python3
"""
MadCore Engine Server
Serves the project root directory over HTTP on port 8000.
"""

import http.server
import socketserver
import os

PORT = 8000

# Serve from the project root (one level up from this script's directory)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def log_message(self, format, *args):
        # Suppress per-request logs for a cleaner terminal
        pass

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"MadCore Engine Server Running at http://localhost:{PORT}")
        httpd.serve_forever()
