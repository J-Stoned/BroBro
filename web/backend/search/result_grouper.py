"""
Group and Organize Search Results by Type
Built with BMAD-METHOD for Epic US: Unified Search

Groups results for organized display:
- Top answer (highest scored)
- Commands section
- Documentation section
- Total counts per type
"""

from typing import List, Dict


class ResultGrouper:
    """Group and organize search results intelligently"""

    def group_by_collection(self, results: List[Dict]) -> Dict:
        """
        Group results by collection and select top answer

        Args:
            results: List of scored search results (sorted by relevance)

        Returns:
            {
                'topAnswer': {...},     # Highest scored result
                'commands': [...],       # Up to 5 command results
                'documentation': [...],  # Up to 5 doc results
                'total_by_type': {
                    'commands': int,
                    'documentation': int
                }
            }
        """
        if not results:
            return {
                'topAnswer': None,
                'commands': [],
                'documentation': [],
                'total_by_type': {'commands': 0, 'documentation': 0}
            }

        grouped = {
            'topAnswer': results[0] if results else None,
            'commands': [],
            'documentation': [],
            'total_by_type': {
                'commands': 0,
                'documentation': 0
            }
        }

        # Count totals and group results
        for result in results:
            collection = result.get('collection', '')

            if collection == 'ghl-knowledge-base':
                grouped['total_by_type']['commands'] += 1
                # Add to commands section (limit to 5)
                if len(grouped['commands']) < 5:
                    grouped['commands'].append(result)

            elif collection == 'ghl-docs':
                grouped['total_by_type']['documentation'] += 1
                # Add to documentation section (limit to 5)
                if len(grouped['documentation']) < 5:
                    grouped['documentation'].append(result)

        # Remove empty groups
        if not grouped['commands']:
            del grouped['commands']
        if not grouped['documentation']:
            del grouped['documentation']

        return grouped

    def format_result_for_display(self, result: Dict) -> Dict:
        """
        Format result with display-friendly fields

        Args:
            result: Raw search result

        Returns:
            Formatted result ready for frontend display
        """
        metadata = result.get('metadata', {})
        collection = result.get('collection', '')

        # Determine result type
        result_type = 'command' if collection == 'ghl-knowledge-base' else 'documentation'

        # Get icon based on type
        icon = self._get_type_icon(collection)

        return {
            'id': result.get('id', ''),
            'title': metadata.get('title', 'Untitled'),
            'description': self._truncate(result.get('document', ''), 200),
            'collection': collection,
            'type': result_type,
            'relevance_score': result.get('relevance_score_normalized', 0),
            'has_examples': metadata.get('has_examples', False),
            'category': metadata.get('category', 'General'),
            'url': metadata.get('url', ''),
            'icon': icon,
            'metadata': metadata  # Include full metadata for detail views
        }

    def _get_type_icon(self, collection: str) -> str:
        """
        Get emoji icon for collection type

        Args:
            collection: Collection name

        Returns:
            Emoji icon string
        """
        icons = {
            'ghl-knowledge-base': '⚡',  # Commands
            'ghl-docs': '📚',            # Documentation
            'workflows': '🔄',           # Workflows (future)
            'conversations': '💬',       # Conversations (future)
            'templates': '📋',           # Templates (future)
            'setup': '⚙️',              # Setup guides (future)
            'api-endpoints': '🔌'        # API docs (future)
        }
        return icons.get(collection, '📄')

    def _truncate(self, text: str, max_length: int) -> str:
        """
        Truncate text to max length with ellipsis

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text
        """
        if not text:
            return ''

        text = text.strip()

        if len(text) <= max_length:
            return text

        return text[:max_length].rsplit(' ', 1)[0] + '...'
