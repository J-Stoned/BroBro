#!/usr/bin/env python3
"""
BroBro - Documentation Embedding Script
Generates embeddings for scraped GHL documentation and indexes in ChromaDB
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class GHLDocsEmbedder:
    """Embeds GHL documentation into ChromaDB"""

    def __init__(self, docs_dir: str, collection_name: str = "ghl-docs"):
        self.docs_dir = Path(docs_dir)
        self.collection_name = collection_name

        # Initialize embedding model
        print("Loading embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("Model loaded successfully")

        # Initialize ChromaDB client
        print("Connecting to ChromaDB...")
        self.client = chromadb.HttpClient(
            host="localhost",
            port=8001,  # ChromaDB Docker container port
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"Using existing collection: {self.collection_name}")
            print(f"  Current document count: {self.collection.count()}")
        except:
            print(f"Creating new collection: {self.collection_name}")
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "GHL Official Documentation"}
            )

        # Statistics
        self.stats = {
            'documents_processed': 0,
            'documents_embedded': 0,
            'documents_failed': 0,
            'chunks_created': 0,
            'total_processing_time': 0
        }

    def load_index(self) -> Dict:
        """Load the index.json file with article metadata"""
        index_path = self.docs_dir / 'index.json'

        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")

        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_article(self, article_id: str, title: str) -> Optional[str]:
        """Load article content from file"""
        # Sanitize filename (same logic as scraper)
        import re
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_title = safe_title[:100]

        filename = f"{article_id}_{safe_title}.txt"
        filepath = self.docs_dir / filename

        if not filepath.exists():
            # Try without the title part (fallback)
            for file in self.docs_dir.glob(f"{article_id}_*.txt"):
                filepath = file
                break

        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract content after metadata header
            if '---' in content:
                parts = content.split('---')
                if len(parts) >= 3:
                    return parts[2].strip()
                elif len(parts) == 2:
                    return parts[1].strip()

            return content
        except Exception as e:
            print(f"  Error loading article: {e}")
            return None

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks by words"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks

    def embed_article(self, article: Dict) -> bool:
        """Embed a single article and add to ChromaDB"""
        article_id = article['id']
        title = article['title']

        # Load article content
        content = self.load_article(article_id, title)

        if not content:
            print(f"  Failed to load content")
            self.stats['documents_failed'] += 1
            return False

        # Split into chunks
        chunks = self.chunk_text(content, chunk_size=500, overlap=50)

        if not chunks:
            print(f"  No chunks created")
            self.stats['documents_failed'] += 1
            return False

        # Generate embeddings for all chunks
        try:
            embeddings = self.model.encode(chunks, show_progress_bar=False)
        except Exception as e:
            print(f"  Embedding failed: {e}")
            self.stats['documents_failed'] += 1
            return False

        # Prepare data for ChromaDB
        ids = [f"{article_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{
            'article_id': article_id,
            'title': title,
            'url': article.get('url', ''),
            'category': article.get('category', 'General'),
            'word_count': article.get('word_count', 0),
            'chunk_index': i,
            'total_chunks': len(chunks),
            'source': 'ghl-docs',
            'indexed_date': datetime.now().isoformat()
        } for i in range(len(chunks))]

        # Add to ChromaDB
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=chunks,
                metadatas=metadatas
            )

            self.stats['documents_embedded'] += 1
            self.stats['chunks_created'] += len(chunks)

            return True
        except Exception as e:
            print(f"  ChromaDB add failed: {e}")
            self.stats['documents_failed'] += 1
            return False

    def embed_all(self, max_documents: Optional[int] = None):
        """Embed all documents from the index"""
        print("\n" + "="*80)
        print("BroBro - Documentation Embedding")
        print("="*80)
        print(f"Input Directory: {self.docs_dir}")
        print(f"Collection: {self.collection_name}")

        if max_documents:
            print(f"Max Documents: {max_documents}")

        # Load index
        print("\nLoading index...")
        index_data = self.load_index()
        articles = index_data.get('articles', [])

        print(f"Found {len(articles)} articles in index")

        if max_documents:
            articles = articles[:max_documents]
            print(f"Processing first {max_documents} articles")

        # Process each article
        print("\n" + "="*80)
        print("Embedding Articles...")
        print("="*80)

        start_time = time.time()

        for i, article in enumerate(articles, 1):
            print(f"[{i}/{len(articles)}] {article['title'][:60]}...", end=' ')

            article_start = time.time()
            success = self.embed_article(article)
            article_time = time.time() - article_start

            if success:
                chunks = self.stats['chunks_created'] - (i - 1) * 5  # Rough estimate
                print(f"OK ({chunks} chunks, {article_time:.2f}s)")
            else:
                print(f"FAILED")

            self.stats['documents_processed'] += 1

        self.stats['total_processing_time'] = time.time() - start_time

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print embedding summary"""
        print("\n" + "="*80)
        print("EMBEDDING COMPLETE")
        print("="*80)
        print(f"Documents Processed: {self.stats['documents_processed']}")
        print(f"Documents Embedded: {self.stats['documents_embedded']}")
        print(f"Documents Failed: {self.stats['documents_failed']}")
        print(f"Total Chunks Created: {self.stats['chunks_created']}")
        print(f"Total Processing Time: {self.stats['total_processing_time']:.2f}s")

        if self.stats['documents_embedded'] > 0:
            avg_time = self.stats['total_processing_time'] / self.stats['documents_embedded']
            avg_chunks = self.stats['chunks_created'] / self.stats['documents_embedded']
            print(f"Average Time/Document: {avg_time:.2f}s")
            print(f"Average Chunks/Document: {avg_chunks:.1f}")

        print(f"\nChromaDB Collection: {self.collection_name}")
        print(f"Total Documents in Collection: {self.collection.count()}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Embed GHL documentation into ChromaDB')
    parser.add_argument('--input', '-i', default='kb/ghl-docs',
                       help='Input directory with scraped docs (default: kb/ghl-docs)')
    parser.add_argument('--collection', '-c', default='ghl-docs',
                       help='ChromaDB collection name (default: ghl-docs)')
    parser.add_argument('--max-docs', '-m', type=int, default=None,
                       help='Maximum number of documents to embed (default: all)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: embed only 5 documents')

    args = parser.parse_args()

    if args.test:
        args.max_docs = 5
        print("\nTEST MODE: Embedding only 5 documents\n")

    try:
        embedder = GHLDocsEmbedder(args.input, args.collection)
        embedder.embed_all(max_documents=args.max_docs)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()
