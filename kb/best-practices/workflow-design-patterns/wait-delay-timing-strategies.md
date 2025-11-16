# Wait and Delay Timing Strategies

## Category
workflow design patterns

## Effectiveness
proven

## Description
Strategic wait actions are essential for creating natural, human-like communication flows in GoHighLevel workflows. The Wait action holds contacts in workflows for specified durations, until conditions are met, or during designated time windows. Proper timing strategies prevent robotic interactions, respect business hours, and allow contacts time to take desired actions before proceeding to subsequent workflow steps. This pattern encompasses multiple wait types including fixed time delays, conditional waits, event-based pauses, and advanced scheduling windows that only count time during specified business hours.

By implementing strategic wait patterns, you create breathing room in automated sequences that increases engagement rates and reduces unsubscribe frequency. Wait actions serve as crucial pacing mechanisms that separate your automation from spam-like rapid-fire messaging while simultaneously providing opportunities for behavioral tracking and conditional routing based on contact responses.

## Implementation Steps

1. **Select the appropriate wait type for your use case**
   - Use Time Delay for fixed durations (minutes, hours, days) when you need consistent pacing between actions
   - Choose Condition wait when you need contacts to meet specific criteria before proceeding
   - Implement Contact Reply wait for email or SMS channels to pause until contacts respond
   - Set up Trigger Link Clicked wait to hold contacts until they engage with specific links
   - Configure Email Event wait to monitor opens, clicks, unsubscribes, bounces, or complaints
   - Use Event/Appointment Time wait to trigger actions before or after scheduled appointments
   - Set Overdue wait to activate on or after invoice due dates

2. **Configure time delay settings for humanized interactions**
   - Add 1-5 minute delays between immediate follow-up actions to create natural conversation flow
   - Implement 20-30 minute delays in cart abandonment sequences to allow reconsideration time
   - Set 24-hour delays between educational content pieces in nurture campaigns
   - Use 3-7 day delays for check-in messages after major milestone events
   - Avoid delays under 1 minute as they provide no practical pacing benefit

3. **Implement Advanced Window settings for business hour compliance**
   - Toggle on the Advance Window option to restrict when wait time counts
   - Specify your business days (e.g., Monday-Friday) when the workflow should be active
   - Set business hours (e.g., 9am-5pm) to ensure contacts only proceed during working hours
   - Understand that contacts entering outside the window will have their timer start at the next available window opening
   - Example: A contact entering Saturday with a 10-minute delay and Monday-Friday 9am-5pm window will start their timer Monday at 9am

4. **Configure conditional wait with segment logic**
   - Create individual conditions like "Contact's Job Title is CEO" or "Tag contains Interested"
   - Group multiple conditions into segments using AND logic (all must be true) or OR logic (any can be true)
   - Build multiple segments to create parallel qualification pathways
   - Remember that contacts exit the wait step when any one segment evaluates as true
   - Add timeout failsafes for events that may never occur by combining "Wait for event OR timeout" patterns

5. **Set timezone handling based on audience geography**
   - Choose Account Timezone for local/regional businesses where all contacts are in similar locations
   - Select Contact Timezone for global audiences to respect individual contact time zones
   - Ensure contact timezone data is populated in custom fields before relying on this feature
   - Test workflows with contacts in different timezones to verify proper timing

6. **Apply wait strategies to common use cases**
   - Welcome sequences: 1-2 day delays between onboarding emails to give customers time to explore
   - Follow-up campaigns: 1-5 minute delays to create conversational pacing without appearing instant
   - Cart recovery: 20-minute initial delay, then 24-hour and 72-hour follow-ups
   - Birthday automation: Wait until specific annual dates using custom date field conditions
   - Post-appointment follow-up: 1-hour delay after appointment end time for feedback requests
   - Re-engagement campaigns: 7-14 day delays between touchpoints to avoid overwhelming dormant contacts

## Expected Outcomes

- Increased email open rates by 15-25% through optimized send timing during business hours
- Reduced unsubscribe rates by 10-20% by eliminating rapid-fire messaging patterns
- Improved conversion rates by 20-30% in cart recovery sequences using strategic delay timing
- Higher appointment show rates through properly timed reminder sequences
- Enhanced contact engagement through humanized, natural-feeling communication flows
- Better workflow performance metrics with conditional waits that route contacts based on behavior
- Reduced workflow executions and costs by holding contacts until meaningful triggers occur
- Increased customer satisfaction scores through timezone-aware delivery timing
- More efficient automation that respects contact preferences and behavioral patterns

## Source
[Official Documentation] HighLevel Support Portal - "Workflow Action - Wait" (2025-10-26) - https://help.gohighlevel.com/support/solutions/articles/155000002470-action-wait

## Date Added
2025-10-26
