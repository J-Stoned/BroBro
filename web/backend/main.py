"""
BroBro Web Backend - FastAPI Server
Built with BMAD-METHOD for Epic 7: Setup Management
Updated: 2025-10-30
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
import sys
import os
import logging
from dotenv import load_dotenv
from anthropic import Anthropic, AsyncAnthropic
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables from .env file
load_dotenv()

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import middleware components
from middleware.logging_middleware import LoggingMiddleware
from middleware.performance_middleware import PerformanceMiddleware
from utils.error_logger import StructuredLogger as ErrorLogger, configure_logging

# Configure structured error logging
configure_logging(log_level=os.getenv('LOG_LEVEL', 'INFO'))

# Import GHL routes
from routes.ghl_routes import router as ghl_router
# Import Workflow routes (Epic 12)
from routes.workflow_routes import router as workflow_router
# Import Analytics routes (Epic 13)
from routes.analytics_routes import router as analytics_router
# Import Workflow Testing routes (Enhancement 5)
from routes.workflow_testing_routes import router as workflow_testing_router
# Import Search Analytics routes (Enhancement 6)
from routes.search_analytics_routes import router as search_analytics_router
# Import AI Generation routes (Enhancement 8)
from routes.ai_generation_routes import router as ai_generation_router
# Import Version Control routes (Enhancement 9)
from routes.version_control_routes import router as version_control_router
# Import Gemini File Search routes (Google AI Integration)
from routes.gemini_routes import router as gemini_router
# Import Conversation/Chat History routes
from routes.conversation_routes import router as conversation_router
# Import Collaboration WebSocket (Enhancement 9)
from websocket.collaboration_server import collaboration_manager
from fastapi import WebSocket, WebSocketDisconnect


# Utility function to strip tool blocks from conversation history
def strip_tool_blocks_from_message(content):
    """
    Strip tool_use and tool_result blocks from message content.
    Returns cleaned text-only content.
    
    Args:
        content: Either a string or list of content blocks
    
    Returns:
        str: Text-only content
    """
    if isinstance(content, str):
        return content
    
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return " ".join(text_parts).strip() if text_parts else ""
    
    return str(content)


# Initialize FastAPI app with comprehensive OpenAPI/Swagger documentation
app = FastAPI(
    title="BroBro API",
    description="""
    # BroBro - GoHighLevel Expert AI Assistant

    Production-ready REST API powered by:
    - **Gemini File Search** for semantic knowledge base queries
    - **Claude API** for intelligent response synthesis
    - **Real-time WebSocket** for collaborative workflows

    ## Key Features
    - 🔍 Semantic search across GHL documentation and best practices
    - 🤖 AI-powered answers using Claude Sonnet/Haiku
    - ⚡ Rate limiting (10 req/min on /api/chat)
    - 🔐 Input validation and security hardening
    - 📊 Analytics and workflow management
    - 🌐 WebSocket support for real-time collaboration

    ## Authentication
    All endpoints require proper API key configuration in `.env`:
    - `ANTHROPIC_API_KEY` - For Claude API
    - `GOOGLE_API_KEY` - For Gemini File Search

    ## Rate Limits
    - `/api/chat`: 10 requests/minute (expensive Claude calls)
    - Other endpoints: No limit
    """,
    version="2.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "chat",
            "description": "Chat and QA endpoints",
        },
        {
            "name": "search",
            "description": "Knowledge base search endpoints",
        },
        {
            "name": "workflows",
            "description": "Workflow management and execution",
        },
        {
            "name": "analytics",
            "description": "Analytics and performance metrics",
        },
        {
            "name": "gemini",
            "description": "Direct Gemini File Search integration",
        },
    ]
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Custom exception handler for rate limit exceeded
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Maximum 10 requests per minute allowed."}
    )

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # From env variable or default to dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register middleware stack (order matters - LIFO for request processing)
# Performance tracking should be before logging to capture accurate timing
app.add_middleware(PerformanceMiddleware)
app.add_middleware(LoggingMiddleware)

# Register GHL API routes (Epic 11: API Integration)
app.include_router(ghl_router)

# Register Workflow routes (Epic 12: Advanced Features)
app.include_router(workflow_router)

# Register Analytics routes (Epic 13: Analytics & Performance)
app.include_router(analytics_router)

# Register Workflow Testing routes (Enhancement 5)
app.include_router(workflow_testing_router)

# Register Search Analytics routes (Enhancement 6)
app.include_router(search_analytics_router)

# Register AI Generation routes (Enhancement 8)
app.include_router(ai_generation_router)

# Register Version Control routes (Enhancement 9)
app.include_router(version_control_router)

# Register Gemini File Search routes (Google AI Integration)
app.include_router(gemini_router)

# Register Conversation/Chat History routes
app.include_router(conversation_router)

# Initialize Claude API client (Gemini File Search initialized in gemini_routes)
claude_client: Optional[Anthropic] = None

# Request/Response Models
class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query", min_length=1)
    n_results: int = Field(5, description="Number of results to return", ge=1, le=50)
    collection_filter: Optional[Literal['commands', 'docs', 'both']] = Field(
        'both',
        description="Filter by collection type"
    )
    include_metadata: bool = Field(True, description="Include metadata in results")


class SearchResponseItem(BaseModel):
    content: str
    relevance_score: float
    source: str
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResponseItem]
    total_results: int
    search_time_ms: float
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    message: str
    chroma_connected: bool
    collections: Dict[str, int]
    model_loaded: bool
    timestamp: str


class CollectionInfo(BaseModel):
    name: str
    count: int
    description: str


class SystemInfo(BaseModel):
    chroma_host: str
    chroma_port: int
    collections: List[CollectionInfo]
    embedding_model: str
    total_documents: int


class ChatRequest(BaseModel):
    query: str = Field(..., description="User's question", min_length=1)
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Previous conversation messages")
    n_results: int = Field(5, description="Number of KB results to use as context", ge=1, le=20)


class ChatResponse(BaseModel):
    success: bool
    answer: str
    sources: List[SearchResponseItem]
    search_time_ms: float
    generation_time_ms: float
    total_time_ms: float
    timestamp: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize backend services on startup (Gemini File Search + Claude API)"""
    global claude_client

    # Debug: Log Python environment
    import sys
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python version: {sys.version}")

    # Debug: Check google-genai version
    try:
        import google.genai
        logger.info(f"google-genai module location: {google.genai.__file__}")
        from google.genai import types
        logger.info(f"types module location: {types.__file__}")
        logger.info(f"types.FileSearch exists: {hasattr(types, 'FileSearch')}")
    except Exception as e:
        logger.error(f"Error checking google-genai: {e}")

    try:
        # Initialize Claude API client (for /api/chat synthesis)
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            claude_client = AsyncAnthropic(api_key=anthropic_api_key)
            logger.info("Claude API client initialized successfully (async)")
        else:
            logger.warning("ANTHROPIC_API_KEY not found - Chat endpoint will not work")
            logger.warning("Please set ANTHROPIC_API_KEY environment variable")
            claude_client = None

        # Check Gemini API (primary search method)
        gemini_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            logger.info("Gemini API configured - Ready for File Search queries")
        else:
            logger.warning("Gemini API not configured - Set GOOGLE_API_KEY or GEMINI_API_KEY")

        logger.info("BroBro Backend initialized: Gemini File Search + Claude API")

    except Exception as e:
        logger.error(f"Failed to initialize backend: {e}", exc_info=True)
        claude_client = None


