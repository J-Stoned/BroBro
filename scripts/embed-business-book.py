"""
BroBro - Large Business Book Embedder
Optimized for large PDFs with intelligent chunking, chapter detection, and page tracking

Usage: python embed-business-book.py <pdf_path> --title "Book Title" [--author "Author"] [--category "Category"]
"""

import sys
import os
import re
from typing import List, Dict, Optional, Tuple
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import hashlib

# PDF support
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[ERROR] PyPDF2 not installed. Install with: pip install PyPDF2")
    sys.exit(1)


class LargeBookEmbedder:
    """Embeds large business books with intelligent chunking and indexing"""

    def __init__(self):
        """Initialize the embedder"""
        print("\n" + "="*70)
        print("BroBro Large Business Book Embedder")
        print("="*70)
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

    def extract_pdf_with_pages(self, pdf_path: str) -> List[Dict[str, any]]:
        """Extract text from PDF with page numbers"""
        print(f"\n>> Extracting PDF content...")

        pages_data = []
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"   Total pages: {total_pages}")

            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                pages_data.append({
                    'page_number': page_num + 1,
                    'text': text,
                    'word_count': len(text.split())
                })

                # Progress indicator
                if (page_num + 1) % 25 == 0 or page_num == 0:
                    print(f"   >> Processed {page_num + 1}/{total_pages} pages...")

        print(f"   [OK] Extracted {total_pages} pages")
        return pages_data

    def detect_chapters(self, pages_data: List[Dict]) -> List[Dict]:
        """Detect chapter boundaries using heuristics"""
        print(f"\n>> Detecting chapter structure...")

        chapter_patterns = [
            r'^Chapter\s+\d+',
            r'^CHAPTER\s+\d+',
            r'^\d+\.\s+[A-Z]',
            r'^Part\s+\d+',
            r'^Section\s+\d+',
        ]

        chapters = []
        current_chapter = None

        for page in pages_data:
            text = page['text'].strip()
            lines = text.split('\n')

            # Check first few lines for chapter markers
            for line in lines[:5]:
                line = line.strip()
                if len(line) > 0:
                    for pattern in chapter_patterns:
                        if re.match(pattern, line, re.IGNORECASE):
                            # Found a chapter!
                            if current_chapter:
                                chapters.append(current_chapter)

                            current_chapter = {
                                'title': line[:100],  # Limit title length
                                'start_page': page['page_number'],
                                'pages': [page]
                            }
                            break

                    if current_chapter and current_chapter['start_page'] == page['page_number']:
                        break

            # Add page to current chapter or create default
            if current_chapter and current_chapter['start_page'] <= page['page_number']:
                if page['page_number'] != current_chapter['start_page']:
                    current_chapter['pages'].append(page)
            elif not current_chapter:
                # No chapter detected yet, create default
                current_chapter = {
                    'title': 'Introduction',
                    'start_page': page['page_number'],
                    'pages': [page]
                }

        # Add final chapter
        if current_chapter:
            chapters.append(current_chapter)

        # If no chapters detected, treat whole book as one section
        if len(chapters) == 0:
            all_pages = pages_data
            chapters.append({
                'title': 'Full Book',
                'start_page': 1,
                'pages': all_pages
            })

        print(f"   [OK] Detected {len(chapters)} chapters/sections")
        for i, chapter in enumerate(chapters[:5]):  # Show first 5
            print(f"      - {chapter['title']} (Page {chapter['start_page']}, {len(chapter['pages'])} pages)")
        if len(chapters) > 5:
            print(f"      ... and {len(chapters) - 5} more")

        return chapters

    def smart_chunk_chapter(self, chapter: Dict, target_words: int = 800, max_words: int = 1200) -> List[Dict]:
        """Intelligently chunk a chapter based on semantic boundaries"""

        # Combine all page text
        full_text = "\n\n".join([page['text'] for page in chapter['pages']])

        # Clean up text
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        # Split into paragraphs (natural semantic boundaries)
        paragraphs = [p.strip() for p in full_text.split('\n') if len(p.strip()) > 50]

        chunks = []
        current_chunk = []
        current_word_count = 0
        current_start_page = chapter['start_page']
        page_idx = 0

        for para in paragraphs:
            para_words = len(para.split())

            # If adding this paragraph exceeds max, save current chunk
            if current_word_count + para_words > max_words and current_word_count > 0:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'start_page': current_start_page,
                    'word_count': current_word_count,
                    'chapter': chapter['title']
                })

                # Start new chunk with overlap (last paragraph)
                current_chunk = [current_chunk[-1]] if len(current_chunk) > 0 else []
                current_word_count = len(current_chunk[0].split()) if len(current_chunk) > 0 else 0

                # Update page tracking
                if page_idx < len(chapter['pages']) - 1:
                    page_idx += 1
                    current_start_page = chapter['pages'][page_idx]['page_number']

            current_chunk.append(para)
            current_word_count += para_words

            # If we've reached target size and have good content, consider breaking
            if current_word_count >= target_words:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'start_page': current_start_page,
                    'word_count': current_word_count,
                    'chapter': chapter['title']
                })
                current_chunk = []
                current_word_count = 0

        # Add remaining content
        if len(current_chunk) > 0:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'start_page': current_start_page,
                'word_count': current_word_count,
                'chapter': chapter['title']
            })

        return chunks

    def embed_book(self, pdf_path: str, title: str, author: Optional[str] = None,
                   category: Optional[str] = None, isbn: Optional[str] = None):
        """Embed a large business book with intelligent chunking"""

        if not os.path.exists(pdf_path):
            print(f"[ERROR] File not found: {pdf_path}")
            return False

        file_name = Path(pdf_path).name

        print(f"\n{'='*70}")
        print(f"BOOK: {title}")
        if author:
            print(f"AUTHOR: {author}")
        print(f"FILE: {file_name}")
        print(f"{'='*70}")

        # Generate unique book ID
        book_hash = hashlib.md5(f"{title}_{author}".encode()).hexdigest()[:8]
        book_id = f"book_{book_hash}"

        # Step 1: Extract PDF with page tracking
        pages_data = self.extract_pdf_with_pages(pdf_path)

        # Calculate total words
        total_words = sum([page['word_count'] for page in pages_data])
        print(f"\n>> Book Statistics:")
        print(f"   Total pages: {len(pages_data)}")
        print(f"   Total words: {total_words:,}")
        print(f"   Avg words/page: {total_words // len(pages_data)}")

        # Step 2: Detect chapters
        chapters = self.detect_chapters(pages_data)

        # Step 3: Smart chunking
        print(f"\n>> Creating intelligent chunks...")
        all_chunks = []

        for chapter in chapters:
            chapter_chunks = self.smart_chunk_chapter(chapter)
            all_chunks.extend(chapter_chunks)

        print(f"   [OK] Created {len(all_chunks)} chunks")
        print(f"   Avg chunk size: {sum([c['word_count'] for c in all_chunks]) // len(all_chunks)} words")

        # Step 4: Embed chunks
        print(f"\n>> Embedding chunks into ChromaDB...")
        added_count = 0
        failed_count = 0

        for idx, chunk in enumerate(all_chunks):
            try:
                embedding = self.model.encode(chunk['text']).tolist()
                doc_id = f"{book_id}_chunk_{idx}"

                metadata = {
                    'source': 'business_book',
                    'type': 'pdf_book',
                    'title': title,
                    'chapter': chunk['chapter'],
                    'page_number': chunk['start_page'],
                    'chunk_index': idx,
                    'total_chunks': len(all_chunks),
                    'word_count': chunk['word_count'],
                    'book_id': book_id
                }

                # Add optional metadata
                if author:
                    metadata['author'] = author
                if category:
                    metadata['category'] = category
                if isbn:
                    metadata['isbn'] = isbn

                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    documents=[chunk['text']],
                    metadatas=[metadata]
                )
                added_count += 1

                # Progress indicator
                if (idx + 1) % 20 == 0 or idx == 0:
                    print(f"   >> Embedded {idx + 1}/{len(all_chunks)} chunks...")

            except Exception as e:
                print(f"   [ERROR] Failed to embed chunk {idx}: {e}")
                failed_count += 1

        print(f"\n{'='*70}")
        print(f"[OK] Book embedding complete!")
        print(f"{'='*70}")
        print(f"   Successfully embedded: {added_count}/{len(all_chunks)} chunks")
        if failed_count > 0:
            print(f"   Failed: {failed_count} chunks")

        final_count = self.collection.count()
        print(f"   Collection now has: {final_count} total documents")
        print(f"{'='*70}\n")

        return True


