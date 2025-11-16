# Rebilling and Markup Configuration for Profitability

## Category
saas mode setup

## Effectiveness
proven

## Description
Configure automated phone and usage rebilling with strategic markup percentages to generate profit from client communication costs. Phone rebilling automates the process of charging clients for their LC Phone usage while allowing agencies to retain markup differences as additional revenue streams beyond base subscription fees. Proper rebilling configuration ensures predictable profit margins and eliminates manual billing reconciliation.

## Implementation Steps

1. **Verify Plan Eligibility and Capabilities**
   - Confirm Agency Pro Plan subscription ($497/month) for custom markup capabilities
   - Note: Freelancer Plan ($297/month) limited to fixed 1.05x (5%) markup with no customization
   - Freelancer Plan only supports LeadConnector Phone rebilling, not Twilio
   - Pro Plan enables custom markups on both LC Phone and Twilio usage

2. **Establish Markup Strategy**
   - Calculate target profit margins based on business model
   - Common markup ranges: 1.15x to 1.50x (15% to 50% markup)
   - Default platform markup: 1.05x (5%) to cover Stripe transaction fees
   - Consider tiered markups: Higher tiers = lower markup percentage (volume pricing psychology)
   - Example: Starter plan 1.40x markup, Pro plan 1.25x markup, Enterprise plan 1.15x markup
   - Document markup rationale for future pricing audits

3. **Configure Plan-Level Rebilling Settings**
   - Navigate to SaaS Configurator → Plans & Pricing tab
   - Click "Edit Details" on each plan
   - Scroll to "SaaS Options" section
   - Locate "Twilio Rebilling Profit" or "LC Phone Rebilling" settings
   - Enter markup multiplier (e.g., 1.25 for 25% markup)
   - Apply consistent or differentiated markups across plans
   - Save each plan configuration

4. **Enable Sub-Account Level Rebilling**
   - Navigate to Agency Account → Sub-Accounts tab
   - Locate target client sub-account
   - Click "Manage Client" link on right side
   - Scroll to "Phone Rebilling" section
   - Toggle "Enable Phone Rebilling" to ON
   - Select payment method option: "Generate new payment link" or "Use existing Stripe customer"
   - Confirm sub-account has at least one account admin to manage payment methods
   - Save configuration

5. **Client Payment Method Setup**
   - Direct client to their Sub-Account Settings → Company Billing
   - Client clicks "Add Payment Method" button
   - Client enters credit card information (not agency's card)
   - System validates payment method through Stripe
   - Rebilling activates only after valid card is added
   - Note: Sub-accounts without payment methods have saved markup configurations but inactive rebilling

6. **Configure Recharge Thresholds**
   - Client navigates to Settings → Company Billing in their sub-account
   - Set "Auto Recharge Threshold" (e.g., when balance drops below $10)
   - Set "Auto Recharge Amount" (e.g., add $50 when threshold is reached)
   - Enable "Auto Recharge" toggle
   - This prevents service disruption from depleted credit balances

7. **Set Up Bulk Rebilling for Existing Accounts**
   - Navigate to SaaS Configurator → Bulk Rebilling Markup Configuration (if available)
   - Select multiple sub-accounts using checkboxes
   - Apply standardized markup percentages to all selected accounts simultaneously
   - Confirm changes to ensure consistency across client base
   - Particularly useful when migrating existing clients to rebilling model

8. **Monitor Usage and Billing Flow**
   - Agency receives monthly invoice from GoHighLevel for LC Phone usage costs
   - Agency's Stripe account automatically charges clients for phone usage at marked-up rate
   - Agency retains markup difference as profit
   - Both agency and client can monitor consumption through respective Company Billing pages
   - Review detailed credit usage reports to validate billing accuracy

9. **Establish Rebilling Policies**
   - Document minimum balance policies in client agreements
   - Set expectations for overage charges beyond included credits
   - Create automated notifications when credits drop below thresholds
   - Develop workflow for payment failure scenarios (suspend service, send notifications, etc.)
   - Communicate rebilling terms clearly in onboarding documentation

10. **Periodic Audit and Optimization**
    - Review markup configurations quarterly to ensure alignment with business goals
    - Analyze profit margins by client tier and usage patterns
    - Identify high-usage clients for potential upsells to higher tiers with better value
    - Adjust markups based on competitive analysis and cost structure changes
    - Monitor Stripe transaction fees and adjust base markup if needed
    - Document all markup changes with effective dates for financial tracking

## Expected Outcomes

- **Automated Profit Generation**: Earn 15-50% markup on all client phone and communication usage without manual billing intervention
- **Predictable Revenue Streams**: Rebilling creates additional recurring revenue beyond base subscription fees, improving lifetime value per client
- **Zero Manual Reconciliation**: Stripe automatically processes client charges and agency receives net profit without invoice matching or billing disputes
- **Scalable Billing Operations**: Handle hundreds of clients with individualized usage patterns without additional billing staff
- **Transparent Cost Tracking**: Both agency and clients monitor usage in real-time through Company Billing dashboards, reducing billing inquiries
- **Reduced Payment Failures**: Automated recharge thresholds prevent service disruptions and maintain continuous revenue flow
- **Strategic Pricing Flexibility**: Differentiated markups by tier enable value-based pricing strategies and competitive positioning
- **Compliance with Stripe Fees**: Minimum 5% markup ensures agency never loses money on Stripe transaction costs (typically 2.9% + $0.30)

## Source
[Documentation] GoHighLevel Support Portal - "Activate SaaS Mode, Request Payment, and Configure Phone Rebilling" (2024-01-15) - https://help.gohighlevel.com/support/solutions/articles/48001177740-activate-saas-mode-request-payment-and-configure-phone-rebilling

## Date Added
2025-10-26
