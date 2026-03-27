"""Celery tasks for executing agent workflows."""

import asyncio
import logging

from workers.celery_app import app
from core.parser import YAMLWorkflowParser
from integrations.registry import get_adapter

logger = logging.getLogger(__name__)


@app.task(bind=True, name="workers.run_workflow")
def run_workflow(self, workflow_path: str, trigger_data: dict | None = None):
    """Execute a YAML-defined workflow end to end."""
    try:
        workflow = YAMLWorkflowParser.parse_file(workflow_path)

        from core.llm import get_llm
        from core.executor import ChainExecutor

        llm = get_llm()
        executor = ChainExecutor(llm)

        # Fetch source data
        source_adapter = get_adapter(workflow.source.adapter)
        source_data = source_adapter.fetch(workflow.source.config)

        # Run the chain
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(executor.execute(workflow, source_data))
        finally:
            loop.close()

        # Push to sink
        sink_config = workflow.sink
        adapter_name = sink_config.adapter if hasattr(sink_config, "adapter") else sink_config["adapter"]
        sink_adapter = get_adapter(adapter_name)
        config = sink_config.config if hasattr(sink_config, "config") else sink_config
        sink_adapter.push(result, config)

        logger.info(f"Workflow '{workflow.name}' completed successfully")
        return {"status": "success", "workflow": workflow.name}

    except Exception as exc:
        logger.error(f"Workflow failed: {exc}")
        raise self.retry(exc=exc)


@app.task(name="workers.healthcheck")
def healthcheck():
    return {"status": "ok"}
