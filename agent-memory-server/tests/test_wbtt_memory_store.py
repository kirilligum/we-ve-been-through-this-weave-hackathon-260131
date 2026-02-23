# TEST-005
from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("case_id", [pytest.param("case", id="TEST-005")])
async def test_memory_store_roundtrip_mock(case_id):
    # TEST-005
    from agent_memory_server.wbtt import memory_store

    artifact = {
        "title": "Dedupe failure caused by legacy fallback",
        "trigger_cues": ["test_event_dedupe_idempotent fails"],
        "evidence_to_check": ["selected_pipeline=legacy_fallback"],
        "root_cause": "v2 throws missing pricingContext.currency",
        "fix_steps": ["derive pricingContext at entrypoint"],
        "anti_patterns": ["editing v2 before verifying executed path"],
        "tags": ["dedupe", "fallback"],
        "confidence": "0.78",
        "source_trace_id": "weave-wbtt-hist-002",
        "created_at": "2026-02-01",
    }

    client = AsyncMock()
    await memory_store.store_memory_artifact(
        client,
        artifact,
        namespace="wbtt",
        session_id="session-1",
        user_id="user-1",
    )

    client.create_long_term_memory.assert_awaited()
    memories = client.create_long_term_memory.call_args.args[0]
    assert memories[0].topics == artifact["tags"]
    assert memories[0].session_id == "session-1"
