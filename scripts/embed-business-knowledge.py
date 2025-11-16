"""
BroBro - Business Knowledge Embedder
Supports: YouTube transcripts, PDF books, Word docs, text files, markdown

Usage: python embed-business-knowledge.py <file_path> [--title "Custom Title"] [--url "Source URL"]
"""

import sys
import os
import re
from typing import List, Dict, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

# PDF support
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[WARNING] PyPDF2 not installed. Install with: pip install PyPDF2")

# Word document support
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("[WARNING] python-docx not installed. Install with: pip install python-docx")


class BusinessKnowledgeEmbedder:
    """Embeds various document types into ChromaDB for business knowledge"""

    def __init__(self):
        """Initialize the embedder"""
        print("\n" + "="*60)
        print("BroBro Business Knowledge Embedder")
        print("="*60)
        print(">> Initializing embedder...")
        print(">> Loading embedding model: all-MiniLM-L6-v2")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        chroma_client = chromadb.HttpClient(host='localhost', port=8001)

        try:
            self.collection = chroma_client.get_collection(name="ghl-business")
            doc_count = self.collection.count()
            print(f">> Connected to existing collection: ghl-business")
            print(f"   Current document count: {doc_count}")
        except:
            self.collection = chroma_client.create_collection(
                name="ghl-business",
                metadata={"description": "Business knowledge: books, docs, articles, transcripts"}
            )
            print(">> Created new collection: ghl-business")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            raise Exception("PyPDF2 not installed. Run: pip install PyPDF2")

        print(f"   >> Extracting text from PDF...")
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"      Total pages: {total_pages}")

            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
                if (page_num + 1) % 10 == 0:
                    print(f"      Processed {page_num + 1}/{total_pages} pages...")

        return text

    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extract text from Word document"""
        if not DOCX_AVAILABLE:
            raise Exception("python-docx not installed. Run: pip install python-docx")

        print(f"   >> Extracting text from Word document...")
        doc = docx.Document(docx_path)
        text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text

    def extract_text_from_txt(self, txt_path: str) -> str:
        """Extract text from text/markdown file"""
        print(f"   >> Reading text file...")
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read()

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks with overlap for better context"""
        # Clean up text
        text = re.sub(r'\s+', ' ', text).strip()

        words = text.split()
        chunks = []

        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)

            if end >= len(words):
                break
            start = end - overlap

        return chunks

    def detect_file_type(self, file_path: str) -> str:
        """Detect file type from extension"""
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.docx', '.doc']:
            return 'docx'
        elif ext in ['.txt', '.md']:
            return 'text'
        else:
            raise Exception(f"Unsupported file type: {ext}")

    def embed_document(self, file_path: str, title: Optional[str] = None, url: Optional[str] = None):
        """Embed any supported document type into ChromaDB"""

        if not os.path.exists(file_path):
            print(f"[ERROR] File not found: {file_path}")
            return False

        # Detect file type
        file_type = self.detect_file_type(file_path)
        file_name = Path(file_path).name

        # Use filename as title if not provided
        if title is None:
            title = Path(file_path).stem.replace('_', ' ').replace('-', ' ')

        print(f"\n>> Processing: {title}")
        print(f"   File: {file_name}")
        print(f"   Type: {file_type.upper()}")

        # Extract text based on file type
        try:
            if file_type == 'pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_type == 'docx':
                text = self.extract_text_from_docx(file_path)
            elif file_type == 'text':
                text = self.extract_text_from_txt(file_path)
            else:
                print(f"[ERROR] Unsupported file type: {file_type}")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to extract text: {e}")
            return False

        print(f"   Extracted text length: {len(text)} characters")

        # Chunk the text
        chunks = self.chunk_text(text)
        print(f"   >> Split into {len(chunks)} chunks")

        # Create unique document ID
        safe_filename = re.sub(r'[^a-zA-Z0-9]', '_', file_name)
        doc_id_base = f"business_{safe_filename}"

        # Embed each chunk
        added_count = 0
        for idx, chunk in enumerate(chunks):
            try:
                embedding = self.model.encode(chunk).tolist()
                doc_id = f"{doc_id_base}_chunk_{idx}"

                metadata = {
                    'source': 'business_knowledge',
                    'file_type': file_type,
                    'file_name': file_name,
                    'title': title,
                    'chunk_index': idx,
                    'total_chunks': len(chunks),
                    'type': f'{file_type}_document'
                }

                # Add URL if provided
                if url:
                    metadata['url'] = url

                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[metadata]
                )
                added_count += 1
            except Exception as e:
                print(f"   [ERROR] Error embedding chunk {idx}: {e}")

        print(f"   [OK] Added {added_count}/{len(chunks)} chunks to database")
        final_count = self.collection.count()
        print(f"\n   Collection now has {final_count} total documents")
        print("="*60)
        print("[OK] Document successfully embedded!")
        print("="*60 + "\n")
        return True


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python embed-business-knowledge.py <file_path> [--title \"Title\"] [--url \"URL\"]")
        print("\nSupported formats:")
        print("  - PDF files (.pdf)")
        print("  - Word documents (.docx, .doc)")
        print("  - Text files (.txt)")
        print("  - Markdown files (.md)")
        print("\nExamples:")
        print("  python embed-business-knowledge.py book.pdf")
        print("  python embed-business-knowledge.py notes.docx --title \"Business Strategy\"")
        print("  python embed-business-knowledge.py article.txt --url \"https://example.com/article\"")
        sys.exit(1)

    file_path = sys.argv[1]

    # Parse optional arguments
    title = None
    url = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--title' and i + 1 < len(sys.argv):
            title = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--url' and i + 1 < len(sys.argv):
            url = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    embedder = BusinessKnowledgeEmbedder()
    embedder.embed_document(file_path, title=title, url=url)


if __name__ == "__main__":
    main()
