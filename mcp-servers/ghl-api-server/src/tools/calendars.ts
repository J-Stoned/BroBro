/**
 * Calendar Management Tools
 *
 * Story 3.5: Contacts, Funnels, Forms, Calendars Tools
 * Provides MCP tools for managing GoHighLevel calendars including:
 * - Listing all calendars in a location
 * - Creating appointments with contacts
 *
 * GHL Calendars Documentation:
 * - Calendars manage appointment scheduling and availability
 * - Each calendar has: name, slots, timezone, booking settings
 * - API Endpoints: /calendars, /calendars/{calendarId}/appointments
 */

import { z } from 'zod';
import { ghlClient } from '../api/ghl-client.js';
import { logger } from '../utils/logger.js';

/**
 * List Calendars Tool
 *
 * Lists all calendars in a GoHighLevel location with availability information.
 */
export const listCalendarsTool = {
  name: 'list_calendars',
  description: 'List all calendars in a GoHighLevel location. Calendars manage appointment scheduling, availability slots, and booking settings.',
  schema: z.object({
    locationId: z.string().describe('The GHL location ID to list calendars from'),
    includeSlots: z.boolean().optional().default(false).describe('Include available time slots for each calendar (can be large)'),
    limit: z.number().optional().default(100).describe('Maximum number of calendars to return (default: 100)'),
    skip: z.number().optional().default(0).describe('Number of calendars to skip for pagination (default: 0)')
  }),

  async handler(args: {
    locationId: string;
    includeSlots?: boolean;
    limit?: number;
    skip?: number;
  }): Promise<string> {
    logger.info('list_calendars tool invoked', {
      locationId: args.locationId,
      includeSlots: args.includeSlots
    });

    try {
      // Build query parameters
      const params: Record<string, any> = {
        locationId: args.locationId,
        limit: args.limit || 100,
        skip: args.skip || 0
      };

      // Get calendars from GHL API
      const result = await ghlClient.get('/calendars/', params);

      const calendars = result.calendars || [];

      logger.info('Calendars retrieved successfully', {
        count: calendars.length,
        locationId: args.locationId
      });

      // Format calendars for better readability
      const formattedCalendars = calendars.map((calendar: any) => {
        const calendarInfo: any = {
          id: calendar.id,
          name: calendar.name,
          description: calendar.description || '',
          slug: calendar.slug || calendar.urlSlug,
          url: calendar.url || calendar.bookingUrl,
          timezone: calendar.timezone || 'UTC',
          duration: calendar.duration || calendar.slotDuration || 30, // minutes
          bufferTime: calendar.bufferTime || 0, // minutes before/after
          availability: calendar.availability || calendar.openHours || {},
          appointmentType: calendar.appointmentType || calendar.meetingType || 'standard',
          isActive: calendar.isActive !== false,
          allowReschedule: calendar.allowReschedule !== false,
          allowCancel: calendar.allowCancel !== false,
          teamMembers: calendar.teamMembers || calendar.assignedUsers || [],
          notifications: {
            sendConfirmation: calendar.sendConfirmationEmail !== false,
            sendReminder: calendar.sendReminderEmail !== false
          },
          createdAt: calendar.createdAt,
          updatedAt: calendar.updatedAt
        };

        // Include slots if requested
        if (args.includeSlots && calendar.slots) {
          calendarInfo.slots = calendar.slots;
        }

        return calendarInfo;
      });

      const response = {
        success: true,
        total: calendars.length,
        calendars: formattedCalendars,
        pagination: {
          limit: args.limit || 100,
          skip: args.skip || 0,
          hasMore: calendars.length === (args.limit || 100)
        },
        summary: {
          active: formattedCalendars.filter((c: any) => c.isActive).length,
          inactive: formattedCalendars.filter((c: any) => !c.isActive).length,
          avgDuration: Math.round(
            formattedCalendars.reduce((sum: number, c: any) => sum + c.duration, 0) /
            formattedCalendars.length
          ),
          byType: formattedCalendars.reduce((acc: any, c: any) => {
            acc[c.appointmentType] = (acc[c.appointmentType] || 0) + 1;
            return acc;
          }, {})
        },
        nextSteps: [
          'Use create_appointment to book appointments on calendars',
          'Share calendar URLs with contacts for self-booking',
          'Configure calendar settings in GHL interface',
          'Set up team member availability',
          'To get more results, increase skip parameter'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to list calendars', {
        locationId: args.locationId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the location ID is correct',
          'Check OAuth token has calendar read permissions',
          'Ensure location has calendars created',
          'Try without includeSlots if request times out'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};

/**
 * Create Appointment Tool
 *
 * Creates a new appointment on a calendar with contact information.
 */
export const createAppointmentTool = {
  name: 'create_appointment',
  description: 'Create a new appointment on a GoHighLevel calendar. Books a time slot with contact information, sends confirmations, and creates calendar events.',
  schema: z.object({
    calendarId: z.string().describe('The calendar ID to book the appointment on'),
    contactId: z.string().describe('The contact ID for the appointment'),
    startTime: z.string().describe('Appointment start time (ISO 8601 format: YYYY-MM-DDTHH:mm:ss or YYYY-MM-DDTHH:mm:ssZ)'),
    endTime: z.string().optional().describe('Appointment end time (ISO 8601 format). If not provided, uses calendar default duration'),
    title: z.string().optional().describe('Appointment title/subject'),
    notes: z.string().optional().describe('Internal notes about the appointment'),
    appointmentStatus: z.enum(['confirmed', 'pending', 'cancelled']).optional().default('confirmed').describe('Initial appointment status'),
    sendNotifications: z.boolean().optional().default(true).describe('Send confirmation email/SMS to contact (default: true)'),
    meetingLocation: z.string().optional().describe('Meeting location (address for in-person, Zoom link for virtual)'),
    appointmentType: z.string().optional().describe('Type of appointment (e.g., "Consultation", "Demo", "Follow-up")')
  }),

  async handler(args: {
    calendarId: string;
    contactId: string;
    startTime: string;
    endTime?: string;
    title?: string;
    notes?: string;
    appointmentStatus?: 'confirmed' | 'pending' | 'cancelled';
    sendNotifications?: boolean;
    meetingLocation?: string;
    appointmentType?: string;
  }): Promise<string> {
    logger.info('create_appointment tool invoked', {
      calendarId: args.calendarId,
      contactId: args.contactId,
      startTime: args.startTime
    });

    try {
      // Get calendar details
      const calendar = await ghlClient.get(`/calendars/${args.calendarId}`);

      // Get contact details
      const contact = await ghlClient.get(`/contacts/${args.contactId}`);

      // Parse start time
      const startDate = new Date(args.startTime);
      if (isNaN(startDate.getTime())) {
        throw new Error('Invalid startTime format. Use ISO 8601 format: YYYY-MM-DDTHH:mm:ss');
      }

      // Calculate end time if not provided
      let endDate: Date;
      if (args.endTime) {
        endDate = new Date(args.endTime);
        if (isNaN(endDate.getTime())) {
          throw new Error('Invalid endTime format. Use ISO 8601 format: YYYY-MM-DDTHH:mm:ss');
        }
      } else {
        // Use calendar default duration
        const durationMinutes = calendar.duration || calendar.slotDuration || 30;
        endDate = new Date(startDate.getTime() + durationMinutes * 60000);
      }

      // Build appointment payload
      const appointmentData: Record<string, any> = {
        calendarId: args.calendarId,
        contactId: args.contactId,
        startTime: startDate.toISOString(),
        endTime: endDate.toISOString(),
        title: args.title || `${calendar.name} - ${contact.firstName || 'Contact'} ${contact.lastName || ''}`.trim(),
        notes: args.notes || '',
        status: args.appointmentStatus || 'confirmed',
        sendNotifications: args.sendNotifications !== false,
        timezone: calendar.timezone || 'UTC'
      };

      // Add optional fields
      if (args.meetingLocation) {
        appointmentData.meetingLocation = args.meetingLocation;
        appointmentData.location = args.meetingLocation;
      }
      if (args.appointmentType) {
        appointmentData.appointmentType = args.appointmentType;
      }

      // Create appointment via GHL API
      const result = await ghlClient.post(`/calendars/${args.calendarId}/appointments`, appointmentData);

      const appointmentId = result.appointment?.id || result.id;

      logger.info('Appointment created successfully', {
        appointmentId: appointmentId,
        calendarId: args.calendarId,
        contactId: args.contactId,
        startTime: args.startTime
      });

      const response = {
        success: true,
        appointment: {
          id: appointmentId,
          calendarId: args.calendarId,
          calendarName: calendar.name,
          contactId: args.contactId,
          contactName: `${contact.firstName || ''} ${contact.lastName || ''}`.trim(),
          contactEmail: contact.email,
          contactPhone: contact.phone,
          startTime: startDate.toISOString(),
          endTime: endDate.toISOString(),
          duration: Math.round((endDate.getTime() - startDate.getTime()) / 60000), // minutes
          title: appointmentData.title,
          status: args.appointmentStatus || 'confirmed',
          timezone: calendar.timezone || 'UTC'
        },
        confirmationDetails: {
          notificationsSent: args.sendNotifications !== false,
          confirmationUrl: result.confirmationUrl || result.url,
          icsFile: result.icsFile || result.icalUrl,
          meetingLocation: args.meetingLocation
        },
        message: `Appointment created successfully for ${appointmentData.title}`,
        nextSteps: [
          'Contact will receive confirmation email/SMS if notifications enabled',
          'Appointment appears in GHL calendar and team member calendars',
          'Use get_contact to verify appointment in contact record',
          'Send reminder before appointment time',
          'Track attendance and follow up after appointment'
        ]
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to create appointment', {
        calendarId: args.calendarId,
        contactId: args.contactId,
        error: error instanceof Error ? error.message : String(error)
      });

      const errorResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        troubleshooting: [
          'Verify the calendar ID is correct',
          'Verify the contact ID is correct',
          'Check OAuth token has appointment creation permissions',
          'Ensure startTime is in ISO 8601 format (YYYY-MM-DDTHH:mm:ss)',
          'Verify time slot is available (not already booked)',
          'Check that startTime is in the future',
          'Ensure startTime falls within calendar availability hours',
          'Use list_calendars to find valid calendar IDs',
          'Use search_contacts or get_contact to verify contact exists'
        ]
      };

      return JSON.stringify(errorResponse, null, 2);
    }
  }
};
