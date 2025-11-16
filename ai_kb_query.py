#!/usr/bin/env python3
"""
BroBro - AI-Powered Knowledge Base Query System
Industry-leading KB interaction with Claude API integration
"""

import os
import sys
import json
import time
from typing import List, Dict, Optional, Literal, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

import anthropic
from dotenv import load_dotenv
from search_api import MultiCollectionSearch, SearchResult

# Load environment variables from .env file
load_dotenv()

# Import elite Claude API manager
try:
    from src.services.claude import ClaudeAPIManager
    ELITE_API_AVAILABLE = True
except ImportError:
    ELITE_API_AVAILABLE = False
    print("[WARN] Elite ClaudeAPIManager not available, using standard client")


class QueryIntent(Enum):
    """Types of user query intents"""
    HOW_TO = "how_to"  # "How do I...?"
    WHAT_IS = "what_is"  # "What is...?"
    TROUBLESHOOTING = "troubleshooting"  # "Why isn't... working?"
    COMPARISON = "comparison"  # "What's the difference between...?"
    BEST_PRACTICE = "best_practice"  # "What's the best way to...?"
    FEATURE_REQUEST = "feature_request"  # "Can I...?" / "Does it support...?"
    EXPLANATION = "explanation"  # "Explain..."
    EXAMPLE = "example"  # "Show me an example..."
    GENERAL = "general"  # General query


class ResponseFormat(Enum):
    """Types of response formats"""
    CONVERSATIONAL = "conversational"  # Natural conversational answer
    STEP_BY_STEP = "step_by_step"  # Step-by-step guide
    COMPARISON_TABLE = "comparison_table"  # Side-by-side comparison
    SUMMARY = "summary"  # Concise summary
    DETAILED = "detailed"  # Detailed explanation
    CODE_EXAMPLE = "code_example"  # Code/configuration example


@dataclass
class ConversationMessage:
    """Single message in conversation history"""
    role: Literal['user', 'assistant']
    content: str
    timestamp: str
    query_intent: Optional[str] = None
    sources_used: Optional[List[str]] = None


@dataclass
class AIResponse:
    """AI-generated response with metadata"""
    answer: str
    sources: List[Dict]
    confidence: float
    query_intent: QueryIntent
    response_format: ResponseFormat
    follow_up_questions: List[str]
    processing_time_ms: float
    tokens_used: int


