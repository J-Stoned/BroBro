"""
BroBro - Snapshot Documentation Embedder
Embeds snapshot documentation into ChromaDB for AI-powered search
"""

import sys
import json
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from datetime import datetime
import hashlib
from typing import List, Dict, Optional

class SnapshotEmbedder:
    """Embeds snapshot documentation into ChromaDB"""

    def __init__(self):
        print("\n" + "="*70)
        print("BroBro - Snapshot Documentation Embedder")
        print("="*70)
        print(">> Initializing embedder...")
        print(">> Loading embedding model: all-MiniLM-L6-v2")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Connect to ChromaDB server
        chroma_client = chromadb.HttpClient(host='localhost', port=8001)

        try:
            self.collection = chroma_client.get_collection(name="ghl-snapshots")
            doc_count = self.collection.count()
            print(f">> Connected to existing collection: ghl-snapshots")
            print(f"   Current document count: {doc_count}")
        except:
            self.collection = chroma_client.create_collection(
                name="ghl-snapshots",
                metadata={"description": "GHL snapshot documentation and templates"}
            )
            print(">> Created new collection: ghl-snapshots")

    def create_searchable_text(self, snapshot: Dict) -> str:
        """
        Create a comprehensive searchable text from snapshot data
        This combines all important information for embedding
        """
        parts = []

        # Basic info
        parts.append(f"Snapshot: {snapshot.get('snapshot_name', 'Unnamed')}")
        parts.append(f"Industry: {snapshot.get('industry', 'General')}")
        parts.append(f"Use Case: {snapshot.get('use_case', '')}")
        parts.append(f"Target Audience: {snapshot.get('target_audience', '')}")

        # Description
        if 'description' in snapshot:
            desc = snapshot['description']
            parts.append(f"Overview: {desc.get('overview', '')}")

            if 'key_benefits' in desc:
                parts.append("Key Benefits: " + "; ".join(desc['key_benefits']))

            if 'ideal_for' in desc:
                parts.append("Ideal For: " + "; ".join(desc['ideal_for']))

        # Components summary
        if 'components' in snapshot:
            comp = snapshot['components']

            if 'funnels' in comp and comp['funnels']:
                funnel_names = [f['name'] for f in comp['funnels']]
                parts.append(f"Funnels: {', '.join(funnel_names)}")
                for funnel in comp['funnels']:
                    parts.append(f"Funnel Purpose: {funnel.get('purpose', '')}")

            if 'workflows' in comp and comp['workflows']:
                workflow_names = [w['name'] for w in comp['workflows']]
                parts.append(f"Workflows: {', '.join(workflow_names)}")
                for workflow in comp['workflows']:
                    parts.append(f"Workflow: {workflow.get('name', '')} - {workflow.get('purpose', '')}")

            if 'campaigns' in comp and comp['campaigns']:
                campaign_names = [c['name'] for c in comp['campaigns']]
                parts.append(f"Campaigns: {', '.join(campaign_names)}")

            if 'pipelines' in comp and comp['pipelines']:
                pipeline_names = [p['name'] for p in comp['pipelines']]
                parts.append(f"Pipelines: {', '.join(pipeline_names)}")

        # Best practices
        if 'best_practices' in snapshot:
            parts.append("Best Practices: " + "; ".join(snapshot['best_practices']))

        # Common use cases
        if 'common_use_cases' in snapshot:
            for use_case in snapshot['common_use_cases']:
                parts.append(f"Use Case: {use_case.get('scenario', '')}")

        # Setup instructions
        if 'setup_instructions' in snapshot:
            setup = snapshot['setup_instructions']
            if 'important_notes' in setup:
                parts.append("Important Notes: " + "; ".join(setup['important_notes']))

        return "\n".join(parts)

    def create_component_chunks(self, snapshot: Dict) -> List[Dict]:
        """
        Create separate chunks for major components
        This allows more granular search
        """
        chunks = []
        snapshot_id = snapshot.get('snapshot_id', 'unknown')
        snapshot_name = snapshot.get('snapshot_name', 'Unnamed')

        # Main overview chunk
        overview_text = self.create_searchable_text(snapshot)
        chunks.append({
            'text': overview_text,
            'chunk_type': 'overview',
            'chunk_name': 'Snapshot Overview'
        })

        # Individual component chunks
        if 'components' in snapshot:
            comp = snapshot['components']

            # Funnels chunk
            if 'funnels' in comp and comp['funnels']:
                funnel_text = f"Snapshot: {snapshot_name}\n\nFunnels:\n"
                for funnel in comp['funnels']:
                    funnel_text += f"\n{funnel.get('name', 'Unnamed Funnel')}\n"
                    funnel_text += f"Purpose: {funnel.get('purpose', 'N/A')}\n"
                    funnel_text += f"Conversion Goal: {funnel.get('conversion_goal', 'N/A')}\n"
                    if 'pages' in funnel:
                        funnel_text += f"Pages: {', '.join(funnel['pages'])}\n"

                chunks.append({
                    'text': funnel_text,
                    'chunk_type': 'funnels',
                    'chunk_name': 'Funnels'
                })

            # Workflows chunk
            if 'workflows' in comp and comp['workflows']:
                workflow_text = f"Snapshot: {snapshot_name}\n\nWorkflows:\n"
                for workflow in comp['workflows']:
                    workflow_text += f"\n{workflow.get('name', 'Unnamed Workflow')}\n"
                    workflow_text += f"Trigger: {workflow.get('trigger', 'N/A')}\n"
                    workflow_text += f"Purpose: {workflow.get('purpose', 'N/A')}\n"
                    if 'steps' in workflow:
                        workflow_text += f"Steps: {'; '.join(workflow['steps'])}\n"

                chunks.append({
                    'text': workflow_text,
                    'chunk_type': 'workflows',
                    'chunk_name': 'Workflows'
                })

            # Setup instructions chunk
            if 'setup_instructions' in snapshot:
                setup = snapshot['setup_instructions']
                setup_text = f"Snapshot: {snapshot_name}\n\nSetup Instructions:\n"

                if 'prerequisites' in setup:
                    setup_text += "\nPrerequisites:\n" + "\n".join([f"- {p}" for p in setup['prerequisites']])

                if 'import_steps' in setup:
                    setup_text += "\n\nImport Steps:\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(setup['import_steps'])])

                if 'post_import_configuration' in setup:
                    setup_text += "\n\nPost-Import Configuration:\n" + "\n".join([f"- {c}" for c in setup['post_import_configuration']])

                if 'important_notes' in setup:
                    setup_text += "\n\nImportant Notes:\n" + "\n".join([f"⚠️ {n}" for n in setup['important_notes']])

                chunks.append({
                    'text': setup_text,
                    'chunk_type': 'setup',
                    'chunk_name': 'Setup Instructions'
                })

        return chunks

    def embed_snapshot(self, snapshot_path: str) -> bool:
        """Embed a single snapshot documentation file"""

        try:
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)

            snapshot_name = snapshot.get('snapshot_name', 'Unnamed')
            snapshot_id = snapshot.get('snapshot_id', hashlib.md5(snapshot_name.encode()).hexdigest()[:8])

            print(f"\n>> Processing: {snapshot_name}")

            # Create chunks
            chunks = self.create_component_chunks(snapshot)
            print(f"   >> Created {len(chunks)} chunks")

            # Embed each chunk
            for idx, chunk in enumerate(chunks):
                try:
                    embedding = self.model.encode(chunk['text']).tolist()

                    doc_id = f"snap_{snapshot_id}_chunk_{idx}"

                    metadata = {
                        'source': 'snapshot_docs',
                        'type': 'snapshot',
                        'snapshot_name': snapshot_name,
                        'snapshot_id': snapshot_id,
                        'chunk_type': chunk['chunk_type'],
                        'chunk_name': chunk['chunk_name'],
                        'chunk_index': idx,
                        'total_chunks': len(chunks),
                        'industry': snapshot.get('industry', 'General'),
                        'use_case': snapshot.get('use_case', ''),
                        'version': snapshot.get('version', '1.0.0'),
                        'last_updated': snapshot.get('last_updated', ''),
                        'indexed_date': datetime.now().isoformat()
                    }

                    # Add optional fields
                    if 'author' in snapshot:
                        metadata['author'] = snapshot['author']

                    if 'tags' in snapshot:
                        metadata['tags'] = ', '.join(snapshot['tags'])

                    if 'pricing_model' in snapshot:
                        metadata['pricing_model'] = snapshot['pricing_model']

                    self.collection.add(
                        ids=[doc_id],
                        embeddings=[embedding],
                        documents=[chunk['text']],
                        metadatas=[metadata]
                    )

                except Exception as e:
                    print(f"   [ERROR] Failed to embed chunk {idx}: {e}")
                    return False

            print(f"   [OK] Embedded {len(chunks)} chunks")
            return True

        except Exception as e:
            print(f"   [ERROR] Failed to process snapshot: {e}")
            return False

    def embed_directory(self, directory: str) -> int:
        """Embed all snapshot JSON files in a directory"""

        snapshot_dir = Path(directory)
        if not snapshot_dir.exists():
            print(f"[ERROR] Directory not found: {directory}")
            return 0

        # Find all JSON files
        json_files = list(snapshot_dir.glob('**/*.json'))

        if not json_files:
            print(f"[WARN] No JSON files found in {directory}")
            return 0

        print(f"\n>> Found {len(json_files)} snapshot files")

        success_count = 0
        for json_file in json_files:
            if self.embed_snapshot(str(json_file)):
                success_count += 1

        return success_count


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python embed-snapshots.py <snapshot_json_or_directory>")
        print("\nExamples:")
        print("  python embed-snapshots.py data/snapshots/josh-wash/lead-gen.json")
        print("  python embed-snapshots.py data/snapshots/josh-wash/")
        print("  python embed-snapshots.py data/snapshots/")
        sys.exit(1)

    path = sys.argv[1]

    embedder = SnapshotEmbedder()

    path_obj = Path(path)

    if path_obj.is_file():
        # Single file
        success = embedder.embed_snapshot(path)
        if success:
            print(f"\n{'='*70}")
            print(f"[OK] Successfully embedded snapshot!")
            print(f"{'='*70}")

    elif path_obj.is_dir():
        # Directory
        success_count = embedder.embed_directory(path)
        print(f"\n{'='*70}")
        print(f"[OK] Successfully embedded {success_count} snapshots!")
        print(f"{'='*70}")

    else:
        print(f"[ERROR] Path not found: {path}")
        sys.exit(1)

    final_count = embedder.collection.count()
    print(f"   Collection now has: {final_count} total documents")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
