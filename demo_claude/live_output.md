# WBTT Live Demo Output

## Discussion 1 (historical, live run)

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

## Discussion 2 (with memory injection)

User: CI red again; same test. Repo: event_pipeline/dedupe/v2.py, event_pipeline/dedupe/legacy.py. Artifact excerpt: [INFO] selected_pipeline=legacy_fallback [WARNING] fallback warning: using legacy_fallback due to missing pricingContext.currency E   AssertionError: expected 1 event, got 2 
Perfect! ✅ **Fix successful!** 

## Summary

The issue was in the **entrypoint's fallback logic**. When `pricing_context=None` was passed to the test, the v2 dedupe would fail trying to access `pricing_context["currency"]`, triggering an exception fallback to the legacy implementation. The legacy implementation doesn't actually deduplicate—it just returns events as-is, causing the test to fail with "expected 1 event, got 2".

### The Fix

I added a **`_derive_minimal_context()` method** that creates a minimal pricingContext with a default currency (`USD`) when one isn't provided:

```python
def run(self, events, pricing_context=None):
    if self.env.get("DEDUPER") != "v2":
        self._log_selected("legacy_fallback")
        return self.legacy.run(events)

    # Derive minimal pricingContext at entrypoint if missing.
    if pricing_context is None:
        pricing_context = self._derive_minimal_context()

    try:
        return self.v2.run(events, pricing_context=pricing_context)
    except Exception:
        self._log_selected("legacy_fallback")
        return self.legacy.run(events)

def _derive_minimal_context(self):
    """Derive minimal pricingContext with required currency."""
    return {"currency": "USD"}
```

This ensures v2 never fails due to missing currency, allowing proper deduplication to occur. The test now passes! 🎉

## Redis: memory search (proof)

{"memories":[{"id":"wbtt-live-20260201222739","text":"title: Dedupe failure caused by legacy fallback\nroot_cause: Unknown\nfix_steps:\n- derive minimal pricingContext at entrypoint","session_id":null,"user_id":"wbtt-demo","namespace":"wbtt","last_accessed":"2026-02-01T22:27:39.524842Z","created_at":"2026-02-01T22:27:39.524850Z","updated_at":"2026-02-01T22:27:39.524852Z","pinned":false,"access_count":0,"topics":null,"entities":null,"memory_hash":null,"discrete_memory_extracted":"f","memory_type":"semantic","persisted_at":null,"extracted_from":null,"event_date":null,"extraction_strategy":"discrete","extraction_strategy_config":{},"dist":1.0}],"total":1,"next_offset":null}

## Redis: memory_prompt (injection block)

{"messages":[{"role":"system","content":{"type":"text","text":"## Long term memories related to the user's query\n - title: Dedupe failure caused by legacy fallback\nroot_cause: Unknown\nfix_steps:\n- derive minimal pricingContext at entrypoint (ID: wbtt-live-20260201222739)","annotations":null,"_meta":null}},{"role":"user","content":{"type":"text","text":"Dedupe failure caused by legacy fallback","annotations":null,"_meta":null}}]}
