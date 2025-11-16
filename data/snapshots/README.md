# GHL Snapshots Documentation

This directory contains structured documentation for GoHighLevel snapshots used in the BroBro knowledge base.

## Snapshot Documentation Format

Each snapshot should be documented in a JSON file with the following structure:

```json
{
  "snapshot_name": "Name of the snapshot",
  "snapshot_id": "unique-identifier",
  "industry": "target industry (e.g., pressure washing, dental, real estate)",
  "use_case": "Brief description of what this snapshot is for",
  "target_audience": "Who should use this snapshot",
  "pricing_model": "Free / One-time / Monthly / Yearly",
  "version": "1.0.0",
  "last_updated": "2025-11-01",
  "author": "Creator name",

  "description": {
    "overview": "Detailed overview of what this snapshot provides",
    "key_benefits": [
      "Benefit 1",
      "Benefit 2"
    ],
    "ideal_for": [
      "Use case 1",
      "Use case 2"
    ]
  },

  "components": {
    "funnels": [
      {
        "name": "Funnel name",
        "pages": ["Page 1", "Page 2"],
        "purpose": "What this funnel does",
        "conversion_goal": "What action you want users to take"
      }
    ],
    "workflows": [
      {
        "name": "Workflow name",
        "trigger": "What starts this workflow",
        "steps": ["Step 1", "Step 2"],
        "purpose": "What this workflow accomplishes"
      }
    ],
    "calendars": [
      {
        "name": "Calendar name",
        "type": "Round Robin / Class / Service",
        "purpose": "What appointments this handles"
      }
    ],
    "forms": [
      {
        "name": "Form name",
        "fields": ["Field 1", "Field 2"],
        "purpose": "What data this collects"
      }
    ],
    "email_templates": [
      {
        "name": "Template name",
        "purpose": "When to use this template",
        "subject_line": "Subject line example"
      }
    ],
    "sms_templates": [
      {
        "name": "Template name",
        "purpose": "When to use this template"
      }
    ],
    "campaigns": [
      {
        "name": "Campaign name",
        "type": "Email / SMS / Mixed",
        "purpose": "What this campaign achieves"
      }
    ],
    "pipelines": [
      {
        "name": "Pipeline name",
        "stages": ["Stage 1", "Stage 2"],
        "purpose": "What process this tracks"
      }
    ],
    "custom_fields": [
      {
        "name": "Field name",
        "type": "Text / Number / Date",
        "purpose": "What data this captures"
      }
    ],
    "trigger_links": [
      {
        "name": "Trigger name",
        "action": "What happens when clicked"
      }
    ]
  },

  "setup_instructions": {
    "prerequisites": [
      "What you need before importing"
    ],
    "import_steps": [
      "Step 1: Import the snapshot",
      "Step 2: Configure custom values",
      "Step 3: Activate teams"
    ],
    "post_import_configuration": [
      "Task 1: Connect integrations",
      "Task 2: Customize branding",
      "Task 3: Test workflows"
    ],
    "important_notes": [
      "Note 1",
      "Note 2"
    ]
  },

  "customization_guide": {
    "quick_customizations": [
      "Easy change 1",
      "Easy change 2"
    ],
    "advanced_customizations": [
      "Advanced change 1",
      "Advanced change 2"
    ],
    "branding_checklist": [
      "Logo placement",
      "Color scheme",
      "Email signatures"
    ]
  },

  "best_practices": [
    "Best practice 1",
    "Best practice 2"
  ],

  "common_use_cases": [
    {
      "scenario": "Scenario description",
      "recommended_workflow": "Which workflow to use",
      "tips": ["Tip 1", "Tip 2"]
    }
  ],

  "integrations_required": [
    {
      "integration": "Stripe / Twilio / etc",
      "required": true,
      "purpose": "Why you need this"
    }
  ],

  "tags": [
    "tag1",
    "tag2",
    "tag3"
  ],

  "related_snapshots": [
    "related-snapshot-id-1",
    "related-snapshot-id-2"
  ]
}
```

## Directory Structure

- `templates/` - Template snapshots for different industries
- `josh-wash/` - Snapshots specific to Josh Wash pressure washing business
- `marketplace/` - Documentation for marketplace snapshots
- `custom/` - Custom-built snapshots

## How to Add a New Snapshot

1. Create a new JSON file following the format above
2. Save it in the appropriate subdirectory
3. Run the embedding script: `python scripts/embed-snapshots.py`

## Snapshot Categories

- **Lead Generation** - Focused on capturing leads
- **Appointment Booking** - Scheduling and booking
- **E-commerce** - Product sales and fulfillment
- **Course/Membership** - Educational content delivery
- **Service Business** - Service-based business workflows
- **Agency** - Agency client management
