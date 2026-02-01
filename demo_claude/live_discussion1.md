User: CI red; test_event_dedupe_idempotent fails. Repo: event_pipeline/dedupe/v2.py, event_pipeline/dedupe/legacy.py, tests/test_dedupe.py. Artifact excerpt: [INFO] selected_pipeline=legacy_fallback [WARNING] fallback warning: using legacy_fallback due to missing pricingContext.currency E   AssertionError: expected 1 event, got 2 . Note: entrypoint falls back to legacy when v2 throws; v2 throws if pricing_context is None; legacy returns events unchanged.
Claude: The test fails because v2 throws when `pricing_context` is None, triggering fallback to legacy which returns both events unchanged, but the test expects deduplication to occur—fix by ensuring v2 handles None pricing_context gracefully or by providing valid pricing_context in the test.

User: Which handler ran, based on the excerpt?
Claude: The legacy handler ran, as indicated by `[INFO] selected_pipeline=legacy_fallback` in the artifact excerpt.

User: We prefer not to edit legacy; keep v2 path. Why didn't v2 run, and where would you add a minimal default pricingContext?
Claude: V2 didn't run because it throws when `pricing_context` is None, triggering fallback to legacy; add a minimal default pricingContext in the test setup (before calling the dedupe handler) or in v2's entrypoint to handle None by creating a default context with required fields like currency.

User: What's the minimal fix to avoid fallback and keep v2?
Claude: Add a default pricingContext in v2's entrypoint before the None check: create a minimal context with `currency="USD"` (or required fields) if pricing_context is None, so v2 executes instead of throwing and triggering fallback to legacy.

User: Summarize fix + lesson in one line.
Claude: Add a default pricingContext with `currency="USD"` in v2's entrypoint when None is passed, so v2 completes deduplication instead of throwing and falling back to legacy.

