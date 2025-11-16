# Lead Re-engagement Workflow

## Category
lead nurturing

## Effectiveness
proven

## Description
Lead re-engagement workflows (also called database reactivation or win-back campaigns) systematically reconnect with inactive contacts who previously showed interest but have gone cold, using personalized multi-channel messaging to revive relationships and drive renewed engagement. By identifying dormant leads through engagement filters, segmenting them based on previous interactions, and delivering compelling value propositions, businesses can reactivate 10-15% of cold databases without additional advertising spend. GoHighLevel's automation capabilities enable sophisticated re-engagement sequences that combine educational content, special offers, and feedback surveys to win back lost opportunities and maximize customer lifetime value.

## Implementation Steps

1. **Identify and Segment Inactive Leads**
   - Navigate to Contacts > Smart Lists > Create Smart List
   - Apply filters to identify cold leads:
     - Last activity date: 90+ days ago for warm leads, 180+ days for cold leads
     - Email engagement: No opens in past 60-90 days
     - Pipeline status: Stalled opportunities or abandoned cart contacts
   - Segment further by original lead source, product interest, or previous engagement level
   - Create separate lists for different inactivity levels (90-day, 6-month, 12-month+)
   - Tag segments appropriately: "Reactivation - 90 Day", "Reactivation - 6 Month"

2. **Perform Database Hygiene**
   - Remove hard bounces, invalid email addresses, and unsubscribed contacts
   - Verify remaining contacts meet re-engagement criteria (previous purchase or strong interest signal)
   - Exclude contacts with "Do Not Disturb" status
   - Document total reactivation target audience size
   - Set baseline metrics for comparison (previous engagement rates, LTV)

3. **Design Multi-Stage Re-engagement Campaign**
   - **Stage 1 (Educational)**: Remind contacts of your value and share helpful content (no ask)
   - **Stage 2 (Offer)**: Present time-limited win-back incentive (discount, bonus, exclusive access)
   - **Stage 3 (Feedback)**: Request feedback via survey to understand why they disengaged
   - **Stage 4 (Final Attempt)**: Last-chance message with strongest offer or option to unsubscribe
   - Plan 4-6 touchpoints over 21-30 day period
   - Craft compelling "we miss you" messaging that acknowledges the gap

4. **Create Re-engagement Workflow in GoHighLevel**
   - Go to Automation > Workflows > Create Workflow
   - Set trigger: "Tag Added" and select your reactivation segment tag
   - Alternatively, use "Manual Action" trigger for batch campaign launch
   - Enable re-entry settings if contacts should receive recurring reactivation attempts
   - Name workflow: "Reactivation Campaign - [Segment]"

5. **Build Stage 1: Educational Reconnection**
   - Add "Send Email" action
   - Subject: "We've been thinking about you, {{contact.first_name}}"
   - Content: Share valuable recent content, industry insights, or company updates
   - Include personalized message acknowledging time since last contact
   - Soft CTA: "See what's new" or "Catch up on what you missed"
   - Add "Wait/Delay" action: 3-5 days

6. **Build Stage 2: Incentive Offer**
   - Add "If/Else Condition": Check if Stage 1 email was opened
   - For engaged contacts (Yes branch):
     - Add "Send SMS" action with stronger offer and urgency
     - Subject: "Special comeback offer just for you"
     - Include time-limited discount code or exclusive benefit
     - Clear CTA to book call or make purchase
   - For unengaged contacts (No branch):
     - Add "Send Email" action with subject line reframe
     - Test different value proposition or pain point
   - Add "Wait/Delay" action: 5-7 days

7. **Build Stage 3: Feedback Request**
   - Add "Send Email" action
   - Subject: "Quick question, {{contact.first_name}}"
   - Include 2-3 question survey link (Why did you stop engaging? What would bring you back? What didn't meet expectations?)
   - Offer small incentive for survey completion (entry into drawing, free resource)
   - Use GoHighLevel Forms for survey or integrate Typeform/Google Forms
   - Add tag for survey respondents to trigger different path
   - Add "Wait/Delay" action: 7 days

8. **Build Stage 4: Final Win-Back Attempt**
   - Add "If/Else Condition": Check if any previous engagement occurred
   - For any engagement (Yes branch):
     - Add "Send Internal Notification" to sales team for personal outreach
     - Add "Create Task" for manual follow-up attempt
   - For no engagement (No branch):
     - Add "Send Email" action: "Last chance" or "Should we say goodbye?"
     - Offer strongest discount/incentive
     - Include unsubscribe option: "Not interested? Update preferences here"
     - Be transparent: "This is our last message unless you'd like to hear from us"

9. **Implement Multi-Channel Approach**
   - Add "Send SMS" actions for contacts with phone numbers after Stage 2
   - Consider voicemail drops for high-value inactive leads
   - Use social media retargeting ads for contacts with matched profiles
   - Combine at least 2 channels (email + SMS recommended) for 35-50% better results
   - Vary messaging slightly across channels while maintaining consistent offer

10. **Set Up Response Handling and Goal Tracking**
    - Add "Customer Replied" trigger to create separate workflow
    - Route engaged responses to sales team or appointment booking
    - Add "Goal Event" action to track conversions (email opened, link clicked, purchase made)
    - Configure "Opportunity Created" for re-engaged leads entering sales pipeline
    - Add "Remove Tag" action for successfully reactivated contacts to exit workflow
    - Update contact score based on re-engagement level

11. **Monitor and Optimize Campaign Performance**
    - Track key metrics: reactivation rate (10-12% target), open rate (15-25% target), response rate, conversion rate
    - Calculate revenue generated from reactivated segment
    - Compare reactivation cost vs. new customer acquisition cost
    - Review which stage drives most re-engagement
    - A/B test subject lines, offers, and timing for future campaigns
    - Document learnings for next quarterly reactivation campaign

## Expected Outcomes

- **Database Reactivation**: 10-15% of dormant contacts re-engage with multi-stage campaigns
- **Revenue Without Ad Spend**: Generate $50,000-$100,000+ from existing database (case study: $83,000 from 2,500 contacts)
- **Higher Email Open Rates**: Reactivation emails achieve 12-15% open rates despite cold audience
- **Improved List Quality**: Clean database by removing permanently disengaged contacts
- **Increased Customer Lifetime Value**: Reactivated customers often have 47% higher purchase value
- **Better Segmentation Insights**: Survey feedback reveals why leads went cold and how to prevent future churn
- **Cost Efficiency**: Reactivation campaigns cost 60-70% less than acquiring new customers
- **Pipeline Refill**: Successful campaigns add 15-25 qualified opportunities back into sales pipeline

## Source
[Blog] GoHighLevel - "The Ultimate Guide to Database Reactivation – Boosting Revenue Without Spending a Dime" (2024-05-18) - https://blog.gohighlevel.com/database-reactivation-the-case-of-gerry-the-gym-owner/

## Date Added
2025-10-26
