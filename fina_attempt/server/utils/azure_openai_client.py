# server/utils/azure_openai_client.py
from __future__ import annotations
import os
from openai import AzureOpenAI

from dotenv import load_dotenv
load_dotenv()

# ---- Env (kept simple & explicit) ----
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")

# Deployments (names, not model IDs)
AZURE_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT") or os.getenv("DEPLOYMENT_NAME")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

# API versions (defaults are safe)
AZURE_OPENAI_CHAT_API_VERSION = os.getenv("AZURE_OPENAI_CHAT_API_VERSION", "2024-06-01")
AZURE_OPENAI_EMBEDDING_API_VERSION = os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION", "2024-02-01")

def get_azure_openai_client() -> AzureOpenAI:
    """
    Returns a configured Azure OpenAI client.
    Works for both chat and embeddings endpoints (version is per-call).
    """
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        raise RuntimeError(
            "Missing Azure creds. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in your environment."
        )
    # We pass the chat api version by default; embeddings calls can still work as AzureOpenAI uses per-call model routing.
    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_CHAT_API_VERSION,
    )

# Back-compat aliases (if any code expects these names)
get_client = get_azure_openai_client
CHAT_API_VERSION = AZURE_OPENAI_CHAT_API_VERSION
EMBED_API_VERSION = AZURE_OPENAI_EMBEDDING_API_VERSION
