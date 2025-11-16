/**
 * Contact Management Tools
 *
 * Story 3.5: Contacts, Funnels, Forms, Calendars Tools
 * Provides MCP tools for managing GoHighLevel contacts including:
 * - Creating new contacts with custom fields
 * - Searching contacts with advanced filters
 * - Updating contact information
 * - Retrieving full contact details
 *
 * GHL Contacts Documentation:
 * - Contacts are the core entity in GHL representing leads/customers
 * - Each contact has: name, email, phone, tags, custom fields, location
 * - API Endpoints: /contacts (base path)
 */

import { z } from 'zod';
import { ghlClient } from '../api/ghl-client.js';
import { logger } from '../utils/logger.js';

/**
 * Create Contact Tool
 *
 * Creates a new contact in GoHighLevel with specified information.
 *
 * Common use cases:
 * - Add lead from form submission
 * - Import contact from external system
 * - Create test contact for workflows
 * - Manual lead entry
 */
export const createContactTool = {
  name: 'create_contact',
  description: 'Create a new contact in GoHighLevel. Contacts are the core entity representing leads and customers. Supports custom fields, tags, and full contact information.',
  schema: z.object({
    locationId: z.string().describe('The GHL location ID where the contact will be created'),
    firstName: z.string().optional().describe('Contact first name'),
    lastName: z.string().optional().describe('Contact last name'),
    email: z.string().email().optional().describe('Contact email address (must be valid email format)'),
    phone: z.string().optional().describe('Contact phone number (E.164 format recommended: +1234567890)'),
    address1: z.string().optional().describe('Street address line 1'),
    city: z.string().optional().describe('City'),
    state: z.string().optional().describe('State/Province'),
    postalCode: z.string().optional().describe('Postal/ZIP code'),
    country: z.string().optional().describe('Country'),
    website: z.string().optional().describe('Website URL'),
    timezone: z.string().optional().describe('Timezone (e.g., America/New_York)'),
    tags: z.array(z.string()).optional().describe('Array of tags to apply to contact'),
    customFields: z.record(z.any()).optional().describe('Custom field values (key-value pairs)'),
    source: z.string().optional().describe('Lead source (e.g., "Website", "Referral")'),
    assignedTo: z.string().optional().describe('User ID to assign contact to')
  }).refine(data => data.email || data.phone, {
    message: 'At least one of email or phone must be provided'
  }),

  async handler(args: {
    locationId: string;
    firstName?: string;
    lastName?: string;
    email?: string;
    phone?: string;
    address1?: string;
    city?: string;
    state?: string;
    postalCode?: string;
    country?: string;
    website?: string;
    timezone?: string;
    tags?: string[];
    customFields?: Record<string, any>;
    source?: string;
    assignedTo?: string;
  }): Promise<string> {
    logger.info('create_contact tool invoked', {
      locationId: args.locationId,
      email: args.email,
      phone: args.phone,
      tags: args.tags?.length || 0
    });

    try {
      // Build contact payload
      const contactData: Record<string, any> = {
        locationId: args.locationId
      };

      // Add provided fields
      if (args.firstName) contactData.firstName = args.firstName;
      if (args.lastName) contactData.lastName = args.lastName;
      if (args.email) contactData.email = args.email;
      if (args.phone) contactData.phone = args.phone;
      if (args.address1) contactData.address1 = args.address1;
      if (args.city) contactData.city = args.city;
      if (args.state) contactData.state = args.state;
      if (args.postalCode) contactData.postalCode = args.postalCode;
      if (args.country) contactData.country = args.country;
      if (args.website) contactData.website = args.website;
      if (args.timezone) contactData.timezone = args.timezone;
      if (args.tags) contactData.tags = args.tags;
      if (args.customFields) contactData.customField = args.customFields;
      if (args.source) contactData.source = args.source;
      if (args.assignedTo) contactData.assignedTo = args.assignedTo;

      // Create contact via GHL API
      const result = await ghlClient.post('/contacts/', contactData);

      logger.info('Contact created successfully', {
        contactId: result.contact?.id || result.id,
        email: args.email,
        phone: args.phone
      });

      const contactId = result.contact?.id || result.id;
      const response = {
        success: true,
        contact: {
          id: contactId,
          firstName: args.firstName,
          lastName: args.lastName,
          email: args.email,
          phone: args.phone,
          tags: args.tags || [],
          locationId: args.locationId
        },
        message: `Contact created successfully`,
        nextSteps: [
          'Use get_contact to view full contact details',
          'Use update_contact to modify contact information',
          'Add contact to workflows or campaigns',
          'Create appointments using create_appointment tool'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to create contact', {
        locationId: args.locationId,
        email: args.email,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the location ID is correct',
          'Check that email format is valid (if provided)',
          'Ensure phone number is in valid format (E.164 recommended)',
          'Verify OAuth token has contact creation permissions',
          'Check if contact with same email already exists (may cause duplicate error)',
          'Verify custom field keys match your GHL location configuration'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};

/**
 * Search Contacts Tool
 *
 * Search for contacts using various filters including email, phone, name, and tags.
 */
export const searchContactsTool = {
  name: 'search_contacts',
  description: 'Search for contacts in GoHighLevel using filters like email, phone, name, or tags. Returns paginated results with full contact information.',
  schema: z.object({
    locationId: z.string().describe('The GHL location ID to search in'),
    query: z.string().optional().describe('Search query (searches name, email, phone)'),
    email: z.string().optional().describe('Filter by exact email address'),
    phone: z.string().optional().describe('Filter by phone number'),
    tags: z.array(z.string()).optional().describe('Filter by tags (contacts must have ALL specified tags)'),
    limit: z.number().optional().default(100).describe('Maximum number of contacts to return (default: 100, max: 100)'),
    skip: z.number().optional().default(0).describe('Number of contacts to skip for pagination (default: 0)')
  }),

  async handler(args: {
    locationId: string;
    query?: string;
    email?: string;
    phone?: string;
    tags?: string[];
    limit?: number;
    skip?: number;
  }): Promise<string> {
    logger.info('search_contacts tool invoked', {
      locationId: args.locationId,
      query: args.query,
      email: args.email,
      tags: args.tags?.length || 0,
      limit: args.limit
    });

    try {
      // Build query parameters
      const params: Record<string, any> = {
        locationId: args.locationId,
        limit: Math.min(args.limit || 100, 100), // Cap at 100
        skip: args.skip || 0
      };

      // Add search filters
      if (args.query) params.query = args.query;
      if (args.email) params.email = args.email;
      if (args.phone) params.phone = args.phone;
      if (args.tags && args.tags.length > 0) {
        params.tags = args.tags.join(',');
      }

      // Search contacts via GHL API
      const result = await ghlClient.get('/contacts/', params);

      const contacts = result.contacts || [];

      logger.info('Contacts search completed', {
        found: contacts.length,
        locationId: args.locationId
      });

      // Format contacts for better readability
      const formattedContacts = contacts.map((contact: any) => ({
        id: contact.id,
        firstName: contact.firstName || '',
        lastName: contact.lastName || '',
        email: contact.email || '',
        phone: contact.phone || '',
        tags: contact.tags || [],
        source: contact.source || '',
        dateAdded: contact.dateAdded,
        assignedTo: contact.assignedTo
      }));

      const response = {
        success: true,
        total: contacts.length,
        contacts: formattedContacts,
        pagination: {
          limit: args.limit || 100,
          skip: args.skip || 0,
          hasMore: contacts.length === (args.limit || 100)
        },
        filters: {
          query: args.query,
          email: args.email,
          phone: args.phone,
          tags: args.tags
        },
        nextSteps: [
          'Use get_contact with contactId to view full details',
          'Use update_contact to modify contact information',
          'To get more results, increase skip parameter',
          'Refine search with more specific query or filters'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to search contacts', {
        locationId: args.locationId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the location ID is correct',
          'Check OAuth token has contact read permissions',
          'Ensure email/phone format is valid if using those filters',
          'Verify tags exist in your GHL location',
          'Try broader search criteria if no results found'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};

/**
 * Get Contact Tool
 *
 * Retrieves detailed information about a specific contact including
 * all fields, tags, custom fields, and recent activity.
 */
export const getContactTool = {
  name: 'get_contact',
  description: 'Get detailed information about a specific contact including all fields, tags, custom fields, and activity. Use this to view complete contact profile.',
  schema: z.object({
    contactId: z.string().describe('The contact ID to retrieve')
  }),

  async handler(args: {
    contactId: string;
  }): Promise<string> {
    logger.info('get_contact tool invoked', {
      contactId: args.contactId
    });

    try {
      // Get contact from GHL API
      const contact = await ghlClient.get(`/contacts/${args.contactId}`);

      logger.info('Contact retrieved successfully', {
        contactId: args.contactId,
        email: contact.email
      });

      const response = {
        success: true,
        contact: {
          // Basic Info
          id: contact.id,
          locationId: contact.locationId,
          firstName: contact.firstName || '',
          lastName: contact.lastName || '',
          fullName: `${contact.firstName || ''} ${contact.lastName || ''}`.trim(),
          email: contact.email || '',
          phone: contact.phone || '',

          // Address
          address: {
            address1: contact.address1 || '',
            city: contact.city || '',
            state: contact.state || '',
            postalCode: contact.postalCode || '',
            country: contact.country || ''
          },

          // Additional Info
          website: contact.website || '',
          timezone: contact.timezone || '',
          source: contact.source || '',
          tags: contact.tags || [],
          customFields: contact.customField || contact.customFields || {},

          // Assignment & Metadata
          assignedTo: contact.assignedTo,
          dateAdded: contact.dateAdded,
          dateUpdated: contact.dateUpdated || contact.lastUpdated,

          // Activity Summary
          activitySummary: {
            lastActivity: contact.lastActivity,
            conversationCount: contact.conversationCount || 0,
            appointmentCount: contact.appointmentCount || 0
          }
        },
        analysis: {
          hasEmail: !!contact.email,
          hasPhone: !!contact.phone,
          hasAddress: !!(contact.address1 && contact.city),
          tagCount: contact.tags?.length || 0,
          customFieldCount: Object.keys(contact.customField || contact.customFields || {}).length,
          isAssigned: !!contact.assignedTo
        },
        nextSteps: [
          'Use update_contact to modify contact information',
          'Use search_contacts to find related contacts',
          'Create appointments with create_appointment tool',
          'Add contact to workflows or campaigns'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to get contact', {
        contactId: args.contactId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the contact ID is correct (format: contact_XXXXXXXXXXXXXXXXXXXX)',
          'Check OAuth token has contact read permissions',
          'Ensure contact exists and is not deleted',
          'Use search_contacts if you only have email/phone instead of ID'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};

/**
 * Update Contact Tool
 *
 * Updates an existing contact's information. Only provided fields will be updated.
 */
export const updateContactTool = {
  name: 'update_contact',
  description: 'Update an existing contact in GoHighLevel. Only provide the fields you want to change. All other fields will remain unchanged.',
  schema: z.object({
    contactId: z.string().describe('The contact ID to update'),
    firstName: z.string().optional().describe('New first name'),
    lastName: z.string().optional().describe('New last name'),
    email: z.string().email().optional().describe('New email address'),
    phone: z.string().optional().describe('New phone number'),
    address1: z.string().optional().describe('New street address'),
    city: z.string().optional().describe('New city'),
    state: z.string().optional().describe('New state/province'),
    postalCode: z.string().optional().describe('New postal code'),
    country: z.string().optional().describe('New country'),
    website: z.string().optional().describe('New website URL'),
    timezone: z.string().optional().describe('New timezone'),
    tags: z.array(z.string()).optional().describe('Replace tags with this array (use empty array to clear all tags)'),
    customFields: z.record(z.any()).optional().describe('Update custom field values'),
    source: z.string().optional().describe('Update lead source'),
    assignedTo: z.string().optional().describe('Assign to new user (user ID)')
  }),

  async handler(args: {
    contactId: string;
    firstName?: string;
    lastName?: string;
    email?: string;
    phone?: string;
    address1?: string;
    city?: string;
    state?: string;
    postalCode?: string;
    country?: string;
    website?: string;
    timezone?: string;
    tags?: string[];
    customFields?: Record<string, any>;
    source?: string;
    assignedTo?: string;
  }): Promise<string> {
    logger.info('update_contact tool invoked', {
      contactId: args.contactId,
      fieldsToUpdate: Object.keys(args).filter(k => k !== 'contactId' && args[k as keyof typeof args] !== undefined)
    });

    try {
      // Build update payload (only include provided fields)
      const updateData: Record<string, any> = {};

      if (args.firstName !== undefined) updateData.firstName = args.firstName;
      if (args.lastName !== undefined) updateData.lastName = args.lastName;
      if (args.email !== undefined) updateData.email = args.email;
      if (args.phone !== undefined) updateData.phone = args.phone;
      if (args.address1 !== undefined) updateData.address1 = args.address1;
      if (args.city !== undefined) updateData.city = args.city;
      if (args.state !== undefined) updateData.state = args.state;
      if (args.postalCode !== undefined) updateData.postalCode = args.postalCode;
      if (args.country !== undefined) updateData.country = args.country;
      if (args.website !== undefined) updateData.website = args.website;
      if (args.timezone !== undefined) updateData.timezone = args.timezone;
      if (args.tags !== undefined) updateData.tags = args.tags;
      if (args.customFields !== undefined) updateData.customField = args.customFields;
      if (args.source !== undefined) updateData.source = args.source;
      if (args.assignedTo !== undefined) updateData.assignedTo = args.assignedTo;

      if (Object.keys(updateData).length === 0) {
        return JSON.stringify({
          success: false,
          error: 'No fields provided to update. Please specify at least one field to change.'
        }, null, 2);
      }

      // Update contact via GHL API
      await ghlClient.put(`/contacts/${args.contactId}`, updateData);

      logger.info('Contact updated successfully', {
        contactId: args.contactId,
        updatedFields: Object.keys(updateData)
      });

      const response = {
        success: true,
        contact: {
          id: args.contactId,
          updatedFields: Object.keys(updateData)
        },
        message: `Contact updated successfully`,
        changes: updateData,
        nextSteps: [
          'Use get_contact to verify changes',
          'Contact will reflect updates immediately in GHL',
          'Workflow triggers may fire based on field changes',
          'Updated information available for campaigns and automations'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to update contact', {
        contactId: args.contactId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the contact ID is correct',
          'Check OAuth token has contact update permissions',
          'Ensure email format is valid if updating email',
          'Verify phone format is correct if updating phone',
          'Check that custom field keys match your location configuration',
          'Ensure contact exists and is not deleted'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};