# Health check endpoint with sampling to reduce logging noise
# Track health check calls to implement sampling
import random
_health_check_counter = 0
_health_check_sample_rate = 0.1  # Log 10% of health checks (every ~10th call)

@app.get("/health", response_model=HealthResponse)
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring system status
    Available at both /health and /api/health for frontend compatibility

    BroBro Backend uses Gemini File Search (primary) + Claude API (synthesis).
    No ChromaDB dependency - cloud-based knowledge management via Gemini.

    Logging: Health checks are sampled (10%) to reduce log noise from monitoring.
    """
    global _health_check_counter
    _health_check_counter += 1

    # Determine if this health check should be logged
    should_log_health = random.random() < _health_check_sample_rate

    # Check if Gemini API key is configured (the primary search method)
    gemini_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')

    # Check if Claude API is available (for /api/chat endpoint synthesis)
    claude_api_key = os.getenv('ANTHROPIC_API_KEY')

    # Determine overall health
    # Backend is healthy if both APIs are configured
    apis_available = {
        'gemini': bool(gemini_api_key),
        'claude': bool(claude_api_key)
    }

    is_healthy = all(apis_available.values())  # Both APIs required

    if is_healthy:
        if should_log_health:
            logger.debug(f"Health check #{_health_check_counter}: OK (sampled)")
        return HealthResponse(
            status="healthy",
            message="BroBro Backend operational - Gemini File Search + Claude API ready",
            chroma_connected=False,  # ChromaDB no longer used
            collections={},  # Collections managed by Gemini File Search (cloud)
            model_loaded=True,
            timestamp=datetime.now().isoformat()
        )
    else:
        missing_apis = [k for k, v in apis_available.items() if not v]
        logger.warning(f"Health check #{_health_check_counter}: FAILED - Missing APIs: {missing_apis}")
        return HealthResponse(
            status="unhealthy",
            message=f"Missing required APIs: {', '.join(missing_apis)}. Set GOOGLE_API_KEY and ANTHROPIC_API_KEY.",
            chroma_connected=False,
            collections={},
            model_loaded=False,
            timestamp=datetime.now().isoformat()
        )


# System info endpoint (Epic 7: Setup Management)
@app.get("/api/system/info", response_model=SystemInfo)
async def get_system_info():
    """
    Get detailed system information
    Epic 7: Setup Management - System monitoring

    BroBro uses Gemini File Search for knowledge base management (cloud-hosted).
    """
    try:
        # All collections are now managed by Gemini File Search (cloud)
        # Document counts are not available locally
        return SystemInfo(
            chroma_host="cloud",
            chroma_port=0,
            collections=[
                CollectionInfo(
                    name="ghl-knowledge-base",
                    count=0,  # Managed by Gemini File Search
                    description="GHL commands and knowledge base (Gemini File Search)"
                ),
                CollectionInfo(
                    name="ghl-docs",
                    count=0,  # Managed by Gemini File Search
                    description="GHL documentation (Gemini File Search)"
                )
            ],
            embedding_model="Google Gemini (adaptive)",
            total_documents=0  # Tracked in Gemini File Search
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")


# Get all commands endpoint (for Command Library)
@app.get("/api/commands/all")
async def get_all_commands():
    """
    Get all GHL commands from knowledge base
    Used by CommandLibrary component to display all available commands

    NOTE: Commands are now managed by Gemini File Search.
    Use /api/gemini/query endpoint for command searches.
    """
    raise HTTPException(
        status_code=501,
        detail="Endpoint deprecated. Use /api/gemini/query to search commands via Gemini File Search."
    )


# Search endpoint
@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Multi-collection semantic search endpoint
    Uses Gemini File Search for knowledge base queries
    """
    try:
        import time
        start_time = time.time()

        # Use Gemini File Search for semantic search
        from gemini.file_search_service import get_gemini_service
        gemini_service = get_gemini_service()

        if not gemini_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Gemini File Search not configured. Please set GOOGLE_API_KEY and GEMINI_FILE_SEARCH_STORE_ID."
            )

        # Query Gemini File Search
        gemini_result = gemini_service.query(
            question=request.query,
            max_tokens=2048,
            include_citations=True
        )

        search_time_ms = (time.time() - start_time) * 1000

        if not gemini_result.get('success', False):
            raise HTTPException(
                status_code=500,
                detail=f"Gemini search failed: {gemini_result.get('error', 'Unknown error')}"
            )

        # Extract citations as search results
        response_items = []
        citations = gemini_result.get('citations', [])
        for citation in citations[:request.n_results]:
            response_items.append(SearchResponseItem(
                content=citation.get('text', ''),
                relevance_score=0.95,  # Gemini doesn't provide scores
                source=citation.get('source', 'Gemini File Search'),
                metadata={
                    'title': citation.get('title', 'Source'),
                    'source': 'gemini-file-search'
                }
            ))

        return SearchResponse(
            query=request.query,
            results=response_items,
            total_results=len(response_items),
            search_time_ms=round(search_time_ms, 2),
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# Quick search endpoint (GET method for simple queries)
@app.get("/api/search/quick")
async def quick_search(
    q: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(5, description="Number of results", ge=1, le=20)
):
    """
    Quick search endpoint using GET method
    Useful for simple queries and testing
    """
    request = SearchRequest(query=q, n_results=limit)
    return await search(request)


# Chat endpoint - AI-powered responses using Claude API + Gemini File Search
@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """
    AI-powered chat endpoint using Claude API + Gemini File Search

    Uses Google's Gemini File Search for knowledge base queries and Claude for synthesis.
    Provides actionable insights based on GHL documentation, commands, and best practices.

    Features:
    - Gemini File Search for semantic search across knowledge base
    - Claude AI synthesis for natural, expert-level responses
    - Source attribution and citations from documents
    - Conversation history support for multi-turn conversations
    """
    if claude_client is None:
        raise HTTPException(
            status_code=503,
            detail="Claude API not initialized. Please set ANTHROPIC_API_KEY environment variable."
        )

    try:
        import time
        start_time = time.time()

        # Step 1: Search knowledge base using Gemini File Search
        search_start = time.time()

        # Get Gemini service and query the knowledge base
        from gemini.file_search_service import get_gemini_service
        gemini_service = get_gemini_service()

        search_results = []
        context = ""

        if gemini_service.is_configured():
            # Query Gemini File Search
            gemini_result = gemini_service.query(
                question=chat_request.query,
                max_tokens=2048,
                include_citations=True
            )

            if gemini_result.get('success', False):
                # Build context from Gemini result
                context = gemini_result.get('answer', '')

                # Extract citations as sources
                citations = gemini_result.get('citations', [])
                for i, citation in enumerate(citations[:chat_request.n_results], 1):
                    search_results.append(SearchResponseItem(
                        content=citation.get('text', ''),
                        relevance_score=0.95,  # Gemini doesn't provide scores, use high default
                        source=citation.get('source', 'Gemini File Search'),
                        metadata={
                            'title': citation.get('title', 'Source'),
                            'source': 'gemini-file-search'
                        }
                    ))
            else:
                raise HTTPException(
                    status_code=503,
                    detail=f"Gemini File Search error: {gemini_result.get('error', 'Unknown error')}"
                )
        else:
            raise HTTPException(
                status_code=503,
                detail="Gemini File Search not configured. Please set GOOGLE_API_KEY and GEMINI_FILE_SEARCH_STORE_ID."
            )

        search_time_ms = (time.time() - search_start) * 1000

        # Step 3: Build conversation messages for Claude
        messages = []
        
        # Environment variable to force text-only mode (strips all tool blocks)
        FORCE_TEXT_ONLY = os.getenv('CLAUDE_FORCE_TEXT_ONLY', 'false').lower() == 'true'

        # Add conversation history if provided
        # CRITICAL FIX: Handle tool_use/tool_result blocks properly
        if chat_request.conversation_history:
            # We need to validate the entire conversation for tool_use/tool_result pairing
            validated_messages = []

            for i, msg in enumerate(chat_request.conversation_history):
                # Skip messages with media
                if 'image' in msg or 'images' in msg or 'media' in msg:
                    logger.warning(f"Skipping message {i} that contains image/media field")
                    continue

                role = msg.get("role", "user")
                if role not in ("user", "assistant"):
                    logger.warning(f"Invalid role '{role}' in message {i}, defaulting to 'user'")
                    role = "user"

                content = msg.get("content", "")

                # Handle both string content and array content (for tool use/results)
                if isinstance(content, str):
                    # Simple string content - clean it
                    content = content.strip()
                    if not content:
                        logger.warning(f"Empty content in message {i}, skipping")
                        continue

                    # Size check: 1MB per message max
                    content_size = len(content.encode('utf-8'))
                    if content_size > 1000000:
                        logger.warning(f"Message {i} too large ({content_size} bytes), truncating")
                        content = content[:500000]
                    
                    validated_messages.append({
                        "role": role,
                        "content": content
                    })
                    
                elif isinstance(content, list):
                    # Array content - likely has tool_use or tool_result blocks
                    
                    # FORCE TEXT ONLY MODE: Strip all tool blocks if enabled
                    if FORCE_TEXT_ONLY:
                        text_only_content = strip_tool_blocks_from_message(content)
                        if text_only_content:
                            validated_messages.append({
                                "role": role,
                                "content": text_only_content
                            })
                        continue
                    
                    # CRITICAL: We need to check if tool_result blocks have matching tool_use
                    
                    # Check for tool_result blocks without checking for tool_use in previous message
                    has_tool_result = any(
                        isinstance(block, dict) and block.get("type") == "tool_result"
                        for block in content
                    )
                    
                    if has_tool_result and role == "user":
                        # This is a tool_result message - we need to verify previous message has tool_use
                        if not validated_messages or validated_messages[-1]["role"] != "assistant":
                            logger.error(f"Message {i} has tool_result but previous message is not from assistant")
                            logger.error(f"Stripping tool_use/tool_result blocks and converting to text-only")

                            # Extract only text content, skip tool blocks
                            text_only = []
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    text_only.append(block.get("text", ""))

                            if text_only:
                                validated_messages.append({
                                    "role": role,
                                    "content": " ".join(text_only).strip()
                                })
                            continue

                        # Check if previous assistant message has matching tool_use
                        prev_content = validated_messages[-1]["content"]
                        if isinstance(prev_content, list):
                            tool_use_ids = {
                                block.get("id")
                                for block in prev_content
                                if isinstance(block, dict) and block.get("type") == "tool_use"
                            }

                            tool_result_ids = {
                                block.get("tool_use_id")
                                for block in content
                                if isinstance(block, dict) and block.get("type") == "tool_result"
                            }

                            if not tool_result_ids.issubset(tool_use_ids):
                                logger.error(f"Message {i} has tool_result IDs that don't match previous tool_use IDs")
                                logger.error(f"  tool_use IDs: {tool_use_ids}")
                                logger.error(f"  tool_result IDs: {tool_result_ids}")
                                logger.error(f"Removing BOTH messages to break the invalid chain")
                                
                                # Remove the previous assistant message too since they're a broken pair
                                if validated_messages:
                                    validated_messages.pop()
                                continue
                    
                    # If we get here, the message structure looks valid
                    validated_messages.append({
                        "role": role,
                        "content": content
                    })
                else:
                    logger.warning(f"Message {i} has invalid content type: {type(content)}, skipping")
                    continue

            # Use the validated messages
            messages = validated_messages
            logger.info(f"Validated {len(messages)} messages from conversation history")

        # Add current query with Gemini File Search context
        # Gemini already provided relevant context, Claude will refine and expand on it
        user_message = f"""User Question: {chat_request.query}

Relevant Information from GHL Knowledge Base (via Gemini File Search):
{context}

Please provide a detailed, actionable answer based on the knowledge base information above. Include specific steps, best practices, and examples where relevant. If the knowledge base doesn't fully address the question, acknowledge what's known and what might need clarification."""

        messages.append({
            "role": "user",
            "content": user_message
        })

        # Step 4: Call Claude API
        generation_start = time.time()

        system_prompt = """You are an expert GoHighLevel consultant and automation specialist. Your role is to provide detailed, actionable guidance on using GoHighLevel (GHL) for marketing automation, CRM, workflows, and AI features.

Guidelines:
- Provide clear, step-by-step instructions when explaining how to do something
- Reference specific GHL features, menus, and settings by name
- Include best practices and common pitfalls to avoid
- Use examples to illustrate concepts
- Be specific about field names, values, and configuration options
- When discussing workflows or automations, explain the logic and reasoning
- If the context doesn't fully answer the question, acknowledge what's known and what might need clarification
- Keep responses concise but comprehensive - aim for depth without unnecessary verbosity

Focus on practical, implementable advice that users can apply immediately to their GHL accounts."""

        # Smart model selection: Use Haiku for speed, Sonnet for deep thinking
        use_sonnet = any(phrase in chat_request.query.lower() for phrase in [
            "think really hard",
            "think deeply",
            "analyze deeply",
            "detailed analysis",
            "complex",
            "architecture"
        ])

        model = "claude-sonnet-4-5-20250929" if use_sonnet else "claude-haiku-4-5-20250929"
        max_tokens = 12000 if use_sonnet else 6000

        response = await claude_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages
        )

        generation_time_ms = (time.time() - generation_start) * 1000

        # Extract Claude's response
        answer = response.content[0].text if response.content else "I apologize, but I couldn't generate a response."

        # Step 5: Format response
        total_time_ms = (time.time() - start_time) * 1000

        # Convert search results to response format
        source_items = [
            SearchResponseItem(
                content=result.content,
                relevance_score=result.relevance_score,
                source=result.source,
                metadata=result.metadata
            )
            for result in search_results
        ]

        return ChatResponse(
            success=True,
            answer=answer,
            sources=source_items,
            search_time_ms=round(search_time_ms, 2),
            generation_time_ms=round(generation_time_ms, 2),
            total_time_ms=round(total_time_ms, 2),
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.get("/api/search/unified")
async def search_unified(
    query: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(20, description="Max results to return", ge=1, le=50),
    user_id: Optional[str] = Query(None, description="Optional user ID for personalization")
):
    """
    Unified Intelligent Search using Gemini File Search

    Uses Gemini File Search for intent-aware, multi-collection search.

    Features:
    - Semantic search across all knowledge base collections
    - Result grouping by relevance
    - Fast response times via Gemini File Search

    Returns:
        {
            "success": true,
            "data": {
                "query": "send sms",
                "total_results": 15,
                "results": [...],
                "search_time_ms": 156.23
            }
        }
    """
    try:
        import time
        start_time = time.time()

        # Use Gemini File Search for unified search
        from gemini.file_search_service import get_gemini_service
        gemini_service = get_gemini_service()

        if not gemini_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Gemini File Search not configured. Please set GOOGLE_API_KEY and GEMINI_FILE_SEARCH_STORE_ID."
            )

        # Query Gemini File Search
        gemini_result = gemini_service.query(
            question=query,
            max_tokens=2048,
            include_citations=True
        )

        search_time_ms = (time.time() - start_time) * 1000

        if not gemini_result.get('success', False):
            error_msg = gemini_result.get('error', 'Unknown error')
            logger.error(f"Gemini search failed: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Search failed: {error_msg}"
            )

        # Extract results from Gemini response
        citations = gemini_result.get('citations', [])
        results_array = []
        for i, citation in enumerate(citations[:limit]):
            results_array.append({
                'id': f"result-{i}",
                'title': citation.get('title', 'Result'),
                'content': citation.get('text', ''),
                'source': citation.get('source', 'Gemini File Search'),
                'relevance_score': 0.95
            })

        # Restructure results to match frontend expectations
        top_answer = results_array[0] if results_array else None
        results_structured = {
            "topAnswer": top_answer,
            "documentation": results_array,
            "commands": [],
            "total_by_type": {
                "documentation": len(results_array),
                "commands": 0
            }
        }

        return {
            "success": True,
            "data": {
                "query": query,
                "intent": "GENERAL_SEARCH",
                "total_results": len(results_array),
                "results": results_structured,
                "suggestions": [],
                "search_time_ms": round(search_time_ms, 2)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unified search failed: {e}", exc_info=True)

        return {
            "success": False,
            "error": str(e),
            "data": {
                "query": query,
                "intent": "GENERAL_SEARCH",
                "total_results": 0,
                "results": {
                    "topAnswer": None,
                    "documentation": [],
                    "commands": [],
                    "total_by_type": {
                        "documentation": 0,
                        "commands": 0
                    }
                },
                "suggestions": [],
                "search_time_ms": 0
            }
        }


# Collections endpoint
@app.get("/api/collections")
async def list_collections():
    """
    List all available collections and their stats
    Epic 7: Setup Management - Collection monitoring

    Collections are now managed by Gemini File Search (cloud-hosted).
    """
    try:
        # All collections are managed by Gemini File Search
        # Document counts are tracked in Gemini, not locally
        return {
            "collections": [
                {
                    "name": "ghl-knowledge-base",
                    "count": 0,  # Managed by Gemini File Search
                    "type": "commands",
                    "description": "GHL commands and knowledge base (Gemini File Search)"
                },
                {
                    "name": "ghl-docs",
                    "count": 0,  # Managed by Gemini File Search
                    "type": "documentation",
                    "description": "GHL official documentation (Gemini File Search)"
                }
            ],
            "total_documents": 0  # Tracked in Gemini File Search
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "BroBro API",
        "version": "1.0.0",
        "description": "GoHighLevel Expert AI Assistant - Multi-Collection Semantic Search",
        "endpoints": {
            "health": "/health",
            "search": "/api/search",
            "quick_search": "/api/search/quick?q=your+query",
            "system_info": "/api/system/info",
            "collections": "/api/collections"
        },
        "docs": "/docs",
        "status": "operational"
    }


# Enhancement 9: WebSocket collaboration endpoint
@app.websocket("/ws/collaborate")
async def websocket_collaborate(
    websocket: WebSocket,
    workflow_id: str = 'default-workflow',
    user_id: str = 'anonymous',
    user_name: str = 'Anonymous User',
    user_color: str = '#667eea'
):
    """
    WebSocket endpoint for real-time collaboration

    Query parameters:
    - workflow_id: The workflow being edited (optional, defaults to 'default-workflow')
    - user_id: Unique user identifier (optional, defaults to 'anonymous')
    - user_name: Display name (optional, defaults to 'Anonymous User')
    - user_color: Cursor/highlight color (optional, defaults to '#667eea')
    """
    try:
        await collaboration_manager.connect(
            websocket,
            workflow_id,
            user_id,
            user_name,
            user_color
        )
    except Exception as e:
        logger.error(f"WebSocket connection failed: {e}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass
        return

    try:
        while True:
            # Receive message from client
            message = await websocket.receive_json()

            # Handle the message
            await collaboration_manager.handle_message(websocket, message)

    except WebSocketDisconnect:
        # Handle disconnect
        disconnect_info = collaboration_manager.disconnect(websocket)

        if disconnect_info:
            # Notify others about the disconnect
            await collaboration_manager.broadcast(
                disconnect_info['workflow_id'],
                {
                    'type': 'user_left',
                    'user_id': disconnect_info['user_id'],
                    'locks_released': disconnect_info['locks_released']
                }
            )


if __name__ == "__main__":
    import uvicorn

    # ALWAYS use port 8000 - no fallback!
    port = 8000
    logger.info(f"Starting BroBro Backend on port {port}...")
    logger.info(f"Backend URL: http://localhost:{port}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disabled to prevent module caching issues
        log_level="info",
        timeout_keep_alive=600  # 10 minute keep-alive for long-running requests
    )
