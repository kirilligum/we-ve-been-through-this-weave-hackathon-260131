User: CI red; test_event_dedupe_idempotent fails. Repo: event_pipeline/dedupe/v2.py, event_pipeline/dedupe/legacy.py, tests/test_dedupe.py. Artifact excerpt: [INFO] selected_pipeline=legacy_fallback [WARNING] fallback warning: using legacy_fallback due to missing pricingContext.currency E   AssertionError: expected 1 event, got 2 . Note: entrypoint falls back to legacy when v2 throws; v2 throws if pricing_context is None; legacy returns events unchanged.
Claude: The test fails because v2 throws when `pricing_context` is None, causing fallback to legacy which returns 2 events unchanged instead of deduping to 1, so you need to either make v2 handle None pricing_context gracefully or ensure the test provides valid pricing_context.currency.

User: Which handler ran, based on the excerpt?
Claude: The legacy handler ran, as indicated by `[INFO] selected_pipeline=legacy_fallback` in the artifact excerpt.

