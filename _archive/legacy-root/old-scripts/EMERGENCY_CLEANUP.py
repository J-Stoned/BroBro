#!/usr/bin/env python3
"""
EMERGENCY CLEANUP SCRIPT - Clear Corrupted localStorage Data
Run this to completely reset the BroBro chat state
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

def clear_chrome_localStorage():
    """Clear localStorage from Chrome's Local State database"""
    
    chrome_data_dir = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default"
    
    print(f"🔍 Checking Chrome data directory: {chrome_data_dir}")
    
    if not chrome_data_dir.exists():
        print("❌ Chrome data directory not found")
        return False
    
    # Try to find and clear IndexedDB data
    indexeddb_path = chrome_data_dir / "IndexedDB" / "https_localhost_3000_0.indexeddb.leveldb"
    
    if indexeddb_path.exists():
        print(f"🗑️  Found IndexedDB data at: {indexeddb_path}")
        print("   (Cannot directly delete, but close Chrome first to ensure clean removal)")
    
    return True

def clear_localStorage_data():
    """Create a clearing script to run in browser console"""
    
    script = """
// ============================================================
// PASTE THIS INTO YOUR BROWSER CONSOLE (F12 -> Console tab)
// ============================================================

console.log('🧹 BroBro Emergency Cleanup Starting...');

// Step 1: Clear all ghl-wiz related localStorage items
const keysToRemove = [
  'ghl-wiz-conversation',
  'ghl-wiz-history',
  'ghl-wiz-settings',
  'ghl-wiz-cache'
];

let cleared = 0;
keysToRemove.forEach(key => {
  if (localStorage.getItem(key)) {
    localStorage.removeItem(key);
    console.log(`✅ Cleared: ${key}`);
    cleared++;
  }
});

// Step 2: Clear sessionStorage too
sessionStorage.clear();
console.log('✅ Cleared sessionStorage');

// Step 3: Clear IndexedDB (if accessible)
console.log('🔄 Clearing IndexedDB...');
const dbRequest = indexedDB.databases ? await indexedDB.databases() : [];
for (const db of dbRequest) {
  indexedDB.deleteDatabase(db.name);
  console.log(`✅ Deleted IndexedDB: ${db.name}`);
}

console.log(`\n✅ Cleanup Complete!`);
console.log(`   - Cleared ${cleared} localStorage items`);
console.log(`   - Cleared sessionStorage`);
console.log('🔄 Refreshing page...');

// Wait 1 second then refresh
setTimeout(() => {
  window.location.reload();
}, 1000);
"""
    
    return script

def main():
    print("=" * 60)
    print("BroBro EMERGENCY CLEANUP")
    print("=" * 60)
    print()
    
    print("📋 STEPS TO CLEAN UP:")
    print()
    print("1️⃣  CLOSE CHROME COMPLETELY")
    print("   - Make sure no Chrome windows are open")
    print()
    print("2️⃣  OPEN YOUR BROWSER CONSOLE")
    print("   - Open BroBro in Chrome")
    print("   - Press F12 to open Developer Tools")
    print("   - Click the 'Console' tab")
    print()
    print("3️⃣  RUN THE CLEANUP SCRIPT")
    print("   - Copy the script below")
    print("   - Paste it into the console")
    print("   - Press Enter")
    print()
    print("=" * 60)
    print("CONSOLE SCRIPT (Copy everything below):")
    print("=" * 60)
    print()
    
    script = clear_localStorage_data()
    print(script)
    
    print()
    print("=" * 60)
    print("WHAT THIS DOES:")
    print("=" * 60)
    print("✅ Clears all ghl-wiz localStorage items")
    print("✅ Clears sessionStorage")
    print("✅ Clears IndexedDB data")
    print("✅ Refreshes the page with clean state")
    print()
    print("After cleanup:")
    print("- You can start fresh with the chat")
    print("- No corrupted data will be loaded")
    print("- The chat should work normally")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