class AIKnowledgeBaseQuery:
    """
    AI-Powered Knowledge Base Query System

    Features:
    - Claude API integration for intelligent responses
    - Context-aware conversation management
    - Automatic source citation
    - Query intent detection
    - Response reranking and quality filtering
    - Interactive clarification
    - Multimodal output generation
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        chroma_host: str = "localhost",
        chroma_port: int = 8001,
        model: str = "claude-sonnet-4-5-20250929",
        max_history: int = 10
    ):
        """Initialize AI KB Query System"""

        print("="*80)
        print("BroBro - AI-Powered Knowledge Base Query System")
        print("="*80)

        # Initialize Anthropic client
        api_key = anthropic_api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")

        # Use elite API manager if available
        if ELITE_API_AVAILABLE:
            self.api_manager = ClaudeAPIManager(api_key)
            self.use_elite = True
            print(f"[OK] Elite Claude API Manager initialized (intelligent routing enabled)")
        else:
            self.client = anthropic.Anthropic(api_key=api_key)
            self.use_elite = False
            print(f"[OK] Claude API initialized (model: {model})")

        self.model = model

        # Initialize search engine
        print("[OK] Initializing hybrid search engine...")
        self.search = MultiCollectionSearch(
            chroma_host=chroma_host,
            chroma_port=chroma_port,
            enable_cache=True
        )

        # Conversation history
        self.conversation_history: List[ConversationMessage] = []
        self.max_history = max_history

        print("="*80)
        print("AI KB Query System Ready!")
        print("="*80)
        print()

    def query(
        self,
        user_query: str,
        n_results: int = 10,
        include_history: bool = True,
        format_preference: Optional[ResponseFormat] = None
    ) -> AIResponse:
        """
        Process user query and generate AI response

        Args:
            user_query: User's question
            n_results: Number of KB results to retrieve
            include_history: Whether to include conversation history
            format_preference: Preferred response format

        Returns:
            AIResponse object with answer and metadata
        """

        start_time = time.time()

        print(f"Processing query: \"{user_query}\"")
        print()

        # Step 1: Detect query intent
        query_intent = self._detect_intent(user_query)
        print(f"[OK] Query intent detected: {query_intent.value}")

        # Step 2: Search knowledge base
        print("[OK] Searching knowledge base...")
        kb_results = self.search.search(
            query=user_query,
            n_results=n_results,
            collection_filter='all'
        )

        # Step 3: Rerank and filter results
        print("[OK] Reranking results by relevance...")
        filtered_results = self._rerank_results(kb_results, user_query, query_intent)

        # Step 4: Determine response format
        response_format = format_preference or self._determine_format(query_intent, user_query)
        print(f"[OK] Response format: {response_format.value}")

        # Step 5: Generate AI response
        print("[OK] Generating AI response with Claude...")
        answer, tokens_used, follow_ups = self._generate_response(
            user_query=user_query,
            kb_results=filtered_results,
            query_intent=query_intent,
            response_format=response_format,
            include_history=include_history
        )

        # Step 6: Calculate confidence
        confidence = self._calculate_confidence(filtered_results, tokens_used)

        # Step 7: Update conversation history
        self._add_to_history(
            role='user',
            content=user_query,
            query_intent=query_intent.value
        )
        self._add_to_history(
            role='assistant',
            content=answer,
            sources_used=[r.metadata.get('title', r.content[:50]) for r in filtered_results[:3]]
        )

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        # Build response object
        response = AIResponse(
            answer=answer,
            sources=self._format_sources(filtered_results),
            confidence=confidence,
            query_intent=query_intent,
            response_format=response_format,
            follow_up_questions=follow_ups,
            processing_time_ms=processing_time,
            tokens_used=tokens_used
        )

        print(f"[OK] Response generated in {processing_time:.0f}ms")
        print(f"  Confidence: {confidence:.1%}")
        print(f"  Tokens used: {tokens_used}")
        print(f"  Sources: {len(filtered_results)}")
        print()

        return response

    def _detect_intent(self, query: str) -> QueryIntent:
        """Detect user's query intent using pattern matching and keywords"""
        query_lower = query.lower()

        # How-to patterns
        how_to_patterns = ['how do i', 'how to', 'how can i', 'steps to', 'guide to']
        if any(pattern in query_lower for pattern in how_to_patterns):
            return QueryIntent.HOW_TO

        # What-is patterns
        what_is_patterns = ['what is', 'what are', 'what does', 'define', 'meaning of']
        if any(pattern in query_lower for pattern in what_is_patterns):
            return QueryIntent.WHAT_IS

        # Troubleshooting patterns
        troubleshoot_patterns = ['not working', 'error', 'problem', 'issue', 'fix', 'troubleshoot', 'why isn\'t', 'why won\'t']
        if any(pattern in query_lower for pattern in troubleshoot_patterns):
            return QueryIntent.TROUBLESHOOTING

        # Comparison patterns
        comparison_patterns = ['difference between', 'compare', 'vs', 'versus', 'better than', 'which is']
        if any(pattern in query_lower for pattern in comparison_patterns):
            return QueryIntent.COMPARISON

        # Best practice patterns
        best_practice_patterns = ['best way', 'best practice', 'recommended', 'should i', 'optimal']
        if any(pattern in query_lower for pattern in best_practice_patterns):
            return QueryIntent.BEST_PRACTICE

        # Feature request patterns
        feature_patterns = ['can i', 'is it possible', 'does it support', 'can you', 'is there a way']
        if any(pattern in query_lower for pattern in feature_patterns):
            return QueryIntent.FEATURE_REQUEST

        # Example patterns
        example_patterns = ['example', 'show me', 'demonstrate', 'sample']
        if any(pattern in query_lower for pattern in example_patterns):
            return QueryIntent.EXAMPLE

        # Explanation patterns
        explanation_patterns = ['explain', 'describe', 'tell me about', 'elaborate']
        if any(pattern in query_lower for pattern in explanation_patterns):
            return QueryIntent.EXPLANATION

        return QueryIntent.GENERAL

    def _determine_format(self, intent: QueryIntent, query: str) -> ResponseFormat:
        """Determine optimal response format based on intent"""
        format_map = {
            QueryIntent.HOW_TO: ResponseFormat.STEP_BY_STEP,
            QueryIntent.TROUBLESHOOTING: ResponseFormat.STEP_BY_STEP,
            QueryIntent.COMPARISON: ResponseFormat.COMPARISON_TABLE,
            QueryIntent.WHAT_IS: ResponseFormat.DETAILED,
            QueryIntent.BEST_PRACTICE: ResponseFormat.DETAILED,
            QueryIntent.EXAMPLE: ResponseFormat.CODE_EXAMPLE,
            QueryIntent.EXPLANATION: ResponseFormat.DETAILED,
            QueryIntent.FEATURE_REQUEST: ResponseFormat.CONVERSATIONAL,
            QueryIntent.GENERAL: ResponseFormat.CONVERSATIONAL
        }

        return format_map.get(intent, ResponseFormat.CONVERSATIONAL)

    def _rerank_results(
        self,
        results: List[SearchResult],
        query: str,
        intent: QueryIntent
    ) -> List[SearchResult]:
        """Rerank and filter results based on quality and relevance"""

        # Filter low-quality results
        MIN_CONFIDENCE = 0.3
        filtered = [r for r in results if r.hybrid_score >= MIN_CONFIDENCE]

        # Apply intent-specific boosts
        for result in filtered:
            boost = 1.0

            # Boost YouTube for how-to queries
            if intent == QueryIntent.HOW_TO and result.source == 'youtube':
                boost = 1.15

            # Boost docs for what-is queries
            elif intent == QueryIntent.WHAT_IS and result.source == 'documentation':
                boost = 1.10

            # Boost commands for troubleshooting
            elif intent == QueryIntent.TROUBLESHOOTING and result.source == 'command':
                boost = 1.12

            result.hybrid_score *= boost

        # Re-sort with new scores
        filtered.sort(key=lambda x: x.hybrid_score, reverse=True)

        # Limit to top results
        return filtered[:8]

    def _generate_response(
        self,
        user_query: str,
        kb_results: List[SearchResult],
        query_intent: QueryIntent,
        response_format: ResponseFormat,
        include_history: bool
    ) -> Tuple[str, int, List[str]]:
        """Generate AI response using Claude API"""

        # Build context from KB results
        context = self._build_context(kb_results)

        # Build conversation history
        history_context = ""
        if include_history and self.conversation_history:
            history_context = self._build_history_context()

        # Build system prompt
        system_prompt = self._build_system_prompt(query_intent, response_format)

        # Build user message
        user_message = f"""User Query: {user_query}

{history_context}

Knowledge Base Context:
{context}

Please provide a comprehensive answer following the {response_format.value} format."""

        # Call Claude API
        try:
            if self.use_elite:
                # Use elite API manager with intelligent routing
                elite_response = self.api_manager.send_message(
                    messages=[{"role": "user", "content": user_message}],
                    profile="detailed-analysis",  # Use detailed-analysis profile for KB queries
                    system_prompt=system_prompt,
                    user_id="kb_query",
                    endpoint="/api/kb/query"
                )

                if not elite_response.success:
                    raise Exception(f"Elite API call failed: {elite_response.error}")

                answer = elite_response.content
                tokens_used = elite_response.input_tokens + elite_response.output_tokens
                print(f"[ELITE] Cost: ${elite_response.cost:.6f} | Model: {elite_response.model_used} | Cached: {elite_response.cached_tokens}")
            else:
                # Fallback to standard client
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=12000,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )

                answer = response.content[0].text
                tokens_used = response.usage.input_tokens + response.usage.output_tokens

            # Generate follow-up questions
            follow_ups = self._generate_follow_ups(user_query, query_intent, kb_results)

            return answer, tokens_used, follow_ups

        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(f"ERROR: {error_msg}")
            return error_msg, 0, []

    def _build_system_prompt(self, intent: QueryIntent, format: ResponseFormat) -> str:
        """Build system prompt based on intent and format"""

        base_prompt = """You are BroBro, an expert AI assistant specializing in GoHighLevel (GHL) automation, workflows, and best practices. Your role is to provide accurate, helpful, and actionable answers based on the knowledge base context provided.

Key Guidelines:
1. ALWAYS cite your sources using [Source: Title/Video] format
2. Be specific and actionable - provide concrete steps when possible
3. If information is incomplete, acknowledge it and suggest what to look for
4. Use GHL terminology correctly
5. Prioritize recent information from YouTube videos over older documentation
6. If multiple approaches exist, explain the pros/cons
7. Never make up information - only use what's in the context"""

        format_instructions = {
            ResponseFormat.STEP_BY_STEP: "\n\nFormat your response as clear, numbered steps. Start with prerequisites if needed.",
            ResponseFormat.COMPARISON_TABLE: "\n\nFormat your response as a comparison. Use bullet points or tables to show differences clearly.",
            ResponseFormat.DETAILED: "\n\nProvide a comprehensive, detailed explanation. Break down complex concepts.",
            ResponseFormat.CODE_EXAMPLE: "\n\nProvide concrete examples with explanations. Show exact steps or configurations.",
            ResponseFormat.CONVERSATIONAL: "\n\nBe conversational and natural. Provide a direct, helpful answer.",
            ResponseFormat.SUMMARY: "\n\nBe concise and to-the-point. Summarize key information."
        }

        intent_instructions = {
            QueryIntent.HOW_TO: "\n\nFocus on practical implementation steps.",
            QueryIntent.TROUBLESHOOTING: "\n\nFocus on identifying the problem and providing solutions.",
            QueryIntent.COMPARISON: "\n\nHighlight key differences and use cases for each option.",
            QueryIntent.BEST_PRACTICE: "\n\nEmphasize recommended approaches and common pitfalls to avoid.",
            QueryIntent.FEATURE_REQUEST: "\n\nClearly state what's possible and any limitations."
        }

        return base_prompt + format_instructions.get(format, "") + intent_instructions.get(intent, "")

    def _build_context(self, results: List[SearchResult]) -> str:
        """Build context string from KB results"""
        if not results:
            return "No relevant information found in knowledge base."

        context_parts = []
        for idx, result in enumerate(results, 1):
            source_type = result.source.upper()
            title = result.metadata.get('title', 'Untitled')

            context_parts.append(f"[Source {idx}] {source_type}: {title}")
            context_parts.append(f"Relevance: {result.hybrid_score:.1%}")
            context_parts.append(f"Content: {result.content}")
            context_parts.append("-" * 40)

        return "\n".join(context_parts)

    def _build_history_context(self) -> str:
        """Build conversation history context"""
        if not self.conversation_history:
            return ""

        # Get last few messages
        recent_history = self.conversation_history[-6:]  # Last 3 exchanges

        history_parts = ["Previous Conversation:"]
        for msg in recent_history:
            role_label = "User" if msg.role == "user" else "Assistant"
            history_parts.append(f"{role_label}: {msg.content[:200]}")

        history_parts.append("")
        return "\n".join(history_parts)

    def _generate_follow_ups(
        self,
        query: str,
        intent: QueryIntent,
        results: List[SearchResult]
    ) -> List[str]:
        """Generate relevant follow-up questions"""

        follow_ups = []

        if intent == QueryIntent.HOW_TO:
            follow_ups = [
                "What are common mistakes to avoid?",
                "Are there any prerequisites I should know about?",
                "Can you show me a complete example?"
            ]
        elif intent == QueryIntent.TROUBLESHOOTING:
            follow_ups = [
                "What are other common causes of this issue?",
                "How can I prevent this in the future?",
                "Are there any related issues I should check?"
            ]
        elif intent == QueryIntent.COMPARISON:
            follow_ups = [
                "Which option is better for my use case?",
                "What are the performance differences?",
                "Can these be used together?"
            ]
        else:
            follow_ups = [
                "Can you explain this in more detail?",
                "Are there any examples available?",
                "What are the best practices for this?"
            ]

        return follow_ups[:3]

    def _calculate_confidence(self, results: List[SearchResult], tokens: int) -> float:
        """Calculate confidence score for the response"""
        if not results:
            return 0.0

        # Average relevance of top 3 results
        avg_relevance = sum(r.hybrid_score for r in results[:3]) / min(3, len(results))

        # Boost confidence if we have multiple sources
        source_diversity_boost = min(len(set(r.source for r in results[:5])) / 3, 1.0)

        # Penalize if very few results
        result_count_factor = min(len(results) / 5, 1.0)

        confidence = (avg_relevance * 0.6) + (source_diversity_boost * 0.2) + (result_count_factor * 0.2)

        return min(confidence, 0.99)  # Cap at 99%

    def _format_sources(self, results: List[SearchResult]) -> List[Dict]:
        """Format sources for response"""
        sources = []
        for result in results:
            source = {
                'type': result.source,
                'title': result.metadata.get('title', 'Untitled'),
                'relevance': result.hybrid_score,
                'content_preview': result.content[:200]
            }

            if 'url' in result.metadata:
                source['url'] = result.metadata['url']
            if 'category' in result.metadata:
                source['category'] = result.metadata['category']

            sources.append(source)

        return sources

    def _add_to_history(self, role: str, content: str, query_intent: str = None, sources_used: List[str] = None):
        """Add message to conversation history"""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            query_intent=query_intent,
            sources_used=sources_used
        )

        self.conversation_history.append(message)

        # Trim history if too long
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("Conversation history cleared.")

    def get_history(self) -> List[Dict]:
        """Get conversation history as list of dicts"""
        return [asdict(msg) for msg in self.conversation_history]

    def export_conversation(self, filepath: str):
        """Export conversation to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.get_history(), f, indent=2, ensure_ascii=False)
        print(f"Conversation exported to: {filepath}")


def format_response(response: AIResponse) -> str:
    """Format AI response for display"""
    output = []

    output.append("=" * 80)
    output.append("AI RESPONSE")
    output.append("=" * 80)
    output.append("")

    # Main answer
    output.append(response.answer)
    output.append("")

    # Metadata
    output.append("=" * 80)
    output.append("METADATA")
    output.append("=" * 80)
    output.append(f"Confidence: {response.confidence:.1%}")
    output.append(f"Intent: {response.query_intent.value}")
    output.append(f"Format: {response.response_format.value}")
    output.append(f"Processing Time: {response.processing_time_ms:.0f}ms")
    output.append(f"Tokens Used: {response.tokens_used}")
    output.append("")

    # Sources
    if response.sources:
        output.append("=" * 80)
        output.append("SOURCES")
        output.append("=" * 80)
        for idx, source in enumerate(response.sources[:5], 1):
            output.append(f"[{idx}] {source['type'].upper()}: {source['title']}")
            output.append(f"    Relevance: {source['relevance']:.1%}")
            if 'url' in source:
                output.append(f"    URL: {source['url']}")
            output.append("")

    # Follow-up questions
    if response.follow_up_questions:
        output.append("=" * 80)
        output.append("FOLLOW-UP QUESTIONS")
        output.append("=" * 80)
        for q in response.follow_up_questions:
            output.append(f"  • {q}")
        output.append("")

    return "\n".join(output)


def main():
    """Interactive CLI for AI KB Query System"""
    import argparse

    parser = argparse.ArgumentParser(description='BroBro AI Knowledge Base Query')
    parser.add_argument('query', nargs='*', help='Query to ask')
    parser.add_argument('--api-key', help='Anthropic API key (or set ANTHROPIC_API_KEY env var)')
    parser.add_argument('--no-history', action='store_true', help='Disable conversation history')
    parser.add_argument('--export', help='Export conversation to file')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')

    args = parser.parse_args()

    try:
        # Initialize system
        ai_kb = AIKnowledgeBaseQuery(anthropic_api_key=args.api_key)

        if args.interactive or not args.query:
            # Interactive mode
            print("Interactive mode. Type 'quit' to exit, 'clear' to clear history.")
            print()

            while True:
                try:
                    query = input("\nYour question: ").strip()

                    if not query:
                        continue

                    if query.lower() in ['quit', 'exit', 'q']:
                        break

                    if query.lower() == 'clear':
                        ai_kb.clear_history()
                        continue

                    # Process query
                    response = ai_kb.query(
                        user_query=query,
                        include_history=not args.no_history
                    )

                    # Display response
                    print()
                    print(format_response(response))

                except KeyboardInterrupt:
                    print("\n\nExiting...")
                    break
                except Exception as e:
                    print(f"\nError: {e}")

            # Export if requested
            if args.export:
                ai_kb.export_conversation(args.export)

        else:
            # Single query mode
            query = ' '.join(args.query)

            response = ai_kb.query(
                user_query=query,
                include_history=False
            )

            print(format_response(response))

            if args.export:
                ai_kb.export_conversation(args.export)

    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set ANTHROPIC_API_KEY environment variable or use --api-key flag")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
