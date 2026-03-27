# Workflow Automation Toolkit

An open-source, LLM-powered automation framework for orchestrating intelligent agents via configurable YAML prompt chains. Built on LangChain, Celery, and Redis with Dockerized microservice deployment and CI/CD through GitHub Actions.

## Features

- **YAML-based agent definitions** — configure prompt chains without writing code
- **Pre-built agents** — email triage, Slack summarization, report generation
- **Async task orchestration** — Celery + Redis for reliable scheduling, retries, and distributed workers
- **Pluggable integrations** — Gmail/IMAP, Slack, S3, Google Docs (add your own with a simple adapter interface)
- **Dockerized deployment** — one command to run locally, production-ready container images
- **CI/CD pipeline** — GitHub Actions for testing, linting, building, and publishing

## Quick Start

```bash
# Clone and start all services
git clone https://github.com/yourorg/workflow-automation-toolkit.git
cd workflow-automation-toolkit
cp .env.example .env  # add your API keys
docker compose up -d

# Trigger an agent manually
curl -X POST http://localhost:8000/api/v1/workflows/slack-daily-summary/run
```

## Architecture

```
Triggers (webhooks, cron, API)
        |
   FastAPI Gateway ---- auth, routing, status
        |
   Celery + Redis ----- queue, retry, concurrency
        |
   YAML Prompt Chains -- LangChain executor
   +----+----+
 Email  Slack  Report
   |     |      |
 Gmail  Slack   S3/GDocs
```

## Project Structure

```
├── agents/              # YAML workflow definitions
│   └── examples/        # Pre-built agent configs
├── core/                # Chain executor, YAML parser, LangChain integration
├── workers/             # Celery task definitions and config
├── api/                 # FastAPI gateway
├── integrations/        # Adapter classes for external services
├── infra/               # Dockerfiles, compose, CI/CD
├── tests/               # Unit and integration tests
└── docs/                # Documentation
```

## Defining an Agent

Create a YAML file in `agents/`:

```yaml
name: email-triage
description: Classify, extract action items, and route incoming emails
schedule: "*/5 * * * *"

source:
  adapter: gmail
  config:
    label: INBOX
    unread_only: true

chain:
  - step: classify
    prompt: prompts/email/classify.txt
    output: category

  - step: extract_actions
    prompt: prompts/email/extract_actions.txt
    input: "{{ source.body }}"
    output: action_items

  - step: route
    prompt: prompts/email/route.txt
    input: "{{ category }}, {{ action_items }}"
    output: routing_decision

sink:
  adapter: slack
  config:
    channel: "#email-triage"
    template: "New {{ category }}: {{ action_items | join(', ') }}"
```

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | LLM provider API key |
| `REDIS_URL` | Redis connection string |
| `SLACK_BOT_TOKEN` | Slack Bot OAuth token |
| `GMAIL_CREDENTIALS` | Path to Gmail service account JSON |
| `CELERY_CONCURRENCY` | Number of concurrent workers |

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Write tests, then code
4. Run `make lint test`
5. Open a PR

## License

MIT
