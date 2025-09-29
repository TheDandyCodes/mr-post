#!/usr/bin/env python3
"""
Development script to run all services locally
"""
import subprocess
import time
import sys
import os
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent

def run_service(service_name, module_path, port):
    """Run a service in a subprocess"""
    print(f"Starting {service_name} on port {port}...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    
    if service_name == "storage":
        env["DATABASE_URL"] = "sqlite:///./data/mr_post.db"
    elif service_name == "agents":
        env["STORAGE_SERVICE_URL"] = "http://localhost:8001"
    elif service_name == "frontend":
        env["STORAGE_SERVICE_URL"] = "http://localhost:8001"
        env["AGENTS_SERVICE_URL"] = "http://localhost:8002"
    
    return subprocess.Popen([
        sys.executable, "-c", 
        f"import sys; sys.path.insert(0, '{PROJECT_ROOT}'); "
        f"from {module_path} import app; "
        f"import uvicorn; uvicorn.run(app, host='0.0.0.0', port={port})"
    ], env=env)

def main():
    """Run all services for development"""
    # Create data directory
    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    
    services = []
    
    try:
        # Start services in order
        services.append(run_service("storage", "services.storage.main", 8001))
        time.sleep(2)  # Give storage time to start
        
        services.append(run_service("agents", "services.agents.main", 8002))
        time.sleep(2)  # Give agents time to start
        
        services.append(run_service("frontend", "services.frontend.main", 8000))
        
        print("\n" + "="*50)
        print("All services started!")
        print("Frontend: http://localhost:8000")
        print("Storage API: http://localhost:8001/docs")
        print("Agents API: http://localhost:8002/docs")
        print("="*50)
        print("Press Ctrl+C to stop all services")
        
        # Wait for interruption
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping services...")
    
    finally:
        # Clean up all processes
        for service in services:
            service.terminate()
            service.wait()

if __name__ == "__main__":
    main()