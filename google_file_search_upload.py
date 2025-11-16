#!/usr/bin/env python3
"""
Google File Search - Complete BroBro Knowledge Base Upload
Uploads ALL content: docs, books, snapshots, transcripts, best practices
"""

import os
import time
from pathlib import Path
from google import genai
from google.genai import types

# Configuration - ALL content directories
CONTENT_PATHS = [
    # BroBro Knowledge Base
    Path(r"C:\Users\justi\BroBro\kb\ghl-docs"),
    Path(r"C:\Users\justi\BroBro\kb\youtube-transcripts"),
    Path(r"C:\Users\justi\BroBro\kb\best-practices"),
    Path(r"C:\Users\justi\BroBro\kb\business-playbooks"),
    Path(r"C:\Users\justi\BroBro\kb\business-playbooks\extracted"),  # Extracted Hormozi books
    Path(r"C:\Users\justi\BroBro\kb\snapshots-reference"),
    Path(r"C:\Users\justi\BroBro\kb\cannabis-tissue-culture"),  # UPGRADED: Full TC research (16MB, 30+ papers)
    Path(r"C:\Users\justi\BroBro\kb\tissue-culture-papers"),  # Legacy: metadata stubs
    Path(r"C:\Users\justi\BroBro\knowledge-base\books"),
    Path(r"C:\Users\justi\BroBro\knowledge-base\transcripts"),
    Path(r"C:\Users\justi\BroBro\data\books"),
    Path(r"C:\Users\justi\BroBro\data\snapshots"),
    Path(r"C:\Users\justi\BroBro\data\youtube-tutorials"),
    Path(r"C:\Users\justi\BroBro\data\best-practices"),
    Path(r"C:\Users\justi\BroBro\data\manual-transcripts"),
    
    # Extracted Business Books (Hormozi, Brunson, Cialdini)
    Path(r"C:\Users\justi\Downloads\extracted_books"),
    
    # GHL Universal Consultant Skill (if accessible)
    Path(r"C:\Users\justi\BroBro\ghl-universal-consultant\references"),
]

STORE_NAME = "ghl-wiz-complete-kb"
SUPPORTED_EXTENSIONS = {'.txt', '.md', '.pdf', '.json', '.html', '.csv'}

# Rate limiting
DELAY_BETWEEN_UPLOADS = 1.5  # seconds
MAX_RETRIES = 3

def count_all_files():
    """Count total files across all directories"""
    count = 0
    seen_files = set()
    
    for base_path in CONTENT_PATHS:
        if not base_path.exists():
            continue
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in ['processed', '__pycache__', 'node_modules']]
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    if str(file_path) not in seen_files:
                        seen_files.add(str(file_path))
                        count += 1
    return count, seen_files


def get_category_from_path(file_path):
    """Extract category from file path for better organization"""
    path_str = str(file_path).lower()

    if 'cannabis-tissue' in path_str or 'cannabis tissue' in path_str:
        return 'cannabis-tissue-culture'
    elif 'tissue' in path_str or 'micropropagation' in path_str or 'cryopreservation' in path_str:
        return 'tissue-culture'
    elif 'hormozi' in path_str or '100m' in path_str:
        return 'hormozi-playbooks'
    elif 'brunson' in path_str:
        return 'brunson-books'
    elif 'cialdini' in path_str or 'cashvertising' in path_str:
        return 'marketing-psychology'
    elif 'ghl-docs' in path_str:
        return 'ghl-official-docs'
    elif 'youtube' in path_str or 'transcript' in path_str:
        return 'youtube-tutorials'
    elif 'best-practices' in path_str:
        return 'best-practices'
    elif 'snapshot' in path_str:
        return 'marketplace-snapshots'
    elif 'book' in path_str:
        return 'business-books'
    elif 'gohighlevel' in path_str or 'ghl' in path_str:
        return 'ghl-training'
    else:
        return 'general'

