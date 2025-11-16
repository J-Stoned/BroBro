#!/usr/bin/env python3
"""
PDF Book Processor using pdfplumber for BroBro Knowledge Base
Better at extracting text from complex PDFs than PyPDF2
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import pdfplumber

def extract_pdf_text_plumber(pdf_path):
    """Extract text from PDF using pdfplumber"""
    print(f"[*] Reading PDF with pdfplumber: {pdf_path}")
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"[*] Total pages: {total_pages}")

            for page_num, page in enumerate(pdf.pages, 1):
                if page_num % 10 == 0:
                    print(f"   -> Processing page {page_num}/{total_pages}...")

                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

        print(f"[OK] Extracted {len(text)} characters")
        return text

    except Exception as e:
        print(f"[ERROR] Failed to extract PDF: {e}")
        return None

def clean_text(text):
    """Clean extracted text"""
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
        "author": "Alex Hormozi",
        "added_date": datetime.now().isoformat(),
        "word_count": word_count,
        "extraction_method": "pdfplumber",
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
        print("Usage: python process_book_pdf_plumber.py <pdf_path> <book_title>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    title = sys.argv[2]

    print("="*80)
    print("BroBro - PDF Book Processor (pdfplumber)")
    print("="*80)
    print(f"Book: {title}")
    print()

    # Extract text
    text = extract_pdf_text_plumber(pdf_path)
    if not text:
        print("[ERROR] Could not extract text from PDF")
        sys.exit(1)

    if len(text.strip()) < 100:
        print(f"[WARNING] Very little text extracted ({len(text)} chars)")
        print(f"[WARNING] This PDF may be image-based and require OCR")
        sys.exit(1)

    # Clean text
    print("[*] Cleaning text...")
    text = clean_text(text)

    # Save as JSON
    pdf_name = Path(pdf_path).stem
    output_dir = Path("data/books")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{pdf_name}_plumber.json"

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
