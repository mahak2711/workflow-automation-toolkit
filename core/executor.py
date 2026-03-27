"""Chain executor — runs YAML-defined prompt chains via LangChain."""

import logging
from typing import Any

from jinja2 import Template
from langchain_core.messages import HumanMessage
from langchain_core.language_models import BaseChatModel

from core.parser import WorkflowDefinition, StepConfig

logger = logging.getLogger(__name__)


class ChainExecutor:
    """Execute a workflow's prompt chain step by step."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def execute(
        self,
        workflow: WorkflowDefinition,
        source_data: dict[str, Any],
    ) -> dict[str, Any]:
        context: dict[str, Any] = {"source": source_data}

        for step in workflow.chain:
            if step.condition and not self._evaluate_condition(step.condition, context):
                logger.info(f"Skipping step '{step.step}' — condition not met")
                continue

            logger.info(f"Executing step: {step.step} (type={step.type})")

            if step.type == "map":
                result = await self._execute_map(step, context)
            elif step.type == "reduce":
                result = await self._execute_reduce(step, context)
            else:
                result = await self._execute_single(step, context)

            context[step.output] = result
            logger.info(f"Step '{step.step}' complete -> {step.output}")

        return context

    async def _execute_single(self, step: StepConfig, context: dict) -> str:
        prompt = self._render_template(step.prompt, context)
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content

    async def _execute_map(self, step: StepConfig, context: dict) -> list[str]:
        items = self._resolve_input(step.input, context)
        results = []
        for item in items:
            item_context = (
                {**context, **item} if isinstance(item, dict) else {**context, "item": item}
            )
            prompt = self._render_template(step.prompt, item_context)
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            results.append(response.content)
        return results

    async def _execute_reduce(self, step: StepConfig, context: dict) -> str:
        prompt = self._render_template(step.prompt, context)
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content

    def _render_template(self, template_str: str, context: dict) -> str:
        return Template(template_str).render(**context)

    def _evaluate_condition(self, condition: str, context: dict) -> bool:
        try:
            rendered = Template("{{ " + condition + " }}").render(**context)
            return rendered.strip().lower() not in ("", "false", "none", "0")
        except Exception:
            return False

    def _resolve_input(self, input_expr: str | None, context: dict) -> list:
        if not input_expr:
            return []
        result = Template("{{ " + input_expr + " }}").render(**context)
        return result if isinstance(result, list) else [result]
