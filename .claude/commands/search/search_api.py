#!/usr/bin/env python3
"""
GHL Command Search API using ChromaDB
Semantic search across 275 Josh Wash enriched GHL commands
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Add project root to path
# File is at: .claude/commands/search/search-api.py
# parent = .claude/commands/search
# parent.parent = .claude/commands
# parent.parent.parent = .claude
# parent.parent.parent.parent = project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class GHLCommandSearchIndex:
    """Vector search index for GHL commands using ChromaDB"""

    def __init__(self, commands_json_path: str, db_path: str = None):
        """
        Initialize search index

        Args:
            commands_json_path: Path to commands.json registry
            db_path: Path to ChromaDB storage (default: ./chromadb/)
        """
        self.commands_json_path = commands_json_path
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), "chromadb")

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Use default embedding function (all-MiniLM-L6-v2)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="ghl_commands",
            embedding_function=self.embedding_function,
            metadata={"description": "GHL commands with Josh Wash business architecture"}
        )

        self.commands = {}
        self.load_commands()

    def load_commands(self):
        """Load commands from JSON registry"""
        with open(self.commands_json_path, 'r', encoding='utf-8') as f:
            self.commands = json.load(f)
        print(f"✓ Loaded {len(self.commands)} commands from registry")

    def create_document_text(self, cmd_name: str, cmd_data: Dict) -> str:
        """
        Create searchable text document from command data

        Combines all relevant fields for semantic search:
        - Command name
        - Description
        - Category
        - Tags
        - Josh Wash workflow name
        - Proven pattern
        - Channels
        - Examples
        """
        parts = [
            f"Command: {cmd_name}",
            f"Description: {cmd_data.get('description', '')}",
            f"Category: {cmd_data.get('category', '')}",
            f"Tags: {', '.join(cmd_data.get('tags', []))}",
            f"Josh Wash Workflow: {cmd_data.get('josh_wash_workflow', '')}",
            f"Proven Pattern: {cmd_data.get('proven_pattern', '')}",
            f"Channels: {cmd_data.get('channels', '')}",
        ]

        # Add examples
        examples = cmd_data.get('examples', [])
        if examples:
            parts.append(f"Examples: {' | '.join(examples)}")

        # Add metrics if available
        metrics = cmd_data.get('metrics', {})
        if metrics:
            metrics_text = ', '.join([f"{k}: {v}" for k, v in metrics.items()])
            parts.append(f"Metrics: {metrics_text}")

        return "\n".join(parts)

    def create_metadata(self, cmd_name: str, cmd_data: Dict) -> Dict:
        """
        Create metadata dictionary for ChromaDB filtering

        Note: ChromaDB metadata only supports string, int, float, bool
        Lists/arrays must be converted to strings
        """
        metadata = {
            "command_name": cmd_name,
            "command_id": cmd_data.get('id', ''),
            "category": cmd_data.get('category', ''),
            "tags": ','.join(cmd_data.get('tags', [])),  # Convert list to comma-separated string
            "josh_wash_workflow": cmd_data.get('josh_wash_workflow', ''),
            "proven_pattern": cmd_data.get('proven_pattern', ''),
            "channels": cmd_data.get('channels', ''),
            "filepath": cmd_data.get('filepath', ''),
        }

        # Add metrics as separate fields if available
        metrics = cmd_data.get('metrics', {})
        for key, value in metrics.items():
            # Convert metric to string for ChromaDB compatibility
            metadata[f"metric_{key}"] = str(value)

        return metadata

    def index_all_commands(self, force_rebuild: bool = False):
        """
        Index all commands into ChromaDB

        Args:
            force_rebuild: If True, clear existing index and rebuild from scratch
        """
        if force_rebuild:
            print("Rebuilding index from scratch...")
            self.client.delete_collection("ghl_commands")
            self.collection = self.client.get_or_create_collection(
                name="ghl_commands",
                embedding_function=self.embedding_function,
                metadata={"description": "GHL commands with Josh Wash business architecture"}
            )

        # Check if already indexed
        existing_count = self.collection.count()
        if existing_count > 0 and not force_rebuild:
            print(f"✓ Index already contains {existing_count} commands")
            return

        print(f"Indexing {len(self.commands)} commands into ChromaDB...")

        # Prepare batch data
        documents = []
        metadatas = []
        ids = []

        for cmd_name, cmd_data in self.commands.items():
            doc_text = self.create_document_text(cmd_name, cmd_data)
            metadata = self.create_metadata(cmd_name, cmd_data)
            doc_id = cmd_data.get('id', cmd_name)

            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(doc_id)

        # Add to collection in batch
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(f"✓ Successfully indexed {len(documents)} commands")
        print(f"✓ Database location: {self.db_path}")

    def search(
        self,
        query: str,
        n_results: int = 10,
        category_filter: Optional[str] = None,
        workflow_filter: Optional[str] = None,
        channel_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for commands using semantic similarity + optional filters

        Args:
            query: Natural language search query
            n_results: Number of results to return
            category_filter: Filter by category (e.g., "sales", "lead")
            workflow_filter: Filter by Josh Wash workflow name
            channel_filter: Filter by channel (e.g., "SMS", "EMAIL")

        Returns:
            List of command dictionaries with scores
        """
        # Build where filter for metadata
        where_filter = {}

        if category_filter:
            where_filter["category"] = category_filter

        if workflow_filter:
            where_filter["josh_wash_workflow"] = workflow_filter

        if channel_filter:
            where_filter["channels"] = {"$contains": channel_filter}

        # Perform semantic search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None
        )

        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                result = {
                    'command_id': results['ids'][0][i],
                    'command_name': results['metadatas'][0][i]['command_name'],
                    'description': results['documents'][0][i].split('\n')[1].replace('Description: ', ''),
                    'category': results['metadatas'][0][i]['category'],
                    'josh_wash_workflow': results['metadatas'][0][i]['josh_wash_workflow'],
                    'proven_pattern': results['metadatas'][0][i]['proven_pattern'],
                    'channels': results['metadatas'][0][i]['channels'],
                    'score': 1 - results['distances'][0][i],  # Convert distance to similarity score
                    'metadata': results['metadatas'][0][i]
                }
                formatted_results.append(result)

        return formatted_results

    def search_by_metrics(self, metric_query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for commands with specific success metrics

        Args:
            metric_query: Query related to metrics (e.g., "85% show-up rate", "high conversion")
            n_results: Number of results to return

        Returns:
            List of command dictionaries with metric data
        """
        # Search for commands that mention these metrics in their workflow
        results = self.search(
            query=f"workflow with {metric_query} success rate metrics",
            n_results=n_results
        )

        return results

    def get_command_by_name(self, command_name: str) -> Optional[Dict]:
        """
        Get specific command by exact name match

        Args:
            command_name: Exact command name

        Returns:
            Command dictionary or None if not found
        """
        if command_name in self.commands:
            return self.commands[command_name]
        return None

    def list_categories(self) -> List[str]:
        """Get list of all unique categories"""
        categories = set()
        for cmd_data in self.commands.values():
            cat = cmd_data.get('category', '')
            if cat:
                categories.add(cat)
        return sorted(list(categories))

    def list_josh_wash_workflows(self) -> List[str]:
        """Get list of all Josh Wash workflow types"""
        workflows = set()
        for cmd_data in self.commands.values():
            workflow = cmd_data.get('josh_wash_workflow', '')
            if workflow:
                workflows.add(workflow)
        return sorted(list(workflows))

    def get_stats(self) -> Dict:
        """Get index statistics"""
        return {
            "total_commands": len(self.commands),
            "indexed_count": self.collection.count(),
            "categories": self.list_categories(),
            "josh_wash_workflows": self.list_josh_wash_workflows(),
            "database_path": self.db_path
        }


def main():
    """CLI interface for search API"""
    import argparse

    parser = argparse.ArgumentParser(
        description="GHL Command Search API - Semantic search across 275 Josh Wash enriched commands"
    )

    parser.add_argument(
        '--index',
        action='store_true',
        help='Index all commands into ChromaDB'
    )

    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='Force rebuild index from scratch'
    )

    parser.add_argument(
        '--search',
        type=str,
        help='Search query (natural language)'
    )

    parser.add_argument(
        '--category',
        type=str,
        help='Filter by category'
    )

    parser.add_argument(
        '--workflow',
        type=str,
        help='Filter by Josh Wash workflow'
    )

    parser.add_argument(
        '--channel',
        type=str,
        help='Filter by channel (SMS, EMAIL)'
    )

    parser.add_argument(
        '--results',
        type=int,
        default=10,
        help='Number of results to return (default: 10)'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show index statistics'
    )

    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='List all categories'
    )

    parser.add_argument(
        '--list-workflows',
        action='store_true',
        help='List all Josh Wash workflows'
    )

    args = parser.parse_args()

    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    # Initialize search index
    # PROJECT_ROOT is already at "C:\Users\justi\BroBro"
    commands_json = os.path.join(str(PROJECT_ROOT), ".claude", "commands", "cli", "commands.json")

    # Debug: Print the path
    print(f"Looking for commands.json at: {commands_json}")

    search_index = GHLCommandSearchIndex(commands_json)

    # Handle commands
    if args.index or args.rebuild:
        search_index.index_all_commands(force_rebuild=args.rebuild)
        return

    if args.stats:
        stats = search_index.get_stats()
        print("\n=== GHL Command Search Index Statistics ===\n")
        print(f"Total commands: {stats['total_commands']}")
        print(f"Indexed count: {stats['indexed_count']}")
        print(f"Categories: {len(stats['categories'])}")
        print(f"Josh Wash workflows: {len(stats['josh_wash_workflows'])}")
        print(f"Database path: {stats['database_path']}")
        return

    if args.list_categories:
        categories = search_index.list_categories()
        print("\n=== All Categories ===\n")
        for cat in categories:
            print(f"  • {cat}")
        return

    if args.list_workflows:
        workflows = search_index.list_josh_wash_workflows()
        print("\n=== Josh Wash Workflows ===\n")
        for workflow in workflows:
            print(f"  • {workflow}")
        return

    if args.search:
        print(f"\nSearching for: '{args.search}'")
        if args.category:
            print(f"Category filter: {args.category}")
        if args.workflow:
            print(f"Workflow filter: {args.workflow}")
        if args.channel:
            print(f"Channel filter: {args.channel}")
        print()

        results = search_index.search(
            query=args.search,
            n_results=args.results,
            category_filter=args.category,
            workflow_filter=args.workflow,
            channel_filter=args.channel
        )

        if not results:
            print("No results found.")
            return

        print(f"Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['command_name']}")
            print(f"   Category: {result['category']}")
            print(f"   Josh Wash Workflow: {result['josh_wash_workflow']}")
            print(f"   Pattern: {result['proven_pattern']}")
            print(f"   Channels: {result['channels']}")
            print(f"   Relevance: {result['score']:.2%}")
            print()

        return

    # If no command specified, show help
    parser.print_help()


if __name__ == "__main__":
    main()
