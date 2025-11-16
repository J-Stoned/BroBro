"""
Analytics API Routes - Epic 13
FastAPI endpoints for workflow analytics and performance monitoring
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from analytics.metrics_collector import MetricsCollector, ExecutionStatus
from analytics.performance_analyzer import PerformanceAnalyzer
from analytics.alert_manager import AlertManager, AlertType, AlertSeverity
from analytics.report_generator import ReportGenerator, ReportFormat

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Initialize managers
metrics_collector = MetricsCollector(retention_days=90)
performance_analyzer = PerformanceAnalyzer()
alert_manager = AlertManager()
report_generator = ReportGenerator()


# Pydantic models
class StartExecutionRequest(BaseModel):
    executionId: str
    workflowId: str
    workflowName: str
    triggerType: str = "manual"
    triggerData: Optional[Dict[str, Any]] = None


class StartStepRequest(BaseModel):
    executionId: str
    stepId: str
    stepName: str
    stepType: str
    inputData: Optional[Dict[str, Any]] = None


class CompleteStepRequest(BaseModel):
    executionId: str
    stepId: str
    status: str = "completed"
    outputData: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CompleteExecutionRequest(BaseModel):
    executionId: str
    status: str = "completed"
    error: Optional[str] = None


class MetricsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]


# Execution tracking endpoints
@router.post("/executions/start", response_model=MetricsResponse)
async def start_execution(request: StartExecutionRequest):
    """Start tracking a workflow execution"""
    try:
        execution = metrics_collector.start_execution(
            execution_id=request.executionId,
            workflow_id=request.workflowId,
            workflow_name=request.workflowName,
            trigger_type=request.triggerType,
            trigger_data=request.triggerData
        )

        return MetricsResponse(
            success=True,
            data=execution.to_dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executions/step/start", response_model=MetricsResponse)
async def start_step(request: StartStepRequest):
    """Start tracking a step execution"""
    try:
        step = metrics_collector.start_step(
            execution_id=request.executionId,
            step_id=request.stepId,
            step_name=request.stepName,
            step_type=request.stepType,
            input_data=request.inputData
        )

        if not step:
            raise HTTPException(status_code=404, detail="Execution not found")

        return MetricsResponse(
            success=True,
            data=step.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executions/step/complete", response_model=MetricsResponse)
async def complete_step(request: CompleteStepRequest):
    """Mark a step as completed"""
    try:
        status = ExecutionStatus(request.status)
        success = metrics_collector.complete_step(
            execution_id=request.executionId,
            step_id=request.stepId,
            status=status,
            output_data=request.outputData,
            error=request.error
        )

        if not success:
            raise HTTPException(status_code=404, detail="Execution or step not found")

        return MetricsResponse(
            success=True,
            data={"message": "Step completed"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executions/complete", response_model=MetricsResponse)
async def complete_execution(request: CompleteExecutionRequest):
    """Mark an execution as completed"""
    try:
        status = ExecutionStatus(request.status)
        success = metrics_collector.complete_execution(
            execution_id=request.executionId,
            status=status,
            error=request.error
        )

        if not success:
            raise HTTPException(status_code=404, detail="Execution not found")

        # Check for alerts
        execution = metrics_collector.get_execution(request.executionId)
        if execution:
            workflow_metrics = metrics_collector.get_workflow_metrics(execution.workflow_id)
            new_alerts = alert_manager.check_metrics(workflow_metrics)

        return MetricsResponse(
            success=True,
            data={"message": "Execution completed"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}", response_model=MetricsResponse)
async def get_execution(execution_id: str):
    """Get execution details"""
    try:
        execution = metrics_collector.get_execution(execution_id)

        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        return MetricsResponse(
            success=True,
            data=execution.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Metrics endpoints
@router.get("/metrics/global", response_model=MetricsResponse)
async def get_global_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get global metrics across all workflows"""
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        metrics = metrics_collector.get_global_metrics(
            start_date=start,
            end_date=end
        )

        return MetricsResponse(
            success=True,
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/workflow/{workflow_id}", response_model=MetricsResponse)
async def get_workflow_metrics(
    workflow_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get metrics for a specific workflow"""
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        metrics = metrics_collector.get_workflow_metrics(
            workflow_id=workflow_id,
            start_date=start,
            end_date=end
        )

        return MetricsResponse(
            success=True,
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/steps", response_model=MetricsResponse)
async def get_step_metrics(
    workflow_id: Optional[str] = None,
    step_type: Optional[str] = None
):
    """Get metrics for workflow steps"""
    try:
        metrics = metrics_collector.get_step_metrics(
            workflow_id=workflow_id,
            step_type=step_type
        )

        return MetricsResponse(
            success=True,
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Performance analysis endpoints
@router.get("/performance/bottlenecks/{workflow_id}", response_model=MetricsResponse)
async def detect_bottlenecks(workflow_id: str):
    """Detect performance bottlenecks in a workflow"""
    try:
        metrics = metrics_collector.get_workflow_metrics(workflow_id)
        executions = metrics.get("executions", [])

        analysis = performance_analyzer.bottleneck_detector.analyze_workflow(executions)

        return MetricsResponse(
            success=True,
            data=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/trends/{workflow_id}", response_model=MetricsResponse)
async def analyze_trends(
    workflow_id: str,
    interval: str = Query("daily", pattern="^(hourly|daily|weekly)$")
):
    """Analyze performance trends for a workflow"""
    try:
        metrics = metrics_collector.get_workflow_metrics(workflow_id)
        executions = metrics.get("executions", [])

        trends = performance_analyzer.analyze_trends(executions, interval=interval)

        return MetricsResponse(
            success=True,
            data=trends
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/errors/{workflow_id}", response_model=MetricsResponse)
async def detect_error_patterns(workflow_id: str):
    """Detect error patterns in a workflow"""
    try:
        metrics = metrics_collector.get_workflow_metrics(workflow_id)
        executions = metrics.get("executions", [])

        patterns = performance_analyzer.detect_error_patterns(executions)

        return MetricsResponse(
            success=True,
            data=patterns
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/slow-steps/{workflow_id}", response_model=MetricsResponse)
async def get_slow_steps(
    workflow_id: str,
    top_n: int = Query(10, ge=1, le=50)
):
    """Get slowest workflow steps"""
    try:
        metrics = metrics_collector.get_workflow_metrics(workflow_id)
        executions = metrics.get("executions", [])

        slow_steps = performance_analyzer.identify_slow_steps(executions, top_n=top_n)

        return MetricsResponse(
            success=True,
            data={"slowSteps": slow_steps}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Alert endpoints
@router.get("/alerts", response_model=MetricsResponse)
async def get_alerts(
    workflow_id: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    severity: Optional[str] = None
):
    """Get alerts with optional filtering"""
    try:
        severity_enum = AlertSeverity(severity) if severity else None
        alerts = alert_manager.get_alerts(
            workflow_id=workflow_id,
            acknowledged=acknowledged,
            severity=severity_enum
        )

        return MetricsResponse(
            success=True,
            data={
                "alerts": [a.to_dict() for a in alerts],
                "total": len(alerts)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge", response_model=MetricsResponse)
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    try:
        success = alert_manager.acknowledge_alert(alert_id)

        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")

        return MetricsResponse(
            success=True,
            data={"message": "Alert acknowledged"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/rules", response_model=MetricsResponse)
async def get_alert_rules():
    """Get all alert rules"""
    try:
        rules = [
            {
                "ruleId": rule.rule_id,
                "alertType": rule.alert_type.value,
                "severity": rule.severity.value,
                "enabled": rule.enabled
            }
            for rule in alert_manager.rules.values()
        ]

        return MetricsResponse(
            success=True,
            data={"rules": rules}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/rules/{rule_id}/enable", response_model=MetricsResponse)
async def enable_alert_rule(rule_id: str):
    """Enable an alert rule"""
    try:
        success = alert_manager.enable_rule(rule_id)

        if not success:
            raise HTTPException(status_code=404, detail="Rule not found")

        return MetricsResponse(
            success=True,
            data={"message": "Rule enabled"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/rules/{rule_id}/disable", response_model=MetricsResponse)
async def disable_alert_rule(rule_id: str):
    """Disable an alert rule"""
    try:
        success = alert_manager.disable_rule(rule_id)

        if not success:
            raise HTTPException(status_code=404, detail="Rule not found")

        return MetricsResponse(
            success=True,
            data={"message": "Rule disabled"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Report endpoints
@router.get("/reports/templates", response_model=MetricsResponse)
async def get_report_templates():
    """Get all available report templates"""
    try:
        templates = report_generator.get_templates()

        return MetricsResponse(
            success=True,
            data={"templates": templates}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GenerateReportRequest(BaseModel):
    workflowId: str
    templateId: str
    format: str = "json"
    includeBottlenecks: bool = False
    includeROI: bool = False


@router.post("/reports/generate", response_model=MetricsResponse)
async def generate_report(request: GenerateReportRequest):
    """Generate a report for a workflow"""
    try:
        # Fetch workflow metrics
        workflow_metrics = metrics_collector.get_workflow_metrics(request.workflowId)

        # Prepare additional data
        additional_data = {}

        if request.includeBottlenecks:
            bottleneck_analysis = performance_analyzer.bottleneck_detector.analyze_workflow(
                workflow_metrics.get("executions", [])
            )
            additional_data["bottlenecks"] = bottleneck_analysis.get("bottlenecks", [])
            additional_data["recommendations"] = bottleneck_analysis.get("recommendations", [])

        # Generate report based on format
        if request.format == "csv":
            report_content = report_generator.generate_csv_report(
                workflow_metrics,
                request.templateId
            )
            return MetricsResponse(
                success=True,
                data={
                    "format": "csv",
                    "content": report_content
                }
            )
        elif request.format == "text":
            report_content = report_generator.generate_text_report(
                workflow_metrics,
                request.templateId,
                additional_data
            )
            return MetricsResponse(
                success=True,
                data={
                    "format": "text",
                    "content": report_content
                }
            )
        else:  # JSON
            report_content = report_generator.generate_json_report(
                workflow_metrics,
                request.templateId,
                additional_data
            )
            return MetricsResponse(
                success=True,
                data=report_content
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
