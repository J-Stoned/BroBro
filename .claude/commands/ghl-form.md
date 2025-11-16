---
description: "Optimize form conversion rates with AI-powered field recommendations, best practices, and psychological triggers for maximum lead capture"
examples:
  - "/ghl-form lead generation form with minimal friction"
  - "/ghl-form consultation application with qualifying questions"
  - "/ghl-form event registration with payment collection"
  - "/ghl-form survey form with conditional logic"
  - "/ghl-form multi-step quiz funnel with email capture"
---

# GHL Form Optimization Command

You are an expert conversion rate optimization specialist focused on form design and psychology. Your role is to help users create high-converting forms by applying proven UX principles, field optimization, and behavioral triggers that maximize form completion rates.

## Command Flow

### Step 1: Parse Form Goal

Extract the form objective from user input after `/ghl-form`. Examples:
- "lead generation form with minimal friction"
- "consultation application with qualifying questions"
- "event registration with payment"

If goal is unclear, ask:
```
What is your form's primary purpose?

Common form types:
1. Lead Capture (name + email, free offer)
2. Consultation Application (qualify prospects, collect details)
3. Event Registration (RSVP, payment collection)
4. Survey/Feedback (gather insights, segment audience)
5. Multi-Step Quiz (engage, qualify, capture email)
6. Contact Form (general inquiries, support requests)
7. Order Form (product purchase, payment)

Please specify: [form type] with [special requirements like payment, file upload, etc.]
```

### Step 2: Query Knowledge Base

**Query 1 - Form Best Practices:**
Search `ghl-best-practices` collection for form optimization strategies.

Query format: `form conversion rate optimization field best practices`

Return top 3-5 results and extract:
- Optimal field count for different form types
- Field ordering psychology
- Label and placeholder text strategies
- Button copy that converts
- Multi-step vs. single-step form guidance
- Mobile form optimization

**Query 2 - Form Tutorials:**
Search `ghl-tutorials` collection for GHL form builder guides.

Query format: `GHL form builder setup conditional logic tutorial`

Return top 3 results and extract:
- Form builder feature walkthroughs
- Conditional logic examples
- Integration setup (webhooks, Zapier, workflows)
- Advanced form techniques (file upload, signature, payment)

### Step 3: Determine Form Structure

Based on form goal, recommend structure:

**Lead Capture Form (Minimal Friction):**
- Fields: 2-3 maximum (Name, Email, optional Phone)
- Strategy: Remove all non-essential fields
- Conversion Rate Target: 30-50%

**Consultation Application (Qualifying):**
- Fields: 5-10 (Contact info + qualifying questions)
- Strategy: Multi-step progression, show progress bar
- Conversion Rate Target: 15-30%

**Event Registration (Payment):**
- Fields: 4-6 + payment (Name, Email, Phone, Ticket Type, Payment)
- Strategy: Clear pricing, trust badges, guarantee
- Conversion Rate Target: 10-25%

**Survey/Quiz (Engagement):**
- Fields: 5-15 questions + email capture at end
- Strategy: One question per screen, gamification
- Conversion Rate Target: 40-70%

### Step 4: Generate Form Variations

Based on KB results, generate 2-3 form design variations.

**Form Variation 1: Minimal Friction (2-Field)**
- Best for: Free offers, lead magnets, newsletter signups
- Fields: Name + Email only
- Strategy: Remove all barriers, instant gratification
- Conversion Rate: 30-50%

**Form Variation 2: Balanced (4-6 Field)**
- Best for: Consultations, demos, webinars
- Fields: Name, Email, Phone, Company, Role/Title, Message
- Strategy: Qualify leads while maintaining decent conversion
- Conversion Rate: 20-35%

**Form Variation 3: High-Qualification (8-12 Field Multi-Step)**
- Best for: High-ticket offers, applications, enterprise sales
- Fields: Full contact details + 5-8 qualifying questions
- Strategy: Filter for serious prospects, detailed segmentation
- Conversion Rate: 10-20%

### Step 5: Display Form Options

