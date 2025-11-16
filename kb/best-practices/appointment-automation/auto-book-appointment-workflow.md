# Automated Appointment Booking from Form Submissions

## Category
appointment automation

## Effectiveness
proven

## Description
Automatically book appointments on team calendars immediately when prospects submit booking forms, eliminating manual scheduling friction and reducing time-to-appointment from hours to seconds. This workflow uses GHL's Book Appointment action to instantly reserve time slots based on form data, calendar availability, and team assignment rules.

## Implementation Steps

1. **Configure Target Calendar**
   - Navigate to Settings → Calendars
   - Create dedicated calendar for automated bookings (e.g., "Sales Discovery Calls")
   - Set availability windows, buffer times, and duration
   - Enable round-robin assignment if using team scheduling
   - Verify calendar does NOT have recurring appointments enabled (limitation)

2. **Create Booking Form**
   - Build form with required fields: Name, Email, Phone, Preferred Date, Preferred Time
   - Use date/time picker fields with proper formatting (MM-DD-YYYY HH:MM format)
   - Add dropdown for appointment type if offering multiple services
   - Include timezone selection to prevent scheduling errors

3. **Build Automation Workflow**
   - Navigate to Automations → Create New Workflow → Start From Scratch
   - Trigger: "Form Submitted" → Select your booking form
   - Add Action → Book Appointment
   - Action Name: "Auto-Book Sales Call"
   - Select target calendar
   - Team Assignment: "Calendar Default" (uses round-robin) or specific member
   - Date/Time Mapping: Map form fields to appointment date/time
   - Enable "Check Availability" (default - prevents double-booking)

4. **Add Conditional Logic**
   - Create branch: "If Appointment Booked Successfully = True"
   - TRUE path: Send confirmation email + SMS with calendar invite
   - FALSE path: Send "Availability Issue" email with alternative booking link
   - Add task notification to admin for failed bookings requiring manual review

5. **Configure Confirmation Communications**
   - Email template with calendar .ics attachment
   - SMS with appointment details and cancellation/rescheduling link
   - Include team member name, video call link (if virtual), or office address
   - Send reminders: 24 hours before, 1 hour before

6. **Test and Monitor**
   - Submit test form with various date/time combinations
   - Verify calendar entries appear correctly
   - Check team member assignments distribute properly
   - Monitor failed booking rate and optimize availability rules

## Expected Outcomes

- **Instant Booking**: Appointments scheduled within 5 seconds of form submission vs. 4-24 hours manually
- **Higher Show Rates**: Immediate confirmation increases show-up by 35% due to commitment consistency
- **Reduced Admin Time**: Eliminates 15-20 minutes per booking of back-and-forth scheduling
- **Better Lead Experience**: Professional, seamless booking process improves brand perception
- **Optimal Calendar Utilization**: Round-robin ensures even distribution across team, maximizing availability
- **Zero Double-Booking**: Automatic availability checking prevents scheduling conflicts

## Source
[Documentation] GoHighLevel - "Book Appointment Action in Workflows" (2024-03-15) - https://help.gohighlevel.com/support/solutions/articles/155000004209-workflow-action-book-appointment

## Date Added
2025-10-26
