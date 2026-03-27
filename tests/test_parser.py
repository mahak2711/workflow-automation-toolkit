"""Tests for YAML workflow parser."""

import pytest
from core.parser import YAMLWorkflowParser, WorkflowDefinition


SAMPLE_YAML = """
name: test-workflow
description: A test workflow
schedule: "0 9 * * *"

source:
  adapter: slack
  config:
    channels: ["#test"]

chain:
  - step: summarize
    prompt: "Summarize: {{ source.messages }}"
    output: summary

sink:
  adapter: slack
  config:
    channel: "#output"
"""


def test_parse_string():
    wf = YAMLWorkflowParser.parse_string(SAMPLE_YAML)
    assert isinstance(wf, WorkflowDefinition)
    assert wf.name == "test-workflow"
    assert len(wf.chain) == 1
    assert wf.chain[0].step == "summarize"


def test_parse_schedule():
    wf = YAMLWorkflowParser.parse_string(SAMPLE_YAML)
    assert wf.schedule == "0 9 * * *"


def test_default_retry_config():
    wf = YAMLWorkflowParser.parse_string(SAMPLE_YAML)
    assert wf.retry.max_attempts == 3
    assert wf.retry.backoff_seconds == 30


def test_empty_chain_raises():
    bad_yaml = """
name: bad
source:
  adapter: slack
chain: []
sink:
  adapter: slack
"""
    with pytest.raises(Exception):
        YAMLWorkflowParser.parse_string(bad_yaml)


def test_missing_name_raises():
    bad_yaml = """
source:
  adapter: slack
chain:
  - step: foo
    prompt: bar
sink:
  adapter: slack
"""
    with pytest.raises(Exception):
        YAMLWorkflowParser.parse_string(bad_yaml)