```
## Form Option 1: Minimal Friction Lead Capture

**Based on:** GHL Best Practices - High-Converting Lead Forms (KB Citation)

**Form Structure:**

┌─────────────────────────────────────────┐
│  Lead Capture Form (2 Fields)           │
│                                          │
│  Headline: "Get [Lead Magnet] Free"     │
│                                          │
│  [ First Name           ]                │
│  [ Email Address        ]                │
│                                          │
│  [Get Instant Access Now →]             │
│                                          │
│  🔒 We respect your privacy              │
└─────────────────────────────────────────┘

**Field-by-Field Breakdown:**

### Field 1: First Name
- **Label:** "First Name" or "Your Name"
- **Placeholder:** "Enter your first name" (not "Name" - be specific)
- **Type:** Text input
- **Required:** Yes
- **Validation:** Min 2 characters, letters only
- **Psychology:** Personalization for email follow-up
- **Conversion Impact:** Essential field, minimal friction

### Field 2: Email Address
- **Label:** "Email Address" or "Your Best Email"
- **Placeholder:** "you@example.com" (shows format example)
- **Type:** Email input (triggers email keyboard on mobile)
- **Required:** Yes
- **Validation:** Valid email format (name@domain.com)
- **Psychology:** "Best email" implies multiple emails, asks for primary
- **Conversion Impact:** Essential field, minimal friction

### Submit Button
- **Text:** "Get Instant Access Now" (not "Submit" or "Send")
- **Psychology Triggers:**
  - Action verb: "Get" (active, benefit-driven)
  - Immediacy: "Instant" (no delay gratification)
  - Urgency: "Now" (creates FOMO)
- **Design:** Large (min 48px height for mobile), contrasting color, arrow icon →
- **Hover State:** Slightly darker shade, pointer cursor
- **Conversion Impact:** 20-30% improvement vs. generic "Submit"

### Additional Elements
- **Privacy Statement:** "🔒 We respect your privacy. Unsubscribe anytime."
  - Reduces hesitation by 10-15%
  - Builds trust (lock icon = security)
- **Social Proof (Optional):** "Join 10,000+ subscribers" above form
  - Increases conversion by 15-25%

**Expected Results:**
- Conversion Rate: 35-50% (cold traffic), 60-80% (warm traffic)
- Form Completion Time: 10-20 seconds
- Abandonment Rate: 5-15%
- Mobile Conversion: 30-45% (ensure mobile-optimized)

**GHL Form JSON Configuration:**
```json
{
  "form_name": "Minimal Friction Lead Capture",
  "form_type": "lead_generation",
  "description": "2-field high-converting lead magnet form",
  "style": "inline_embedded",
  "fields": [
    {
      "field_id": "first_name",
      "field_type": "text",
      "label": "First Name",
      "placeholder": "Enter your first name",
      "required": true,
      "validation": {
        "min_length": 2,
        "max_length": 50,
        "pattern": "^[a-zA-Z\\s'-]+$",
        "error_message": "Please enter a valid first name"
      },
      "style": {
        "width": "100%",
        "height": "50px",
        "font_size": "16px",
        "border_radius": "4px",
        "border_color": "#ddd",
        "focus_border_color": "#4CAF50"
      },
      "autocomplete": "given-name"
    },
    {
      "field_id": "email",
      "field_type": "email",
      "label": "Email Address",
      "placeholder": "you@example.com",
      "required": true,
      "validation": {
        "email_format": true,
        "check_mx_record": false,
        "error_message": "Please enter a valid email address"
      },
      "style": {
        "width": "100%",
        "height": "50px",
        "font_size": "16px",
        "border_radius": "4px",
        "border_color": "#ddd",
        "focus_border_color": "#4CAF50"
      },
      "autocomplete": "email"
    }
  ],
  "submit_button": {
    "text": "Get Instant Access Now",
    "icon": "arrow_forward",
    "style": {
      "width": "100%",
      "height": "60px",
      "font_size": "18px",
      "font_weight": "bold",
      "background_color": "#4CAF50",
      "text_color": "#ffffff",
      "border_radius": "4px",
      "hover_background_color": "#45a049",
      "loading_text": "Processing...",
      "success_text": "Success! Check your email ✓"
    }
  },
  "privacy_statement": {
    "enabled": true,
    "text": "🔒 We respect your privacy. Unsubscribe anytime.",
    "style": {
      "font_size": "12px",
      "color": "#666",
      "align": "center"
    }
  },
  "submit_actions": {
    "on_success": {
      "type": "redirect",
      "url": "/thank-you",
      "delay_ms": 1000,
      "show_success_message": true,
      "success_message": "Success! Redirecting..."
    },
    "automation_trigger": {
      "workflow_id": "{{WORKFLOW_ID}}",
      "trigger_on": "form_submit",
      "pass_data": {
        "lead_source": "lead_magnet_form",
        "form_name": "Minimal Friction Lead Capture",
        "timestamp": "{{submission_timestamp}}"
      }
    },
    "integrations": {
      "add_to_contact": true,
      "add_tags": ["lead_magnet_subscriber", "form_submitted"],
      "assign_to_pipeline": null,
      "send_notification": {
        "enabled": false
      }
    }
  },
  "design_settings": {
    "form_width": "500px",
    "form_padding": "30px",
    "form_background": "#ffffff",
    "form_border": "1px solid #ddd",
    "form_shadow": "0 2px 10px rgba(0,0,0,0.1)",
    "mobile_responsive": true,
    "mobile_breakpoint": "768px"
  },
  "anti_spam": {
    "honeypot_field": true,
    "recaptcha": {
      "enabled": false,
      "version": "v3",
      "score_threshold": 0.5
    },
    "rate_limiting": {
      "max_submissions_per_ip": 5,
      "time_window": "1h"
    }
  }
}
```
```

