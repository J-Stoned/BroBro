"""
Template Management - Epic 12: Story 12.6
Pre-built workflow templates for common use cases
"""

from typing import Dict, Any, List, Optional


# Template categories
TEMPLATE_CATEGORIES = [
    "Sales",
    "Marketing",
    "Customer Service",
    "Lead Nurture",
    "Onboarding",
    "Appointment",
    "E-commerce",
    "Real Estate",
    "Healthcare",
    "General"
]


class WorkflowTemplate:
    """Represents a workflow template"""

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        category: str,
        workflow: Dict[str, Any],
        tags: List[str] = None,
        difficulty: str = "beginner",
        author: str = "GHL WHIZ",
        version: str = "1.0"
    ):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.workflow = workflow
        self.tags = tags or []
        self.difficulty = difficulty
        self.author = author
        self.version = version

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "workflow": self.workflow,
            "tags": self.tags,
            "difficulty": self.difficulty,
            "author": self.author,
            "version": self.version
        }


class TemplateManager:
    """Manages workflow templates"""

    def __init__(self):
        self.templates: Dict[str, WorkflowTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default templates"""
        # Template 1: Lead Nurture Sequence
        self.add_template(WorkflowTemplate(
            id="lead-nurture-email",
            name="Lead Nurture Email Sequence",
            description="5-day email sequence to nurture new leads",
            category="Lead Nurture",
            workflow={
                "name": "Lead Nurture Sequence",
                "nodes": [
                    {"id": "1", "type": "trigger", "title": "New Lead", "position": {"x": 100, "y": 100}},
                    {"id": "2", "type": "delay", "title": "Wait 1 Day", "position": {"x": 100, "y": 200}},
                    {"id": "3", "type": "action", "title": "Send Welcome Email", "position": {"x": 100, "y": 300}},
                ],
                "connections": [
                    {"from": "1", "to": "2"},
                    {"from": "2", "to": "3"}
                ]
            },
            tags=["email", "nurture", "sales"],
            difficulty="beginner"
        ))

        # Template 2: Appointment Reminder
        self.add_template(WorkflowTemplate(
            id="appointment-reminder",
            name="Appointment Reminder System",
            description="Automated reminders 24h and 1h before appointments",
            category="Appointment",
            workflow={
                "name": "Appointment Reminders",
                "nodes": [
                    {"id": "1", "type": "trigger", "title": "Appointment Booked", "position": {"x": 100, "y": 100}},
                    {"id": "2", "type": "delay", "title": "Wait Until 24h Before", "position": {"x": 100, "y": 200}},
                    {"id": "3", "type": "action", "title": "Send Reminder SMS", "position": {"x": 100, "y": 300}},
                ],
                "connections": [
                    {"from": "1", "to": "2"},
                    {"from": "2", "to": "3"}
                ]
            },
            tags=["appointment", "reminder", "sms"],
            difficulty="beginner"
        ))

        # Template 3: Abandoned Cart Recovery
        self.add_template(WorkflowTemplate(
            id="abandoned-cart",
            name="Abandoned Cart Recovery",
            description="Recover abandoned carts with timed email sequence",
            category="E-commerce",
            workflow={
                "name": "Cart Recovery",
                "nodes": [
                    {"id": "1", "type": "trigger", "title": "Cart Abandoned", "position": {"x": 100, "y": 100}},
                    {"id": "2", "type": "delay", "title": "Wait 1 Hour", "position": {"x": 100, "y": 200}},
                    {"id": "3", "type": "action", "title": "Send Recovery Email", "position": {"x": 100, "y": 300}},
                ],
                "connections": [
                    {"from": "1", "to": "2"},
                    {"from": "2", "to": "3"}
                ]
            },
            tags=["ecommerce", "cart", "recovery"],
            difficulty="intermediate"
        ))

    def add_template(self, template: WorkflowTemplate) -> bool:
        """Add a template"""
        self.templates[template.id] = template
        return True

    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a template by ID"""
        return self.templates.get(template_id)

    def list_templates(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List templates with optional filtering"""
        templates = list(self.templates.values())

        # Filter by category
        if category:
            templates = [t for t in templates if t.category == category]

        # Filter by difficulty
        if difficulty:
            templates = [t for t in templates if t.difficulty == difficulty]

        # Search in name/description/tags
        if search:
            search_lower = search.lower()
            templates = [
                t for t in templates
                if search_lower in t.name.lower()
                or search_lower in t.description.lower()
                or any(search_lower in tag.lower() for tag in t.tags)
            ]

        return [t.to_dict() for t in templates]

    def get_categories(self) -> List[str]:
        """Get all template categories"""
        return TEMPLATE_CATEGORIES