def upload_all_documents():
    """Main upload function"""
    print("=" * 70)
    print("  GOOGLE FILE SEARCH - BroBro COMPLETE KNOWLEDGE BASE UPLOAD")
    print("=" * 70)
    
    # Initialize client
    print("\nInitializing Google GenAI client...")
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')

    if not api_key:
        print("✗ ERROR: No API key found!")
        print("\nSet your API key with:")
        print('  PowerShell: $env:GOOGLE_API_KEY = "your-key"')
        print("  Or add to .env file")
        return False

    client = genai.Client(api_key=api_key)
    print("✓ Connected to Google GenAI API")
    
    # Count files first
    print("\nScanning all content directories...")
    total_files, all_files = count_all_files()
    print(f"✓ Found {total_files} unique files to upload")
    
    # Show breakdown by directory
    print("\nContent breakdown:")
    for base_path in CONTENT_PATHS:
        if base_path.exists():
            count = sum(1 for f in all_files if str(base_path) in f)
            if count > 0:
                print(f"  • {base_path.name}: {count} files")
    
    # Create the File Search store
    print(f"\nCreating File Search store: {STORE_NAME}")
    file_search_store = client.file_search_stores.create(
        config={'display_name': STORE_NAME}
    )
    store_id = file_search_store.name
    print(f"✓ Created store: {store_id}")
    
    # Track progress
    uploaded = 0
    failed = []
    skipped = 0
    
    # Process all files
    print("\n" + "=" * 70)
    print("  STARTING UPLOAD PROCESS")
    print("=" * 70)
    
    processed_files = set()
    
    for file_path_str in sorted(all_files):
        file_path = Path(file_path_str)
        
        # Skip if already processed (deduplication)
        if file_path_str in processed_files:
            skipped += 1
            continue
        processed_files.add(file_path_str)
        
        # Skip files larger than 100MB
        try:
            file_size = file_path.stat().st_size
            if file_size > 100 * 1024 * 1024:
                print(f"\n⚠ Skipping (>100MB): {file_path.name}")
                skipped += 1
                continue
        except:
            pass
        
        # Create display name with category
        category = get_category_from_path(file_path)
        display_name = f"{category}/{file_path.stem}"[:100]
        
        print(f"\n[{uploaded + 1}/{total_files}] {category}/{file_path.name}")
        
        # Retry logic
        success = False
        for attempt in range(MAX_RETRIES):
            try:
                operation = client.file_search_stores.upload_to_file_search_store(
                    file=str(file_path),
                    file_search_store_name=store_id,
                    config={
                        'display_name': display_name,
                    }
                )
                uploaded += 1
                success = True
                print(f"  ✓ Uploaded")
                break
                
            except Exception as e:
                error_msg = str(e)
                if attempt < MAX_RETRIES - 1:
                    print(f"  ⚠ Retry {attempt + 1}: {error_msg[:60]}")
                    time.sleep(3)
                else:
                    print(f"  ✗ Failed: {error_msg[:80]}")
                    failed.append((str(file_path), error_msg))
        
        # Rate limiting to avoid API limits
        if success:
            time.sleep(DELAY_BETWEEN_UPLOADS)
    
    # Final summary
    print("\n" + "=" * 70)
    print("  UPLOAD COMPLETE")
    print("=" * 70)
    print(f"✓ Successfully uploaded: {uploaded}")
    print(f"⚠ Skipped: {skipped}")
    print(f"✗ Failed: {len(failed)}")
    print(f"\n📦 Store ID: {store_id}")
    print(f"📛 Store Name: {STORE_NAME}")
    
    if failed:
        print(f"\nFailed uploads (showing first 10):")
        for path, error in failed[:10]:
            print(f"  • {Path(path).name}")
            print(f"    Error: {error[:100]}")
    
    # Save store info for future reference
    info_file = Path(r"C:\Users\justi\BroBro\GOOGLE_FILE_SEARCH_STORE.txt")
    with open(info_file, 'w') as f:
        f.write("GOOGLE FILE SEARCH - BroBro KNOWLEDGE BASE\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Store ID: {store_id}\n")
        f.write(f"Display Name: {STORE_NAME}\n")
        f.write(f"Total Documents Uploaded: {uploaded}\n")
        f.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("USE IN CODE:\n")
        f.write("-" * 50 + "\n")
        f.write(f'''
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your question about GHL here",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=["{store_id}"]
                )
            )
        ]
    )
)

print(response.text)
''')
    
    print(f"\n✓ Store info saved to: {info_file}")
    print("\n⏳ Note: Google will index your documents in the background.")
    print("   This may take 30-60 minutes. You can start querying immediately,")
    print("   but results will improve as indexing completes.")
    
    return store_id


if __name__ == "__main__":
    print("\n🚀 BroBro Knowledge Base → Google File Search\n")
    
    # Check for API key
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ ERROR: No API key found!")
        print("\nSet your API key first:")
        print("  PowerShell: $env:GOOGLE_API_KEY = 'your-key-here'")
        print("  Or set GEMINI_API_KEY environment variable")
        exit(1)
    
    print(f"✓ API key found: {api_key[:10]}...")
    
    # Confirm before starting
    total, _ = count_all_files()
    print(f"\nThis will upload {total} documents to Google File Search.")
    print("Estimated time: {:.0f}-{:.0f} minutes".format(total * 2 / 60, total * 3 / 60))
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        exit(0)
    
    try:
        store_id = upload_all_documents()
        print(f"\n🎉 SUCCESS! Your knowledge base is now in Google File Search!")
        print(f"Store ID: {store_id}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
