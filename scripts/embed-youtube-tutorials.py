"""
BroBro - YouTube Tutorial Embedder
Embeds YouTube tutorial transcripts into the ghl-tutorials collection
"""

import sys
import json
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class YouTubeTutorialEmbedder:
    """Embeds YouTube tutorials into ChromaDB"""

    def __init__(self):
        print("\n" + "="*70)
        print("BroBro - YouTube Tutorial Embedder")
        print("="*70)
        print(">> Initializing embedder...")
        print(">> Loading embedding model: all-MiniLM-L6-v2")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Connect to ChromaDB server
        chroma_client = chromadb.HttpClient(host='localhost', port=8001)

        try:
            self.collection = chroma_client.get_collection(name="ghl-tutorials")
            doc_count = self.collection.count()
            print(f">> Connected to existing collection: ghl-tutorials")
            print(f"   Current document count: {doc_count}")
        except:
            self.collection = chroma_client.create_collection(
                name="ghl-tutorials",
                metadata={"description": "YouTube tutorials for GoHighLevel"}
            )
            print(">> Created new collection: ghl-tutorials")

    def chunk_transcript(self, transcript: str, max_chunk_words: int = 800) -> List[str]:
        """
        Split long transcripts into chunks for better embedding
        """
        words = transcript.split()
        total_words = len(words)

        if total_words <= max_chunk_words:
            return [transcript]

        chunks = []
        overlap_words = 100

        start = 0
        while start < total_words:
            end = min(start + max_chunk_words, total_words)
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)

            start = end - overlap_words if end < total_words else total_words

        return chunks

    def embed_video(self, video_data: Dict) -> bool:
        """Embed a single video transcript"""

        try:
            video_id = video_data.get('video_id', 'unknown')
            title = video_data.get('title', 'Untitled Video')

            print(f"\n>> Processing: {title}")
            print(f"   Video ID: {video_id}")
            print(f"   Duration: {video_data.get('duration', 0)} seconds")
            print(f"   Words: {video_data.get('word_count', 0)}")

            # Chunk the transcript
            transcript = video_data.get('transcript', '')
            chunks = self.chunk_transcript(transcript)

            print(f"   >> Created {len(chunks)} chunks")

            # Embed each chunk
            for idx, chunk in enumerate(chunks):
                try:
                    embedding = self.model.encode(chunk).tolist()

                    doc_id = f"yt_{video_id}_chunk_{idx}"

                    metadata = {
                        'source': 'youtube',
                        'type': 'tutorial',
                        'video_id': video_id,
                        'title': title,
                        'url': video_data.get('url', f"https://www.youtube.com/watch?v={video_id}"),
                        'channel': video_data.get('channel', 'Unknown'),
                        'duration_seconds': video_data.get('duration', 0),
                        'chunk_index': idx,
                        'total_chunks': len(chunks),
                        'word_count': len(chunk.split()),
                        'language': video_data.get('language', 'en'),
                        'is_generated': video_data.get('is_generated', False),
                        'upload_date': video_data.get('upload_date', ''),
                        'scraped_date': video_data.get('scraped_date', ''),
                        'indexed_date': datetime.now().isoformat()
                    }

                    # Add optional metadata
                    if 'description' in video_data:
                        metadata['description'] = video_data['description'][:500]

                    if 'tags' in video_data and video_data['tags']:
                        metadata['tags'] = ', '.join(video_data['tags'][:10])

                    if 'categories' in video_data and video_data['categories']:
                        metadata['categories'] = ', '.join(video_data['categories'])

                    self.collection.add(
                        ids=[doc_id],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[metadata]
                    )

                except Exception as e:
                    print(f"   [ERROR] Failed to embed chunk {idx}: {e}")
                    return False

            print(f"   [OK] Embedded {len(chunks)} chunks")
            return True

        except Exception as e:
            print(f"   [ERROR] Failed to process video: {e}")
            return False

    def embed_from_file(self, json_path: str) -> bool:
        """Embed video from JSON file"""

        with open(json_path, 'r', encoding='utf-8') as f:
            video_data = json.load(f)

        return self.embed_video(video_data)

    def embed_from_directory(self, directory: str) -> int:
        """Embed all videos from a directory"""

        video_dir = Path(directory)
        if not video_dir.exists():
            print(f"[ERROR] Directory not found: {directory}")
            return 0

        # Find all JSON files
        json_files = list(video_dir.glob('*.json'))

        if not json_files:
            print(f"[WARN] No JSON files found in {directory}")
            return 0

        print(f"\n>> Found {len(json_files)} video files")

        success_count = 0
        for json_file in json_files:
            if self.embed_from_file(str(json_file)):
                success_count += 1

        return success_count


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python embed-youtube-tutorials.py <json_file_or_directory>")
        print("\nExamples:")
        print("  python embed-youtube-tutorials.py data/youtube-tutorials/youtube_VIDEO_ID.json")
        print("  python embed-youtube-tutorials.py data/youtube-tutorials/")
        sys.exit(1)

    path = sys.argv[1]

    embedder = YouTubeTutorialEmbedder()

    path_obj = Path(path)

    if path_obj.is_file():
        # Single file
        success = embedder.embed_from_file(path)
        if success:
            print(f"\n{'='*70}")
            print(f"[OK] Successfully embedded tutorial!")
            print(f"{'='*70}")

    elif path_obj.is_dir():
        # Directory
        success_count = embedder.embed_from_directory(path)
        print(f"\n{'='*70}")
        print(f"[OK] Successfully embedded {success_count} tutorials!")
        print(f"{'='*70}")

    else:
        print(f"[ERROR] Path not found: {path}")
        sys.exit(1)

    final_count = embedder.collection.count()
    print(f"   Collection now has: {final_count} total documents")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
