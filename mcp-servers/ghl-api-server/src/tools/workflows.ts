/**
 * Workflow Management Tools
 *
 * Story 3.4: Workflow Management Tools
 * Provides MCP tools for managing GoHighLevel workflows including:
 * - Creating workflows with triggers and actions
 * - Listing all workflows for a location
 * - Getting workflow details
 * - Updating workflow configuration
 * - Deleting workflows
 *
 * GHL Workflows Documentation:
 * - Workflows automate actions based on triggers (form submission, appointment booking, etc.)
 * - Each workflow has: name, trigger config, action sequence
 * - API Endpoints: /workflows (base path)
 */

import { z } from 'zod';
import { ghlClient } from '../api/ghl-client.js';
import { logger } from '../utils/logger.js';

/**
 * Create Workflow Tool
 *
 * Creates a new workflow in GoHighLevel with specified trigger and actions.
 *
 * Common trigger types:
 * - 'contact_created': When a new contact is added
 * - 'form_submitted': When a form is submitted
 * - 'appointment_booked': When an appointment is scheduled
 * - 'tag_added': When a tag is added to a contact
 *
 * Common action types:
 * - 'send_email': Send an email to contact
 * - 'send_sms': Send SMS to contact
 * - 'add_tag': Add tag to contact
 * - 'create_task': Create a task
 * - 'wait': Wait for specified time
 */
