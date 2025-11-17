"""
Conversation Routes for Chat History

Provides REST API endpoints for managing conversations and messages.
Follows the pattern from other route files in the codebase.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from chat.conversation_manager import get_conversation_manager
import logging

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/conversations", tags=["conversations"])
conversation_manager = get_conversation_manager()


# ============================================================================
# Pydantic Models (Request/Response)
# ============================================================================

class CreateConversationRequest(BaseModel):
    """Request to create a new conversation"""
    session_id: str = Field(..., description="Session identifier")
    title: Optional[str] = Field(None, description="Optional conversation title")


class UpdateConversationRequest(BaseModel):
    """Request to update conversation metadata"""
    title: Optional[str] = Field(None, description="New conversation title")
    archived: Optional[bool] = Field(None, description="Archive status")
    pinned: Optional[bool] = Field(None, description="Pin status")
    backend_type: Optional[str] = Field(None, description="Backend type (claude or gemini)")


class AddMessageRequest(BaseModel):
    """Request to add a message to a conversation"""
    role: str = Field(..., description="Message role (user or assistant)", pattern="^(user|assistant)$")
    content: str = Field(..., description="Message content", min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata (sources, timing, etc.)")


class MessageResponse(BaseModel):
    """Response containing a single message"""
    id: int
    role: str
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]]


class ConversationResponse(BaseModel):
    """Response containing conversation details"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ConversationListResponse(BaseModel):
    """Response containing list of conversations"""
    success: bool
    conversations: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/")
async def create_conversation(request: CreateConversationRequest) -> ConversationResponse:
    """
    Create a new conversation

    - **session_id**: User's session identifier (required)
    - **title**: Optional conversation title (auto-generated if not provided)

    Returns the created conversation with its ID
    """
    try:
        result = conversation_manager.create_conversation(
            session_id=request.session_id,
            title=request.title
        )

        if result.get('success'):
            return ConversationResponse(success=True, data=result)
        else:
            raise HTTPException(status_code=400, detail=result.get('error'))

    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_conversations(
    session_id: str = Query(..., description="Session identifier"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Results offset for pagination"),
    archived: bool = Query(False, description="Include archived conversations"),
    backend: Optional[str] = Query(None, description="Filter by backend type (claude or gemini)")
) -> ConversationListResponse:
    """
    Get all conversations for a session

    - **session_id**: User's session identifier (required)
    - **limit**: Maximum results (default: 100, max: 500)
    - **offset**: Pagination offset (default: 0)
    - **archived**: Include archived conversations (default: false)
    - **backend**: Filter by backend type ('claude' or 'gemini', optional)

    Returns list of conversations sorted by pinned status (pinned first), then most recently updated
    """
    try:
        result = conversation_manager.get_conversations(
            session_id=session_id,
            limit=limit,
            offset=offset,
            archived=archived,
            backend_type=backend
        )

        if result.get('success'):
            return ConversationListResponse(
                success=True,
                conversations=result.get('conversations', []),
                total=result.get('total', 0),
                limit=limit,
                offset=offset
            )
        else:
            raise HTTPException(status_code=400, detail=result.get('error'))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_conversations(
    session_id: str = Query(..., description="Session identifier"),
    q: str = Query(..., description="Search query"),
    backend: Optional[str] = Query(None, description="Filter by backend type (claude or gemini)"),
    archived: bool = Query(False, description="Include archived conversations"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
) -> ConversationListResponse:
    """
    Search conversations by message content using full-text search

    - **session_id**: User's session identifier (required)
    - **q**: Search query string (required)
    - **backend**: Filter by backend type ('claude' or 'gemini', optional)
    - **archived**: Include archived conversations (default: false)
    - **limit**: Maximum results (default: 20, max: 100)

    Returns conversations that contain matching message content, sorted by relevance and pinned status
    """
    try:
        result = conversation_manager.search_conversations(
            session_id=session_id,
            query=q,
            backend_type=backend,
            archived=archived,
            limit=limit
        )

        if result.get('success'):
            return ConversationListResponse(
                success=True,
                conversations=result.get('conversations', []),
                total=result.get('total', 0),
                limit=limit,
                offset=0
            )
        else:
            raise HTTPException(status_code=400, detail=result.get('error'))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str) -> ConversationResponse:
    """
    Get a conversation with all its messages

    - **conversation_id**: ID of the conversation to retrieve

    Returns the conversation details and all its messages ordered by timestamp
    """
    try:
        result = conversation_manager.get_conversation(conversation_id)

        if result.get('success'):
            return ConversationResponse(success=True, data=result)
        else:
            raise HTTPException(status_code=404, detail=result.get('error'))

    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest
) -> ConversationResponse:
    """
    Update conversation metadata (title, archived status, pin status, backend type)

    - **conversation_id**: ID of the conversation to update
    - **title**: New conversation title (optional)
    - **archived**: Archive status (optional, auto-unpins when set to true)
    - **pinned**: Pin status (optional)
    - **backend_type**: Backend type ('claude' or 'gemini', optional)

    Returns the updated conversation details
    """
    try:
        result = conversation_manager.update_conversation(
            conversation_id=conversation_id,
            title=request.title,
            archived=request.archived,
            pinned=request.pinned,
            backend_type=request.backend_type
        )

        if result.get('success'):
            return ConversationResponse(success=True, data=result)
        else:
            raise HTTPException(status_code=404, detail=result.get('error'))

    except Exception as e:
        logger.error(f"Error updating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str) -> ConversationResponse:
    """
    Delete a conversation and all its messages

    - **conversation_id**: ID of the conversation to delete

    Returns success status
    """
    try:
        result = conversation_manager.delete_conversation(conversation_id)

        if result.get('success'):
            return ConversationResponse(success=True, data=result)
        else:
            raise HTTPException(status_code=404, detail=result.get('error'))

    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{conversation_id}/messages")
async def add_message(
    conversation_id: str,
    request: AddMessageRequest
) -> ConversationResponse:
    """
    Add a message to a conversation

    - **conversation_id**: ID of the conversation
    - **role**: Message role ('user' or 'assistant') (required)
    - **content**: Message content (required)
    - **metadata**: Optional metadata object (sources, generation time, etc.)

    Returns the created message with its ID
    """
    try:
        result = conversation_manager.add_message(
            conversation_id=conversation_id,
            role=request.role,
            content=request.content,
            metadata=request.metadata
        )

        if result.get('success'):
            return ConversationResponse(success=True, data=result)
        else:
            raise HTTPException(status_code=400, detail=result.get('error'))

    except Exception as e:
        logger.error(f"Error adding message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Results offset for pagination")
) -> ConversationResponse:
    """
    Get messages from a conversation

    - **conversation_id**: ID of the conversation
    - **limit**: Maximum results (default: 100, max: 500)
    - **offset**: Pagination offset (default: 0)

    Returns list of messages sorted by timestamp (oldest first)
    """
    try:
        result = conversation_manager.get_messages(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )

        if result.get('success'):
            return ConversationResponse(success=True, data=result)
        else:
            raise HTTPException(status_code=404, detail=result.get('error'))

    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))
