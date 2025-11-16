"""
BroBro - Best Practices Embedder
Embeds scraped best practices articles into ChromaDB
"""

import sys
import json
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from datetime import datetime
import hashlib
from typing import List, Dict

class BestPracticesEmbedder:
    """Embeds best practices content into ChromaDB"""

    def __init__(self):
        print("\n" + "="*70)
        print("BroBro - Best Practices Embedder")
        print("="*70)
        print(">> Initializing embedder...")
        print(">> Loading embedding model: all-MiniLM-L6-v2")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Connect to ChromaDB server
        chroma_client = chromadb.HttpClient(host='localhost', port=8001)

        try:
            self.collection = chroma_client.get_collection(name="ghl-best-practices")
            doc_count = self.collection.count()
            print(f">> Connected to existing collection: ghl-best-practices")
            print(f"   Current document count: {doc_count}")
        except:
            self.collection = chroma_client.create_collection(
                name="ghl-best-practices",
                metadata={"description": "GHL best practices, guides, and implementation tips"}
            )
            print(">> Created new collection: ghl-best-practices")

    def chunk_article(self, article: Dict, max_chunk_words: int = 800) -> List[Dict]:
        """
        Split long articles into smaller chunks for better embedding
        """
        content = article['content']
        words = content.split()
        total_words = len(words)

        # If article is short enough, return as single chunk
        if total_words <= max_chunk_words:
            return [{
                'text': content,
                'chunk_index': 0,
                'total_chunks': 1,
                'word_count': total_words
            }]

        # Split into chunks with overlap
        chunks = []
        overlap_words = 100  # Overlap between chunks
        start = 0

        while start < total_words:
            end = min(start + max_chunk_words, total_words)
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)

            chunks.append({
                'text': chunk_text,
                'chunk_index': len(chunks),
                'word_count': len(chunk_words)
            })

            # Move forward with overlap
            start = end - overlap_words if end < total_words else total_words

        # Update total_chunks for all chunks
        for chunk in chunks:
            chunk['total_chunks'] = len(chunks)

        return chunks

    def embed_articles(self, json_path: str) -> bool:
        """Embed all articles from JSON file into ChromaDB"""

        print(f"\n>> Loading articles from: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)

        print(f"   [OK] Loaded {len(articles)} articles")

        # Embed each article
        added_count = 0
        failed_count = 0
        chunk_count = 0

        print(f"\n>> Embedding articles into ChromaDB...\n")

        for article_idx, article in enumerate(articles):
            try:
                title = article.get('title', 'Untitled')
                print(f"[{article_idx + 1}/{len(articles)}] Processing: {title}")

                # Generate unique article ID
                article_hash = hashlib.md5(article['url'].encode()).hexdigest()[:8]
                article_id = f"bp_{article_hash}"

                # Chunk the article
                chunks = self.chunk_article(article)
                print(f"   >> Created {len(chunks)} chunks")

                # Embed each chunk
                for chunk in chunks:
                    try:
                        embedding = self.model.encode(chunk['text']).tolist()

                        doc_id = f"{article_id}_chunk_{chunk['chunk_index']}"

                        # Build metadata
                        metadata = {
                            'source': 'best_practices',
                            'type': article.get('source_type', 'article'),
                            'title': title,
                            'url': article['url'],
                            'chunk_index': chunk['chunk_index'],
                            'total_chunks': chunk['total_chunks'],
                            'word_count': chunk['word_count'],
                            'article_id': article_id,
                            'scraped_date': article.get('scraped_date', ''),
                            'indexed_date': datetime.now().isoformat()
                        }

                        # Add optional metadata
                        if 'description' in article:
                            metadata['description'] = article['description'][:500]  # Limit length

                        if 'categories' in article and article['categories']:
                            metadata['categories'] = ', '.join(article['categories'][:3])

                        if 'category' in article:
                            metadata['category'] = article['category']

                        self.collection.add(
                            ids=[doc_id],
                            embeddings=[embedding],
                            documents=[chunk['text']],
                            metadatas=[metadata]
                        )

                        chunk_count += 1

                    except Exception as e:
                        print(f"   [ERROR] Failed to embed chunk {chunk['chunk_index']}: {e}")
                        failed_count += 1
                        continue

                added_count += 1
                print(f"   [OK] Embedded {len(chunks)} chunks")

            except Exception as e:
                print(f"   [ERROR] Failed to process article: {e}")
                failed_count += 1
                continue

        print(f"\n{'='*70}")
        print(f"[OK] Embedding complete!")
        print(f"{'='*70}")
        print(f"   Articles processed: {added_count}/{len(articles)}")
        print(f"   Total chunks embedded: {chunk_count}")
        if failed_count > 0:
            print(f"   Failed: {failed_count}")

        final_count = self.collection.count()
        print(f"   Collection now has: {final_count} total documents")
        print(f"{'='*70}\n")

        return True


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python embed-best-practices.py <json_file>")
        print("\nExample:")
        print("  python embed-best-practices.py data/best-practices/best-practices_20251101_120000.json")
        sys.exit(1)

    json_path = sys.argv[1]

    if not Path(json_path).exists():
        print(f"[ERROR] File not found: {json_path}")
        sys.exit(1)

    embedder = BestPracticesEmbedder()
    embedder.embed_articles(json_path)


if __name__ == "__main__":
    main()
