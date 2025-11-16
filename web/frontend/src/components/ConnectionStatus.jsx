import React, { useState, useEffect } from 'react';
import { Activity, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

/**
 * ConnectionStatus Component
 * Monitors backend connection status and displays indicator
 * Polls /api/health every 10 seconds
 */

const ConnectionStatus = ({ onStatusChange }) => {
  const [status, setStatus] = useState('checking'); // checking, online, offline, degraded
  const [healthData, setHealthData] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);
  const [error, setError] = useState(null);

  const checkHealth = async () => {
    try {
      const response = await fetch('/api/health', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(10000) // 10 second timeout for initial check
      });

      if (!response.ok) {
        throw new Error(`Health check returned status ${response.status}`);
      }

      const data = await response.json();
      setHealthData(data);
      setLastChecked(new Date());
      setError(null);

      // Determine status
      if (data.status === 'healthy') {
        setStatus('online');
      } else if (data.status === 'degraded') {
        setStatus('degraded');
      } else {
        setStatus('offline');
      }

      // Notify parent of status change
      if (onStatusChange) {
        onStatusChange({ status: data.status, data });
      }
    } catch (err) {
      console.error('Health check failed:', err);
      setStatus('offline');
      setError(err.message);
      setHealthData(null);

      if (onStatusChange) {
        onStatusChange({ status: 'offline', error: err.message });
      }
    }
  };

  // Check health on mount and every 10 seconds
  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const getStatusConfig = () => {
    switch (status) {
      case 'online':
        return {
          icon: CheckCircle,
          color: '#10b981',
          bgColor: '#d1fae5',
          text: 'Online',
          message: 'All systems operational'
        };
      case 'degraded':
        return {
          icon: AlertCircle,
          color: '#f59e0b',
          bgColor: '#fed7aa',
          text: 'Degraded',
          message: healthData?.message || 'Some features may be unavailable'
        };
      case 'offline':
        return {
          icon: XCircle,
          color: '#ef4444',
          bgColor: '#fee2e2',
          text: 'Offline',
          message: 'Backend server is not responding'
        };
      default: // checking
        return {
          icon: Activity,
          color: '#6b7280',
          bgColor: '#f3f4f6',
          text: 'Checking...',
          message: 'Verifying connection'
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '6px 12px',
      background: config.bgColor,
      borderRadius: '6px',
      border: `1px solid ${config.color}40`
    }}>
      <Icon size={16} color={config.color} />
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '2px'
      }}>
        <span style={{
          fontSize: '12px',
          fontWeight: '600',
          color: config.color
        }}>
          {config.text}
        </span>
      </div>
    </div>
  );
};

export default ConnectionStatus;
