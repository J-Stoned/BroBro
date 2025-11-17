"""
Gemini File Search Service
Integrates Google's File Search API with GHL WHIZ
"""

import os
import json
from google import genai
from google.genai import types
from typing import Optional, Dict, Any, List

class GeminiFileSearchService:
    """
    Service for querying GHL WHIZ knowledge base via Google File Search
    """
    
    def __init__(self):
        self.client = None
        self.store_id = None
        self.model = "gemini-2.5-pro"
        self._initialize()
    
    def _initialize(self):
        """Initialize the Gemini client and load store ID"""
        # Get API key from environment
        api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable required")

        # Initialize client with explicit API key (best practice)
        self.client = genai.Client(api_key=api_key)

        # Try environment variable first (preferred)
        self.store_id = os.environ.get('GEMINI_FILE_SEARCH_STORE_ID')

        # If not in environment, load from config file
        if not self.store_id:
            store_file = os.path.join(
                os.path.dirname(__file__),
                '..', '..', '..',
                'GOOGLE_FILE_SEARCH_STORE.txt'
            )

            if os.path.exists(store_file):
                with open(store_file, 'r') as f:
                    for line in f:
                        if line.startswith('Store ID:'):
                            self.store_id = line.split(':', 1)[1].strip()
                            break
    
    def is_configured(self) -> bool:
        """Check if service is properly configured"""
        return self.client is not None and self.store_id is not None
    
    def query(
        self, 
        question: str, 
        max_tokens: int = 2048,
        include_citations: bool = True
    ) -> Dict[str, Any]:
        """
        Query the knowledge base using semantic search
        
        Args:
            question: User's question
            max_tokens: Maximum response tokens
            include_citations: Whether to include source citations
            
        Returns:
            Dict with 'answer', 'citations', 'model', 'store_id'
        """
        if not self.is_configured():
            return {
                'error': 'Gemini File Search not configured. Missing store ID.',
                'answer': None,
                'citations': []
            }
        
        try:
            # Create the file search tool configuration using proper types
            file_search_config = types.FileSearch(
                fileSearchStoreNames=[self.store_id]
            )
            tool_config = types.Tool(fileSearch=file_search_config)

            response = self.client.models.generate_content(
                model=self.model,
                contents=question,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    tools=[tool_config]
                )
            )

            # Extract answer
            answer = response.text if hasattr(response, 'text') else str(response)

            # Extract citations if available
            citations = []
            if include_citations and hasattr(response, 'candidates'):
                for candidate in response.candidates:
                    if hasattr(candidate, 'grounding_metadata'):
                        metadata = candidate.grounding_metadata
                        if hasattr(metadata, 'grounding_chunks'):
                            for chunk in metadata.grounding_chunks:
                                citations.append({
                                    'source': getattr(chunk, 'source', 'Unknown'),
                                    'content': getattr(chunk, 'content', '')[:200]
                                })

            return {
                'answer': answer,
                'citations': citations,
                'model': self.model,
                'store_id': self.store_id,
                'success': True
            }

        except Exception as e:
            return {
                'error': str(e),
                'answer': None,
                'citations': [],
                'success': False
            }
    
    def get_default_system_prompt(self) -> str:
        """
        Get the default system prompt for grounded responses
        Enforces knowledge base usage and proper response style
        """
        return """You are an AI assistant powered by a comprehensive knowledge base containing:
- GoHighLevel official documentation and best practices
- Business strategy frameworks (Alex Hormozi, Russell Brunson)
- Cannabis tissue culture research and protocols
- YouTube tutorials and industry expertise

RESPONSE GUIDELINES:
1. ALWAYS prioritize information from the knowledge base
2. Ground your answers in retrieved documents - cite sources naturally
3. For tissue culture: provide specific protocols and research-backed information
4. For GHL: give exact setup steps and workflow configurations
5. For business: reference the frameworks and proven strategies from the knowledge base
6. If information isn't in the knowledge base, clearly state: "I don't have specific information about [topic] in my knowledge base"
7. NEVER fabricate technical details, procedures, or statistics

STYLE:
- Be direct and actionable
- Use numbered steps for procedures
- Explain the reasoning behind recommendations
- Keep responses focused (200-400 words unless more detail is needed)
- Ask clarifying questions when user intent is unclear"""

    def _extract_citations_from_response(self, response) -> List[Dict[str, Any]]:
        """
        Extract citations from Gemini response grounding metadata

        Args:
            response: Gemini API response object

        Returns:
            List of citation dictionaries with source and content
        """
        citations = []
        try:
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'grounding_metadata'):
                        metadata = candidate.grounding_metadata
                        if hasattr(metadata, 'grounding_chunks'):
                            for chunk in metadata.grounding_chunks:
                                citation = {
                                    'source': getattr(chunk, 'web', {}).get('title', 'Knowledge Base') if hasattr(chunk, 'web') else 'Knowledge Base',
                                    'url': getattr(chunk, 'web', {}).get('uri', '') if hasattr(chunk, 'web') else '',
                                    'content': getattr(chunk, 'content', '')[:200] if hasattr(chunk, 'content') else ''
                                }
                                if citation not in citations:  # Avoid duplicates
                                    citations.append(citation)
        except Exception as e:
            # Silently fail on citation extraction - response is still valid
            pass

        return citations

    def count_tokens(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> int:
        """
        Count tokens in message history using Gemini API

        Args:
            messages: List of messages to count
            system_prompt: Optional system prompt

        Returns:
            Total token count
        """
        if not self.client:
            # Fallback to estimation
            total_chars = sum(len(msg.get('content', '')) for msg in messages)
            if system_prompt:
                total_chars += len(system_prompt)
            return total_chars // 4  # Rough estimate: 4 chars = 1 token

        try:
            # Build contents in Gemini format
            contents = []
            if system_prompt and messages:
                first_msg = messages[0]
                combined_text = f"{system_prompt}\n\n[User Query: {first_msg['content']}]"
                contents.append({'role': 'user', 'parts': [{'text': combined_text}]})

                for msg in messages[1:]:
                    role = 'model' if msg['role'] == 'assistant' else 'user'
                    contents.append({
                        'role': role,
                        'parts': [{'text': msg['content']}]
                    })
            else:
                # No system prompt, just messages
                for msg in messages:
                    role = 'model' if msg['role'] == 'assistant' else 'user'
                    contents.append({
                        'role': role,
                        'parts': [{'text': msg['content']}]
                    })

            # Use Gemini's count_tokens API
            result = self.client.models.count_tokens(
                model=self.model,
                contents=contents
            )

            return result.total_tokens

        except Exception as e:
            # Fallback to estimation on error
            print(f"[WARNING] Token counting failed: {e}. Using estimation.")
            total_chars = sum(len(msg.get('content', '')) for msg in messages)
            if system_prompt:
                total_chars += len(system_prompt)
            return total_chars // 4

    def summarize_conversation(
        self,
        messages: List[Dict[str, str]],
        preserve_recent: int = 10
    ) -> Dict[str, Any]:
        """
        Summarize old conversation history, preserving recent messages

        Args:
            messages: Full message history
            preserve_recent: Number of recent messages to keep uncompacted

        Returns:
            Dict with compacted messages, summary, and token count
        """
        if len(messages) <= preserve_recent:
            return {
                'summary': None,
                'compacted_messages': messages,
                'token_count': self.count_tokens(messages),
                'compaction_performed': False
            }

        # Split messages: old to summarize, recent to preserve
        old_messages = messages[:-preserve_recent]
        recent_messages = messages[-preserve_recent:]

        # Build conversation text from old messages
        conversation_text = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in old_messages
        ])

        summary_prompt = f"""You are summarizing a conversation history to preserve context while reducing token usage.

CONVERSATION HISTORY TO SUMMARIZE:
{conversation_text}

Create a comprehensive but concise summary that:
1. Preserves all key facts, decisions, and context
2. Maintains technical details and specific recommendations
3. Notes any ongoing questions or unresolved issues
4. Uses a structured, scannable format

Format as:
## Previous Conversation Summary
**Topics Discussed:** [concise list]
**Key Recommendations:** [specific technical details]
**Important Context:** [facts to remember]
**Open Questions:** [any unresolved items]

Keep under 500 tokens while retaining ALL critical information."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=summary_prompt,
                config={
                    'max_output_tokens': 1000,
                    'temperature': 0.1  # Low temperature for factual accuracy
                }
            )

            summary_text = response.text

            # Create compacted message list with summary as first message
            compacted_messages = [
                {
                    'role': 'system',
                    'content': f"[Previous conversation summary]\n\n{summary_text}"
                },
                *recent_messages
            ]

            new_token_count = self.count_tokens(compacted_messages)

            print(f"[COMPACTION] Summarized {len(old_messages)} messages. Tokens: {self.count_tokens(messages)} → {new_token_count}")

            return {
                'summary': summary_text,
                'compacted_messages': compacted_messages,
                'token_count': new_token_count,
                'compaction_performed': True,
                'messages_summarized': len(old_messages),
                'messages_preserved': len(recent_messages)
            }

        except Exception as e:
            print(f"[ERROR] Summarization failed: {e}. Returning original messages.")
            return {
                'error': str(e),
                'summary': None,
                'compacted_messages': messages,
                'token_count': self.count_tokens(messages),
                'compaction_performed': False
            }

    def _generate_follow_up_questions(self, user_query: str, response_text: str) -> List[str]:
        """
        Generate intelligent follow-up questions based on the response

        Args:
            user_query: Original user question
            response_text: AI-generated response

        Returns:
            List of suggested follow-up questions
        """
        follow_ups = []

        # Extract key topics from response to generate relevant follow-ups
        topics = []

        # Simple topic extraction - look for capitalized phrases and technical terms
        import re

        # Extract phrases in bold or technical terms
        bold_phrases = re.findall(r'\*\*([^*]+)\*\*', response_text)
        topics.extend(bold_phrases[:3])

        # Generate contextual follow-up questions
        if 'setup' in user_query.lower() or 'how' in user_query.lower():
            if 'GHL' in response_text or 'GoHighLevel' in response_text:
                follow_ups.append("What are the next steps to activate this feature?")
            if 'best practice' in response_text.lower() or 'recommend' in response_text.lower():
                follow_ups.append("Are there any common mistakes to avoid?")

        if 'problem' in user_query.lower() or 'issue' in user_query.lower() or 'error' in user_query.lower():
            follow_ups.append("What troubleshooting steps would you recommend?")
            follow_ups.append("Are there workarounds if the standard approach doesn't work?")

        # Add a general deepening question
        if len(follow_ups) < 2:
            follow_ups.append("Can you elaborate on any specific aspect of this?")

        return follow_ups[:2]  # Return top 2 follow-up questions

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 50000,
        temperature: Optional[float] = 0.2,
        auto_compact: bool = True,
        compact_threshold: int = 1500000
    ) -> Dict[str, Any]:
        """
        Multi-turn chat with knowledge base context (falls back to regular chat if File Search not configured)

        Args:
            messages: List of {'role': 'user'/'assistant', 'content': '...'}
            system_prompt: Optional system instructions (uses default if not provided)
            max_tokens: Maximum response tokens
            auto_compact: Whether to auto-compact conversation at threshold
            compact_threshold: Token threshold for auto-compaction (1.5M for 2M context window)

        Returns:
            Dict with response and metadata including citations and follow-up questions
        """
        if not self.client:
            return {
                'error': 'Gemini API not configured',
                'answer': None,
                'success': False
            }

        try:
            # Use provided prompt or default
            if not system_prompt:
                system_prompt = self.get_default_system_prompt()

            # Check token count and auto-compact if needed
            if auto_compact and messages:
                token_count = self.count_tokens(messages, system_prompt)

                if token_count > compact_threshold:
                    print(f"[AUTO-COMPACT] Token count ({token_count}) exceeds threshold ({compact_threshold}). Compacting...")
                    compaction_result = self.summarize_conversation(
                        messages,
                        preserve_recent=10
                    )

                    if compaction_result['compaction_performed']:
                        messages = compaction_result['compacted_messages']
                        print(f"[AUTO-COMPACT] Successfully compacted. New token count: {compaction_result['token_count']}")

            # Build conversation content - prepend system prompt to first user message
            contents = []

            # Get the last user message for follow-up generation
            last_user_message = messages[-1]['content'] if messages else ''

            # Add system prompt as the first user message if there are messages
            if messages:
                # Combine system prompt with first user message
                first_msg = messages[0]
                combined_text = f"{system_prompt}\n\n[User Query: {first_msg['content']}]"
                contents.append({
                    'role': 'user',
                    'parts': [{'text': combined_text}]
                })

                # Add remaining messages
                for msg in messages[1:]:
                    role = 'model' if msg['role'] == 'assistant' else 'user'
                    contents.append({
                        'role': role,
                        'parts': [{'text': msg['content']}]
                    })
            else:
                # No messages, just system prompt
                contents = [{'role': 'user', 'parts': [{'text': system_prompt}]}]

            # If store_id is configured, use File Search; otherwise use regular chat
            tools = None
            if self.store_id:
                # Use File Search if configured
                file_search_config = types.FileSearch(
                    fileSearchStoreNames=[self.store_id]
                )
                tools = [types.Tool(fileSearch=file_search_config)]

            config = types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                tools=tools
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )

            response_text = response.text if hasattr(response, 'text') else str(response)

            # Extract citations from response metadata
            citations = self._extract_citations_from_response(response)

            # Generate intelligent follow-up questions
            follow_up_questions = self._generate_follow_up_questions(last_user_message, response_text)

            return {
                'answer': response_text,
                'success': True,
                'model': self.model,
                'response': response_text,
                'citations': citations,
                'follow_up_questions': follow_up_questions
            }

        except Exception as e:
            return {
                'error': str(e),
                'answer': None,
                'success': False
            }
    
    def get_store_info(self) -> Dict[str, Any]:
        """Get information about the configured store"""
        return {
            'store_id': self.store_id,
            'model': self.model,
            'configured': self.is_configured()
        }


# Singleton instance
_service_instance = None

def get_gemini_service() -> GeminiFileSearchService:
    """Get or create the Gemini File Search service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = GeminiFileSearchService()
    return _service_instance
