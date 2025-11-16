"""
Task Creator - Create tasks for distributed processing
"""
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
TODO_DIR = BASE_DIR / "todo"

def create_task(task_type, **kwargs):
    """
    Create a new task in the todo folder
    
    Args:
        task_type: Type of task (command, analysis, etc.)
        **kwargs: Additional task-specific parameters
    """
    task_data = {
        "type": task_type,
        "created_at": datetime.now().isoformat(),
        **kwargs
    }
    
    # Create unique filename
    timestamp = int(datetime.now().timestamp() * 1000)
    filename = TODO_DIR / f"task_{task_type}_{timestamp}.json"
    
    # Write task file
    with open(filename, 'w') as f:
        json.dump(task_data, f, indent=2)
    
    print(f"✅ Created task: {filename.name}")
    return filename

if __name__ == "__main__":
    # Example: Create some sample tasks
    
    # Command task
    create_task("command", command="echo 'Hello from distributed task'")
    
    # Analysis task
    create_task("analysis", data={"values": [1, 2, 3, 4, 5]})
    
    # You can create as many tasks as you want
    # Both machines will pick them up and process in parallel!
