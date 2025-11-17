# Chat History Sidebar Feature

## Overview
This feature implements a **LEFT-side collapsible sidebar** for managing chat conversation history with full CRUD operations, auto-save functionality, and auto-generated conversation titles.

## Architecture

### Backend (Python/FastAPI)

#### Database
- **Location**: `web/backend/database/conversations.db`
- **Manager**: `web/backend/chat/conversation_manager.py`
- **Tables**:
  - `conversations`: Stores conversation metadata
  - `messages`: Stores conversation messages

#### API Routes
- **Module**: `web/backend/routes/conversation_routes.py`
- **Base URL**: `/api/conversations`

**Endpoints**:
```
POST   /api/conversations                    # Create new conversation
GET    /api/conversations                    # List conversations (filter by session_id)
GET    /api/conversations/{id}               # Get conversation with messages
PUT    /api/conversations/{id}               # Update (rename, archive)
DELETE /api/conversations/{id}               # Delete conversation
POST   /api/conversations/{id}/messages      # Add message
GET    /api/conversations/{id}/messages      # Get messages (with pagination)
```

#### Registration
- Added to `web/backend/main.py` line 49 (import)
- Registered in `web/backend/main.py` line 182 (router inclusion)

### Frontend (React)

#### Core Components

1. **ChatHistorySidebar** (`ChatHistorySidebar.jsx`)
   - LEFT-side collapsible sidebar
   - Lists all conversations for current session
   - Create new, rename, delete conversations
   - Click to resume/load conversation
   - Auto-formatted timestamps (now, 5m ago, 2h ago, etc.)

2. **UnifiedChatContainer** (`UnifiedChatContainer.jsx`)
   - **Main integration point** for using the feature
   - Combines ChatHistorySidebar + ChatInterface/GeminiChatInterface
   - Handles conversation creation and selection
   - Manages sidebar collapse state
   - Provides auto-save callbacks

3. **Session Manager** (`utils/sessionManager.js`)
   - Generates/manages unique session IDs
   - Stores session ID in localStorage
   - Used to filter conversations by user/session

4. **Conversation API Client** (`api/conversationApi.js`)
   - All HTTP calls to backend
   - Handles error management
   - Convenience methods: renameConversation, archiveConversation, etc.

#### Styling
- **ChatHistorySidebar.css**: Left sidebar styling (320px width)
- **UnifiedChatContainer.css**: Layout integration

## Usage

### Basic Integration

In your main app component (e.g., `App.jsx`):

```jsx
import UnifiedChatContainer from './components/UnifiedChatContainer';

export default function App() {
  return (
    <UnifiedChatContainer defaultBackend="claude" />
  );
}
```

### Advanced Integration

If you want more control:

```jsx
import React, { useState } from 'react';
import ChatHistorySidebar from './components/ChatHistorySidebar';
import ChatInterface from './components/ChatInterface';
import { getSessionId } from './utils/sessionManager';
import * as conversationApi from './api/conversationApi';

export default function CustomChatSetup() {
  const [selectedConvId, setSelectedConvId] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const sessionId = getSessionId();

  const handleAutoSave = async (conversationId, role, content) => {
    if (conversationId) {
      await conversationApi.addMessage(conversationId, role, content);
    }
  };

  return (
    <div style={{ display: 'flex' }}>
      <ChatHistorySidebar
        currentConversationId={selectedConvId}
        onSelectConversation={setSelectedConvId}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <div style={{ flex: 1 }}>
        <ChatInterface
          conversationId={selectedConvId}
          onAutoSaveMessage={handleAutoSave}
        />
      </div>
    </div>
  );
}
```

## Features Implemented (MVP Phase 1)

✅ **Session-based user identification** (via localStorage)
✅ **Create new conversation** - Empty conversation ready for chat
✅ **List conversations** - Sorted by most recently updated
✅ **Resume conversation** - Click to load past messages
✅ **Rename conversation** - Inline edit or modal
✅ **Delete conversation** - With confirmation dialog
✅ **Auto-generated titles** - From first user message (first 50 chars)
✅ **Collapsible sidebar** - LEFT side, toggle button
✅ **Error handling** - Network errors, validation errors
✅ **Pagination** - Supports limit/offset for large conversation lists
✅ **Timestamps** - Smart formatting (now, 5m ago, 2h ago, Yesterday, etc.)

## Features for Phase 2 (Deferred)

- [ ] Google OAuth authentication
- [ ] Search conversations
- [ ] Archive conversations (soft delete)
- [ ] Export conversations
- [ ] Pin important conversations
- [ ] Filter by backend type (Claude/Gemini)
- [ ] Conversation sharing
- [ ] Multi-user support

## Testing

### Manual Testing Checklist

#### 1. Create Conversation
- [ ] Click "New Chat" button
- [ ] New conversation appears at top of list
- [ ] Conversation ID is generated (UUID)
- [ ] Conversation is empty (no messages)
- [ ] Timestamp shows "now"

#### 2. Send Messages
- [ ] Type message in input
- [ ] Click send or press Enter
- [ ] Message appears in chat
- [ ] Assistant response appears
- [ ] First message auto-generates title
- [ ] Title updates in sidebar (no need to refresh)

#### 3. Resume Conversation
- [ ] Create a conversation with messages
- [ ] Click on different conversation in sidebar
- [ ] Chat clears and loads messages from selected conversation
- [ ] All messages display correctly
- [ ] Markdown, sources, citations render properly

#### 4. Rename Conversation
- [ ] Hover over conversation in sidebar
- [ ] Click pencil (✏️) icon
- [ ] Title becomes editable input
- [ ] Type new title
- [ ] Press Enter or click away
- [ ] Sidebar updates with new title
- [ ] Backend is updated

