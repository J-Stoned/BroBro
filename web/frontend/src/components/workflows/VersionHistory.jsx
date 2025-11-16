/**
 * Enhancement 9: Version History Component
 * Displays commit history with timeline and diff viewing
 */

import React, { useState, useEffect } from 'react';
import { GitCommit, GitBranch, Tag, Clock, User, ChevronRight, Eye, RotateCcw } from 'lucide-react';
import './VersionHistory.css';

export function VersionHistory({ workflowId, currentBranch, onRestore, onClose }) {
  const [history, setHistory] = useState([]);
  const [branches, setBranches] = useState([]);
  const [tags, setTags] = useState([]);
  const [selectedCommit, setSelectedCommit] = useState(null);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('history'); // history, branches, tags

  useEffect(() => {
    if (workflowId) {
      loadHistory();
      loadBranches();
      loadTags();
    }
  }, [workflowId, currentBranch]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/version-control/history/${workflowId}?branch=${currentBranch}&limit=50`
      );
      const data = await response.json();

      if (data.success) {
        setHistory(data.data.commits || []);
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadBranches = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/version-control/branches/${workflowId}`
      );
      const data = await response.json();

      if (data.success) {
        setBranches(data.data.branches || []);
      }
    } catch (err) {
      console.error('Failed to load branches:', err);
    }
  };

  const loadTags = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/version-control/tags/${workflowId}`
      );
      const data = await response.json();

      if (data.success) {
        setTags(data.data.tags || []);
      }
    } catch (err) {
      console.error('Failed to load tags:', err);
    }
  };

  const handleRestore = async (commitId) => {
    if (!confirm('Restore workflow to this version? Current changes will be lost.')) {
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/api/version-control/restore/${commitId}`
      );
      const data = await response.json();

      if (data.success && onRestore) {
        onRestore(data.data.workflow);
      }
    } catch (err) {
      console.error('Failed to restore:', err);
    }
  };

  const handleViewDiff = async (commitId) => {
    // View diff between this commit and parent
    try {
      const commit = history.find((c) => c.commit_id === commitId);
      if (!commit || !commit.parent) {
        alert('No parent commit to compare');
        return;
      }

      const response = await fetch(
        `http://localhost:8000/api/version-control/diff/${commit.parent}/${commitId}`
      );
      const data = await response.json();

      if (data.success) {
        setSelectedCommit({
          ...commit,
          diff: data.data
        });
      }
    } catch (err) {
      console.error('Failed to load diff:', err);
    }
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;

    // Less than 1 hour
    if (diff < 3600000) {
      const mins = Math.floor(diff / 60000);
      return `${mins} minute${mins !== 1 ? 's' : ''} ago`;
    }

    // Less than 24 hours
    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000);
      return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    }

    // Less than 7 days
    if (diff < 604800000) {
      const days = Math.floor(diff / 86400000);
      return `${days} day${days !== 1 ? 's' : ''} ago`;
    }

    // Full date
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="version-history-panel">
      {/* Header */}
      <div className="version-header">
        <h3>Version History</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      {/* Tabs */}
      <div className="version-tabs">
        <button
          className={`tab ${view === 'history' ? 'active' : ''}`}
          onClick={() => setView('history')}
        >
          <GitCommit size={16} />
          <span>History</span>
        </button>
        <button
          className={`tab ${view === 'branches' ? 'active' : ''}`}
          onClick={() => setView('branches')}
        >
          <GitBranch size={16} />
          <span>Branches</span>
        </button>
        <button
          className={`tab ${view === 'tags' ? 'active' : ''}`}
          onClick={() => setView('tags')}
        >
          <Tag size={16} />
          <span>Tags</span>
        </button>
      </div>

      {/* Content */}
      <div className="version-content">
        {/* History View */}
        {view === 'history' && (
          <div className="history-view">
            {loading ? (
              <div className="loading">Loading history...</div>
            ) : history.length === 0 ? (
              <div className="empty">No commits yet</div>
            ) : (
              <div className="commit-timeline">
                {history.map((commit, idx) => (
                  <div key={commit.commit_id} className="commit-item">
                    <div className="commit-dot"></div>
                    {idx < history.length - 1 && <div className="commit-line"></div>}

                    <div className="commit-card">
                      <div className="commit-header">
                        <div className="commit-info">
                          <GitCommit size={14} />
                          <span className="commit-id">{commit.commit_id.substring(0, 7)}</span>
                        </div>
                        <div className="commit-actions">
                          <button
                            className="action-btn"
                            onClick={() => handleViewDiff(commit.commit_id)}
                            title="View changes"
                          >
                            <Eye size={14} />
                          </button>
                          <button
                            className="action-btn"
                            onClick={() => handleRestore(commit.commit_id)}
                            title="Restore to this version"
                          >
                            <RotateCcw size={14} />
                          </button>
                        </div>
                      </div>

                      <div className="commit-message">{commit.message}</div>

                      <div className="commit-meta">
                        <div className="commit-author">
                          <User size={12} />
                          <span>{commit.author}</span>
                        </div>
                        <div className="commit-time">
                          <Clock size={12} />
                          <span>{formatDate(commit.timestamp)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Branches View */}
        {view === 'branches' && (
          <div className="branches-view">
            {branches.length === 0 ? (
              <div className="empty">No branches</div>
            ) : (
              <div className="branches-list">
                {branches.map((branch) => (
                  <div key={branch.name} className="branch-item">
                    <div className="branch-header">
                      <GitBranch size={16} />
                      <span className="branch-name">{branch.name}</span>
                      {branch.name === currentBranch && (
                        <span className="current-badge">Current</span>
                      )}
                    </div>
                    <div className="branch-meta">
                      <span>Created {formatDate(branch.created_at)}</span>
                      <span>by {branch.created_by}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tags View */}
        {view === 'tags' && (
          <div className="tags-view">
            {tags.length === 0 ? (
              <div className="empty">No tags</div>
            ) : (
              <div className="tags-list">
                {tags.map((tag) => (
                  <div key={tag.name} className="tag-item">
                    <div className="tag-header">
                      <Tag size={16} />
                      <span className="tag-name">{tag.name}</span>
                    </div>
                    {tag.description && (
                      <div className="tag-description">{tag.description}</div>
                    )}
                    <div className="tag-meta">
                      <span>Commit: {tag.commit_id.substring(0, 7)}</span>
                      <span>{formatDate(tag.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Diff Modal */}
      {selectedCommit && (
        <div className="diff-modal-overlay" onClick={() => setSelectedCommit(null)}>
          <div className="diff-modal" onClick={(e) => e.stopPropagation()}>
            <div className="diff-header">
              <h4>Changes in {selectedCommit.commit_id.substring(0, 7)}</h4>
              <button onClick={() => setSelectedCommit(null)}>×</button>
            </div>

            <div className="diff-content">
              <div className="diff-summary">
                <div className="diff-stat">
                  <span className="stat-label">Nodes Added:</span>
                  <span className="stat-value added">
                    +{selectedCommit.diff.summary.nodes_added}
                  </span>
                </div>
                <div className="diff-stat">
                  <span className="stat-label">Nodes Removed:</span>
                  <span className="stat-value removed">
                    -{selectedCommit.diff.summary.nodes_removed}
                  </span>
                </div>
                <div className="diff-stat">
                  <span className="stat-label">Nodes Modified:</span>
                  <span className="stat-value modified">
                    ~{selectedCommit.diff.summary.nodes_modified}
                  </span>
                </div>
              </div>

              {/* Added Nodes */}
              {selectedCommit.diff.added_nodes.length > 0 && (
                <div className="diff-section">
                  <h5>Added Nodes</h5>
                  {selectedCommit.diff.added_nodes.map((node) => (
                    <div key={node.id} className="diff-node added">
                      <span>+ {node.data?.title || node.id}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Removed Nodes */}
              {selectedCommit.diff.removed_nodes.length > 0 && (
                <div className="diff-section">
                  <h5>Removed Nodes</h5>
                  {selectedCommit.diff.removed_nodes.map((node) => (
                    <div key={node.id} className="diff-node removed">
                      <span>- {node.data?.title || node.id}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Modified Nodes */}
              {selectedCommit.diff.modified_nodes.length > 0 && (
                <div className="diff-section">
                  <h5>Modified Nodes</h5>
                  {selectedCommit.diff.modified_nodes.map((mod) => (
                    <div key={mod.id} className="diff-node modified">
                      <span>~ {mod.before.data?.title || mod.id}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
