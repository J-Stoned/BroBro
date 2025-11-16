/**
 * Workflow Defaults & Constants
 * Epic 10: Story 10.2
 */

export const NODE_TYPES = {
  trigger: {
    title: 'Trigger',
    color: '#3b82f6',
    bgColor: '#eff6ff',
    icon: '▶',
    maxOutputs: 1,
    defaultParams: ['trigger_type', 'source']
  },
  action: {
    title: 'Action',
    color: '#10b981',
    bgColor: '#f0fdf4',
    icon: '⚡',
    maxOutputs: 1,
    defaultParams: ['action_type', 'message']
  },
  condition: {
    title: 'Condition',
    color: '#f59e0b',
    bgColor: '#fffbeb',
    icon: '🔀',
    maxOutputs: 2,
    defaultParams: ['condition_type']
  },
  delay: {
    title: 'Delay',
    color: '#f97316',
    bgColor: '#fff7ed',
    icon: '⏱',
    maxOutputs: 1,
    defaultParams: ['duration', 'unit']
  },
  end: {
    title: 'End',
    color: '#ef4444',
    bgColor: '#fef2f2',
    icon: '⏹',
    maxOutputs: 0,
    defaultParams: []
  }
};

export const CONNECTION_TYPES = {
  default: { color: '#9ca3af', label: '' },
  success: { color: '#10b981', label: 'yes' },
  error: { color: '#ef4444', label: 'no' },
  data: { color: '#3b82f6', label: 'data' }
};

export const BLANK_WORKFLOW = {
  id: null,
  name: 'New Workflow',
  description: '',
  niche: 'general',
  difficulty: 'beginner',
  version: '1.0',
  nodes: [],
  connections: [],
  metadata: {
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    source: 'manual'
  }
};
