#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Server for Smile Cafe POS System
A minimal, reliable server that serves all files correctly
"""

import http.server
import socketserver
import os
import sys
import webbrowser
import threading
import time

# Configuration
PORT = 8000
HOST = 'localhost'
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers to allow all requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Set proper content type for HTML files
        if self.path.endswith('.html') or self.path == '/':
            self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        # Handle root path
        if self.path == '/':
            self.path = '/index.html'
        
        # Handle specific routes
        elif self.path == '/pos':
            self.path = '/templates/pos.html'
        elif self.path == '/admin':
            self.path = '/templates/admin.html'
        elif self.path == '/menu':
            self.path = '/menu.html'
        elif self.path == '/qr':
            self.path = '/qr.html'
        
        # Try to serve the file
        try:
            return super().do_GET()
        except FileNotFoundError:
            # If file not found, try to serve index.html
            self.path = '/index.html'
            try:
                return super().do_GET()
            except FileNotFoundError:
                self.send_error(404, "File not found")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    urls = [
        f'http://{HOST}:{PORT}/index.html',
        f'http://{HOST}:{PORT}/templates/pos.html',
        f'http://{HOST}:{PORT}/templates/admin.html',
        f'http://{HOST}:{PORT}/test.html'
    ]
    
    print("\n" + "="*60)
    print("  SMILE CAFE POS SYSTEM - OPENING IN BROWSER")
    print("="*60)
    print("\nAvailable URLs:")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")
        try:
            webbrowser.open(url)
            print(f"   Opened {url}")
            break
        except:
            print(f"   Could not open {url}")
    print("\n" + "="*60)

def start_server():
    """Start the server"""
    handler = CustomHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    SMILE CAFE POS SERVER                   ║
╠══════════════════════════════════════════════════════════════╣
║  Server running at:                                        ║
║     http://localhost:{PORT}                                    ║
║     http://127.0.0.1:{PORT}                                   ║
║                                                              ║
║  Direct URLs:                                              ║
║     • Main Page:    http://localhost:{PORT}/                  ║
║     • POS:          http://localhost:{PORT}/templates/pos.html ║
║     • Admin:        http://localhost:{PORT}/templates/admin.html║
║     • Test:         http://localhost:{PORT}/test.html        ║
║                                                              ║
║  Professional Design Ready!                                ║
║     • 73 products with custom icons                         ║
║     • 8 organized sections                                   ║
║     • Full Arabic language support                           ║
║     • Professional animations                               ║
║                                                              ║
║  Press Ctrl+C to stop the server                          ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Open browser after 2 seconds
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        try:
            print(f"\n Server is ready! Opening browser...")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n Server stopped successfully")
            sys.exit(0)

if __name__ == "__main__":
    start_server()