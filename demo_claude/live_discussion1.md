User: CI red; test_event_dedupe_idempotent fails. Repo: event_pipeline/dedupe/v2.py, event_pipeline/dedupe/legacy.py, tests/test_dedupe.py. Artifact excerpt: [INFO] selected_pipeline=legacy_fallback [WARNING] fallback warning: using legacy_fallback due to missing pricingContext.currency E   AssertionError: expected 1 event, got 2 . Note: legacy.py returns events unchanged; v2.py throws if pricing_context is None.
Claude: The test fails because `legacy.py` passes through unparsed events when `pricing_context.currency` is missing, while `v2.py` requires it—`legacy_fallback` returns 2 events (original + duplicate), but the deduplication expects 1; fix by validating `pricing_context.currency` exists before falling back to legacy in the pipeline selector.

User: Which handler ran, based on the excerpt?
Claude: The `legacy_fallback` handler ran, as indicated by the `[INFO] selected_pipeline=legacy_fallback` log in the artifact excerpt.

User: If I only edit v2, why would the failure persist?
Claude: Because `legacy_fallback` selected `legacy.py` as the handler—editing only `v2.py` won't affect the code path that's actually running; you must either fix `legacy.py` or change the pipeline selection logic to use `v2.py` instead.

User: Fix the executed path only, using the given context.
Claude: Fix `legacy.py` to validate `pricing_context.currency` before returning events, preventing the duplicate from passing through when the currency is missing.

User: Summarize fix + lesson in one line.
Claude: Add `pricing_context.currency` validation in `legacy.py` before returning events—the fallback handler must enforce the same constraints as the primary handler to prevent duplicates from bypassing deduplication logic.

