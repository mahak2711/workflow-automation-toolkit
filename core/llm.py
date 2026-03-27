"""LLM provider configuration."""

import os
from langchain_openai import ChatOpenAI


def get_llm():
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048")),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
