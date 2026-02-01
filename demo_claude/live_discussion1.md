User: CI red; test_event_dedupe_idempotent fails. Repo: event_pipeline/dedupe/v2.py, event_pipeline/dedupe/legacy.py, tests/test_dedupe.py. Artifact excerpt: [INFO] selected_pipeline=legacy_fallback [WARNING] fallback warning: using legacy_fallback due to missing pricingContext.currency E   AssertionError: expected 1 event, got 2 . Note: legacy.py run(self, events) only and returns events unchanged; v2.py throws if pricing_context is None.
Claude: The test fails because `legacy.py` returns events unchanged while `v2.py` requires `pricing_context.currency`; the fallback to legacy mode isn't deduping, so you get 2 events instead of 1—fix by adding deduplication logic to `legacy.py`'s run method or ensuring `pricing_context` is populated before pipeline execution.

User: Which handler ran, based on the excerpt?
Claude: The `legacy_fallback` handler ran, as indicated by `[INFO] selected_pipeline=legacy_fallback` in the artifact excerpt.

User: If I only edit v2, why would the failure persist?
Claude: Because the test falls back to `legacy_fallback` (which runs `legacy.py`), editing only `v2.py` won't affect the code path being executed—you must fix `legacy.py`'s deduplication logic or ensure `pricing_context.currency` is provided so `v2.py` runs instead.

User: Fix the executed path only, using the given context.
Claude: Fix `legacy.py`'s `run()` method to deduplicate events before returning them, since that's the code path currently executing.

User: Summarize fix + lesson in one line.
Claude: Add deduplication logic to `legacy.py`'s `run()` method to remove duplicate events before returning—the fallback handler won't fix itself by editing the primary path.

