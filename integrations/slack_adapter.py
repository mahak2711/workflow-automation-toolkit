"""Slack integration adapter."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from integrations import SourceAdapter, SinkAdapter
from integrations.registry import register


@register("slack")
class SlackAdapter(SourceAdapter, SinkAdapter):
    def __init__(self):
        self.token = os.getenv("SLACK_BOT_TOKEN")

    def fetch(self, config: dict[str, Any]) -> dict[str, Any]:
        from slack_sdk import WebClient

        client = WebClient(token=self.token)
        channels = config.get("channels", [])
        lookback = config.get("lookback_hours", 24)
        oldest = (datetime.now(timezone.utc) - timedelta(hours=lookback)).timestamp()

        results = {}
        for channel in channels:
            resp = client.conversations_history(channel=channel, oldest=str(oldest))
            results[channel] = [
                {"user": m.get("user", "unknown"), "text": m.get("text", "")}
                for m in resp.get("messages", [])
            ]
        return {"channels": results}

    def push(self, data: dict[str, Any], config: dict[str, Any]) -> None:
        from slack_sdk import WebClient

        client = WebClient(token=self.token)
        channel = config.get("channel", "#general")
        message = (
            config.get("template", "").format(**data)
            if "template" in config
            else str(data)
        )
        client.chat_postMessage(channel=channel, text=message)
