"""
Distributed Task Worker - Runs on both laptop and desktop
Uses file-based coordination via Syncthing for parallel processing
"""
import os
import json
import time
import socket
from pathlib import Path
from datetime import datetime

# Get machine identifier
MACHINE_NAME = socket.gethostname()

# Paths
BASE_DIR = Path(__file__).parent
TODO_DIR = BASE_DIR / "todo"
PROCESSING_DIR = BASE_DIR / "processing"
COMPLETED_DIR = BASE_DIR / "completed"

def log(message):
    """Log with timestamp and machine name"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{MACHINE_NAME}] {message}")

def claim_task():
    """
    Try to claim a task from the todo folder
    Returns task file path if claimed, None if no tasks available
    """
    try:
        # Get all JSON files in todo folder
        task_files = list(TODO_DIR.glob("*.json"))
        
        if not task_files:
            return None
        
        # Try to claim the first available task
        task_file = task_files[0]
        
        # Create unique processing filename with machine identifier
        processing_file = PROCESSING_DIR / f"{task_file.stem}_{MACHINE_NAME}_{int(time.time())}.json"
        
        # Try to move file atomically (race condition protection)
        try:
            # Read task before moving
            with open(task_file, 'r') as f:
                task_data = json.load(f)
            
            # Try to move - if another machine already claimed it, this will fail
            os.rename(task_file, processing_file)
            
            log(f"✅ Claimed task: {task_file.name}")
            return processing_file, task_data
            
        except (FileNotFoundError, PermissionError):
            # Another machine already claimed it
            log(f"⚠️  Task {task_file.name} already claimed by another machine")
            return None
            
    except Exception as e:
        log(f"❌ Error claiming task: {e}")
        return None

def process_task(task_data):
    """
    Process the actual task
    Modify this function based on your specific task type
    """
    task_type = task_data.get("type", "unknown")
    
    log(f"🔄 Processing task type: {task_type}")
    
    # Example: Simple command execution
    if task_type == "command":
        command = task_data.get("command")
        log(f"Executing: {command}")
        # Add your actual processing logic here
        time.sleep(2)  # Simulate work
        result = {"status": "success", "output": "Task completed", "machine": MACHINE_NAME}
    
    elif task_type == "analysis":
        data = task_data.get("data")
        log(f"Analyzing data: {data}")
        # Add your analysis logic here
        time.sleep(3)  # Simulate work
        result = {"status": "success", "analysis": "Completed analysis", "machine": MACHINE_NAME}
    
    else:
        log(f"⚠️  Unknown task type: {task_type}")
        result = {"status": "error", "error": f"Unknown task type: {task_type}", "machine": MACHINE_NAME}
    
    return result

def complete_task(processing_file, task_data, result):
    """
    Move completed task to completed folder with results
    """
    try:
        # Create result file with same name in completed folder
        result_file = COMPLETED_DIR / processing_file.name
        
        # Combine task data with results
        output_data = {
            "task": task_data,
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "processed_by": MACHINE_NAME
        }
        
        # Write results
        with open(result_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Remove from processing
        os.remove(processing_file)
        
        log(f"✅ Completed task: {processing_file.name}")
        
    except Exception as e:
        log(f"❌ Error completing task: {e}")

def run_worker(poll_interval=5):
    """
    Main worker loop - continuously checks for and processes tasks
    """
    log(f"🚀 Worker started on {MACHINE_NAME}")
    log(f"📁 Watching: {TODO_DIR}")
    
    try:
        while True:
            # Try to claim a task
            task_info = claim_task()
            
            if task_info:
                processing_file, task_data = task_info
                
                # Process the task
                result = process_task(task_data)
                
                # Complete the task
                complete_task(processing_file, task_data, result)
            else:
                # No tasks available, wait before checking again
                time.sleep(poll_interval)
                
    except KeyboardInterrupt:
        log("⏹️  Worker stopped by user")
    except Exception as e:
        log(f"❌ Worker error: {e}")

if __name__ == "__main__":
    import sys
    
    # Optional: custom poll interval from command line
    poll_interval = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    run_worker(poll_interval)
