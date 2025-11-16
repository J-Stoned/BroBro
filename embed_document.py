#!/usr/bin/env python3
"""
Universal document embedder for GHL WHIZ knowledge base.

Supports: .txt, .md, .pdf, .docx, and other text formats
Embeds into ghl-youtube collection (same as video content)
"""

import argparse
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
from datetime import datetime
import re

# File format handlers
def read_txt(file_path):
    """Read plain text or markdown."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf(file_path):
    """Read PDF using PyPDF2."""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except ImportError:
        print("[WARN]  PyPDF2 not installed. Install with: pip install PyPDF2")
        return None

def read_docx(file_path):
    """Read Word document using python-docx."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except ImportError:
        print("[WARN]  python-docx not installed. Install with: pip install python-docx")
        return None

def detect_and_read_file(file_path):
    """Auto-detect file type and read content."""
    suffix = Path(file_path).suffix.lower()

    if suffix in ['.txt', '.md']:
        return read_txt(file_path)
    elif suffix == '.pdf':
        return read_pdf(file_path)
    elif suffix == '.docx':
        return read_docx(file_path)
    else:
        # Try reading as text
        try:
            return read_txt(file_path)
        except:
            print(f"[ERROR] Unsupported file format: {suffix}")
            return None

def clean_text(text):
    """Clean and normalize text content."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Split text into overlapping chunks.

    Same strategy as YouTube embedder for consistency.
    """
    if not text or len(text) == 0:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Only add non-empty chunks
        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - overlap

    return chunks

def embed_document(
    file_path: str,
    title: str,
    content_type: str = "business",
    collection_name: str = "ghl-youtube",
    chunk_size: int = 1000,
    overlap: int = 200
):
    """
    Embed a document into the knowledge base.

    Args:
        file_path: Path to document file
        title: Descriptive title for the content
        content_type: Type of content (business, training, case_study, script, etc.)
        collection_name: ChromaDB collection (default: ghl-youtube)
        chunk_size: Characters per chunk
        overlap: Character overlap between chunks
    """

    print(f"\n[*] Processing: {file_path}")
    print(f"[*] Title: {title}")
    print(f"[*] Type: {content_type}")

    # Read file
    content = detect_and_read_file(file_path)
    if not content:
        print("[ERROR] Failed to read file")
        return False

    print(f"[OK] Read {len(content):,} characters")

    # Clean content
    content = clean_text(content)

    # Chunk content
    chunks = chunk_text(content, chunk_size, overlap)
    if not chunks:
        print("[ERROR] No content to embed (empty file?)")
        return False

    print(f"[*]  Split into {len(chunks)} chunks")

    # Initialize embedding model (same as YouTube pipeline)
    print("[*] Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Generate embeddings
    print("[*] Generating embeddings...")
    embeddings = []
    for i, chunk in enumerate(chunks):
        if i % 10 == 0 and i > 0:
            print(f"   -> Processing chunk {i}/{len(chunks)}...")
        embedding = model.encode(chunk)
        embeddings.append(embedding.tolist())

    # Connect to ChromaDB
    print("[*] Connecting to ChromaDB...")
    client = chromadb.HttpClient(host='localhost', port=8001)

    try:
        collection = client.get_collection(collection_name)
        current_count = collection.count()
        print(f"[OK] Connected to collection: {collection_name} ({current_count} docs)")
    except Exception as e:
        print(f"[ERROR] Collection '{collection_name}' not found: {e}")
        return False

    # Generate unique IDs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_id = title.lower().replace(" ", "_").replace("/", "_")[:50]
    base_id = re.sub(r'[^a-z0-9_]', '', base_id)

    # Prepare metadata
    metadatas = []
    for i in range(len(chunks)):
        metadatas.append({
            "source": "business_content",
            "title": title,
            "type": content_type,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "file_path": str(file_path),
            "date_added": datetime.now().isoformat(),
            "content_format": "document",
            "video_id": f"doc_{base_id}"
        })

    # Add to collection in batches
    print("[*] Adding to knowledge base...")
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        end_idx = min(i + batch_size, len(chunks))

        batch_ids = [f"doc_{base_id}_{timestamp}_chunk_{j}" for j in range(i, end_idx)]
        batch_embeddings = embeddings[i:end_idx]
        batch_chunks = chunks[i:end_idx]
        batch_metadatas = metadatas[i:end_idx]

        collection.add(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_chunks,
            metadatas=batch_metadatas
        )

        if end_idx < len(chunks):
            print(f"   -> Added chunks {i+1}-{end_idx}/{len(chunks)}")

    new_count = collection.count()

    print(f"\n[OK] SUCCESS! Embedded {len(chunks)} chunks")
    print(f"   Source: {title}")
    print(f"   Type: {content_type}")
    print(f"   Collection: {collection_name}")
    print(f"   Total docs in collection: {new_count} (+{new_count - current_count})")

    return True

def main():
    parser = argparse.ArgumentParser(
        description="Embed documents into GHL WHIZ knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Embed a sales script
  python embed_document.py --file "sales_script.txt" --title "Discovery Call Framework"

  # Embed a case study PDF
  python embed_document.py --file "case_study.pdf" --title "Real Estate Agency Success Story" --type "case_study"

  # Embed a training document
  python embed_document.py --file "training.docx" --title "Agency Building Masterclass" --type "training"

  # Embed a markdown playbook
  python embed_document.py --file "playbook.md" --title "Lead Generation Playbook" --type "playbook"
        """
    )

    parser.add_argument(
        '--file',
        required=True,
        help='Path to document file (txt, md, pdf, docx)'
    )

    parser.add_argument(
        '--title',
        required=True,
        help='Descriptive title for the content'
    )

    parser.add_argument(
        '--type',
        default='business',
        help='Content type: business, training, case_study, script, playbook, framework (default: business)'
    )

    parser.add_argument(
        '--collection',
        default='ghl-youtube',
        help='ChromaDB collection name (default: ghl-youtube)'
    )

    parser.add_argument(
        '--chunk-size',
        type=int,
        default=1000,
        help='Characters per chunk (default: 1000)'
    )

    parser.add_argument(
        '--overlap',
        type=int,
        default=200,
        help='Character overlap between chunks (default: 200)'
    )

    args = parser.parse_args()

    # Validate file exists
    if not Path(args.file).exists():
        print(f"[ERROR] File not found: {args.file}")
        return 1

    # Embed the document
    success = embed_document(
        file_path=args.file,
        title=args.title,
        content_type=args.type,
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        overlap=args.overlap
    )

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
