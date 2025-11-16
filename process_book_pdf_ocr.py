#!/usr/bin/env python3
"""
OCR-Enabled PDF Book Processor for BroBro Knowledge Base
Extracts text from image-based PDFs using Tesseract OCR
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Set Tesseract path (update this after installing Tesseract)
# Default Windows installation path:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_pdf_text_with_ocr(pdf_path, max_pages=None):
    """Extract text from PDF using OCR"""
    print(f"[*] Reading PDF with OCR: {pdf_path}")
    print(f"[*] This may take several minutes for large files...")
    text = ""

    try:
        # Convert PDF pages to images
        print(f"[*] Converting PDF to images...")
        images = convert_from_path(pdf_path, dpi=300)
        total_pages = len(images) if not max_pages else min(len(images), max_pages)

        print(f"[*] Total pages to process: {total_pages}")
        print(f"[*] Starting OCR extraction...")

        for page_num, image in enumerate(images[:total_pages], 1):
            if page_num % 10 == 0:
                print(f"   -> Processing page {page_num}/{total_pages}...")

            # Extract text from image using OCR
            page_text = pytesseract.image_to_string(image, lang='eng')
            text += page_text + "\n\n"

        print(f"[OK] Extracted {len(text)} characters")
        return text

    except FileNotFoundError as e:
        if 'tesseract' in str(e).lower():
            print(f"[ERROR] Tesseract not found!")
            print(f"")
            print(f"Please install Tesseract OCR:")
            print(f"1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            print(f"2. Run the installer")
            print(f"3. Note the installation path")
            print(f"4. Update line 17 in this script with your path")
            print(f"")
            print(f"Current path set to: {pytesseract.pytesseract.tesseract_cmd}")
        else:
            print(f"[ERROR] Failed to read PDF: {e}")
        return None

    except Exception as e:
        print(f"[ERROR] Failed to extract PDF with OCR: {e}")
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
        "author": "Unknown",
        "added_date": datetime.now().isoformat(),
        "word_count": word_count,
        "extraction_method": "OCR",
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
        print("Usage: python process_book_pdf_ocr.py <pdf_path> <book_title> [max_pages]")
        print("")
        print("Example:")
        print('python process_book_pdf_ocr.py "book.pdf" "Book Title" 50')
        print("")
        print("Note: OCR is SLOW. A 331-page book may take 30-60 minutes!")
        sys.exit(1)

    pdf_path = sys.argv[1]
    title = sys.argv[2]
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else None

    print("="*80)
    print("BroBro - OCR PDF Book Processor")
    print("="*80)
    print(f"Book: {title}")
    if max_pages:
        print(f"Max pages: {max_pages}")
    print()
    print("[WARNING] OCR extraction is SLOW!")
    print("[WARNING] Large PDFs (300+ pages) may take 30-60 minutes")
    print()

    # Extract text with OCR
    text = extract_pdf_text_with_ocr(pdf_path, max_pages)
    if not text:
        print("[ERROR] Could not extract text from PDF")
        sys.exit(1)

    if len(text.strip()) < 100:
        print(f"[WARNING] Very little text extracted ({len(text)} chars)")
        print(f"[WARNING] This may not be a valid book or OCR failed")

    # Clean text
    print("[*] Cleaning text...")
    text = clean_text(text)

    # Save as JSON
    pdf_name = Path(pdf_path).stem
    output_dir = Path("data/books")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{pdf_name}_ocr.json"

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
