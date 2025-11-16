/**
 * Sample Workflows
 * Epic 10: Story 10.1
 *
 * Pre-built workflow examples for testing and templates
 */

export const SAMPLE_WORKFLOWS = {
  leadNurture: {
    id: 'wf-sample-lead-nurture',
    name: 'Lead Nurture Sequence',
    description: 'Automatically nurture new leads with SMS and email follow-ups',
    niche: 'pressure_washing',
    difficulty: 'intermediate',
    version: '1.0',
    metadata: {
      createdAt: '2025-01-15T10:00:00Z',
      updatedAt: '2025-01-15T10:00:00Z',
      source: 'sample',
      author: 'BroBro',
      tags: ['lead-gen', 'nurture', 'sms', 'email']
    },
    nodes: [
      {
        id: 'node-1',
        type: 'trigger',
        title: 'New Lead Added',
        description: 'Triggered when new contact is created',
        position: { x: 50, y: 100 },
        params: {
          trigger_type: 'contact_created',
          source: 'web_form'
        }
      },
      {
        id: 'node-2',
        type: 'action',
        title: 'Send Welcome SMS',
        description: 'Send immediate SMS to new lead',
        position: { x: 300, y: 100 },
        params: {
          action_type: 'send_sms',
          message: 'Hi {{firstName}}! Thanks for your interest in our pressure washing services. We\'ll be in touch soon!',
          delay: 0
        }
      },
      {
        id: 'node-3',
        type: 'delay',
        title: 'Wait 2 Hours',
        description: 'Delay before next action',
        position: { x: 550, y: 100 },
        params: {
          duration: 120,
          unit: 'minutes'
        }
      },
      {
        id: 'node-4',
        type: 'action',
        title: 'Send Email with Info',
        description: 'Send detailed email about services',
        position: { x: 800, y: 100 },
        params: {
          action_type: 'send_email',
          subject: 'About Our Pressure Washing Services',
          template: 'service_overview',
          delay: 0
        }
      },
      {
        id: 'node-5',
        type: 'delay',
        title: 'Wait 24 Hours',
        description: 'Wait for response',
        position: { x: 1050, y: 100 },
        params: {
          duration: 24,
          unit: 'hours'
        }
      },
      {
        id: 'node-6',
        type: 'condition',
        title: 'Email Opened?',
        description: 'Check if email was opened',
        position: { x: 1300, y: 100 },
        params: {
          condition_type: 'email_opened',
          email_id: 'service_overview'
        }
      },
      {
        id: 'node-7',
        type: 'action',
        title: 'Send Follow-up SMS',
        description: 'SMS for engaged leads',
        position: { x: 1550, y: 50 },
        params: {
          action_type: 'send_sms',
          message: 'Hi {{firstName}}! I noticed you checked out our services. Ready for a free quote?',
          delay: 0
        }
      },
      {
        id: 'node-8',
        type: 'end',
        title: 'End Sequence',
        description: 'Workflow complete',
        position: { x: 1550, y: 200 },
        params: {}
      }
    ],
    connections: [
      { id: 'conn-1', from: 'node-1', to: 'node-2', type: 'default', label: '' },
      { id: 'conn-2', from: 'node-2', to: 'node-3', type: 'default', label: '' },
      { id: 'conn-3', from: 'node-3', to: 'node-4', type: 'default', label: '' },
      { id: 'conn-4', from: 'node-4', to: 'node-5', type: 'default', label: '' },
      { id: 'conn-5', from: 'node-5', to: 'node-6', type: 'default', label: '' },
      { id: 'conn-6', from: 'node-6', to: 'node-7', type: 'success', label: 'yes' },
      { id: 'conn-7', from: 'node-6', to: 'node-8', type: 'error', label: 'no' },
      { id: 'conn-8', from: 'node-7', to: 'node-8', type: 'default', label: '' }
    ]
  },

  smsCampaign: {
    id: 'wf-sample-sms-campaign',
    name: 'SMS Campaign',
    description: 'Simple SMS broadcast campaign',
    niche: 'general',
    difficulty: 'beginner',
    version: '1.0',
    metadata: {
      createdAt: '2025-01-15T10:00:00Z',
      updatedAt: '2025-01-15T10:00:00Z',
      source: 'sample',
      author: 'BroBro',
      tags: ['sms', 'campaign', 'broadcast']
    },
    nodes: [
      {
        id: 'node-1',
        type: 'trigger',
        title: 'Manual Start',
        description: 'Manually start campaign',
        position: { x: 50, y: 150 },
        params: {
          trigger_type: 'manual'
        }
      },
      {
        id: 'node-2',
        type: 'action',
        title: 'Send SMS Blast',
        description: 'Send SMS to all contacts',
        position: { x: 300, y: 150 },
        params: {
          action_type: 'send_sms',
          message: 'Hi {{firstName}}! Special offer this week only. Reply YES for details!',
          delay: 0
        }
      },
      {
        id: 'node-3',
        type: 'delay',
        title: 'Wait 48 Hours',
        description: 'Wait for responses',
        position: { x: 550, y: 150 },
        params: {
          duration: 48,
          unit: 'hours'
        }
      },
      {
        id: 'node-4',
        type: 'condition',
        title: 'Replied YES?',
        description: 'Check if contact replied',
        position: { x: 800, y: 150 },
        params: {
          condition_type: 'sms_replied',
          keyword: 'YES'
        }
      },
      {
        id: 'node-5',
        type: 'action',
        title: 'Send Details',
        description: 'Send offer details',
        position: { x: 1050, y: 100 },
        params: {
          action_type: 'send_sms',
          message: 'Great! Here are the details: [offer link]',
          delay: 0
        }
      },
      {
        id: 'node-6',
        type: 'end',
        title: 'Campaign Complete',
        description: 'End of campaign',
        position: { x: 1050, y: 200 },
        params: {}
      }
    ],
    connections: [
      { id: 'conn-1', from: 'node-1', to: 'node-2', type: 'default', label: '' },
      { id: 'conn-2', from: 'node-2', to: 'node-3', type: 'default', label: '' },
      { id: 'conn-3', from: 'node-3', to: 'node-4', type: 'default', label: '' },
      { id: 'conn-4', from: 'node-4', to: 'node-5', type: 'success', label: 'yes' },
      { id: 'conn-5', from: 'node-4', to: 'node-6', type: 'error', label: 'no' },
      { id: 'conn-6', from: 'node-5', to: 'node-6', type: 'default', label: '' }
    ]
  },

  customerFollowup: {
    id: 'wf-sample-customer-followup',
    name: 'Customer Follow-up',
    description: 'Follow up with customers after service completion',
    niche: 'general',
    difficulty: 'beginner',
    version: '1.0',
    metadata: {
      createdAt: '2025-01-15T10:00:00Z',
      updatedAt: '2025-01-15T10:00:00Z',
      source: 'sample',
      author: 'BroBro',
      tags: ['customer-service', 'follow-up', 'review']
    },
    nodes: [
      {
        id: 'node-1',
        type: 'trigger',
        title: 'Job Completed',
        description: 'Triggered when job marked complete',
        position: { x: 50, y: 150 },
        params: {
          trigger_type: 'opportunity_won',
          pipeline: 'services'
        }
      },
      {
        id: 'node-2',
        type: 'delay',
        title: 'Wait 24 Hours',
        description: 'Give customer time',
        position: { x: 300, y: 150 },
        params: {
          duration: 24,
          unit: 'hours'
        }
      },
      {
        id: 'node-3',
        type: 'action',
        title: 'Send Thank You SMS',
        description: 'Thank customer',
        position: { x: 550, y: 150 },
        params: {
          action_type: 'send_sms',
          message: 'Hi {{firstName}}! Thanks for choosing us. How did everything go?',
          delay: 0
        }
      },
      {
        id: 'node-4',
        type: 'delay',
        title: 'Wait 48 Hours',
        description: 'Wait for feedback',
        position: { x: 800, y: 150 },
        params: {
          duration: 48,
          unit: 'hours'
        }
      },
      {
        id: 'node-5',
        type: 'action',
        title: 'Request Review',
        description: 'Ask for online review',
        position: { x: 1050, y: 150 },
        params: {
          action_type: 'send_email',
          subject: 'We\'d love your feedback!',
          template: 'review_request',
          delay: 0
        }
      },
      {
        id: 'node-6',
        type: 'end',
        title: 'Follow-up Complete',
        description: 'Workflow complete',
        position: { x: 1300, y: 150 },
        params: {}
      }
    ],
    connections: [
      { id: 'conn-1', from: 'node-1', to: 'node-2', type: 'default', label: '' },
      { id: 'conn-2', from: 'node-2', to: 'node-3', type: 'default', label: '' },
      { id: 'conn-3', from: 'node-3', to: 'node-4', type: 'default', label: '' },
      { id: 'conn-4', from: 'node-4', to: 'node-5', type: 'default', label: '' },
      { id: 'conn-5', from: 'node-5', to: 'node-6', type: 'default', label: '' }
    ]
  }
};

export const getSampleWorkflow = (name) => {
  return SAMPLE_WORKFLOWS[name] || null;
};

export const getAllSampleWorkflows = () => {
  return Object.values(SAMPLE_WORKFLOWS);
};
