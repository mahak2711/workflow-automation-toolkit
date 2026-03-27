"""Auto-discover YAML workflows and register Celery Beat schedules."""

from pathlib import Path
from celery.schedules import crontab

from core.parser import YAMLWorkflowParser
from workers.celery_app import app


def register_schedules(agents_dir: str = "agents"):
    """Scan agent YAML files and register periodic tasks."""
    workflows = YAMLWorkflowParser.discover_workflows(agents_dir)
    beat_schedule = {}

    for wf in workflows:
        if not wf.schedule:
            continue

        parts = wf.schedule.split()
        if len(parts) != 5:
            continue

        beat_schedule[f"workflow-{wf.name}"] = {
            "task": "workers.run_workflow",
            "schedule": crontab(
                minute=parts[0],
                hour=parts[1],
                day_of_month=parts[2],
                month_of_year=parts[3],
                day_of_week=parts[4],
            ),
            "args": [str(Path(agents_dir) / f"{wf.name}.yaml")],
        }

    app.conf.beat_schedule = beat_schedule
    return beat_schedule
