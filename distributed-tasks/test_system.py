"""
Quick Test - Verify the distributed task system works
Run this on your laptop to test the setup
"""
import json
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
TODO_DIR = BASE_DIR / "todo"
COMPLETED_DIR = BASE_DIR / "completed"

def create_test_tasks(count=5):
    """Create some test tasks"""
    print(f"\n🧪 Creating {count} test tasks...")
    
    for i in range(count):
        task_data = {
            "type": "command",
            "command": f"echo 'Test task {i+1}'",
            "test_id": i+1,
            "created_at": datetime.now().isoformat()
        }
        
        timestamp = int(datetime.now().timestamp() * 1000) + i
        filename = TODO_DIR / f"test_task_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(task_data, f, indent=2)
        
        print(f"  ✅ Created: {filename.name}")
        time.sleep(0.1)  # Small delay to ensure unique timestamps
    
    print(f"\n✅ Created {count} test tasks in {TODO_DIR}")
    return count

def monitor_completion(expected_count, timeout=60):
    """Monitor the completed folder for results"""
    print(f"\n👀 Monitoring for completion (timeout: {timeout}s)...")
    print("   Start worker.py on this machine (and optionally your desktop) to process tasks\n")
    
    start_time = time.time()
    last_count = 0
    
    while time.time() - start_time < timeout:
        completed_files = list(COMPLETED_DIR.glob("*.json"))
        current_count = len(completed_files)
        
        if current_count > last_count:
            print(f"  📦 {current_count}/{expected_count} tasks completed")
            last_count = current_count
        
        if current_count >= expected_count:
            print(f"\n🎉 All {expected_count} tasks completed!")
            
            # Show which machines processed tasks
            machines = set()
            for f in completed_files:
                with open(f, 'r') as file:
                    data = json.load(file)
                    machines.add(data.get('processed_by', 'unknown'))
            
            print(f"\n📊 Tasks processed by: {', '.join(machines)}")
            return True
        
        time.sleep(1)
    
    print(f"\n⏱️  Timeout reached. {last_count}/{expected_count} tasks completed.")
    return False

def cleanup_test_files():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    
    # Clean completed
    for f in COMPLETED_DIR.glob("test_task_*.json"):
        f.unlink()
        print(f"  🗑️  Removed: {f.name}")
    
    # Clean any leftover in todo
    for f in TODO_DIR.glob("test_task_*.json"):
        f.unlink()
        print(f"  🗑️  Removed: {f.name}")
    
    print("✅ Cleanup complete!")

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("  DISTRIBUTED TASK SYSTEM - QUICK TEST")
    print("=" * 60)
    
    # Check if cleanup flag
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_test_files()
        sys.exit(0)
    
    # Create test tasks
    count = create_test_tasks(5)
    
    print("\n" + "=" * 60)
    print("  NEXT STEPS:")
    print("=" * 60)
    print("\n1. Open a terminal and run:")
    print("   cd C:\\Users\\justi\\BroBro\\distributed-tasks")
    print("   python worker.py")
    print("\n2. (Optional) Start worker on your desktop too!")
    print("\n3. Watch this window for completion status...")
    print("=" * 60 + "\n")
    
    # Monitor completion
    success = monitor_completion(count, timeout=120)
    
    if success:
        print("\n✅ Test PASSED! Your distributed task system is working!")
    else:
        print("\n⚠️  Test incomplete. Check that:")
        print("   - worker.py is running")
        print("   - Syncthing is connected (if testing across machines)")
    
    print("\nRun 'python test_system.py --cleanup' to remove test files")