def main():
    if len(sys.argv) < 3:
        print("\nUsage: python embed-business-book.py <pdf_path> --title \"Book Title\" [OPTIONS]")
        print("\nRequired:")
        print("  --title \"Book Title\"     The title of the book")
        print("\nOptional:")
        print("  --author \"Author Name\"   Book author")
        print("  --category \"Category\"    Business category (e.g., 'Marketing', 'Leadership')")
        print("  --isbn \"ISBN\"            ISBN number")
        print("\nExamples:")
        print("  python embed-business-book.py book.pdf --title \"The Lean Startup\"")
        print("  python embed-business-book.py book.pdf --title \"Traction\" --author \"Gabriel Weinberg\"")
        print("  python embed-business-book.py book.pdf --title \"$100M Offers\" --author \"Alex Hormozi\" --category \"Sales\"")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Parse arguments
    title = None
    author = None
    category = None
    isbn = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--title' and i + 1 < len(sys.argv):
            title = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--author' and i + 1 < len(sys.argv):
            author = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--category' and i + 1 < len(sys.argv):
            category = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--isbn' and i + 1 < len(sys.argv):
            isbn = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if not title:
        print("[ERROR] --title is required")
        sys.exit(1)

    embedder = LargeBookEmbedder()
    embedder.embed_book(pdf_path, title=title, author=author, category=category, isbn=isbn)


if __name__ == "__main__":
    main()
