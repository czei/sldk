#!/usr/bin/env python3
"""Debug the web server startup issue"""

import socket
import sys
import time

# Test if port 8080 is available
def test_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

print("Testing port 8080 availability...")
if test_port('localhost', 8080):
    print("Port 8080 is in use by another process")
else:
    print("Port 8080 is available")

# Now run a minimal web server test
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Test Server Running')

print("\nTrying to start a minimal test server on port 8080...")
try:
    server = HTTPServer(('localhost', 8080), TestHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print("Test server started successfully")
    
    # Test connection
    time.sleep(1)
    if test_port('localhost', 8080):
        print("Test server is accessible")
    else:
        print("Test server is NOT accessible")
    
    server.shutdown()
except Exception as e:
    print(f"Error starting test server: {e}")

# Check for firewall or permission issues
print("\nChecking system-level issues...")
try:
    # Try different bind addresses
    for addr in ['localhost', '127.0.0.1', '0.0.0.0']:
        print(f"Testing bind address: {addr}")
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.bind((addr, 0))  # Bind to random port
            test_sock.close()
            print(f"  ✓ Can bind to {addr}")
        except Exception as e:
            print(f"  ✗ Cannot bind to {addr}: {e}")
except Exception as e:
    print(f"Socket test error: {e}")