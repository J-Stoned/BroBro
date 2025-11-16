# Post-Appointment Feedback and Review Request Automation

## Category
appointment automation

## Effectiveness
proven

## Description
Automate post-appointment feedback collection and review requests through GHL's workflow triggers, capturing customer satisfaction data immediately after appointments and converting positive experiences into online reviews. This systematic approach increases review volume by 300-400%, identifies service issues in real-time, and provides actionable data for team performance optimization.

## Implementation Steps

1. **Create Post-Appointment Survey**
   - Navigate to Sites → Surveys → Create New Survey
   - Survey Type: "Appointment Feedback Survey"
   - Add 3-5 key questions:
     - Q1: "How would you rate your appointment experience?" (1-5 star rating)
     - Q2: "How satisfied are you with [Team Member Name]?" (1-10 scale)
     - Q3: "What did we do well?" (open text)
     - Q4: "What could we improve?" (open text)
     - Q5: "How likely are you to recommend us?" (0-10 NPS scale)
   - Enable "Thank You" page with custom message
   - Set survey to single submission per contact

2. **Create Appointment Follow-Up Workflow**
   - Navigate to Automations → Workflows → Create New Workflow
   - Trigger: "Appointment Status" = "Showed" (confirmed attendance)
   - Add Filter: Appointment Type = [Select types to follow up on]
   - Add Filter: Exclude if contact has "Do Not Survey" tag

3. **Configure Timing Strategy**
   - **Service-Based Appointments** (consultations, haircuts, etc.):
     - Wait: 2-3 hours after appointment end time
     - Rationale: Experience fresh in memory, but not immediate (avoid interruption)
   - **Medical/Professional Services**:
     - Wait: 24 hours after appointment
     - Rationale: Allow time for processing information, more thoughtful responses
   - **Sales Discovery Calls**:
     - Wait: 1 hour after call end
     - Rationale: Capture immediate sentiment before competitors engage

4. **Send Survey Request**
   - Add Action: Send SMS
   - Message Template: "Hi {{contact.first_name}}! Thanks for meeting with {{appointment.assigned_user}}. We'd love your feedback (30 seconds): [Survey Link]"
   - Add Action: Send Email (backup channel)
   - Email Template: Professional format with embedded survey link or inline questions
   - Subject Line: "How did we do, {{contact.first_name}}?"

5. **Branch Based on Survey Response**
   - Add Wait: 3 days for survey completion
   - Add Condition: "Survey Submitted" = "Appointment Feedback Survey"
   - **Branch A: Survey Completed**
     - Proceed to step 6 (review request logic)
   - **Branch B: Survey NOT Completed**
     - Send one reminder SMS after 48 hours
     - Alternative: Skip survey holdouts, move to generic review request after 7 days

6. **Implement Review Request Logic**
   - Add Condition: Survey Rating (Q1) >= 4 stars AND NPS (Q5) >= 8
   - **Positive Response Path** (4-5 stars, NPS 8-10):
     - Wait: 1 hour after survey submission
     - Send SMS: "So glad you had a great experience! Would you mind sharing a quick review? [Google/Facebook Review Link]"
     - Send Email: Detailed review request with direct links to Google, Facebook, Yelp
     - Add to "Happy Customers" segment for testimonial requests
     - Tag: "Review Requested"
   - **Neutral Response Path** (3 stars, NPS 6-7):
     - Send internal notification to manager: "Neutral feedback from [Contact Name] - review needed"
     - Do NOT request public review
     - Create task: "Follow up with {{contact.first_name}} on feedback"
   - **Negative Response Path** (1-2 stars, NPS 0-5):
     - Immediate internal alert to manager + assigned team member
     - Send SMS to customer: "We're sorry we didn't meet expectations. [Manager Name] will call you within 24 hours to make this right."
     - Create urgent task for manager with survey responses
     - Tag: "Service Recovery Required"
     - Do NOT request public review

7. **Set Up Survey Response Workflow**
   - Create separate workflow: Trigger "Survey Submitted" = "Appointment Feedback Survey"
   - Extract custom field values: Rating, NPS Score, Open Text Responses
   - Update contact record with latest survey data
   - Calculate rolling average satisfaction score (last 5 appointments)
   - Tag contacts based on response patterns:
     - "Promoter" (NPS 9-10)
     - "Passive" (NPS 7-8)
     - "Detractor" (NPS 0-6)

8. **Track Team Member Performance**
   - For each survey submission, update team member performance dashboard
   - Metrics to track:
     - Average rating by team member
     - NPS score by team member
     - Response rate to surveys
     - Common themes in open-text feedback
   - Weekly automated report sent to managers with performance summary
   - Identify top performers for recognition and training opportunities

9. **Optimize Response Rates**
   - A/B test survey timing (2 hours vs. 24 hours post-appointment)
   - Test message personalization level (team member name, appointment type details)
   - Test survey length (3 questions vs. 5 questions - shorter = higher completion)
   - Offer small incentive for survey completion: "$5 off next appointment" or "Entry into monthly $100 gift card drawing"
   - Track completion rate by channel (SMS vs. Email) and optimize send strategy

10. **Close the Feedback Loop**
    - Monthly review of survey responses with full team
    - Share positive feedback publicly (team channel, monthly meeting)
    - Address common improvement themes with action plans
    - Follow up with detractors personally to resolve issues
    - Update service processes based on feedback trends

## Expected Outcomes

- **300-400% Increase in Review Volume**: Systematic review requests from happy customers (vs. sporadic manual requests)
- **65-75% Survey Completion Rate**: Well-timed, short surveys achieve high response rates
- **Real-Time Issue Detection**: Identify service problems within hours, not weeks or months
- **Improved Team Accountability**: Public performance metrics drive service quality improvements
- **Higher Customer Retention**: Service recovery for negative feedback prevents churn (70-80% retention for addressed complaints)
- **Authentic Social Proof**: Continuous stream of fresh reviews improves online reputation and conversion rates
- **Data-Driven Coaching**: Specific feedback enables targeted training for team members
- **NPS Benchmark Tracking**: Quarterly NPS trends reveal overall business health and customer satisfaction trajectory

## Source
[Documentation] GoHighLevel - "How To Build Automated Appointment Follow-up Surveys in Workflow Builder" (2024-04-15) - https://help.gohighlevel.com/support/solutions/articles/48001165881-how-to-build-automated-appointment-follow-up-surveys-in-workflow-builder

## Date Added
2025-10-26
