#!/usr/bin/env python3
"""
Batch PDF extraction script for Hormozi books.
Extracts all 5 books and saves as structured text files ready for Google File Search upload.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import pdfplumber

# Define books to process
BOOKS = {
    "100M-Offers.pdf": "100M Offers: How To Create Irresistible Business Offers",
    "100M-Leads.pdf": "100M Leads: How To Get Strangers To Want To Buy Your Stuff",
    "100M-Money-Models.pdf": "100M Money Models: How To Design Your Business",
    "100M-Ads.pdf": "100M Ads: How To Get Customers Cheaply",
    "100M-Playbook-Lead-Nurture.pdf": "100M Playbook: Lead Nurturing Framework",
}

def extract_pdf_text(pdf_path):
    """Extract text from PDF using pdfplumber"""
    print(f"\n[*] Extracting: {pdf_path.name}")
    text = ""

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            total_pages = len(pdf.pages)
            print(f"    Pages: {total_pages}")

            for page_num, page in enumerate(pdf.pages, 1):
                if page_num % 20 == 0:
                    print(f"    Processing page {page_num}/{total_pages}...")

                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n[Page {page_num}]\n{page_text}\n"
                except Exception as e:
                    print(f"    Warning: Could not extract page {page_num}: {e}")
                    continue

        print(f"    [OK] Extracted {len(text):,} characters from {total_pages} pages")
        return text

    except Exception as e:
        print(f"    [ERROR] Failed to extract PDF: {e}")
        return None

def clean_text(text):
    """Clean extracted text"""
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    cleaned = '\n'.join(lines)
    return cleaned

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks"""
    if not text or len(text) == 0:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - overlap

    return chunks

def save_as_text(text, title, output_path):
    """Save extracted text as plain text file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"Extracted: {datetime.now().isoformat()}\n")
        f.write(f"Word count: {len(text.split()):,}\n")
        f.write("=" * 80 + "\n\n")
        f.write(text)

    word_count = len(text.split())
    print(f"    [OK] Saved {len(text):,} characters ({word_count:,} words)")
    return output_path

def main():
    """Process all Hormozi books"""

    print("=" * 80)
    print("BroBro - Hormozi Books Batch Extractor")
    print("=" * 80)

    kb_path = Path(__file__).parent / "kb" / "business-playbooks"
    output_dir = kb_path / "extracted"
    output_dir.mkdir(exist_ok=True)

    results = []

    for filename, title in BOOKS.items():
        pdf_path = kb_path / filename

        if not pdf_path.exists():
            print(f"\n[SKIP] File not found: {pdf_path}")
            continue

        # Extract text
        text = extract_pdf_text(pdf_path)
        if not text or len(text.strip()) < 500:
            print(f"[ERROR] Insufficient content extracted")
            continue

        # Clean text
        print(f"    Cleaning text...")
        text = clean_text(text)

        # Chunk text
        chunks = chunk_text(text, chunk_size=1000, overlap=200)
        print(f"    Chunks created: {len(chunks)}")

        # Save as text file
        output_filename = Path(filename).stem + "_extracted.txt"
        output_path = output_dir / output_filename
        save_as_text(text, title, output_path)

        results.append({
            "filename": filename,
            "title": title,
            "output_file": str(output_path.relative_to(Path(__file__).parent)),
            "characters": len(text),
            "words": len(text.split()),
            "chunks": len(chunks),
            "status": "success"
        })

    # Save summary
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "books_processed": len(results),
        "output_directory": str(output_dir.relative_to(Path(__file__).parent)),
        "results": results
    }

    summary_path = output_dir / "extraction_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    total_chars = sum(r.get('characters', 0) for r in results)
    total_words = sum(r.get('words', 0) for r in results)
    total_chunks = sum(r.get('chunks', 0) for r in results)

    print(f"\nProcessed: {len(results)} books")
    print(f"Total characters: {total_chars:,}")
    print(f"Total words: {total_words:,}")
    print(f"Total chunks: {total_chunks:,}")
    print(f"Output directory: {output_dir}")
    print(f"Summary saved to: {summary_path}")

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Review extracted files in kb/business-playbooks/extracted/")
    print("2. Update google_file_search_upload.py to include extracted/ directory")
    print("3. Run: python google_file_search_upload.py")
    print("4. Wait 30-60 minutes for Google to index")
    print()

if __name__ == "__main__":
    main()