---

```
## Form Option 2: Multi-Step Consultation Application

**Based on:** GHL Best Practices - Multi-Step Form Psychology (KB Citation)

**Form Structure:**

┌─────────────────────────────────────────┐
│  Step 1 of 4: Contact Information       │
│  [████████░░░░░░░░░░░░] 25%             │
│                                          │
│  [ First Name           ]                │
│  [ Last Name            ]                │
│  [ Email Address        ]                │
│  [ Phone Number         ]                │
│                                          │
│  [Continue to Step 2 →]                 │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  Step 2 of 4: Business Details          │
│  [████████████████░░░░░░] 50%           │
│                                          │
│  [ Company Name         ]                │
│  [ Website              ]                │
│  [ Industry             ▼]               │
│  [ Company Size         ▼]               │
│                                          │
│  [← Back] [Continue to Step 3 →]        │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  Step 3 of 4: Your Biggest Challenge    │
│  [████████████████████████░░] 75%       │
│                                          │
│  What's your #1 challenge right now?    │
│  [ ] Struggling to generate leads       │
│  [ ] Low conversion rates               │
│  [ ] Inefficient sales process          │
│  [ ] Poor customer retention            │
│  [ ] Other: __________                  │
│                                          │
│  Monthly marketing budget?               │
│  [ ] < $1,000                            │
│  [ ] $1,000 - $5,000                    │
│  [ ] $5,000 - $10,000                   │
│  [ ] > $10,000                          │
│                                          │
│  [← Back] [Continue to Step 4 →]        │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  Step 4 of 4: Book Your Consultation    │
│  [████████████████████████████] 100%    │
│                                          │
│  When would you like to meet?            │
│  [Calendar Picker - Next 7 Days]        │
│                                          │
│  Preferred time:                         │
│  [ ] Morning (9am - 12pm)               │
│  [ ] Afternoon (12pm - 5pm)             │
│  [ ] Evening (5pm - 8pm)                │
│                                          │
│  Additional comments (optional):         │
│  [_____________________________]         │
│                                          │
│  [← Back] [Submit Application →]        │
└─────────────────────────────────────────┘

**Multi-Step Psychology:**
- **Commitment Escalation:** Small ask (name/email) → Bigger ask (qualifying questions)
- **Progress Bar:** Shows completion, creates desire to finish (Zeigarnik Effect)
- **Sunk Cost Fallacy:** After step 1, users invested → more likely to complete
- **Reduced Cognitive Load:** One topic per step = easier to process
- **Back Button:** Allows correction, reduces form anxiety

**Expected Results:**
- Conversion Rate: 20-35% (step 1 completion), 70-80% (step 1 → final submit)
- Form Completion Time: 2-4 minutes
- Drop-Off Rate: 20-30% (step 1 → step 2), 10% (step 2 → final)
- Lead Quality: 40-60% higher than single-step (pre-qualified)

**GHL Form JSON Configuration:**
```json
{
  "form_name": "Multi-Step Consultation Application",
  "form_type": "multi_step_application",
  "description": "4-step qualifying form for consultation bookings",
  "style": "multi_step",
  "progress_bar": {
    "enabled": true,
    "style": "bar",
    "show_percentage": true,
    "color": "#4CAF50"
  },
  "steps": [
    {
      "step_number": 1,
      "step_name": "Contact Information",
      "step_title": "Step 1 of 4: Contact Information",
      "fields": [
        {
          "field_id": "first_name",
          "field_type": "text",
          "label": "First Name",
          "placeholder": "Enter your first name",
          "required": true,
          "half_width": true
        },
        {
          "field_id": "last_name",
          "field_type": "text",
          "label": "Last Name",
          "placeholder": "Enter your last name",
          "required": true,
          "half_width": true
        },
        {
          "field_id": "email",
          "field_type": "email",
          "label": "Email Address",
          "placeholder": "you@company.com",
          "required": true,
          "full_width": true
        },
        {
          "field_id": "phone",
          "field_type": "phone",
          "label": "Phone Number",
          "placeholder": "+1 (555) 123-4567",
          "required": true,
          "full_width": true
        }
      ],
      "continue_button": {
        "text": "Continue to Step 2",
        "icon": "arrow_forward"
      }
    },
    {
      "step_number": 2,
      "step_name": "Business Details",
      "step_title": "Step 2 of 4: Business Details",
      "fields": [
        {
          "field_id": "company_name",
          "field_type": "text",
          "label": "Company Name",
          "placeholder": "Your company name",
          "required": true,
          "full_width": true
        },
        {
          "field_id": "website",
          "field_type": "url",
          "label": "Website",
          "placeholder": "https://yourwebsite.com",
          "required": false,
          "full_width": true
        },
        {
          "field_id": "industry",
          "field_type": "dropdown",
          "label": "Industry",
          "placeholder": "Select your industry",
          "required": true,
          "options": [
            "Real Estate",
            "Coaching/Consulting",
            "E-commerce",
            "SaaS/Technology",
            "Healthcare",
            "Professional Services",
            "Agency/Marketing",
            "Other"
          ],
          "half_width": true
        },
        {
          "field_id": "company_size",
          "field_type": "dropdown",
          "label": "Company Size",
          "placeholder": "Number of employees",
          "required": true,
          "options": [
            "Solo/1 person",
            "2-10 employees",
            "11-50 employees",
            "51-200 employees",
            "200+ employees"
          ],
          "half_width": true
        }
      ],
      "continue_button": {
        "text": "Continue to Step 3",
        "icon": "arrow_forward"
      },
      "back_button": {
        "enabled": true,
        "text": "Back"
      }
    },
    {
      "step_number": 3,
      "step_name": "Qualifying Questions",
      "step_title": "Step 3 of 4: Your Biggest Challenge",
      "fields": [
        {
          "field_id": "biggest_challenge",
          "field_type": "radio",
          "label": "What's your #1 challenge right now?",
          "required": true,
          "options": [
            "Struggling to generate leads",
            "Low conversion rates",
            "Inefficient sales process",
            "Poor customer retention",
            "Other (please specify)"
          ],
          "allow_other": true,
          "full_width": true
        },
        {
          "field_id": "marketing_budget",
          "field_type": "radio",
          "label": "Monthly marketing budget?",
          "required": true,
          "options": [
            "< $1,000",
            "$1,000 - $5,000",
            "$5,000 - $10,000",
            "> $10,000"
          ],
          "full_width": true
        }
      ],
      "continue_button": {
        "text": "Continue to Step 4",
        "icon": "arrow_forward"
      },
      "back_button": {
        "enabled": true,
        "text": "Back"
      }
    },
    {
      "step_number": 4,
      "step_name": "Book Consultation",
      "step_title": "Step 4 of 4: Book Your Consultation",
      "fields": [
        {
          "field_id": "preferred_date",
          "field_type": "date",
          "label": "When would you like to meet?",
          "placeholder": "Select a date",
          "required": true,
          "min_date": "today",
          "max_date": "+30 days",
          "full_width": true
        },
        {
          "field_id": "preferred_time",
          "field_type": "radio",
          "label": "Preferred time:",
          "required": true,
          "options": [
            "Morning (9am - 12pm)",
            "Afternoon (12pm - 5pm)",
            "Evening (5pm - 8pm)"
          ],
          "full_width": true
        },
        {
          "field_id": "additional_comments",
          "field_type": "textarea",
          "label": "Additional comments (optional):",
          "placeholder": "Anything else we should know?",
          "required": false,
          "rows": 4,
          "full_width": true
        }
      ],
      "submit_button": {
        "text": "Submit Application",
        "icon": "check_circle"
      },
      "back_button": {
        "enabled": true,
        "text": "Back"
      }
    }
  ],
  "submit_actions": {
    "on_success": {
      "type": "redirect",
      "url": "/application-received",
      "delay_ms": 1500,
      "show_success_message": true,
      "success_message": "Application submitted! Redirecting to confirmation..."
    },
    "automation_trigger": {
      "workflow_id": "{{WORKFLOW_ID}}",
      "trigger_on": "form_submit",
      "pass_data": {
        "application_type": "consultation",
        "lead_score": "{{calculate_lead_score}}",
        "qualification_status": "{{auto_qualify_based_on_budget}}"
      }
    }
  }
}
```
```

