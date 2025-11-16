/**
 * Form Management Tools
 *
 * Story 3.5: Contacts, Funnels, Forms, Calendars Tools
 * Provides MCP tools for managing GoHighLevel forms including:
 * - Listing all forms in a location
 * - Getting form submissions with filtering
 *
 * GHL Forms Documentation:
 * - Forms capture lead information (contact, survey, booking forms)
 * - Each form has: name, fields, submission count, embed code
 * - API Endpoints: /forms, /forms/{formId}/submissions
 */

import { z } from 'zod';
import { ghlClient } from '../api/ghl-client.js';
import { logger } from '../utils/logger.js';

/**
 * List Forms Tool
 *
 * Lists all forms in a GoHighLevel location with filtering and details.
 */
export const listFormsTool = {
  name: 'list_forms',
  description: 'List all forms in a GoHighLevel location. Forms are used to capture leads, surveys, bookings, and other information from contacts.',
  schema: z.object({
    locationId: z.string().describe('The GHL location ID to list forms from'),
    type: z.enum(['all', 'contact', 'survey', 'booking']).optional().default('all').describe('Filter by form type'),
    limit: z.number().optional().default(100).describe('Maximum number of forms to return (default: 100)'),
    skip: z.number().optional().default(0).describe('Number of forms to skip for pagination (default: 0)')
  }),

  async handler(args: {
    locationId: string;
    type?: 'all' | 'contact' | 'survey' | 'booking';
    limit?: number;
    skip?: number;
  }): Promise<string> {
    logger.info('list_forms tool invoked', {
      locationId: args.locationId,
      type: args.type
    });

    try {
      // Build query parameters
      const params: Record<string, any> = {
        locationId: args.locationId,
        limit: args.limit || 100,
        skip: args.skip || 0
      };

      // Add type filter if not 'all'
      if (args.type && args.type !== 'all') {
        params.type = args.type;
      }

      // Get forms from GHL API
      const result = await ghlClient.get('/forms/', params);

      const forms = result.forms || [];

      logger.info('Forms retrieved successfully', {
        count: forms.length,
        locationId: args.locationId
      });

      // Format forms for better readability
      const formattedForms = forms.map((form: any) => ({
        id: form.id,
        name: form.name,
        type: form.type || 'contact',
        fields: form.fields || [],
        fieldCount: form.fields?.length || form.fieldCount || 0,
        submissionCount: form.submissionCount || form.submissions || 0,
        status: form.status || 'active',
        embedCode: form.embedCode,
        url: form.url || form.shareableUrl,
        createdAt: form.createdAt,
        updatedAt: form.updatedAt
      }));

      const response = {
        success: true,
        total: forms.length,
        forms: formattedForms,
        pagination: {
          limit: args.limit || 100,
          skip: args.skip || 0,
          hasMore: forms.length === (args.limit || 100)
        },
        filters: {
          type: args.type
        },
        summary: {
          byType: formattedForms.reduce((acc: any, f: any) => {
            acc[f.type] = (acc[f.type] || 0) + 1;
            return acc;
          }, {}),
          totalSubmissions: formattedForms.reduce((sum: number, f: any) => sum + (f.submissionCount || 0), 0),
          activeforms: formattedForms.filter((f: any) => f.status === 'active').length
        },
        nextSteps: [
          'Use get_form_submissions to view submissions for a specific form',
          'Embed forms on websites using embedCode',
          'Track form performance and conversion rates',
          'To get more results, increase skip parameter'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to list forms', {
        locationId: args.locationId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the location ID is correct',
          'Check OAuth token has form read permissions',
          'Ensure location has forms created',
          'Try without type filter if no results found'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};

/**
 * Get Form Submissions Tool
 *
 * Retrieves submissions for a specific form with date filtering and pagination.
 */
export const getFormSubmissionsTool = {
  name: 'get_form_submissions',
  description: 'Get all submissions for a specific form with date filtering. Returns contact information and form responses for analysis and follow-up.',
  schema: z.object({
    formId: z.string().describe('The form ID to get submissions from'),
    startDate: z.string().optional().describe('Start date for filtering submissions (ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss)'),
    endDate: z.string().optional().describe('End date for filtering submissions (ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss)'),
    limit: z.number().optional().default(100).describe('Maximum number of submissions to return (default: 100)'),
    skip: z.number().optional().default(0).describe('Number of submissions to skip for pagination (default: 0)'),
    includeContact: z.boolean().optional().default(true).describe('Include full contact details for each submission (default: true)')
  }),

  async handler(args: {
    formId: string;
    startDate?: string;
    endDate?: string;
    limit?: number;
    skip?: number;
    includeContact?: boolean;
  }): Promise<string> {
    logger.info('get_form_submissions tool invoked', {
      formId: args.formId,
      startDate: args.startDate,
      endDate: args.endDate,
      limit: args.limit
    });

    try {
      // Build query parameters
      const params: Record<string, any> = {
        limit: args.limit || 100,
        skip: args.skip || 0
      };

      // Add date filters if provided
      if (args.startDate) {
        params.startDate = args.startDate;
      }
      if (args.endDate) {
        params.endDate = args.endDate;
      }

      // Get form details first
      const form = await ghlClient.get(`/forms/${args.formId}`);

      // Get submissions for the form
      const submissionsResult = await ghlClient.get(`/forms/${args.formId}/submissions`, params);

      const submissions = submissionsResult.submissions || submissionsResult || [];

      logger.info('Form submissions retrieved successfully', {
        formId: args.formId,
        count: submissions.length
      });

      // Format submissions for better readability
      const formattedSubmissions = await Promise.all(submissions.map(async (submission: any) => {
        const submissionData: any = {
          id: submission.id,
          formId: args.formId,
          submittedAt: submission.submittedAt || submission.createdAt,
          contactId: submission.contactId,
          responses: submission.responses || submission.data || {},
          pageUrl: submission.pageUrl,
          ipAddress: submission.ipAddress,
          userAgent: submission.userAgent
        };

        // Include contact details if requested
        if (args.includeContact && submission.contactId) {
          try {
            const contact = await ghlClient.get(`/contacts/${submission.contactId}`);
            submissionData.contact = {
              id: contact.id,
              name: `${contact.firstName || ''} ${contact.lastName || ''}`.trim(),
              email: contact.email,
              phone: contact.phone,
              tags: contact.tags || []
            };
          } catch (contactError) {
            // Contact fetch failed, include minimal info
            submissionData.contact = {
              id: submission.contactId,
              error: 'Unable to fetch contact details'
            };
          }
        }

        return submissionData;
      }));

      const response = {
        success: true,
        form: {
          id: form.id,
          name: form.name,
          type: form.type,
          fieldCount: form.fields?.length || 0
        },
        submissionCount: submissions.length,
        submissions: formattedSubmissions,
        pagination: {
          limit: args.limit || 100,
          skip: args.skip || 0,
          hasMore: submissions.length === (args.limit || 100)
        },
        dateRange: {
          startDate: args.startDate || 'beginning',
          endDate: args.endDate || 'now'
        },
        analysis: {
          uniqueContacts: new Set(formattedSubmissions.map((s: any) => s.contactId).filter(Boolean)).size,
          submissionsWithEmail: formattedSubmissions.filter((s: any) => s.contact?.email).length,
          submissionsWithPhone: formattedSubmissions.filter((s: any) => s.contact?.phone).length
        },
        nextSteps: [
          'Use get_contact to view full contact details',
          'Follow up with contacts who submitted',
          'Export data for analysis or reporting',
          'Create workflows based on form submissions',
          'To get more results, increase skip parameter'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to get form submissions', {
        formId: args.formId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the form ID is correct',
          'Check OAuth token has form read permissions',
          'Ensure form exists and is not deleted',
          'Check date format is correct (ISO 8601: YYYY-MM-DD)',
          'Use list_forms to find valid form IDs',
          'Verify form has submissions in the specified date range'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};
