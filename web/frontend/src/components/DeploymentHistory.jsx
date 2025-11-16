import React, { useState, useEffect } from 'react';
import { History, ExternalLink, Trash2, Calendar, MapPin } from 'lucide-react';

/**
 * DeploymentHistory - Epic 11: Story 11.7
 * Track and view deployment history
 */

const DeploymentHistory = ({ onViewWorkflow }) => {
  const [history, setHistory] = useState([]);
  const [filter, setFilter] = useState('all'); // 'all' | 'today' | 'week' | 'month'

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    try {
      const stored = localStorage.getItem('ghl_deployment_history');
      if (stored) {
        const parsed = JSON.parse(stored);
        setHistory(parsed);
      }
    } catch (error) {
      console.error('Failed to load deployment history:', error);
    }
  };

  const clearHistory = () => {
    if (window.confirm('Clear all deployment history? This cannot be undone.')) {
      localStorage.removeItem('ghl_deployment_history');
      setHistory([]);
    }
  };

  const deleteEntry = (index) => {
    const updated = history.filter((_, i) => i !== index);
    setHistory(updated);
    localStorage.setItem('ghl_deployment_history', JSON.stringify(updated));
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTimeCategory = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffDays === 0) return 'today';
    if (diffDays < 7) return 'week';
    if (diffDays < 30) return 'month';
    return 'older';
  };

  const filteredHistory = history.filter(item => {
    if (filter === 'all') return true;
    return getTimeCategory(item.deployed_at) === filter;
  });

  const groupedHistory = filteredHistory.reduce((acc, item) => {
    const category = getTimeCategory(item.deployed_at);
    if (!acc[category]) acc[category] = [];
    acc[category].push(item);
    return acc;
  }, {});

  const categories = [
    { key: 'today', label: 'Today' },
    { key: 'week', label: 'This Week' },
    { key: 'month', label: 'This Month' },
    { key: 'older', label: 'Older' }
  ];

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
        paddingBottom: '16px',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <History size={24} color="#3b82f6" />
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#111827' }}>
              Deployment History
            </h3>
            <p style={{ margin: '2px 0 0 0', fontSize: '13px', color: '#6b7280' }}>
              {history.length} total deployments
            </p>
          </div>
        </div>
        {history.length > 0 && (
          <button
            onClick={clearHistory}
            style={{
              padding: '6px 12px',
              background: 'white',
              color: '#ef4444',
              border: '1px solid #ef4444',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Trash2 size={14} />
            Clear All
          </button>
        )}
      </div>

      {/* Filters */}
      {history.length > 0 && (
        <div style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '16px',
          overflowX: 'auto',
          paddingBottom: '4px'
        }}>
          <FilterButton
            label="All"
            active={filter === 'all'}
            count={history.length}
            onClick={() => setFilter('all')}
          />
          <FilterButton
            label="Today"
            active={filter === 'today'}
            count={groupedHistory.today?.length || 0}
            onClick={() => setFilter('today')}
          />
          <FilterButton
            label="This Week"
            active={filter === 'week'}
            count={groupedHistory.week?.length || 0}
            onClick={() => setFilter('week')}
          />
          <FilterButton
            label="This Month"
            active={filter === 'month'}
            count={groupedHistory.month?.length || 0}
            onClick={() => setFilter('month')}
          />
        </div>
      )}

      {/* History List */}
      {history.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '48px 20px',
          color: '#6b7280'
        }}>
          <History size={48} color="#d1d5db" style={{ margin: '0 auto 16px' }} />
          <div style={{ fontSize: '16px', fontWeight: '500', marginBottom: '8px' }}>
            No Deployments Yet
          </div>
          <div style={{ fontSize: '14px' }}>
            Deploy a workflow to see it in your history
          </div>
        </div>
      ) : filteredHistory.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '32px 20px',
          color: '#6b7280',
          fontSize: '14px'
        }}>
          No deployments in this time period
        </div>
      ) : (
        <div style={{
          maxHeight: '500px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          {categories.map(category => {
            const items = groupedHistory[category.key];
            if (!items || items.length === 0) return null;

            return (
              <div key={category.key}>
                <div style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#6b7280',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  marginBottom: '8px',
                  marginTop: category.key !== 'today' ? '16px' : '0'
                }}>
                  {category.label}
                </div>
                {items.map((item, idx) => (
                  <DeploymentItem
                    key={item.workflow_id + idx}
                    item={item}
                    onDelete={() => deleteEntry(history.indexOf(item))}
                    onView={onViewWorkflow}
                  />
                ))}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// Filter Button Component
const FilterButton = ({ label, active, count, onClick }) => (
  <button
    onClick={onClick}
    style={{
      padding: '6px 12px',
      background: active ? '#3b82f6' : 'white',
      color: active ? 'white' : '#6b7280',
      border: `1px solid ${active ? '#3b82f6' : '#e5e7eb'}`,
      borderRadius: '6px',
      fontSize: '13px',
      fontWeight: '500',
      cursor: 'pointer',
      whiteSpace: 'nowrap',
      display: 'flex',
      alignItems: 'center',
      gap: '6px',
      transition: 'all 0.2s'
    }}
  >
    {label}
    <span style={{
      padding: '2px 6px',
      background: active ? 'rgba(255,255,255,0.2)' : '#f3f4f6',
      borderRadius: '4px',
      fontSize: '11px',
      fontWeight: '600'
    }}>
      {count}
    </span>
  </button>
);

// Deployment Item Component
const DeploymentItem = ({ item, onDelete, onView }) => (
  <div style={{
    padding: '12px',
    background: '#f9fafb',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    transition: 'all 0.2s'
  }}
    onMouseOver={(e) => {
      e.currentTarget.style.borderColor = '#3b82f6';
      e.currentTarget.style.background = '#eff6ff';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.borderColor = '#e5e7eb';
      e.currentTarget.style.background = '#f9fafb';
    }}
  >
    <div style={{ flex: 1 }}>
      <div style={{
        fontSize: '14px',
        fontWeight: '600',
        color: '#111827',
        marginBottom: '4px'
      }}>
        {item.workflow_name}
      </div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        fontSize: '12px',
        color: '#6b7280'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Calendar size={12} />
          <span>{new Date(item.deployed_at).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <MapPin size={12} />
          <span>{item.location_id.substring(0, 8)}...</span>
        </div>
      </div>
      <div style={{
        marginTop: '6px',
        fontSize: '11px',
        fontFamily: 'monospace',
        color: '#9ca3af'
      }}>
        ID: {item.workflow_id}
      </div>
    </div>
    <div style={{ display: 'flex', gap: '8px' }}>
      {onView && (
        <button
          onClick={() => onView(item.workflow_id)}
          style={{
            padding: '6px 10px',
            background: 'white',
            color: '#3b82f6',
            border: '1px solid #3b82f6',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: '500',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          <ExternalLink size={12} />
          View
        </button>
      )}
      <button
        onClick={onDelete}
        style={{
          padding: '6px',
          background: 'white',
          color: '#ef4444',
          border: '1px solid #e5e7eb',
          borderRadius: '6px',
          cursor: 'pointer',
          display: 'flex'
        }}
      >
        <Trash2 size={14} />
      </button>
    </div>
  </div>
);

export default DeploymentHistory;
