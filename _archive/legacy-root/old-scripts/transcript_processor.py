"""
GHL Knowledge Base - Transcript Processor
Bulletproof system for adding transcripts to the KB
"""

import os
import json
from pathlib import Path

class TranscriptProcessor:
    def __init__(self, kb_root="C:/Users/justi/BroBro/ghl-universal-consultant"):
        self.kb_root = Path(kb_root)
        self.transcripts_base = self.kb_root / "references" / "transcripts"
        
    def process_transcript(self, file_path, domain=None):
        """Process a single transcript file"""
        file_path = Path(file_path)
        
        # Auto-detect domain if not provided
        if not domain:
            domain = self.detect_domain(file_path)
        
        # Create domain folder if needed
        domain_folder = self.transcripts_base / domain
        domain_folder.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        dest_file = domain_folder / file_path.name
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Saved: {dest_file}")
        return dest_file
    
    def detect_domain(self, file_path):
        """Auto-detect domain from filename"""
        filename = file_path.name.lower()
        
        if 'highlevel' in filename or 'ghl' in filename:
            return 'ghl'
        elif 'hormozi' in filename:
            return 'hormozi'
        elif 'cannabis' in filename:
            return 'cannabis'
        elif 'business' in filename or 'strategy' in filename:
            return 'business-strategy'
        elif 'marketing' in filename:
            return 'marketing'
        else:
            return 'general'
    
    def batch_process(self, folder_path):
        """Process all .txt files in folder"""
        folder = Path(folder_path)
        txt_files = list(folder.glob("*.txt"))
        
        print(f"Found {len(txt_files)} files")
        
        for txt_file in txt_files:
            try:
                self.process_transcript(txt_file)
            except Exception as e:
                print(f"❌ Failed: {txt_file.name} - {e}")

if __name__ == "__main__":
    processor = TranscriptProcessor()
    # processor.batch_process("C:/path/to/transcripts")
