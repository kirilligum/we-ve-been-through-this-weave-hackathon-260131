"""Synthetic tests for dedupe pipeline."""
from event_pipeline.dedupe.entrypoint import DedupeEntrypoint


def test_event_dedupe_idempotent():
    env = {"DEDUPER": "v2"}
    entrypoint = DedupeEntrypoint(env)
    events = ["e1", "e1"]
    # Pricing context is intentionally missing for demo scenario.
    result = entrypoint.run(events, pricing_context=None)
    assert len(result) == 1
