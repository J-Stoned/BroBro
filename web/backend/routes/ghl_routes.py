"""
GHL API Routes - Epic 11: Story 11.1
FastAPI endpoints for GoHighLevel integration
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from pydantic import BaseModel
import logging

from ghl_api.client import GHLClient
from ghl_api.rate_limiter import RateLimiter
from ghl_api.validation import validate_workflow_for_deployment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ghl", tags=["GHL API"])

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


# Request/Response Models
class TestConnectionRequest(BaseModel):
    api_key: str
    location_id: str


class DeployWorkflowRequest(BaseModel):
    api_key: str
    location_id: str
    workflow: dict


class UpdateWorkflowRequest(BaseModel):
    api_key: str
    location_id: str
    workflow: dict


class GetWorkflowsRequest(BaseModel):
    api_key: str
    location_id: str
    limit: Optional[int] = 100


class GetWorkflowRequest(BaseModel):
    api_key: str
    location_id: str


class DeleteWorkflowRequest(BaseModel):
    api_key: str
    location_id: str


class GetExecutionsRequest(BaseModel):
    api_key: str
    location_id: str
    limit: Optional[int] = 50


class ValidateWorkflowRequest(BaseModel):
    workflow: dict


@router.post("/test")
async def test_connection(request: TestConnectionRequest):
    """
    Test GHL API connection and validate API key

    Returns:
        {
            "success": bool,
            "location": {...},
            "message": str
        }
    """
    try:
        # Check rate limit
        if not rate_limiter.is_allowed(request.api_key):
            remaining_time = rate_limiter.get_reset_time(request.api_key)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Try again in {int(remaining_time)} seconds",
                    "reset_in": remaining_time
                }
            )

        # Test connection
        client = GHLClient(request.api_key, request.location_id)
        result = await client.test_connection()

        # Add rate limit info
        result["rate_limit"] = {
            "remaining": rate_limiter.get_remaining(request.api_key),
            "reset_in": rate_limiter.get_reset_time(request.api_key)
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/validate")
async def validate_workflow(request: ValidateWorkflowRequest):
    """
    Validate workflow before deployment

    Returns:
        {
            "valid": bool,
            "errors": [...],
            "warnings": [...]
        }
    """
    try:
        result = validate_workflow_for_deployment(request.workflow)
        return result
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/deploy")
async def deploy_workflow(request: DeployWorkflowRequest):
    """
    Deploy workflow to GHL

    Returns:
        {
            "success": bool,
            "workflow_id": str,
            "workflow": {...},
            "message": str
        }
    """
    try:
        # Check rate limit
        if not rate_limiter.is_allowed(request.api_key):
            remaining_time = rate_limiter.get_reset_time(request.api_key)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Try again in {int(remaining_time)} seconds",
                    "reset_in": remaining_time
                }
            )

        # Validate workflow first
        validation = validate_workflow_for_deployment(request.workflow)
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Validation failed",
                "validation": validation
            }

        # Deploy to GHL
        client = GHLClient(request.api_key, request.location_id)
        result = await client.create_workflow(request.workflow)

        # Add rate limit info
        result["rate_limit"] = {
            "remaining": rate_limiter.get_remaining(request.api_key),
            "reset_in": rate_limiter.get_reset_time(request.api_key)
        }

        # Add validation warnings
        if validation.get("warnings"):
            result["warnings"] = validation["warnings"]

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deploy workflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows")
async def get_workflows(request: GetWorkflowsRequest):
    """
    Get all workflows from GHL location

    Returns:
        {
            "success": bool,
            "workflows": [...],
            "count": int
        }
    """
    try:
        # Check rate limit
        if not rate_limiter.is_allowed(request.api_key):
            remaining_time = rate_limiter.get_reset_time(request.api_key)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Try again in {int(remaining_time)} seconds",
                    "reset_in": remaining_time
                }
            )

        client = GHLClient(request.api_key, request.location_id)
        result = await client.get_workflows(limit=request.limit)

        # Add rate limit info
        result["rate_limit"] = {
            "remaining": rate_limiter.get_remaining(request.api_key),
            "reset_in": rate_limiter.get_reset_time(request.api_key)
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workflows error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, request: GetWorkflowRequest):
    """
    Get single workflow from GHL

    Returns:
        {
            "success": bool,
            "workflow": {...}
        }
    """
    try:
        # Check rate limit
        if not rate_limiter.is_allowed(request.api_key):
            remaining_time = rate_limiter.get_reset_time(request.api_key)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Try again in {int(remaining_time)} seconds",
                    "reset_in": remaining_time
                }
            )

        client = GHLClient(request.api_key, request.location_id)
        result = await client.get_workflow(workflow_id)

        # Add rate limit info
        result["rate_limit"] = {
            "remaining": rate_limiter.get_remaining(request.api_key),
            "reset_in": rate_limiter.get_reset_time(request.api_key)
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, request: UpdateWorkflowRequest):
    """
    Update existing workflow in GHL

    Returns:
        {
            "success": bool,
            "workflow": {...},
            "message": str
        }
    """
    try:
        # Check rate limit
        if not rate_limiter.is_allowed(request.api_key):
            remaining_time = rate_limiter.get_reset_time(request.api_key)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Try again in {int(remaining_time)} seconds",
                    "reset_in": remaining_time
                }
            )

        # Validate workflow first
        validation = validate_workflow_for_deployment(request.workflow)
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Validation failed",
                "validation": validation
            }

        client = GHLClient(request.api_key, request.location_id)
        result = await client.update_workflow(workflow_id, request.workflow)

        # Add rate limit info
        result["rate_limit"] = {
            "remaining": rate_limiter.get_remaining(request.api_key),
            "reset_in": rate_limiter.get_reset_time(request.api_key)
        }

        # Add validation warnings
        if validation.get("warnings"):
            result["warnings"] = validation["warnings"]

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update workflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str, request: DeleteWorkflowRequest):
    """
    Delete workflow from GHL

    Returns:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        # Check rate limit
        if not rate_limiter.is_allowed(request.api_key):
            remaining_time = rate_limiter.get_reset_time(request.api_key)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Try again in {int(remaining_time)} seconds",
                    "reset_in": remaining_time
                }
            )

        client = GHLClient(request.api_key, request.location_id)
        result = await client.delete_workflow(workflow_id)

        # Add rate limit info
        result["rate_limit"] = {
            "remaining": rate_limiter.get_remaining(request.api_key),
            "reset_in": rate_limiter.get_reset_time(request.api_key)
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete workflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/executions")
async def get_workflow_executions(workflow_id: str, request: GetExecutionsRequest):
    """
    Get workflow execution history from GHL

    Returns:
        {
            "success": bool,
            "executions": [...],
            "count": int
        }
    """
    try:
        # Check rate limit
        if not rate_limiter.is_allowed(request.api_key):
            remaining_time = rate_limiter.get_reset_time(request.api_key)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Try again in {int(remaining_time)} seconds",
                    "reset_in": remaining_time
                }
            )

        client = GHLClient(request.api_key, request.location_id)
        result = await client.get_workflow_executions(workflow_id, limit=request.limit)

        # Add rate limit info
        result["rate_limit"] = {
            "remaining": rate_limiter.get_remaining(request.api_key),
            "reset_in": rate_limiter.get_reset_time(request.api_key)
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get executions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
