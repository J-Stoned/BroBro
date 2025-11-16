# Self-Service Appointment Rescheduling and Cancellation Workflow

## Category
appointment automation

## Effectiveness
proven

## Description
Empower customers to reschedule or cancel appointments independently through automated self-service workflows using GHL's chatbot and calendar link features. This reduces administrative burden by 70-80% while improving customer satisfaction through 24/7 flexibility and instant confirmation.

## Implementation Steps

1. **Enable Lab Features (Required for Chatbot Method)**
   - Navigate to Settings → Labs
   - Enable "Cancel And Reschedule" feature
   - Enable "Form Based Bot" feature
   - **WARNING**: These features cannot be disabled once activated - test in sub-account first
   - Alternative: Use calendar link method (no Lab features required)

2. **Method A: Chatbot-Based Self-Service (Conversational)**
   - Navigate to Conversation AI → Select Bot → Bot Goals
   - Toggle "Enable Cancellation" and "Enable Rescheduling" in Appointment Details section
   - Configure bot personality: "Helpful scheduling assistant - professional but friendly"
   - Set multi-calendar support: Allow rescheduling "from any calendar"
   - Enable bulk cancellation: Allow contacts to cancel multiple appointments in single interaction
   - Test using Bot Trial feature before deployment

3. **Method B: Calendar Link Self-Service (Click-Based)**
   - Navigate to Calendars → Select Calendar → Settings
   - Enable "Allow Rescheduling" and "Allow Cancellation" options
   - Set cancellation/reschedule window: "Up to 24 hours before appointment" (prevents abuse)
   - Generate unique calendar link with management tokens
   - Configure confirmation page: Show success message + new appointment details

4. **Integrate Self-Service Links into Communications**
   - Add reschedule/cancel links to all appointment confirmations (SMS + email)
   - Template example: "Need to reschedule? Click: {{appointment.reschedule_link}} | Cancel: {{appointment.cancel_link}}"
   - Include links in reminder sequence (48hr, 24hr, 2hr reminders)
   - Add links to appointment confirmation page
   - Include in email signatures for booking-related communications

5. **Configure Rescheduling Workflow Automation**
   - Trigger: "Appointment Status" = "Rescheduled"
   - Enable "Allow Re-entry" (critical - lets contacts re-enter workflow for new appointment)
   - Add Condition: Check if reschedule was customer-initiated vs. staff-initiated
   - **Customer-Initiated Path**:
     - Send confirmation SMS: "Your appointment has been rescheduled to {{appointment.date}} at {{appointment.time}}"
     - Send email with updated .ics calendar file
     - Tag contact: "Self-Service User" (indicates tech-savvy, low-maintenance)
     - Re-enter standard reminder workflow
   - **Staff-Initiated Path**:
     - Send explanation SMS if reason provided
     - Offer alternative times via booking link

6. **Configure Cancellation Workflow Automation**
   - Trigger: "Appointment Status" = "Cancelled"
   - Add Condition: Check if cancellation was customer-initiated
   - **Customer-Initiated Path**:
     - Send confirmation SMS: "Your appointment for {{appointment.date}} has been cancelled"
     - Add Wait: 2 hours
     - Send re-booking offer: "Changed your mind? Reschedule here: [Booking Link]"
     - Move to "Cancelled - Needs Re-engagement" pipeline stage
     - Create task for follow-up in 1 week if no rebooking
   - **Staff-Initiated Path**:
     - Send apology + explanation SMS
     - Offer priority rebooking link

7. **Set Up Bulk Cancellation Handling (Chatbot Only)**
   - Enable "Support multiple cancellations in single interaction"
   - Bot flow: "Which appointments would you like to cancel?" → Show list → Confirm selection
   - Send single confirmation message with all cancelled appointment details
   - Purpose: Weather emergencies, illness, schedule changes

8. **Implement Abuse Prevention Rules**
   - Set cancellation/reschedule limits: Max 3 times per appointment
   - Set time window restrictions: No changes within 2 hours of appointment (or custom threshold)
   - Set cool-down period: Prevent immediate re-booking after cancellation (24-hour window)
   - Flag chronic reschedulers: Tag contacts who reschedule >3 times → manual booking required

9. **Monitor and Optimize**
   - Track self-service adoption rate (target: 70-80% of all reschedules/cancellations)
   - Monitor cancellation/reschedule reasons (add optional feedback question)
   - Analyze time-to-reschedule patterns (how quickly customers rebook)
   - Measure admin time savings (calls avoided, manual booking reduction)
   - Track "chronic reschedule" rate and adjust policies if needed

## Expected Outcomes

- **70-80% Admin Reduction**: Eliminate majority of scheduling coordination calls and emails
- **24/7 Flexibility**: Customers can manage appointments outside business hours when it's convenient
- **Higher Satisfaction**: Self-service convenience increases NPS scores by 15-20 points
- **Faster Rebooking**: Average 5 minutes for customer self-reschedule vs. 2-3 days for manual coordination
- **Reduced No-Shows**: Easy rescheduling reduces no-show rate by 25-30% (customers reschedule instead of ghosting)
- **Bulk Efficiency**: Handle emergency mass cancellations (weather, illness) with single bot conversation
- **Professional Experience**: Instant confirmations and automated updates improve brand perception
- **Calendar Optimization**: Real-time availability updates prevent double-booking during reschedules

## Source
[Documentation] GoHighLevel - "Chatbot Appointment Cancellation & Rescheduling Guide" (2024-07-10) - https://help.gohighlevel.com/support/solutions/articles/155000005503-cancellation-and-rescheduling-of-appointments-in-form-based-bots

## Date Added
2025-10-26
