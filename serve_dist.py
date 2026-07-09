#!/usr/bin/env python3
import http.server
import socketserver
import os

# Change to dist directory
os.chdir(r"C:\Users\Oden\Desktop\Hackathon\brainconnect-ai-multiagent-medical-consensus-system\dist")
print(f"Serving from: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

with open("index.html", "r") as f:
    print(f"index.html: {f.read()[:200]}")

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"Request: {self.path}")
        return super().do_GET()

with socketserver.TCPServer(("", 5173), Handler) as httpd:
    print("Serving on port 5173...")
    httpd.serve_forever()