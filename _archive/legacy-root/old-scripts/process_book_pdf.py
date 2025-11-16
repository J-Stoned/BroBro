#!/usr/bin/env python3
"""
Simple PDF Book Processor for BroBro Knowledge Base
Extracts text from PDFs and prepares them for embedding
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import PyPDF2

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    print(f"[*] Reading PDF: {pdf_path}")
    text = ""

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"[*] Total pages: {total_pages}")

            for page_num, page in enumerate(pdf_reader.pages, 1):
                if page_num % 10 == 0:
                    print(f"   -> Processing page {page_num}/{total_pages}...")
                text += page.extract_text() + "\n\n"

        print(f"[OK] Extracted {len(text)} characters")
        return text

    except Exception as e:
        print(f"[ERROR] Failed to extract PDF: {e}")
        return None

def clean_text(text):
    """Clean extracted text"""
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    cleaned = '\n'.join(lines)
    return cleaned

def save_as_json(text, title, output_path):
    """Save extracted text as JSON for embedding"""
    word_count = len(text.split())

    data = {
        "title": title,
        "type": "book",
        "author": "Russell Brunson",
        "added_date": datetime.now().isoformat(),
        "word_count": word_count,
        "entries": [
            {
                "text": text
            }
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[OK] Saved to: {output_path}")
    print(f"   Word count: {word_count:,}")
    return output_path

def main():
    if len(sys.argv) < 3:
        print("Usage: python process_book_pdf.py <pdf_path> <book_title>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    title = sys.argv[2]

    print("="*80)
    print("BroBro - PDF Book Processor")
    print("="*80)
    print(f"Book: {title}")
    print()

    # Extract text
    text = extract_pdf_text(pdf_path)
    if not text:
        print("[ERROR] Could not extract text from PDF")
        sys.exit(1)

    # Clean text
    print("[*] Cleaning text...")
    text = clean_text(text)

    # Save as JSON
    pdf_name = Path(pdf_path).stem
    output_dir = Path("data/books")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{pdf_name}.json"

    save_as_json(text, title, output_path)

    print()
    print("="*80)
    print("NEXT STEP: Embed this book into ChromaDB")
    print("="*80)
    print(f"Run:")
    print(f'python embed_document.py --file "{output_path}" --title "{title}" --type book --collection ghl-knowledge-base')
    print()

if __name__ == "__main__":
    main()
