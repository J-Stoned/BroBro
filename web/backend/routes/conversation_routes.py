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


# ============================================================================
# USER PREFERENCES ENDPOINTS
# ============================================================================

class PreferencesRequest(BaseModel):
    """Request to update user preferences"""
    theme: Optional[str] = Field(None, description="Theme (light or dark)")
    notification_enabled: Optional[bool] = Field(None, description="Enable notifications")
    auto_save_enabled: Optional[bool] = Field(None, description="Enable auto-save")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Additional preferences JSON")


@router.get("/preferences")
async def get_preferences(session_id: str = Query(..., description="Session ID")) -> ConversationResponse:
    """
    Get user preferences for a session

    - **session_id**: Session identifier

    Returns user preferences (theme, notifications, etc.)
    """
    try:
        conn = conversation_manager._get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT theme, notification_enabled, auto_save_enabled,
                   preferences_json, created_at, updated_at
            FROM user_preferences
            WHERE session_id = ?
        """, (session_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            # Return defaults if no preferences exist
            return ConversationResponse(
                success=True,
                data={
                    "theme": "light",
                    "notification_enabled": True,
                    "auto_save_enabled": True,
                    "preferences": {}
                }
            )

        return ConversationResponse(
            success=True,
            data={
                "theme": row[0],
                "notification_enabled": bool(row[1]),
                "auto_save_enabled": bool(row[2]),
                "preferences": json.loads(row[3]) if row[3] else {},
                "created_at": row[4],
                "updated_at": row[5]
            }
        )
    except Exception as e:
        logger.error(f"Error fetching preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences")
async def update_preferences(
    session_id: str = Query(..., description="Session ID"),
    theme: Optional[str] = Query(None, description="Theme (light or dark)"),
    notification_enabled: Optional[bool] = Query(None, description="Enable notifications"),
    auto_save_enabled: Optional[bool] = Query(None, description="Enable auto-save"),
    preferences: Optional[str] = Query(None, description="Additional preferences as JSON string")
) -> ConversationResponse:
    """
    Update user preferences for a session

    - **session_id**: Session identifier
    - **theme**: Theme preference (light or dark)
    - **notification_enabled**: Enable notifications
    - **auto_save_enabled**: Enable auto-save
    - **preferences**: Additional preferences as JSON string
    """
    try:
        # Default values for optional parameters
        theme = theme or "light"
        notification_enabled = notification_enabled if notification_enabled is not None else True
        auto_save_enabled = auto_save_enabled if auto_save_enabled is not None else True

        # Parse preferences JSON
        prefs_json = "{}"
        if preferences:
            import json as json_lib
            prefs_json = json_lib.dumps(json_lib.loads(preferences))

        conn = conversation_manager._get_db_connection()
        cursor = conn.cursor()

        # Upsert preferences
        cursor.execute("""
            INSERT INTO user_preferences
            (session_id, theme, notification_enabled, auto_save_enabled, preferences_json, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(session_id) DO UPDATE SET
                theme = excluded.theme,
                notification_enabled = excluded.notification_enabled,
                auto_save_enabled = excluded.auto_save_enabled,
                preferences_json = excluded.preferences_json,
                updated_at = CURRENT_TIMESTAMP
        """, (session_id, theme, int(notification_enabled), int(auto_save_enabled), prefs_json))

        conn.commit()
        conn.close()

        return ConversationResponse(
            success=True,
            data={"message": "Preferences updated successfully"}
        )
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

def format_conversations_as_markdown(conversations: List[Dict]) -> str:
    """Format conversations as markdown"""
    from datetime import datetime
    output = ["# BroBro Conversation Export\n"]
    output.append(f"Exported: {datetime.now().isoformat()}\n")
    output.append(f"Total Conversations: {len(conversations)}\n\n")
    output.append("---\n\n")

    for conv in conversations:
        output.append(f"## {conv.get('title', 'Untitled')}\n")
        output.append(f"**Created:** {conv.get('created_at', 'Unknown')}\n")
        output.append(f"**Backend:** {conv.get('backend_type', 'claude')}\n")
        output.append(f"**ID:** {conv.get('id', 'Unknown')}\n\n")
        output.append("---\n\n")

    return "".join(output)


def format_conversations_as_json(conversations: List[Dict]) -> str:
    """Format conversations as JSON"""
    from datetime import datetime
    import json as json_lib

    export_data = {
        "exported_at": datetime.now().isoformat(),
        "total_conversations": len(conversations),
        "conversations": conversations
    }

    return json_lib.dumps(export_data, indent=2, ensure_ascii=False)


@router.post("/export")
async def export_conversations(
    session_id: str = Query(..., description="Session ID"),
    format_type: str = Query("json", description="Export format (json or markdown)", regex="^(json|markdown)$"),
    include_archived: bool = Query(True, description="Include archived conversations")
) -> ConversationResponse:
    """
    Export all conversations for a session

    - **session_id**: Session identifier
    - **format_type**: Export format (json or markdown)
    - **include_archived**: Whether to include archived conversations

    Returns conversation export data
    """
    try:
        # Get all conversations
        result = conversation_manager.get_conversations(
            session_id=session_id,
            include_archived=include_archived
        )

        if not result.get('success'):
            raise HTTPException(status_code=404, detail="No conversations found")

        conversations = result.get('data', [])

        # Format based on requested type
        if format_type == "markdown":
            content = format_conversations_as_markdown(conversations)
            return ConversationResponse(
                success=True,
                data={
                    "format": "markdown",
                    "content": content,
                    "filename": f"brobro-export.md"
                }
            )
        else:  # json
            content = format_conversations_as_json(conversations)
            return ConversationResponse(
                success=True,
                data={
                    "format": "json",
                    "content": json.loads(content),
                    "filename": f"brobro-export.json"
                }
            )
    except Exception as e:
        logger.error(f"Error exporting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
