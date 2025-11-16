"""
Enhancement 9: Version Control API Routes
REST API for workflow version control operations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from version_control.workflow_versions import version_control

router = APIRouter()

# Request Models
class CreateWorkflowRequest(BaseModel):
    workflow_id: str
    name: str

class CommitRequest(BaseModel):
    workflow_id: str
    workflow_data: Dict
    message: str
    author: str
    branch: str = 'main'

class CreateBranchRequest(BaseModel):
    workflow_id: str
    branch_name: str
    from_branch: str = 'main'
    author: str

class MergeRequest(BaseModel):
    workflow_id: str
    source_branch: str
    target_branch: str
    author: str
    strategy: str = 'auto'  # auto, ours, theirs

class CreateTagRequest(BaseModel):
    workflow_id: str
    tag_name: str
    commit_id: str
    author: str
    description: str = ''

# Endpoints

@router.post("/api/version-control/create-workflow")
async def create_workflow(request: CreateWorkflowRequest):
    """Initialize version control for a new workflow"""
    try:
        result = version_control.create_workflow(
            workflow_id=request.workflow_id,
            name=request.name
        )

        if result['success']:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create workflow'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating workflow: {str(e)}")

@router.post("/api/version-control/commit")
async def create_commit(request: CommitRequest):
    """Create a new commit"""
    try:
        result = version_control.commit(
            workflow_id=request.workflow_id,
            workflow_data=request.workflow_data,
            message=request.message,
            author=request.author,
            branch=request.branch
        )

        if result['success']:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create commit'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating commit: {str(e)}")

@router.get("/api/version-control/history/{workflow_id}")
async def get_history(workflow_id: str, branch: str = 'main', limit: int = 50):
    """Get commit history for a branch"""
    try:
        history = version_control.get_history(
            workflow_id=workflow_id,
            branch=branch,
            limit=limit
        )

        return {
            "success": True,
            "data": {
                "branch": branch,
                "commits": history,
                "total": len(history)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@router.get("/api/version-control/commit/{commit_id}")
async def get_commit(commit_id: str):
    """Get complete commit data"""
    try:
        commit = version_control.get_commit(commit_id)

        if commit:
            return {"success": True, "data": commit}
        else:
            raise HTTPException(status_code=404, detail="Commit not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching commit: {str(e)}")

@router.post("/api/version-control/branch")
async def create_branch(request: CreateBranchRequest):
    """Create a new branch"""
    try:
        result = version_control.create_branch(
            workflow_id=request.workflow_id,
            branch_name=request.branch_name,
            from_branch=request.from_branch,
            author=request.author
        )

        if result['success']:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create branch'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating branch: {str(e)}")

@router.get("/api/version-control/branches/{workflow_id}")
async def list_branches(workflow_id: str):
    """List all branches for a workflow"""
    try:
        branches = version_control.list_branches(workflow_id)

        return {
            "success": True,
            "data": {
                "workflow_id": workflow_id,
                "branches": branches,
                "total": len(branches)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing branches: {str(e)}")

@router.get("/api/version-control/diff/{commit_a}/{commit_b}")
async def get_diff(commit_a: str, commit_b: str):
    """Calculate diff between two commits"""
    try:
        diff = version_control.calculate_diff(commit_a, commit_b)

        if diff['success']:
            return {"success": True, "data": diff}
        else:
            raise HTTPException(status_code=400, detail=diff.get('error', 'Failed to calculate diff'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating diff: {str(e)}")

@router.post("/api/version-control/merge")
async def merge_branches(request: MergeRequest):
    """Merge source branch into target branch"""
    try:
        result = version_control.merge_branches(
            workflow_id=request.workflow_id,
            source_branch=request.source_branch,
            target_branch=request.target_branch,
            author=request.author,
            strategy=request.strategy
        )

        if result['success']:
            return {"success": True, "data": result}
        elif result.get('conflict'):
            # Return conflict information with 409 status
            return {
                "success": False,
                "conflict": True,
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to merge branches'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging branches: {str(e)}")

@router.post("/api/version-control/tag")
async def create_tag(request: CreateTagRequest):
    """Create a tag for a commit"""
    try:
        result = version_control.create_tag(
            workflow_id=request.workflow_id,
            tag_name=request.tag_name,
            commit_id=request.commit_id,
            author=request.author,
            description=request.description
        )

        if result['success']:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create tag'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating tag: {str(e)}")

@router.get("/api/version-control/tags/{workflow_id}")
async def list_tags(workflow_id: str):
    """List all tags for a workflow"""
    try:
        tags = version_control.list_tags(workflow_id)

        return {
            "success": True,
            "data": {
                "workflow_id": workflow_id,
                "tags": tags,
                "total": len(tags)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tags: {str(e)}")

@router.get("/api/version-control/restore/{commit_id}")
async def restore_commit(commit_id: str):
    """Get workflow snapshot from a specific commit (for restoration)"""
    try:
        commit = version_control.get_commit(commit_id)

        if commit:
            return {
                "success": True,
                "data": {
                    "commit_id": commit_id,
                    "workflow": commit['workflow'],
                    "metadata": {
                        "message": commit['message'],
                        "author": commit['author'],
                        "timestamp": commit['timestamp']
                    }
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Commit not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restoring commit: {str(e)}")
