"""S3 output adapter for storing generated reports."""

import os
from typing import Any

from integrations import SinkAdapter
from integrations.registry import register


@register("s3")
class S3Adapter(SinkAdapter):
    def fetch(self, config):
        raise NotImplementedError("S3 is a sink-only adapter")

    def push(self, data: dict[str, Any], config: dict[str, Any]) -> None:
        import boto3

        s3 = boto3.client("s3")
        bucket = config.get("bucket", os.getenv("S3_BUCKET"))
        key = config.get("key", "output.md")

        content = data.get("final_report", data.get("result", str(data)))
        s3.put_object(
            Bucket=bucket, Key=key, Body=content.encode(), ContentType="text/markdown"
        )
