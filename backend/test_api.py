#!/usr/bin/env python
"""Quick test of API endpoints"""
import time
import subprocess
import sys
from pathlib import Path

# Start the server in a subprocess
print("Starting backend server...")
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=Path(__file__).parent,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Wait for server to start
time.sleep(3)

try:
    import requests
    
    # Test health endpoint
    print("\n[TEST] Health Endpoint")
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("\n[SUCCESS] Backend is working!")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    
finally:
    # Kill the server
    print("\nShutting down server...")
    proc.terminate()
    proc.wait(timeout=5)
