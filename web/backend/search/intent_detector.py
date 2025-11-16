"""
Query Intent Detection for Intelligent Search Routing
Built with BMAD-METHOD for Epic US: Unified Search

Detects user intent from search queries to:
- Prioritize relevant collections
- Boost appropriate result types
- Provide better suggestions
"""

class QueryIntentDetector:
    """Detects user intent from search queries"""

    INTENT_PATTERNS = {
        'HOW_TO': [
            'how', 'how to', 'how do i', 'how can i',
            'steps to', 'guide to', 'tutorial', 'guide for'
        ],
        'WHAT_IS': [
            'what is', 'what are', 'define', 'explain',
            'tell me about', 'describe', 'meaning of'
        ],
        'EXAMPLE': [
            'example', 'show me', 'sample', 'demo',
            'template', 'examples of', 'can you show'
        ],
        'FIND': [
            'find', 'search', 'locate', 'where',
            'which', 'show', 'get', 'looking for'
        ],
        'SETUP': [
            'setup', 'configure', 'install', 'initialize',
            'connect', 'integrate', 'set up'
        ],
        'TROUBLESHOOT': [
            'error', 'not working', 'fix', 'problem',
            'issue', 'help', 'broken', 'failed', 'cant', "can't"
        ],
        'LIST': [
            'list', 'all', 'show all', 'available',
            'options', 'what can', 'give me all'
        ]
    }

    def detect_intent(self, query: str) -> str:
        """
        Detect primary intent from query

        Args:
            query: User's search query

        Returns:
            One of: HOW_TO, WHAT_IS, EXAMPLE, FIND,
                   SETUP, TROUBLESHOOT, LIST, GENERAL
        """
        if not query:
            return 'GENERAL'

        query_lower = query.lower().strip()

        # Check each intent pattern
        for intent, keywords in self.INTENT_PATTERNS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return intent

        return 'GENERAL'

    def get_collection_preference(self, intent: str) -> dict:
        """
        Return which collections to prioritize based on intent

        Args:
            intent: Detected intent type

        Returns:
            {
                'primary': str,    # Collection to boost most
                'secondary': str,  # Secondary collection
                'boost': int       # Points to add to primary
            }
        """
        # NOTE: ghl-knowledge-base currently empty, but ready for when populated
        preferences = {
            'HOW_TO': {
                'primary': 'ghl-knowledge-base',  # Commands show "how to"
                'secondary': 'ghl-docs',
                'boost': 30
            },
            'WHAT_IS': {
                'primary': 'ghl-docs',  # Docs explain concepts
                'secondary': 'ghl-knowledge-base',
                'boost': 35
            },
            'EXAMPLE': {
                'primary': 'ghl-knowledge-base',  # Commands have examples
                'secondary': 'ghl-docs',
                'boost': 25
            },
            'FIND': {
                'primary': 'ghl-knowledge-base',  # Finding specific commands
                'secondary': 'ghl-docs',
                'boost': 20
            },
            'SETUP': {
                'primary': 'ghl-docs',  # Setup guides in docs
                'secondary': 'ghl-knowledge-base',
                'boost': 30
            },
            'TROUBLESHOOT': {
                'primary': 'ghl-docs',  # Troubleshooting guides in docs
                'secondary': 'ghl-knowledge-base',
                'boost': 25
            },
            'LIST': {
                'primary': 'ghl-knowledge-base',  # Lists of commands
                'secondary': 'ghl-docs',
                'boost': 20
            }
        }

        return preferences.get(intent, {
            'primary': 'ghl-docs',  # Default to docs
            'secondary': 'ghl-knowledge-base',
            'boost': 0
        })
