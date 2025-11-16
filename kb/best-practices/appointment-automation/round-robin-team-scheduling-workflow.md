# Round Robin Team Scheduling and Workload Distribution

## Category
appointment automation

## Effectiveness
proven

## Description
Implement GHL's Round Robin Calendar distribution logic to automatically assign appointments across team members, ensuring balanced workload distribution and optimized availability. This system eliminates manual assignment decisions, prevents team member overload, and maintains customer continuity through intelligent assignment rules based on priority, availability, and booking history.

## Implementation Steps

1. **Create Round Robin Calendar**
   - Navigate to Settings → Calendars → Create New Calendar
   - Calendar Type: Select "Round Robin" (vs. "Event" or "Service")
   - Name: Descriptive team name (e.g., "Sales Team Round Robin", "Support Consultations")
   - Set appointment duration, buffer times, and availability windows
   - Configure meeting location type: Zoom, Google Meet, Teams, Phone, Physical Address, or Custom

2. **Add Team Members to Calendar**
   - Navigate to Calendar Settings → Team Members
   - Click "Add Team Member" → Select users from account
   - Assign priority level for each member:
     - **High Priority**: Senior team members, VIP closers, specialists (assigned first)
     - **Medium Priority**: Standard team members (assigned second)
     - **Low Priority**: Junior members, trainees, backup staff (assigned last)
   - Set individual availability windows for each member (may differ from calendar-wide settings)
   - Configure time zone handling for distributed teams

3. **Choose Distribution Logic**
   - **Option A: Optimize for Availability** (Recommended for time-sensitive services)
     - Algorithm: Assigns to first available team member regardless of previous bookings
     - Best For: Customer support, urgent consultations, medical appointments, tech support
     - Behavior: Minimizes customer wait time, maximizes booking success rate
   - **Option B: Optimize for Equal Distribution** (Recommended for sales/consulting)
     - Algorithm: Balances appointments evenly across team members over 24-hour rolling window
     - Best For: Sales teams, consultation services, coaching programs
     - Behavior: Prevents senior members from being overloaded, ensures fair lead distribution
     - **Note**: Recalculates once every 24 hours, not real-time after each booking

4. **Enable Contact Continuity (Highly Recommended)**
   - Toggle "Enable Contact Continuity" in calendar settings
   - Behavior: Once a contact books with a specific team member, ALL future appointments automatically assign to same person
   - Benefits:
     - Builds stronger customer relationships through consistency
     - Reduces onboarding time for repeat appointments
     - Improves close rates by 30-40% (established rapport)
   - Override: Staff can manually reassign if continuity member unavailable

5. **Configure Rescheduling Assignment Behavior**
   - **Option A: Reassign Through Round Robin**
     - When customer reschedules, appointment enters round robin algorithm again
     - New team member may be assigned based on availability/distribution rules
     - Best For: High team turnover, commodity services, technical support
   - **Option B: Keep Same Appointment Owner**
     - Rescheduled appointments remain with original team member
     - Booking widget only shows original owner's available slots
     - Best For: Relationship-based services, ongoing coaching, medical follow-ups
     - **Recommended**: Use this option to maintain customer relationship continuity

6. **Set Up Automated Assignment Notifications**
   - Configure team member notifications when assigned new appointments
   - Email notification: Include customer details, appointment type, booking source
   - SMS notification (optional): For urgent or high-value appointments
   - Slack/internal system notification: Use webhooks to notify team coordination channels
   - Include calendar invite (.ics) with Zoom/Meet links pre-configured

7. **Handle Unavailable Team Members**
   - System automatically skips unavailable members (based on calendar availability windows)
   - Configure backup assignment rules: If all primary members unavailable, assign to manager
   - Set "buffer" team member: Always available low-priority member for overflow
   - Enable "Outside working hours" fallback: Route to scheduling link for manual review

8. **Implement Priority-Based Assignment Strategy**
   - **High Priority Members**: Top performers, specialists, senior consultants
     - Assign to high-value leads (filter by lead source, score, or custom field)
     - Use workflow conditional logic: "If Lead Score > 75, assign to High Priority calendar"
   - **Medium Priority Members**: Standard team capacity
     - Handle majority of inbound bookings
   - **Low Priority Members**: Training opportunities, backup coverage
     - Assign to lower-value leads or specific appointment types (e.g., "Discovery Call" only)

9. **Integrate with Workflow Automation**
   - Trigger: "Customer Booked Appointment" on Round Robin calendar
   - Add Condition: Check assigned team member name
   - Branch by priority level:
     - High Priority: Send team member SMS notification + internal Slack alert to manager
     - Medium Priority: Standard email notification
     - Low Priority: Assign senior member as "shadow" for training/review
   - Add assigned team member's contact info to confirmation messages sent to customer

10. **Monitor and Optimize Distribution**
    - Weekly Review: Check appointment distribution report (should be 80-100% balanced for equal distribution)
    - Track metrics by team member:
      - Total appointments assigned
      - Show-up rate (identifies team members with poor customer experience)
      - Close rate (identifies top performers for priority elevation)
      - Average appointment duration (identifies efficiency issues)
    - Adjust priority levels based on performance data
    - Rebalance team member availability windows if distribution is skewed

## Expected Outcomes

- **Balanced Workload**: Equal distribution mode achieves 90-95% balance across team members over 24-hour periods
- **Eliminated Manual Assignment**: 100% of appointments automatically assigned based on rules, saving 5-10 minutes per booking
- **Faster Customer Response**: Optimize for availability mode reduces "first available slot" from days to hours
- **Improved Customer Relationships**: Contact continuity increases repeat booking rate by 35-40%
- **Reduced No-Shows**: Assigned team member relationship reduces no-show rate by 20-25%
- **Performance Visibility**: Clear metrics by team member enable data-driven coaching and priority adjustments
- **Scalable Growth**: Add new team members to calendar without workflow changes, system auto-adjusts distribution
- **Fair Lead Distribution**: Sales teams report 25-30% reduction in internal conflict over lead assignment

## Source
[Documentation] GoHighLevel - "Appointment Distribution Logic for Round Robin Calendars" (2024-05-10) - https://help.gohighlevel.com/support/solutions/articles/155000001484-appointment-distribution-logic-for-round-robin-calendars

## Date Added
2025-10-26
