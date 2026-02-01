from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _ensure_client_imports() -> None:
    try:
        import agent_memory_client  # noqa: F401
        return
    except ImportError:
        demo_root = Path(__file__).resolve().parents[1]
        repo_root = demo_root.parents[0]
        client_path = repo_root / "agent-memory-server" / "agent-memory-client"
        if client_path.exists() and str(client_path) not in sys.path:
            sys.path.insert(0, str(client_path))


_ensure_client_imports()

from agent_memory_client import MemoryAPIClient, MemoryClientConfig  # type: ignore
from agent_memory_client.models import ClientMemoryRecord  # type: ignore


@dataclass
class MemoryServerBackend:
    base_url: str
    namespace: str

    def _run(self, coro: Any):
        return asyncio.run(coro)

    def health_check(self) -> None:
        config = MemoryClientConfig(base_url=self.base_url, default_namespace=self.namespace)
        client = MemoryAPIClient(config)

        async def _check():
            await client.health_check()
            await client.close()

        self._run(_check())

    def store_guardrails(self, memory_id: str, memory_payload: dict) -> None:
        config = MemoryClientConfig(base_url=self.base_url, default_namespace=self.namespace)
        client = MemoryAPIClient(config)
        record = ClientMemoryRecord(
            id=memory_id,
            text=json.dumps(memory_payload, sort_keys=True),
            memory_type="semantic",
            topics=["guardrails", "demo"],
            entities=["self_learning_guardrails"],
            session_id=memory_id,
            namespace=self.namespace,
        )

        async def _store():
            await client.create_long_term_memory([record])
            await client.close()

        self._run(_store())


class InMemoryBackend:
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def health_check(self) -> None:
        return

    def store_guardrails(self, memory_id: str, memory_payload: dict) -> None:
        self._store[memory_id] = memory_payload

    def get_guardrails(self, memory_id: str) -> dict | None:
        return self._store.get(memory_id)
