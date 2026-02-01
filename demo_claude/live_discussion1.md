User: CI red; test_event_dedupe_idempotent fails. Repo: event_pipeline/dedupe/v2.py, event_pipeline/dedupe/legacy.py, tests/test_dedupe.py. Artifact excerpt: [INFO] selected_pipeline=legacy_fallback [WARNING] fallback warning: using legacy_fallback due to missing pricingContext.currency E   AssertionError: expected 1 event, got 2 . Note: legacy.py run(self, events) only and returns events unchanged; v2.py throws if pricing_context is None.
Claude: The test fails because `legacy.py` returns events unchanged while `v2.py` requires `pricing_context.currency`; the fallback to legacy mode isn't deduping, so you get 2 events instead of 1—fix by adding deduplication logic to `legacy.py`'s run method or ensuring `pricing_context` is populated before pipeline execution.

User: Which handler ran, based on the excerpt?
Claude: The `legacy_fallback` handler ran, as indicated by `[INFO] selected_pipeline=legacy_fallback` in the artifact excerpt.

