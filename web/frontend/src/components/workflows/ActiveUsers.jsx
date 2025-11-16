/**
 * Enhancement 9: Active Users Component
 * Display active collaborators in sidebar
 */

import React from 'react';
import { Users, Circle } from 'lucide-react';
import './ActiveUsers.css';

export function ActiveUsers({ users, currentUserId }) {
  if (!users || users.length === 0) {
    return null;
  }

  const getInitials = (name) => {
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return parts[0][0] + parts[1][0];
    }
    return name.substring(0, 2);
  };

  const formatLastSeen = (isoString) => {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) {
      return 'just now';
    } else if (diff < 3600000) {
      const mins = Math.floor(diff / 60000);
      return `${mins}m ago`;
    } else if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000);
      return `${hours}h ago`;
    }
    return 'inactive';
  };

  const isActive = (lastSeen) => {
    const diff = new Date() - new Date(lastSeen);
    return diff < 300000; // Active if seen in last 5 minutes
  };

  return (
    <div className="active-users-panel">
      <div className="active-users-header">
        <Users size={16} />
        <span>Active Users ({users.length})</span>
      </div>

      <div className="active-users-list">
        {users.map((user) => (
          <div
            key={user.user_id}
            className={`user-item ${user.user_id === currentUserId ? 'current-user' : ''}`}
          >
            <div
              className="user-avatar"
              style={{ background: user.user_color || '#667eea' }}
            >
              {getInitials(user.user_name)}
            </div>

            <div className="user-info">
              <div className="user-name">
                {user.user_name}
                {user.user_id === currentUserId && (
                  <span className="you-badge">(You)</span>
                )}
              </div>
              <div className="user-status">
                <Circle
                  size={8}
                  fill={isActive(user.last_seen) ? '#10b981' : '#9ca3af'}
                  color={isActive(user.last_seen) ? '#10b981' : '#9ca3af'}
                />
                <span>{formatLastSeen(user.last_seen)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