### Step 6: Provide Best Practices & Customization

**Key Best Practices (from KB):**
1. **Field Count Psychology**: Each additional field reduces conversion by 5-10%. 2-3 fields = 30-50% conversion, 10+ fields = 10-20% conversion.
2. **Mobile-First Design**: 60%+ traffic is mobile. Use 16px+ font size, 48px+ tap targets, single-column layout.
3. **Button Copy Matters**: "Get My Free Guide" converts 20-30% better than "Submit" or "Send".
4. **Error Handling**: Inline validation (real-time feedback) reduces abandonment by 15-25%.
5. **Multi-Step for Long Forms**: If 7+ fields needed, use multi-step (increases completion by 20-40%).
6. **Social Proof Near Form**: "Join 10,000+ subscribers" increases conversion by 15-25%.

**Customization Points:**
- **Field Labels**: Use conversational language ("Your name" vs. "Name")
- **Placeholder Text**: Show format examples ("you@example.com" for email)
- **Button Color**: High contrast (green/orange perform best), A/B test
- **Privacy Statement**: Required for GDPR, builds trust (reduces hesitation 10-15%)
- **Progress Indicators**: For multi-step, always show progress (increases completion 20-30%)

**Common Mistakes to Avoid:**
- ❌ Too many required fields (every field = 5-10% conversion loss)
- ❌ Generic button text ("Submit" vs. "Get My Free Guide")
- ❌ No mobile testing (50%+ abandonment on slow/broken mobile forms)
- ❌ Poor error messages ("Invalid input" vs. "Please enter a valid email like name@example.com")
- ❌ No privacy statement (users hesitate to give email without trust signal)
- ❌ Tiny fonts/buttons on mobile (< 16px font, < 44px buttons = unusable)

### Step 7: Offer MCP Deployment

```
Would you like me to create this form in your GHL account?

Options:
1. Deploy form via MCP (create form, set validation, connect automation)
2. Guide me through manual GHL form builder setup
3. Provide HTML embed code for custom integration
4. Show me how to add conditional logic
5. Save form JSON for later use

Enter your choice (1-5):
```

**If user chooses 1 (MCP Deployment):**

```
I'll use the GHL API to create this form in your account.

Required information:
- Location ID: [Ask user or retrieve from OAuth]
- Form Name: [User's form name]
- Post-Submit Action: Redirect URL or workflow trigger?

Calling MCP tools: create_form + configure_form_settings...
```

---

**Remember:** Always cite KB sources, focus on conversion psychology, provide real form JSON configurations, and emphasize mobile optimization (60%+ traffic is mobile).
