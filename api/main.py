"""FastAPI gateway — REST endpoints for workflow management."""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.parser import YAMLWorkflowParser
from workers.tasks import run_workflow

app = FastAPI(
    title="Workflow Automation Toolkit",
    version="0.1.0",
    description="LLM-powered workflow automation API",
)

AGENTS_DIR = Path(os.getenv("AGENTS_DIR", "agents"))


class WorkflowTriggerRequest(BaseModel):
    data: dict | None = None


class WorkflowTriggerResponse(BaseModel):
    task_id: str
    workflow: str
    status: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/workflows")
async def list_workflows():
    """List all available workflows."""
    workflows = YAMLWorkflowParser.discover_workflows(AGENTS_DIR)
    return [
        {
            "name": wf.name,
            "description": wf.description,
            "schedule": wf.schedule,
            "steps": len(wf.chain),
        }
        for wf in workflows
    ]


@app.post("/api/v1/workflows/{name}/run", response_model=WorkflowTriggerResponse)
async def trigger_workflow(name: str, request: WorkflowTriggerRequest | None = None):
    """Trigger a workflow by name."""
    workflow_path = AGENTS_DIR / f"{name}.yaml"
    if not workflow_path.exists():
        workflow_path = AGENTS_DIR / "examples" / f"{name}.yaml"
        if not workflow_path.exists():
            raise HTTPException(status_code=404, detail=f"Workflow '{name}' not found")

    task = run_workflow.delay(
        str(workflow_path),
        request.data if request else None,
    )
    return WorkflowTriggerResponse(
        task_id=task.id,
        workflow=name,
        status="queued",
    )


@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Check the status of a running task."""
    from workers.celery_app import app as celery_app

    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
