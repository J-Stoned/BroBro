# Distributed Task Processing System

## Overview
This system enables parallel processing across your laptop and desktop using Syncthing for file synchronization.

## How It Works

1. **File-Based Coordination**: Tasks are JSON files in shared folders
2. **Syncthing Sync**: Files sync in real-time between machines
3. **Atomic Claiming**: Workers claim tasks by moving files (prevents conflicts)
4. **Parallel Execution**: Both machines process different tasks simultaneously

## Directory Structure

```
distributed-tasks/
├── todo/          # Place new tasks here
├── processing/    # Tasks currently being worked on (machine_name in filename)
├── completed/     # Finished tasks with results
├── worker.py      # Worker script (run on both machines)
└── create_tasks.py # Helper to create tasks
```

## Setup

### On Laptop (st0nes_laptop) - DONE ✅
Syncthing is already syncing `C:\Users\justi\BroBro` to your desktop!

### On Desktop (DESKTOP-A7HV9S3) - TODO
1. Make sure Syncthing is running and connected
2. Verify the BroBro folder is syncing
3. Navigate to the synced folder

## Usage

### Step 1: Start Workers on Both Machines

**On Laptop:**
```bash
cd "C:\Users\justi\BroBro\distributed-tasks"
python worker.py
```

**On Desktop:**
```bash
cd "[synced path]\BroBro\distributed-tasks"
python worker.py
```

### Step 2: Create Tasks (on either machine)

**Option A: Use the helper script**
```bash
python create_tasks.py
```

**Option B: Create tasks manually**
Create a JSON file in the `todo/` folder:

```json
{
  "type": "command",
  "command": "python process_data.py --input data.csv",
  "created_at": "2025-11-13T..."
}
```

### Step 3: Watch the Magic! ✨

Both workers will:
1. Check `todo/` folder for new tasks
2. Claim tasks atomically (no conflicts!)
3. Move to `processing/` with machine identifier
4. Process the task
5. Save results to `completed/`
6. Syncthing syncs everything in real-time!

## Monitoring

Watch the worker output to see which machine is processing which task:

```
[2025-11-13 14:30:15] [st0nes_laptop] ✅ Claimed task: task_command_1699890615.json
[2025-11-13 14:30:15] [st0nes_laptop] 🔄 Processing task type: command
[2025-11-13 14:30:17] [st0nes_laptop] ✅ Completed task: task_command_1699890615_st0nes_laptop_1699890615.json

[2025-11-13 14:30:16] [DESKTOP-A7HV9S3] ✅ Claimed task: task_analysis_1699890616.json
[2025-11-13 14:30:16] [DESKTOP-A7HV9S3] 🔄 Processing task type: analysis
[2025-11-13 14:30:19] [DESKTOP-A7HV9S3] ✅ Completed task: task_analysis_1699890616_DESKTOP-A7HV9S3_1699890616.json
```

## Customizing Task Processing

Edit `worker.py` and modify the `process_task()` function to handle your specific task types:

```python
def process_task(task_data):
    task_type = task_data.get("type")
    
    if task_type == "ghl_automation":
        # Your GHL automation logic
        pass
    elif task_type == "data_analysis":
        # Your data analysis logic
        pass
    # Add more task types as needed
```

## Advanced: Batch Task Creation

Create multiple tasks at once:

```python
from create_tasks import create_task

# Create 100 tasks that will be distributed across both machines
for i in range(100):
    create_task("analysis", 
                data_id=i, 
                input_file=f"data_{i}.csv")
```

## Benefits

✅ **No Network Configuration**: Syncthing handles all networking  
✅ **Automatic Load Balancing**: Fastest machine gets more tasks  
✅ **Fault Tolerant**: If one machine crashes, the other keeps working  
✅ **Simple Coordination**: File-based, no complex distributed systems  
✅ **Easy Debugging**: All tasks and results are visible as files  

## Troubleshooting

### Tasks Not Processing
- Check both workers are running
- Verify Syncthing shows "Up to Date"
- Check `processing/` folder for stuck tasks

### Syncthing Not Syncing
- Open http://localhost:8384 on both machines
- Verify both devices show "Connected"
- Check folder status shows "Up to Date"

### Tasks Processed Twice
- This shouldn't happen due to atomic file operations
- If it does, check your Syncthing sync interval

## Real-World Example: GHL Command Processing

```python
# On laptop: Create 50 GHL automation tasks
from create_tasks import create_task

ghl_commands = [
    "workflow_create",
    "contact_import", 
    "email_send",
    # ... 47 more commands
]

for cmd in ghl_commands:
    create_task("ghl_command", 
                command=cmd,
                api_key="your_key",
                location="abc123")
```

**Result**: Both machines process ~25 commands each in parallel! 🚀

## Integration with Claude Code

When using Claude Code (Desktop Commander), you can:

1. **Generate tasks programmatically**
2. **Monitor progress across machines**
3. **Collect and analyze results**
4. **Automatically retry failed tasks**

Example workflow:
```bash
# Generate 100 tasks
python generate_ghl_tasks.py

# Start workers on both machines
# Laptop: python worker.py
# Desktop: python worker.py

# Check progress
ls completed/ | wc -l

# Analyze results
python analyze_results.py
```

---

**Ready to Go!** 🎉

Your distributed task system is set up and ready. Just start the workers on both machines and create some tasks!
