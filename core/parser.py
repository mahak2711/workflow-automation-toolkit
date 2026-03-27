"""YAML workflow parser — loads and validates agent definitions."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, field_validator


class StepConfig(BaseModel):
    step: str
    prompt: str
    type: str = "single"  # single | map | reduce
    input: str | None = None
    output: str = "result"
    condition: str | None = None


class SourceConfig(BaseModel):
    adapter: str
    config: dict[str, Any] = {}


class SinkConfig(BaseModel):
    adapter: str
    config: dict[str, Any] = {}
    condition: str | None = None


class RetryConfig(BaseModel):
    max_attempts: int = 3
    backoff_seconds: int = 30


class WorkflowDefinition(BaseModel):
    name: str
    description: str = ""
    schedule: str | None = None
    source: SourceConfig
    chain: list[StepConfig]
    sink: SinkConfig | dict[str, Any]
    retry: RetryConfig = RetryConfig()

    @field_validator("chain")
    @classmethod
    def chain_must_have_steps(cls, v: list) -> list:
        if not v:
            raise ValueError("Workflow chain must have at least one step")
        return v


class YAMLWorkflowParser:
    """Parse YAML workflow files into validated WorkflowDefinition objects."""

    @staticmethod
    def parse_file(path: str | Path) -> WorkflowDefinition:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {path}")
        with open(path) as f:
            raw = yaml.safe_load(f)
        return WorkflowDefinition(**raw)

    @staticmethod
    def parse_string(yaml_str: str) -> WorkflowDefinition:
        raw = yaml.safe_load(yaml_str)
        return WorkflowDefinition(**raw)

    @staticmethod
    def discover_workflows(directory: str | Path) -> list[WorkflowDefinition]:
        directory = Path(directory)
        workflows = []
        for path in sorted(directory.rglob("*.yaml")):
            try:
                workflows.append(YAMLWorkflowParser.parse_file(path))
            except Exception as e:
                print(f"Warning: skipping {path}: {e}")
        return workflows
