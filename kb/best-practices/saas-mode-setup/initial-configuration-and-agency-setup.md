# Initial Configuration and Agency Setup for SaaS Mode

## Category
saas mode setup

## Effectiveness
proven

## Description
Establish the foundational infrastructure for GoHighLevel SaaS Mode by configuring agency-level settings, payment processing, and technical prerequisites. This critical setup phase transforms your Agency Pro account into a white-labeled software platform capable of automated client provisioning and recurring revenue generation. Proper initial configuration prevents common pitfalls like failed account creation, payment processing errors, and branding inconsistencies.

## Implementation Steps

1. **Verify Agency Pro Plan Subscription**
   - Confirm active Agency Pro Plan subscription ($497/month or $4,970/year)
   - Ensure billing is current and account has full SaaS Mode access
   - Note: SaaS Mode features are unavailable on Freelancer Plan ($297/month)

2. **Connect Stripe Payment Processor**
   - Navigate to Agency Settings → Payments → Connect Stripe
   - Complete Stripe account verification and business information
   - Confirm Stripe account is in live mode, not test mode
   - Important: Stripe is the mandatory payment processor - PayPal and other gateways are not supported

3. **Create Dedicated Agency Sub-Account**
   - Go to Sub-Accounts → Add Sub-Account → Create fresh agency management account
   - Name it clearly (e.g., "SaaS Management Hub" or "Internal Operations")
   - Purpose: Separate internal operations from client accounts
   - This sub-account manages payments and internal workflows, never exposed to clients

4. **Activate LC Phone System**
   - Navigate to Agency Settings → Telephony
   - Enable LeadConnector Phone system for rebilling capabilities
   - Configure area codes and phone number pools for client provisioning
   - Test phone number assignment to ensure proper allocation

5. **Configure White-Label Domain Infrastructure**
   - Purchase or designate custom domain for client login portal (e.g., app.yourbrand.com)
   - Navigate to Agency Settings → White Label Settings → Custom Domain
   - Add CNAME records per GHL instructions for login portal
   - Configure API domain URL for branded system-generated links
   - Set up SSL certificates for secure connections
   - Test domain resolution before proceeding

6. **Set Up Email Infrastructure**
   - Configure Mailgun subdomain for transactional emails
   - Navigate to Agency Settings → Email Services → Mailgun Setup
   - Add DNS records (SPF, DKIM, CNAME) for email authentication
   - Test email delivery to confirm proper sender reputation
   - Customize email templates with your branding

7. **Enable SaaS Configurator**
   - Go to Agency Settings → Enable SaaS Configurator
   - Complete domain, logo, and billing configuration wizard
   - Upload company logo (recommended: 512x512px PNG with transparent background)
   - Select brand colors for platform interface customization
   - Configure company information and support contact details

8. **Link Agency Sub-Account to SaaS Configurator**
   - Navigate to SaaS Configurator → Configure tab
   - Click "Select Sub-Accounts" button
   - Choose your previously created Agency Sub-Account from dropdown
   - Click "Add Sub-Account" to establish connection
   - This enables payment processing through the designated sub-account

9. **Pre-Flight Validation Checklist**
   - Verify Stripe connection shows "Connected" status in live mode
   - Confirm custom domain resolves and loads login page
   - Test email delivery from Mailgun subdomain
   - Ensure LC Phone shows available number inventory
   - Validate agency sub-account appears in SaaS Configurator
   - Document all credentials and API keys in secure password manager

10. **Plan Initial SaaS Product Strategy**
    - Determine target pricing tiers (e.g., $297 Starter, $497 Pro, $997 Enterprise)
    - Define feature differentiation between tiers
    - Calculate rebilling markup percentages for profitability
    - Prepare snapshot templates for each tier
    - Document trial period strategy (7-day, 14-day, or 30-day options)
    - Note: Maximum 20 SaaS plans per agency account limitation

## Expected Outcomes

- **Automated Revenue Infrastructure**: Complete technical foundation for recurring subscription business with automated billing and provisioning
- **White-Label Brand Consistency**: Clients access platform through your branded domain with no GoHighLevel references visible
- **Payment Processing Reliability**: Stripe integration handles subscriptions, rebilling, and automated client charges without manual intervention
- **Scalable Account Provisioning**: System ready to automatically create sub-accounts with proper permissions upon client signup
- **Professional Email Deliverability**: Transactional emails send from your domain with proper authentication, improving inbox placement rates
- **Reduced Setup Errors**: Proper initial configuration prevents common pitfalls including failed account creation (wrong Stripe mode), currency lock-in issues, and payment processing failures
- **Compliance and Security**: SSL-secured custom domains and authenticated email infrastructure meet professional SaaS standards
- **Clear Operational Foundation**: Separated agency management account prevents confusion between internal operations and client accounts

## Source
[Documentation] GoHighLevel Support Portal - "SaaS Mode - Full Setup Guide + FAQ" (2024-01-15) - https://help.gohighlevel.com/support/solutions/articles/48001184920-saas-mode-full-setup-guide-faq

## Date Added
2025-10-26
