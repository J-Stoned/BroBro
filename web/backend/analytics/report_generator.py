"""
Report Generation System - Epic 13: Story 13.9
Generate PDF and CSV reports with 5+ templates and scheduling
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import csv
import io


class ReportType(Enum):
    """Available report types"""
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_PERFORMANCE = "detailed_performance"
    BOTTLENECK_ANALYSIS = "bottleneck_analysis"
    ROI_ANALYSIS = "roi_analysis"
    COMPARATIVE_ANALYSIS = "comparative_analysis"


class ReportFormat(Enum):
    """Report output formats"""
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"


class ReportTemplate:
    """Represents a report template"""

    def __init__(
        self,
        template_id: str,
        name: str,
        description: str,
        report_type: ReportType,
        sections: List[str]
    ):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.report_type = report_type
        self.sections = sections

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "templateId": self.template_id,
            "name": self.name,
            "description": self.description,
            "reportType": self.report_type.value,
            "sections": self.sections
        }


class ReportGenerator:
    """Generates analytics reports in various formats"""

    def __init__(self):
        self.templates = self._setup_templates()

    def _setup_templates(self) -> Dict[str, ReportTemplate]:
        """Setup default report templates"""
        return {
            "executive_summary": ReportTemplate(
                template_id="executive_summary",
                name="Executive Summary",
                description="High-level overview of workflow performance",
                report_type=ReportType.EXECUTIVE_SUMMARY,
                sections=["overview", "key_metrics", "trends", "recommendations"]
            ),
            "detailed_performance": ReportTemplate(
                template_id="detailed_performance",
                name="Detailed Performance Report",
                description="Comprehensive workflow performance analysis",
                report_type=ReportType.DETAILED_PERFORMANCE,
                sections=["metrics", "execution_history", "step_analysis", "errors", "trends"]
            ),
            "bottleneck_analysis": ReportTemplate(
                template_id="bottleneck_analysis",
                name="Bottleneck Analysis",
                description="Identify and analyze performance bottlenecks",
                report_type=ReportType.BOTTLENECK_ANALYSIS,
                sections=["bottlenecks", "slow_steps", "recommendations", "optimization_tips"]
            ),
            "roi_analysis": ReportTemplate(
                template_id="roi_analysis",
                name="ROI Analysis",
                description="Calculate return on investment for workflows",
                report_type=ReportType.ROI_ANALYSIS,
                sections=["cost_savings", "time_savings", "roi_metrics", "payback_period"]
            ),
            "comparative_analysis": ReportTemplate(
                template_id="comparative_analysis",
                name="Comparative Analysis",
                description="Compare multiple workflows side-by-side",
                report_type=ReportType.COMPARATIVE_ANALYSIS,
                sections=["comparison_table", "performance_scores", "winners", "recommendations"]
            )
        }

    def get_templates(self) -> List[Dict[str, Any]]:
        """Get all available templates"""
        return [t.to_dict() for t in self.templates.values()]

    def generate_csv_report(
        self,
        workflow_metrics: Dict[str, Any],
        template_id: str = "detailed_performance"
    ) -> str:
        """Generate CSV report"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Invalid template: {template_id}")

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([f"{template.name} - Generated {datetime.now().isoformat()}"])
        writer.writerow([])

        # Write metrics
        if "overview" in template.sections:
            writer.writerow(["Workflow Overview"])
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Workflow ID", workflow_metrics.get("workflowId", "N/A")])
            writer.writerow(["Total Executions", workflow_metrics.get("totalExecutions", 0)])
            writer.writerow(["Successful Executions", workflow_metrics.get("successfulExecutions", 0)])
            writer.writerow(["Failed Executions", workflow_metrics.get("failedExecutions", 0)])
            writer.writerow(["Success Rate (%)", f"{workflow_metrics.get('successRate', 0):.2f}"])
            writer.writerow(["Average Duration (ms)", workflow_metrics.get("averageDurationMs", 0)])
            writer.writerow([])

        # Write execution history
        if "execution_history" in template.sections and workflow_metrics.get("executions"):
            writer.writerow(["Execution History"])
            writer.writerow(["Execution ID", "Status", "Duration (ms)", "Steps", "Started At"])

            for execution in workflow_metrics["executions"][:100]:  # Limit to 100
                writer.writerow([
                    execution.get("executionId", ""),
                    execution.get("status", ""),
                    execution.get("durationMs", ""),
                    f"{execution.get('completedSteps', 0)}/{execution.get('totalSteps', 0)}",
                    execution.get("startedAt", "")
                ])
            writer.writerow([])

        return output.getvalue()

    def generate_json_report(
        self,
        workflow_metrics: Dict[str, Any],
        template_id: str = "detailed_performance",
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate JSON report"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Invalid template: {template_id}")

        report = {
            "reportType": template.report_type.value,
            "templateId": template_id,
            "templateName": template.name,
            "generatedAt": datetime.now().isoformat(),
            "sections": {}
        }

        # Add overview section
        if "overview" in template.sections:
            report["sections"]["overview"] = {
                "workflowId": workflow_metrics.get("workflowId", ""),
                "totalExecutions": workflow_metrics.get("totalExecutions", 0),
                "successfulExecutions": workflow_metrics.get("successfulExecutions", 0),
                "failedExecutions": workflow_metrics.get("failedExecutions", 0),
                "successRate": workflow_metrics.get("successRate", 0),
                "averageDurationMs": workflow_metrics.get("averageDurationMs", 0)
            }

        # Add key metrics section
        if "key_metrics" in template.sections:
            report["sections"]["keyMetrics"] = {
                "successRate": workflow_metrics.get("successRate", 0),
                "avgDuration": workflow_metrics.get("averageDurationMs", 0),
                "minDuration": workflow_metrics.get("minDurationMs", 0),
                "maxDuration": workflow_metrics.get("maxDurationMs", 0),
                "totalDuration": workflow_metrics.get("totalDurationMs", 0)
            }

        # Add execution history
        if "execution_history" in template.sections:
            report["sections"]["executionHistory"] = workflow_metrics.get("executions", [])[:50]

        # Add additional data
        if additional_data:
            for section, data in additional_data.items():
                if section in template.sections:
                    report["sections"][section] = data

        return report

    def generate_text_report(
        self,
        workflow_metrics: Dict[str, Any],
        template_id: str = "executive_summary",
        additional_data: Dict[str, Any] = None
    ) -> str:
        """Generate plain text report (used for PDF generation)"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Invalid template: {template_id}")

        lines = []

        # Header
        lines.append("=" * 80)
        lines.append(template.name.upper())
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")

        # Overview section
        if "overview" in template.sections:
            lines.append("WORKFLOW OVERVIEW")
            lines.append("-" * 80)
            lines.append(f"Workflow ID: {workflow_metrics.get('workflowId', 'N/A')}")
            lines.append(f"Total Executions: {workflow_metrics.get('totalExecutions', 0)}")
            lines.append(f"Successful: {workflow_metrics.get('successfulExecutions', 0)}")
            lines.append(f"Failed: {workflow_metrics.get('failedExecutions', 0)}")
            lines.append(f"Success Rate: {workflow_metrics.get('successRate', 0):.2f}%")
            lines.append("")

        # Key metrics section
        if "key_metrics" in template.sections:
            lines.append("KEY PERFORMANCE METRICS")
            lines.append("-" * 80)
            lines.append(f"Average Duration: {workflow_metrics.get('averageDurationMs', 0)}ms")
            lines.append(f"Min Duration: {workflow_metrics.get('minDurationMs', 0)}ms")
            lines.append(f"Max Duration: {workflow_metrics.get('maxDurationMs', 0)}ms")
            lines.append(f"Total Duration: {workflow_metrics.get('totalDurationMs', 0)}ms")
            lines.append("")

        # Bottlenecks section
        if "bottlenecks" in template.sections and additional_data and "bottlenecks" in additional_data:
            lines.append("PERFORMANCE BOTTLENECKS")
            lines.append("-" * 80)
            bottlenecks = additional_data["bottlenecks"]
            if bottlenecks:
                for idx, bottleneck in enumerate(bottlenecks[:10], 1):
                    lines.append(f"{idx}. {bottleneck.get('stepName', 'Unknown')}")
                    lines.append(f"   Type: {bottleneck.get('stepType', 'Unknown')}")
                    lines.append(f"   Severity: {bottleneck.get('severity', 'Unknown').upper()}")
                    lines.append(f"   Avg Duration: {bottleneck.get('averageDurationMs', 0)}ms")
                    lines.append(f"   P95 Duration: {bottleneck.get('p95DurationMs', 0)}ms")
                    lines.append("")
            else:
                lines.append("No bottlenecks detected - workflow is performing optimally!")
                lines.append("")

        # Recommendations section
        if "recommendations" in template.sections:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 80)

            success_rate = workflow_metrics.get('successRate', 0)
            avg_duration = workflow_metrics.get('averageDurationMs', 0)

            if success_rate < 80:
                lines.append("• Investigate failure causes to improve success rate")
            if avg_duration > 30000:
                lines.append("• Optimize workflow steps to reduce execution time")
            if workflow_metrics.get('failedExecutions', 0) > 10:
                lines.append("• Review error patterns and implement error handling")

            if additional_data and "bottlenecks" in additional_data:
                bottlenecks = additional_data["bottlenecks"]
                if bottlenecks:
                    lines.append(f"• Address {len(bottlenecks)} identified bottlenecks")

            if success_rate >= 95 and avg_duration < 10000:
                lines.append("• Workflow is performing excellently - maintain current standards")

            lines.append("")

        # ROI section
        if "roi_metrics" in template.sections and additional_data and "roi" in additional_data:
            roi = additional_data["roi"]
            lines.append("ROI ANALYSIS")
            lines.append("-" * 80)
            lines.append(f"Monthly Cost Savings: ${roi.get('monthlyCostSavings', 0):.2f}")
            lines.append(f"Annual Cost Savings: ${roi.get('annualCostSavings', 0):.2f}")
            lines.append(f"ROI Percentage: {roi.get('roiPercentage', 0):.2f}%")
            lines.append(f"Payback Period: {roi.get('paybackMonths', 0):.2f} months")
            lines.append("")

        # Footer
        lines.append("=" * 80)
        lines.append("End of Report")
        lines.append("=" * 80)

        return "\n".join(lines)


class ScheduledReport:
    """Represents a scheduled report configuration"""

    def __init__(
        self,
        schedule_id: str,
        workflow_id: str,
        template_id: str,
        format: ReportFormat,
        frequency: str,  # daily, weekly, monthly
        recipients: List[str],
        enabled: bool = True
    ):
        self.schedule_id = schedule_id
        self.workflow_id = workflow_id
        self.template_id = template_id
        self.format = format
        self.frequency = frequency
        self.recipients = recipients
        self.enabled = enabled
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = self._calculate_next_run()

    def _calculate_next_run(self) -> datetime:
        """Calculate next run time based on frequency"""
        now = datetime.now()

        if self.frequency == "daily":
            return now + timedelta(days=1)
        elif self.frequency == "weekly":
            return now + timedelta(weeks=1)
        elif self.frequency == "monthly":
            return now + timedelta(days=30)
        else:
            return now + timedelta(days=1)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "scheduleId": self.schedule_id,
            "workflowId": self.workflow_id,
            "templateId": self.template_id,
            "format": self.format.value,
            "frequency": self.frequency,
            "recipients": self.recipients,
            "enabled": self.enabled,
            "lastRun": self.last_run.isoformat() if self.last_run else None,
            "nextRun": self.next_run.isoformat() if self.next_run else None
        }
