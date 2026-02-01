User: CI red again; same test. Repo: event_pipeline/dedupe/v2.py, event_pipeline/dedupe/legacy.py. Artifact excerpt: [INFO] selected_pipeline=legacy_fallback [WARNING] fallback warning: using legacy_fallback due to missing pricingContext.currency E   AssertionError: expected 1 event, got 2 
Claude: The legacy fallback is triggering due to missing `pricingContext.currency` at the dedupe entrypoint, causing duplicate events—derive a minimal `pricingContext` with required currency field before calling the deduplication pipeline.

