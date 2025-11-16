/**
 * Enhancement 9: Collaborator Cursor Component
 * Displays real-time cursor positions of other users
 */

import React from 'react';
import { MousePointer2 } from 'lucide-react';
import './CollaboratorCursor.css';

export function CollaboratorCursor({ cursorPositions }) {
  if (!cursorPositions || Object.keys(cursorPositions).length === 0) {
    return null;
  }

  return (
    <>
      {Object.entries(cursorPositions).map(([userId, position]) => (
        <div
          key={userId}
          className="collaborator-cursor"
          style={{
            left: `${position.x}px`,
            top: `${position.y}px`,
            '--cursor-color': position.user_color || '#667eea'
          }}
        >
          <MousePointer2
            size={20}
            fill={position.user_color || '#667eea'}
            color="white"
            strokeWidth={1}
            className="cursor-icon"
          />
          <div
            className="cursor-label"
            style={{ background: position.user_color || '#667eea' }}
          >
            {position.user_name}
          </div>
        </div>
      ))}
    </>
  );
}
