from __future__ import annotations

from typing import Any

from agent_memory_client.models import ClientMemoryRecord


def _artifact_to_text(artifact: dict[str, Any]) -> str:
    title = artifact.get("title", "WBTT Memory Artifact")
    root_cause = artifact.get("root_cause", "Unknown")
    fix_steps = artifact.get("fix_steps", []) or []
    return "\n".join(
        [
            f"title: {title}",
            f"root_cause: {root_cause}",
            "fix_steps:",
            *_list_to_lines(fix_steps),
        ]
    )


def _list_to_lines(items: list[Any]) -> list[str]:
    return [f"- {item}" for item in items]


async def store_memory_artifact(
    client,
    artifact: dict[str, Any],
    namespace: str,
    session_id: str,
    user_id: str,
) -> ClientMemoryRecord:
    record = ClientMemoryRecord(
        text=_artifact_to_text(artifact),
        topics=artifact.get("tags", []),
        session_id=session_id,
        user_id=user_id,
        namespace=namespace,
    )

    await client.create_long_term_memory([record])
    return record
