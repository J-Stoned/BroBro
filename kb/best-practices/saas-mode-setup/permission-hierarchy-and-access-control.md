# Permission Hierarchy and Access Control Strategy

## Category
saas mode setup

## Effectiveness
proven

## Description
Implement a two-tier permission architecture that controls feature access at both the sub-account level (determined by SaaS plan tier) and individual user level (assigned by account admins). This hierarchical permission model ensures clients receive only the features included in their subscription plan while maintaining flexibility for internal role assignments. Proper permission configuration prevents feature leakage to lower-tier clients, enforces product differentiation, and maintains security boundaries between client accounts.

## Implementation Steps

1. **Understand Permission Hierarchy Fundamentals**
   - GoHighLevel SaaS operates on two permission tiers: Sub-Account Level and User Level
   - Sub-Account Level Permissions: Set by SaaS plan configuration, determine maximum available features for entire account
   - User Level Permissions: Set by account admin, assign specific features to individual team members within sub-account
   - Core constraint: "A User cannot have more permissions than the Sub-Account Level permissions allow"
   - Sub-account settings create a permission ceiling that individual users cannot exceed
   - Location permissions are applied based on feature set of purchased plan in SaaS Configurator

2. **Design Plan-Based Feature Matrix**
   - Document feature availability by plan tier in spreadsheet or chart
   - Example Starter Plan ($297/month): Basic CRM, email/SMS, 1 user, 1,000 contacts, no AI features
   - Example Pro Plan ($497/month): Full CRM, email/SMS/voice, 3 users, 10,000 contacts, AI assistant, advanced automation
   - Example Enterprise Plan ($997/month): Unlimited features, unlimited users/contacts, white-label reselling, priority support
   - Map each GHL feature to specific plan tiers to prevent feature creep
   - Consider feature differentiation that creates clear upgrade incentives
   - Balance value perception with upsell opportunities

3. **Configure Sub-Account Level Permissions in SaaS Plans**
   - Navigate to Agency View → SaaS Configurator → Plans & Pricing tab
   - Select plan to configure → Click "Edit Details" button
   - Scroll to "Enable/Disable Products" or "Feature Configuration" section
   - Toggle ON features included in this plan tier:
     - Conversations (SMS, email, voice, Facebook, Instagram, GMB, webchat)
     - Contacts & Smart Lists (set maximum contact limit)
     - Workflows & Automations (limit number of active workflows)
     - Calendars & Appointments (limit number of calendars)
     - Funnels & Websites (limit number of funnels/sites)
     - Opportunities & Pipelines (CRM features)
     - Reporting & Analytics
     - Marketing tools (email builder, template library)
     - AI features (Conversation AI, Content AI, Workflow AI)
     - Membership & Courses
     - Payments & Invoicing
     - Reputation Management
     - Phone System & Call Tracking
   - Set numerical limits where applicable (contacts, workflows, users, phone numbers)
   - Save configuration and repeat for each plan tier

4. **Establish User Role Structures**
   - Define common user roles within client organizations:
     - Account Admin: Full access to all sub-account level permitted features and settings
     - Marketing Manager: Access to campaigns, funnels, email/SMS, reporting
     - Sales Rep: Access to contacts, opportunities, calendar, conversations (assigned data only)
     - Support Agent: Access to conversations, contacts, tickets (assigned data only)
     - Limited User: Minimal access for specific tasks (e.g., appointment setter with calendar-only access)
   - Document role definitions and permission mappings for client handoff materials
   - Create role assignment guide for clients to manage their own team

5. **Configure User Permissions Within Sub-Accounts**
   - As agency admin, navigate to target sub-account
   - Go to Settings → Team Management (or My Staff)
   - Click "+ Add Employee" to create new user or click Edit icon next to existing user
   - Assign Role: Select "Admin" or "User"
     - Admin: Full access to all features enabled at sub-account level, can manage other users
     - User: Restricted access based on granular permission toggles
   - For "User" role, configure granular permissions:
     - Enable/disable access to specific modules (Contacts, Workflows, Calendars, etc.)
     - Set visibility: "All Data" vs. "Only Assigned Data" (restricts to records assigned to this user)
     - Configure notification preferences and default settings
   - Save user configuration
   - Send invitation email with temporary password or login instructions

6. **Implement "Only Assigned Data" Restrictions**
   - For sales teams and support agents, enable "Only Assigned Data" visibility toggle
   - User can only view/edit contacts, opportunities, and conversations explicitly assigned to them
   - Prevents team member access to all client data, maintaining privacy and focus
   - Assign data using workflow automation or manual assignment in contact/opportunity records
   - Test restriction by logging in as limited user to validate data visibility boundaries

