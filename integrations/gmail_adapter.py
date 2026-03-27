"""Gmail / IMAP integration adapter."""

import os
from typing import Any

from integrations import SourceAdapter, SinkAdapter
from integrations.registry import register


@register("gmail")
class GmailAdapter(SourceAdapter, SinkAdapter):
    def __init__(self):
        self.credentials_path = os.getenv("GMAIL_CREDENTIALS")

    def fetch(self, config: dict[str, Any]) -> dict[str, Any]:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        )
        service = build("gmail", "v1", credentials=creds)

        query = "is:unread" if config.get("unread_only") else ""
        if label := config.get("label"):
            query += f" in:{label}"

        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=config.get("max_batch", 20))
            .execute()
        )

        emails = []
        for msg_ref in results.get("messages", []):
            msg = service.users().messages().get(userId="me", id=msg_ref["id"]).execute()
            headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
            emails.append({
                "id": msg["id"],
                "sender": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "body": msg.get("snippet", ""),
            })
        return {"emails": emails}

    def push(self, data: dict[str, Any], config: dict[str, Any]) -> None:
        # Archive, label, forward — based on config action
        pass
