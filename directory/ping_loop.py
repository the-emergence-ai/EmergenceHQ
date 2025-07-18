#!/usr/bin/env python
"""
Health monitoring loop for Emergence agents.
Polls every agent image, runs a 2-second echo test,
updates status + last_ping in the directory DB.
"""
import requests
import subprocess
import json
import datetime
import time
import sys

# Directory API endpoint
DIR = "http://127.0.0.1:8000"

# Standard health check message following Emergence protocol
HELLO = {
    "id": "health-check",
    "from": "pinger",
    "to": "agent",
    "verb": "HELP",
    "data": {"prompt": "ping"}
}

def check_agent_health(image, agent_name):
    """
    Run a quick health check on an agent image.
    Returns "healthy" if agent responds correctly, "error" otherwise.
    """
    try:
        print(f"Checking {agent_name} ({image})...")
        
        # Run the agent with a timeout
        proc = subprocess.run(
        ["docker", "run", "-i", "--rm", image],  # <- Add -i flag
        input=json.dumps(HELLO).encode(),
        capture_output=True,
        timeout=5
        )
        
        # Debug output
        print(f"  Return code: {proc.returncode}")
        print(f"  Stdout: {proc.stdout.decode()}")
        print(f"  Stderr: {proc.stderr.decode()}")
        
        # Check if agent responded correctly
        success = (
            proc.returncode == 0 and 
            b'"verb": "DONE"' in proc.stdout
        )
        
        status = "healthy" if success else "error"
        print(f"  → {status}")
        return status
        
    except subprocess.TimeoutExpired:
        print(f"  → timeout (error)")
        return "error"
    except Exception as e:
        print(f"  → exception: {e}")
        return "error"

def update_agent_status(agent_name, status):
    """Update agent status in the directory"""
    try:
        response = requests.patch(f"{DIR}/agents/{agent_name}", json={
            "status": status,
            "last_ping": datetime.datetime.utcnow().isoformat()
        })
        if response.status_code != 200:
            print(f"Failed to update {agent_name}: {response.text}")
    except Exception as e:
        print(f"Failed to update {agent_name}: {e}")

def ping_loop():
    """Main loop that continuously monitors all agents"""
    print("Starting health monitoring loop...")
    
    while True:
        try:
            # Get all registered agents
            response = requests.get(f"{DIR}/agents")
            agents = response.json()
            
            if not agents:
                print("No agents registered, waiting...")
            else:
                print(f"Checking {len(agents)} agents...")
                
                # Check each agent
                for agent in agents:
                    status = check_agent_health(agent["image"], agent["name"])
                    update_agent_status(agent["name"], status)
            
            print("Waiting 60 seconds until next check...\n")
            time.sleep(60)  # Check every minute
            
        except KeyboardInterrupt:
            print("\nStopping health monitoring...")
            break
        except Exception as e:
            print(f"Error in ping loop: {e}")
            time.sleep(10)  # Wait before retrying

if __name__ == "__main__":
    ping_loop()