7. **Manage Client Permission Adjustments Post-Purchase**
   - If client upgrades from Starter to Pro plan mid-subscription:
     - Navigate to Agency Account → Sub-Accounts tab
     - Find client sub-account → Click "Manage Client" link on right side
     - Scroll to "Enable/Disable Products" section
     - Toggle ON additional features now included in upgraded plan
     - Increase usage limits (contacts, workflows, users) as applicable
     - Save changes - client immediately gains access to new features
   - If client downgrades or fails payment:
     - Reverse process by disabling premium features
     - Consider grace period (7 days) before feature removal to allow payment resolution

8. **Prevent Permission Escalation Vulnerabilities**
   - Regular audit: Review sub-account permissions quarterly to ensure alignment with active plan
   - Validate no features enabled that exceed plan tier (indicates manual override that creates revenue leakage)
   - Document any custom permission adjustments with business justification
   - If granting temporary feature access for testing, set calendar reminder to revoke after trial period
   - Monitor for clients attempting workarounds (e.g., sharing credentials to bypass user limits)

9. **Create Client-Facing Permission Documentation**
   - Build help center article or PDF guide explaining permission structure to clients
   - Include: "What features are included in my plan?", "How do I add team members?", "What permissions should I assign to different roles?"
   - Provide permission matrix showing recommended settings for common job functions
   - Address upgrade path: "Need more features? Upgrade to Pro plan to unlock AI assistant, advanced automation, and increased limits"
   - Reduces support inquiries about feature access and positions upgrades as solutions

10. **Implement Permission Change Workflows**
    - Build automation triggered when client reaches usage limits
    - Example: Client on Pro plan reaches 10,000 contact limit
    - Trigger: Contact count reaches 9,500 (95% threshold)
    - Action 1: Send internal notification to account manager
    - Action 2: Send email to client: "You're growing fast! Upgrade to Enterprise for unlimited contacts"
    - Action 3: Create opportunity in sales pipeline for proactive outreach
    - Same logic for workflow limits, user limits, phone number limits
    - Automated upsell prompts increase upgrade conversion rates by 25-40%

11. **Test Permission Boundaries Thoroughly**
    - Create test client accounts for each plan tier
    - Log in as client and attempt to access features from higher tiers
    - Verify denied access shows appropriate messaging: "This feature is available on Pro plan. Upgrade now."
    - Test user-level restrictions by creating users with varying permissions
    - Log in as restricted user to validate "Only Assigned Data" enforcement
    - Document any permission leaks and submit support tickets if features accessible beyond plan tier

12. **Monitor and Audit Permission Compliance**
    - Generate monthly report of all sub-accounts with manually adjusted permissions
    - Identify accounts with features enabled beyond their plan tier
    - Investigate discrepancies: Valid business reason (custom contract) or error?
    - Correct errors immediately to prevent revenue leakage
    - Calculate revenue impact of any feature giveaways (opportunity cost)
    - Establish approval process for any custom permission arrangements

## Expected Outcomes

- **Enforced Product Differentiation**: Clear feature boundaries between plan tiers create compelling upgrade incentives and protect pricing integrity
- **Revenue Protection**: Permission ceiling prevents lower-tier clients from accessing premium features without upgrading, eliminating $100s-$1000s in monthly revenue leakage per account
- **Scalable Account Management**: Clients self-manage team member permissions within their plan limits, reducing agency support burden by 70%
- **Granular Security Control**: "Only Assigned Data" restrictions enable clients to safely provision access to contractors and junior staff without exposing sensitive data
- **Compliance and Privacy**: Permission boundaries support data privacy requirements (GDPR, CCPA) by limiting user access to necessary information only
- **Upgrade Conversion Catalyst**: Usage limit notifications and feature restriction messaging drive 25-40% of clients to upgrade within first 6 months
- **Professional Multi-User Experience**: Enterprise clients onboard 10+ team members with appropriate role-based access, mirroring enterprise SaaS platforms
- **Reduced Support Tickets**: Clear permission documentation and automated limit notifications reduce "why can't I access X feature?" inquiries by 60%
- **Audit Trail and Accountability**: User-level permissions track who has access to what features for compliance reporting and security audits
- **Competitive Positioning**: Sophisticated permission hierarchy signals enterprise-grade platform capability, justifying premium pricing vs. single-user tools

## Source
[Documentation] GoHighLevel Support Portal - "SaaS User Level Permissions Vs Sub-Account Level Permissions" (2024-01-15) - https://help.gohighlevel.com/support/solutions/articles/48001184431-saas-user-level-permissions-vs-sub-account-level-permissions

## Date Added
2025-10-26
