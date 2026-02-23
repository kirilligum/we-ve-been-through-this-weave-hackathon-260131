Known Error Record: dedupe test fails due to legacy fallback path

KER slug: 20260201-test-fails-legacy-fallback
Git reference: Unknown (How to confirm: use git rev-parse HEAD during incident)
Applies to (scope): CI test runs for event dedupe pipeline (How to confirm: check Weave trace + W&B pytest artifact)
Tags: dedupe, fallback, selected_pipeline, weavetrace, artifact
Anomaly classification (IEEE 1044–inspired, lightweight):
  - anomaly type: defect
  - reproducibility: always
  - impact: medium
  - likely cause category: config

Trigger patterns (for fast matching)
- "test_event_dedupe_idempotent fails"
- "selected_pipeline=legacy_fallback"
- "fallback warning"

Problem Record (conceptual guidance)

Symptoms
- CI test fails with "expected 1 got 2" on dedupe idempotence
- Logs show fallback warning and legacy path execution
- Fixing v2 code does not change runtime behavior

Likely causes (ranked mental model)
1) Pipeline selection uses legacy_fallback due to missing DEDUPER env or v2 exception
2) v2 throws missing pricingContext.currency, forcing fallback
3) Duplicate implementations cause edits in the wrong path

Diagnostic decision path
1) Check: selected_pipeline at top of pytest artifact
   How: open full W&B pytest artifact (not truncated) and read startup lines
   If true: legacy_fallback
   Next step: inspect lines above fallback warning for v2 exception
2) Check: exception preceding fallback
   How: read 5–20 lines above fallback warning
   If true: missing pricingContext.currency
   Next step: derive minimal pricingContext at entrypoint and ensure legacy delegates to v2

Evidence from this incident
- key error excerpt:
  [INFO] selected_pipeline=legacy_fallback
  [WARNING] fallback warning: using legacy_fallback due to v2 exception
- logs / files involved: W&B pytest artifact; Weave trace tree
- code / config areas involved: dedupe/v2 entrypoint; legacy dedupe; DEDUPER env
- what did NOT work:
  edit v2 dedupe logic -> no change in runtime path

Decisions and tradeoffs
Options considered
- option: patch v2 only
  description: modify v2 dedupe logic
  pros: minimal change
  cons / risks: ineffective if legacy_fallback executes
  decision: rejected
  rationale: evidence shows legacy_fallback path

- option: set DEDUPER=v2 in tests
  description: force pipeline selection
  pros: immediate path control
  cons / risks: hides real fallback triggers
  decision: accepted (temporary)
  rationale: ensures v2 path while fixing root cause

Key constraints influencing decisions
- No code changes without evidence from full artifact
- Avoid changing tests unless required for pipeline selection

Non-obvious context
- Terminal snippets are truncated; full artifact is required to see selected_pipeline

Workarounds
- Set DEDUPER=v2 for test run to confirm v2 path (temporary)

Known Error Record (what actually worked)

Root cause (best current understanding)
- v2 throws missing pricingContext.currency, triggering legacy_fallback; edits were made in the wrong path

Permanent fix
1) Derive minimal pricingContext at v2 entrypoint from receipt or defaults
2) Make legacy dedupe delegate to v2 to avoid duplicated logic

Verification
How to confirm the fix:
  Run CI test and verify selected_pipeline=v2 in full W&B pytest artifact
Expected result:
  test_event_dedupe_idempotent passes and fallback warning is absent

Prevention / guardrails
- Add a check that asserts selected_pipeline=v2 for this test
- Add a log warning when v2 exception triggers fallback
