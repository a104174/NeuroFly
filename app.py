"""Vercel ASGI entrypoint; local Uvicorn continues using its existing factory."""

from pathlib import Path

from tools.vercel_runtime_entrypoint import application

app = application(Path(__file__).resolve().parent)