export const createWorkflowTool = {
  name: 'create_workflow',
  description: 'Create a new workflow in GoHighLevel with triggers and actions. Workflows automate repetitive tasks like sending emails, adding tags, or creating appointments based on events.',
  schema: z.object({
    locationId: z.string().describe('The GHL location ID where the workflow will be created'),
    name: z.string().describe('Workflow name (e.g., "Welcome Email Sequence")'),
    description: z.string().optional().describe('Optional workflow description'),
    trigger: z.object({
      type: z.string().describe('Trigger type: contact_created, form_submitted, appointment_booked, tag_added, etc.'),
      config: z.record(z.any()).describe('Trigger configuration (varies by type)')
    }).describe('What event starts this workflow'),
    actions: z.array(z.object({
      type: z.string().describe('Action type: send_email, send_sms, add_tag, create_task, wait, etc.'),
      config: z.record(z.any()).describe('Action configuration (varies by type)')
    })).describe('Sequence of actions to perform when triggered'),
    status: z.enum(['active', 'inactive']).optional().default('active').describe('Initial workflow status')
  }),

  async handler(args: {
    locationId: string;
    name: string;
    description?: string;
    trigger: { type: string; config: Record<string, any> };
    actions: Array<{ type: string; config: Record<string, any> }>;
    status?: 'active' | 'inactive';
  }): Promise<string> {
    logger.info('create_workflow tool invoked', {
      locationId: args.locationId,
      name: args.name,
      triggerType: args.trigger.type,
      actionCount: args.actions.length
    });

    try {
      // Build workflow payload
      const workflowData = {
        name: args.name,
        description: args.description || '',
        locationId: args.locationId,
        trigger: args.trigger,
        actions: args.actions,
        status: args.status || 'active'
      };

      // Create workflow via GHL API
      const result = await ghlClient.post(`/workflows/`, workflowData);

      logger.info('Workflow created successfully', {
        workflowId: result.id,
        name: args.name
      });

      const response = {
        success: true,
        workflow: result,
        message: `Workflow "${args.name}" created successfully`,
        nextSteps: [
          'Use get_workflow to view full workflow details',
          'Use update_workflow to modify workflow configuration',
          'Monitor workflow executions in GHL dashboard'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to create workflow', {
        name: args.name,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the location ID is correct',
          'Check that trigger type is valid for your GHL plan',
          'Ensure action configurations are complete',
          'Verify OAuth token has workflow creation permissions'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};

/**
 * List Workflows Tool
 *
 * Retrieves all workflows for a location with optional filtering.
 */
export const listWorkflowsTool = {
  name: 'list_workflows',
  description: 'List all workflows in a GoHighLevel location. Returns workflow names, IDs, status, and trigger types.',
  schema: z.object({
    locationId: z.string().describe('The GHL location ID to list workflows from'),
    status: z.enum(['active', 'inactive', 'all']).optional().default('all').describe('Filter by workflow status'),
    limit: z.number().optional().default(100).describe('Maximum number of workflows to return (default: 100)'),
    skip: z.number().optional().default(0).describe('Number of workflows to skip for pagination (default: 0)')
  }),

  async handler(args: {
    locationId: string;
    status?: 'active' | 'inactive' | 'all';
    limit?: number;
    skip?: number;
  }): Promise<string> {
    logger.info('list_workflows tool invoked', {
      locationId: args.locationId,
      status: args.status,
      limit: args.limit
    });

    try {
      // Build query parameters
      const params: Record<string, any> = {
        locationId: args.locationId,
        limit: args.limit || 100,
        skip: args.skip || 0
      };

      // Add status filter if not 'all'
      if (args.status && args.status !== 'all') {
        params.status = args.status;
      }

      // Get workflows from GHL API
      const result = await ghlClient.get('/workflows/', params);

      logger.info('Workflows retrieved successfully', {
        count: result.workflows?.length || 0,
        locationId: args.locationId
      });

      // Format workflows for better readability
      const workflows = (result.workflows || []).map((workflow: any) => ({
        id: workflow.id,
        name: workflow.name,
        status: workflow.status,
        triggerType: workflow.trigger?.type || 'unknown',
        actionCount: workflow.actions?.length || 0,
        createdAt: workflow.createdAt,
        updatedAt: workflow.updatedAt
      }));

      const response = {
        success: true,
        total: workflows.length,
        workflows: workflows,
        pagination: {
          limit: args.limit || 100,
          skip: args.skip || 0,
          hasMore: workflows.length === (args.limit || 100)
        },
        summary: {
          active: workflows.filter((w: any) => w.status === 'active').length,
          inactive: workflows.filter((w: any) => w.status === 'inactive').length
        }
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to list workflows', {
        locationId: args.locationId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the location ID is correct',
          'Check OAuth token has workflow read permissions',
          'Ensure location has workflows created'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};

/**
 * Get Workflow Tool
 *
 * Retrieves detailed information about a specific workflow including
 * full trigger config, action sequence, and execution statistics.
 */
export const getWorkflowTool = {
  name: 'get_workflow',
  description: 'Get detailed information about a specific workflow including trigger configuration, action sequence, and status.',
  schema: z.object({
    workflowId: z.string().describe('The workflow ID to retrieve'),
    locationId: z.string().optional().describe('The location ID (required by some GHL API versions)')
  }),

  async handler(args: {
    workflowId: string;
    locationId?: string;
  }): Promise<string> {
    logger.info('get_workflow tool invoked', {
      workflowId: args.workflowId
    });

    try {
      // Build query params
      const params: Record<string, any> = {};
      if (args.locationId) {
        params.locationId = args.locationId;
      }

      // Get workflow from GHL API
      const workflow = await ghlClient.get(`/workflows/${args.workflowId}`, params);

      logger.info('Workflow retrieved successfully', {
        workflowId: args.workflowId,
        name: workflow.name
      });

      const response = {
        success: true,
        workflow: {
          id: workflow.id,
          name: workflow.name,
          description: workflow.description,
          status: workflow.status,
          locationId: workflow.locationId,
          trigger: workflow.trigger,
          actions: workflow.actions,
          metadata: {
            createdAt: workflow.createdAt,
            updatedAt: workflow.updatedAt,
            createdBy: workflow.createdBy,
            version: workflow.version
          }
        },
        analysis: {
          triggerType: workflow.trigger?.type || 'unknown',
          totalActions: workflow.actions?.length || 0,
          actionTypes: workflow.actions?.map((a: any) => a.type) || [],
          estimatedExecutionTime: this.estimateExecutionTime(workflow.actions)
        }
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to get workflow', {
        workflowId: args.workflowId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the workflow ID is correct',
          'Check OAuth token has workflow read permissions',
          'Ensure workflow exists and is not deleted'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  },

  estimateExecutionTime(actions: any[]): string {
    if (!actions || actions.length === 0) return '0s';

    let totalSeconds = 0;
    for (const action of actions) {
      if (action.type === 'wait') {
        // Wait actions have configurable delays
        const delay = action.config?.delay || 0;
        totalSeconds += delay;
      } else {
        // Other actions estimated at 1-2 seconds each
        totalSeconds += 1.5;
      }
    }

    if (totalSeconds < 60) {
      return `${Math.round(totalSeconds)}s`;
    } else if (totalSeconds < 3600) {
      return `${Math.round(totalSeconds / 60)}m`;
    } else {
      return `${Math.round(totalSeconds / 3600)}h`;
    }
  }
};

/**
 * Update Workflow Tool
 *
 * Updates an existing workflow's configuration including name, trigger, actions, and status.
 */
export const updateWorkflowTool = {
  name: 'update_workflow',
  description: 'Update an existing workflow. Can modify name, description, trigger, actions, or status. Only provide fields you want to change.',
  schema: z.object({
    workflowId: z.string().describe('The workflow ID to update'),
    name: z.string().optional().describe('New workflow name'),
    description: z.string().optional().describe('New workflow description'),
    trigger: z.object({
      type: z.string(),
      config: z.record(z.any())
    }).optional().describe('New trigger configuration'),
    actions: z.array(z.object({
      type: z.string(),
      config: z.record(z.any())
    })).optional().describe('New action sequence'),
    status: z.enum(['active', 'inactive']).optional().describe('New workflow status')
  }),

  async handler(args: {
    workflowId: string;
    name?: string;
    description?: string;
    trigger?: { type: string; config: Record<string, any> };
    actions?: Array<{ type: string; config: Record<string, any> }>;
    status?: 'active' | 'inactive';
  }): Promise<string> {
    logger.info('update_workflow tool invoked', {
      workflowId: args.workflowId,
      fieldsToUpdate: Object.keys(args).filter(k => k !== 'workflowId')
    });

    try {
      // Build update payload (only include provided fields)
      const updateData: Record<string, any> = {};
      if (args.name !== undefined) updateData.name = args.name;
      if (args.description !== undefined) updateData.description = args.description;
      if (args.trigger !== undefined) updateData.trigger = args.trigger;
      if (args.actions !== undefined) updateData.actions = args.actions;
      if (args.status !== undefined) updateData.status = args.status;

      if (Object.keys(updateData).length === 0) {
        return JSON.stringify({
          success: false,
          error: 'No fields provided to update. Please specify at least one field to change.'
        }, null, 2);
      }

      // Update workflow via GHL API
      const result = await ghlClient.put(`/workflows/${args.workflowId}`, updateData);

      logger.info('Workflow updated successfully', {
        workflowId: args.workflowId,
        updatedFields: Object.keys(updateData)
      });

      const response = {
        success: true,
        workflow: result,
        message: `Workflow updated successfully`,
        updatedFields: Object.keys(updateData),
        nextSteps: [
          'Use get_workflow to verify changes',
          'Test workflow with sample trigger event',
          'Monitor workflow executions for expected behavior'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to update workflow', {
        workflowId: args.workflowId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the workflow ID is correct',
          'Check OAuth token has workflow update permissions',
          'Ensure new trigger/action configurations are valid',
          'Verify workflow is not currently executing'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};

/**
 * Delete Workflow Tool
 *
 * Permanently deletes a workflow from GoHighLevel.
 * WARNING: This action cannot be undone.
 */
export const deleteWorkflowTool = {
  name: 'delete_workflow',
  description: 'Permanently delete a workflow from GoHighLevel. WARNING: This cannot be undone. Consider setting status to "inactive" instead if you may need the workflow later.',
  schema: z.object({
    workflowId: z.string().describe('The workflow ID to delete'),
    confirm: z.boolean().describe('Must be true to confirm deletion')
  }),

  async handler(args: {
    workflowId: string;
    confirm: boolean;
  }): Promise<string> {
    if (!args.confirm) {
      return JSON.stringify({
        success: false,
        message: 'Deletion cancelled - confirmation required',
        usage: 'Call with { workflowId: "...", confirm: true } to delete workflow',
        alternative: 'Consider using update_workflow to set status to "inactive" instead'
      }, null, 2);
    }

    logger.warn('delete_workflow tool invoked', {
      workflowId: args.workflowId
    });

    try {
      // Delete workflow via GHL API
      await ghlClient.delete(`/workflows/${args.workflowId}`);

      logger.info('Workflow deleted successfully', {
        workflowId: args.workflowId
      });

      const response = {
        success: true,
        message: `Workflow deleted successfully`,
        workflowId: args.workflowId,
        warning: 'This action cannot be undone',
        nextSteps: [
          'Workflow is permanently removed',
          'Any active executions will be terminated',
          'Historical execution data may be retained per GHL retention policy'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to delete workflow', {
        workflowId: args.workflowId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the workflow ID is correct',
          'Check OAuth token has workflow delete permissions',
          'Ensure workflow exists and is not already deleted',
          'Check if workflow is currently executing (may prevent deletion)'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};
