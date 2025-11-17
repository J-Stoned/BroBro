"""
Gemini File Search API Routes
Provides endpoints for querying the GHL WHIZ knowledge base via Google File Search
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from gemini.file_search_service import get_gemini_service

router = APIRouter(prefix="/api/gemini", tags=["gemini"])


class QueryRequest(BaseModel):
    question: str
    max_tokens: Optional[int] = 2048
    include_citations: Optional[bool] = True


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = 50000
    temperature: Optional[float] = 0.2  # 0.0 (factual) to 1.0 (creative)


@router.get("/status")
async def get_status():
    """Check if Gemini File Search is configured and ready"""
    service = get_gemini_service()
    info = service.get_store_info()
    return {
        "status": "ready" if info['configured'] else "not_configured",
        "store_id": info['store_id'],
        "model": info['model'],
        "message": "Gemini File Search is ready" if info['configured'] 
                   else "Store ID not configured. Run upload script first."
    }


@router.post("/query")
async def query_knowledge_base(request: QueryRequest):
    """
    Query the GHL WHIZ knowledge base

    Returns AI-generated answer with citations from your documents
    """
    service = get_gemini_service()

    if not service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Gemini File Search not configured. Please set GOOGLE_API_KEY and run the upload script."
        )

    result = service.query(
        question=request.question,
        max_tokens=request.max_tokens,
        include_citations=request.include_citations
    )

    if not result.get('success', False):
        # Use categorized error response with proper status code
        status_code = result.get('status_code', 500)
        error_detail = {
            'error': result.get('error', 'Unknown error'),
            'error_type': result.get('error_type'),
            'retry_after': result.get('retry_after')
        }
        raise HTTPException(status_code=status_code, detail=error_detail)

    return result


@router.post("/chat")
async def chat_with_knowledge_base(request: ChatRequest):
    """
    Multi-turn chat with knowledge base context

    Maintains conversation history for follow-up questions
    """
    service = get_gemini_service()

    if not service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Gemini File Search not configured"
        )

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    result = service.chat(
        messages=messages,
        system_prompt=request.system_prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )

    if not result.get('success', False):
        # Use categorized error response with proper status code
        status_code = result.get('status_code', 500)
        error_detail = {
            'error': result.get('error', 'Unknown error'),
            'error_type': result.get('error_type'),
            'retry_after': result.get('retry_after')
        }
        raise HTTPException(status_code=status_code, detail=error_detail)

    return result


@router.post("/suggest")
async def get_suggestions(request: QueryRequest):
    """
    Get AI-powered suggestions for a GHL task
    
    Uses knowledge base to provide actionable recommendations
    """
    service = get_gemini_service()
    
    if not service.is_configured():
        raise HTTPException(status_code=503, detail="Gemini File Search not configured")
    
    # Enhanced prompt for suggestions
    enhanced_question = f"""Based on the GHL documentation and best practices, provide specific actionable suggestions for:

{request.question}

Format your response as:
1. Clear step-by-step recommendations
2. Reference specific GHL features or settings
3. Include any relevant warnings or best practices
4. Mention related features they should consider"""
    
    result = service.query(
        question=enhanced_question,
        max_tokens=request.max_tokens,
        include_citations=request.include_citations
    )
    
    return result


@router.post("/compact")
async def compact_conversation(request: ChatRequest):
    """
    Compact conversation history by summarizing old messages

    Triggered when conversation approaches token limits
    Returns summary and compacted message list
    """
    service = get_gemini_service()

    if not service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Gemini File Search not configured"
        )

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    result = service.summarize_conversation(
        messages=messages,
        preserve_recent=10
    )

    if result.get('error'):
        # Use categorized error response with proper status code
        status_code = result.get('status_code', 500)
        error_detail = {
            'error': result['error'],
            'error_type': result.get('error_type'),
            'retry_after': result.get('retry_after')
        }
        raise HTTPException(status_code=status_code, detail=error_detail)

    return {
        'summary': result['summary'],
        'token_count': result['token_count'],
        'compacted_messages': result['compacted_messages'],
        'compaction_performed': result['compaction_performed'],
        'messages_summarized': result.get('messages_summarized', 0),
        'messages_preserved': result.get('messages_preserved', 0)
    }


@router.post("/count-tokens")
async def count_conversation_tokens(request: ChatRequest):
    """
    Count tokens in conversation without making a chat request

    Useful for monitoring token usage and determining if compaction is needed
    """
    service = get_gemini_service()

    if not service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Gemini File Search not configured"
        )

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    token_count = service.count_tokens(
        messages=messages,
        system_prompt=request.system_prompt
    )

    CONTEXT_WINDOW = 2097152  # Gemini 2.5 Pro: 2M tokens
    WARNING_THRESHOLD = 1000000  # 50% of context window
    COMPACT_THRESHOLD = 1500000  # 75% of context window

    utilization_percent = (token_count / CONTEXT_WINDOW) * 100

    return {
        'token_count': token_count,
        'message_count': len(messages),
        'context_window': CONTEXT_WINDOW,
        'utilization_percent': round(utilization_percent, 2),
        'warning_threshold': WARNING_THRESHOLD,
        'compact_threshold': COMPACT_THRESHOLD,
        'should_warn': token_count > WARNING_THRESHOLD,
        'should_compact': token_count > COMPACT_THRESHOLD
    }


@router.get("/examples")
async def get_example_queries():
    """Get example queries to try"""
    return {
        "examples": [
            "How do I set up email deliverability with DKIM and SPF?",
            "What's the best workflow for lead nurturing?",
            "How do I configure AI chatbot for lead qualification?",
            "What are best practices for SMS campaigns?",
            "How do I set up reputation management automation?",
            "What's the process for setting up a funnel?",
            "How do I integrate webhooks with workflows?",
            "What are tissue culture sterilization protocols?",
            "How does Alex Hormozi recommend pricing offers?",
            "What's the $100M Leads acquisition strategy?"
        ]
    }
