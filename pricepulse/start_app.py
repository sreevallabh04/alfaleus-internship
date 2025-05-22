#!/usr/bin/env python
"""
PricePulse Application Launcher
This script launches both the backend and frontend servers for the PricePulse application.
"""

import os
import sys
import subprocess
import time
import webbrowser
import platform

def print_colored(text, color):
    """Print colored text in the console."""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    
    # Windows cmd doesn't support ANSI color codes by default
    if platform.system() == 'Windows':
        print(text)
    else:
        print(f"{colors.get(color, '')}{text}{colors['end']}")

def check_prerequisites():
    """Check if the required software is installed."""
    print_colored("Checking prerequisites...", "blue")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print_colored("Error: Python 3.8 or higher is required.", "red")
        return False
    
    # Check Node.js
    try:
        node_process = subprocess.run(
            ["node", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        if node_process.returncode != 0:
            print_colored("Error: Node.js is not installed or not in PATH.", "red")
            return False
    except FileNotFoundError:
        print_colored("Error: Node.js is not installed or not in PATH.", "red")
        return False
    
    print_colored("✓ All prerequisites are met.", "green")
    return True

def start_backend():
    """Start the Flask backend server."""
    print_colored("\nStarting backend server...", "blue")
    
    # Determine the backend directory
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    
    # Check if the app.py file exists
    app_path = os.path.join(backend_dir, "app.py")
    if not os.path.isfile(app_path):
        print_colored(f"Error: Backend app.py not found at {app_path}", "red")
        return None
    
    # Start the backend server based on the OS
    if platform.system() == "Windows":
        process = subprocess.Popen(
            ["python", app_path],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        process = subprocess.Popen(
            ["python", app_path],
            cwd=backend_dir
        )
    
    # Give the server some time to start
    print_colored("Waiting for backend server to initialize...", "yellow")
    time.sleep(3)
    
    # Check if the server started successfully
    try:
        import requests
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print_colored("✓ Backend server started successfully!", "green")
            return process
        else:
            print_colored(f"Warning: Backend server started but health check failed with status {response.status_code}", "yellow")
            return process
    except:
        print_colored("Warning: Backend server might not have started correctly. Check the backend console for errors.", "yellow")
        return process

def start_frontend():
    """Start the React frontend server."""
    print_colored("\nStarting frontend server...", "blue")
    
    # Determine the frontend directory
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    
    # Check if package.json exists
    package_path = os.path.join(frontend_dir, "package.json")
    if not os.path.isfile(package_path):
        print_colored(f"Error: Frontend package.json not found at {package_path}", "red")
        return None
    
    # Start the frontend server
    if platform.system() == "Windows":
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir
        )
    
    print_colored("Frontend server starting...", "yellow")
    print_colored("A browser window should open automatically when ready.", "yellow")
    
    return process

def main():
    """Main function to start the application."""
    print_colored("\n======================================", "bold")
    print_colored("       PricePulse Application        ", "bold")
    print_colored("======================================\n", "bold")
    
    if not check_prerequisites():
        return
    
    backend_process = start_backend()
    if not backend_process:
        print_colored("Failed to start the backend server. Aborting.", "red")
        return
    
    frontend_process = start_frontend()
    if not frontend_process:
        print_colored("Failed to start the frontend server.", "red")
        print_colored("Shutting down backend server...", "yellow")
        backend_process.terminate()
        return
    
    print_colored("\n======================================", "bold")
    print_colored("  PricePulse Application is running  ", "bold")
    print_colored("======================================", "bold")
    print_colored("\nBackend URL: http://localhost:5000", "green")
    print_colored("Frontend URL: http://localhost:3000", "green")
    print_colored("\nPress Ctrl+C to shut down both servers.\n", "yellow")
    
    try:
        # Keep the script running to handle Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_colored("\nShutting down servers...", "yellow")
        frontend_process.terminate()
        backend_process.terminate()
        print_colored("Servers have been shut down.", "green")

if __name__ == "__main__":
    main()