#### 5. Delete Conversation
- [ ] Hover over conversation in sidebar
- [ ] Click trash (🗑️) icon
- [ ] Confirmation dialog appears
- [ ] Click confirm
- [ ] Conversation removed from sidebar
- [ ] Backend is updated

#### 6. Sidebar Collapse
- [ ] Click left arrow (◀) in sidebar header
- [ ] Sidebar collapses to thin strip (60px)
- [ ] Chat area expands to fill space
- [ ] Collapsed sidebar shows only icon button
- [ ] Click right arrow (▶) to expand
- [ ] Sidebar expands back to normal width

#### 7. Session Persistence
- [ ] Load app
- [ ] Create conversations
- [ ] Refresh page
- [ ] Same session ID is used (stored in localStorage)
- [ ] Conversations still appear in sidebar
- [ ] Clicking conversation loads messages from backend

#### 8. Error Handling
- [ ] Disconnect backend (stop server)
- [ ] Try to list conversations
- [ ] Error message appears in sidebar
- [ ] Dismiss error button works
- [ ] Restart backend
- [ ] Conversations load successfully

### Testing Steps

```bash
# 1. Start backend
cd web/backend
python -m uvicorn main:app --reload

# 2. Start frontend (in another terminal)
cd web/frontend
npm run dev

# 3. Open http://localhost:5173 (or your dev URL)

# 4. Test features from checklist above
```

### Debug Browser Console

Check browser DevTools Console for:
- Session ID generation
- API request logs
- Error messages
- Auto-save logs

### Check Backend Database

```python
# In Python REPL
import sqlite3
from pathlib import Path

db = sqlite3.connect("web/backend/database/conversations.db")
cursor = db.cursor()

# List conversations
cursor.execute("SELECT id, session_id, title, created_at FROM conversations")
print(cursor.fetchall())

# List messages for a conversation
cursor.execute("""
  SELECT id, role, content, timestamp FROM messages
  WHERE conversation_id = ?
  ORDER BY timestamp
""", ("CONVERSATION_ID_HERE",))
print(cursor.fetchall())

db.close()
```

## File Structure

```
web/
├── backend/
│   ├── chat/
│   │   ├── __init__.py
│   │   └── conversation_manager.py          # Database operations
│   ├── database/
│   │   └── conversations.db                 # SQLite database
│   ├── routes/
│   │   └── conversation_routes.py           # API endpoints
│   └── main.py                              # Register router
│
└── frontend/
    └── src/
        ├── components/
        │   ├── ChatHistorySidebar.jsx       # Sidebar component
        │   ├── ChatHistorySidebar.css       # Sidebar styles
        │   ├── UnifiedChatContainer.jsx     # Integration wrapper
        │   ├── UnifiedChatContainer.css     # Layout styles
        │   └── CHAT_HISTORY_FEATURE.md      # This file
        ├── api/
        │   └── conversationApi.js           # API client
        └── utils/
            └── sessionManager.js            # Session management
```

## Implementation Notes

### Key Decisions

1. **Session-based instead of Google OAuth** - Simpler implementation, can add OAuth later
2. **Separate database file** - `conversations.db` (not mixed with workflow DB)
3. **Client-side title generation** - Title from first message, fast & simple
4. **LEFT sidebar** - Per user requirement (opposite of NodeSidebar which is on right)
5. **Collapsible design** - Full hide option to maximize chat area
6. **Wrapper component pattern** - UnifiedChatContainer keeps ChatInterface unchanged

### Auto-Save Strategy

Currently, the feature is designed to auto-save messages when:
1. User sends a message (role='user')
2. Assistant responds (role='assistant')

Both save to backend automatically when:
- `conversationId` prop is provided to ChatInterface/GeminiChatInterface
- `onAutoSaveMessage` callback is triggered

### Title Generation

First user message is used to generate title:
- Takes first 50 characters
- Trims whitespace
- Updates conversation title via API

```javascript
const generateTitleFromMessage = (message) => {
  const maxLength = 50;
  const text = message.trim();
  return text.length <= maxLength ? text : text.substring(0, maxLength) + '...';
};
```

## Known Limitations

1. **localStorage quota** - Session ID stored in localStorage (small, ~50 bytes)
2. **No multi-window sync** - Changes in one tab don't reflect in another immediately
3. **No real-time updates** - Conversation list requires refresh to see new messages from other clients
4. **Basic search** - Phase 2 feature, not implemented yet

## Next Steps / Phase 2

See "Features for Phase 2" section above. Priority order:
1. Google OAuth (user identification)
2. Search conversations
3. Archive functionality
4. Export conversations

## Troubleshooting

### "Failed to list conversations" Error
- Check backend is running: `http://localhost:8000/docs`
- Check network tab in DevTools
- Check backend logs for errors
- Verify database file exists: `web/backend/database/conversations.db`

### Sidebar not showing
- Check import in your main component
- Verify CSS files are loaded
- Check browser console for component errors
- Ensure UnifiedChatContainer is rendering

### Messages not auto-saving
- Verify `conversationId` is passed to ChatInterface
- Check `onAutoSaveMessage` callback is provided
- Check backend API is accessible
- Look for errors in browser console

### Collapsed sidebar stuck
- Hard refresh browser (Ctrl+F5)
- Check browser localStorage isn't corrupted
- Clear localStorage and reload: `localStorage.clear()`

## Support & Contact

For issues or questions about this feature, see the main BroBro documentation or contact the development team.
