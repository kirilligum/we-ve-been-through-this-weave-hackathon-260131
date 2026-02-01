Known Error Record: Plain-text metadata fields flaky selector in E2E (order-dependent textarea lookup)

KER slug: 20260122-plain-text-field-selector-flake
Git reference: 40508619ff1d54029eacec74c936d194c8eaee6c (fix staged in working tree)
Applies to (scope): Playwright E2E running against remote dev (app-dev) metadata editors; confirm by running widget edit suite
Tags: e2e, playwright, metadata-editor, selector, data-testid, plain-text
Anomaly classification (IEEE 1044–inspired, lightweight):
  - anomaly type: defect
  - reproducibility: intermittent
  - impact: medium
  - likely cause category: code

Trigger patterns (for fast matching)
- "Expected product plain text mode to expose at least two inputs"
- "Expected company plain text mode to expose at least two inputs"
- "nth(1)" / "second field" lookup on textareas in plain-text mode
- E2E failures after toggling plain-text mode and adding a new row

Problem Record (conceptual guidance)

Symptoms
- E2E tests occasionally fail right after switching metadata editor to plain-text mode and adding a new row.
- The test assumes two textareas are present and immediately uses the second one (URL field), but the DOM sometimes only has one textarea on the first render tick.
- Failures appear as assertion errors or element-not-found errors when trying to edit the URL field.

Likely causes (ranked mental model)
1) Order-dependent DOM selectors: the test uses `textarea` order instead of a deterministic field selector, so if the second field renders asynchronously, the test fails.
2) UI render timing variance: the first field appears before the second; switching modes triggers a React re-render that is not synchronous across fields.
3) Missing or inconsistent field-level selectors: even though `data-testid` exists on metadata fields, the helper for E2E selection did not resolve them in a reusable, row-specific way.

Diagnostic decision path
1) Check: do metadata fields have stable `data-testid` already?
   How: inspect `client/src/components/EditableItemDisplay.tsx` for `data-testid={\`metadata-field-${fieldKey}-${id}\`}`
   If true: a deterministic selector scheme exists and should be used.
   Next step: update E2E helpers/tests to use those selectors rather than DOM order.

2) Check: does the E2E helper target the wrapper/testid or only `[contenteditable]` / `textarea`?
   How: inspect `e2e/utils/widget-edit/widgetEditorHelpers.js` and `editableFieldLocator`.
   If it only locates `[contenteditable], textarea` under a prefix without row id, it is order-dependent.
   Next step: add helper that resolves by docId and covers both wrapper and nested contenteditable.

Evidence from this incident
- key error excerpt:
  Unknown (not observed directly in logs for this incident). The test assertion strings indicate the likely failure point when only one textarea exists.
- logs / files involved:
  - tests: `e2e/widget-edit-company-product.e2e.test.js`
  - helper: `e2e/utils/widget-edit/widgetEditorHelpers.js`
  - UI: `client/src/components/EditableItemDisplay.tsx`
- code / config areas involved:
  - metadata editor field rendering and data-testid contract
  - E2E helper selector logic
- what did NOT work:
  - Polling for textarea count (adds ad-hoc timeouts, still order-based and not reusable)

Decisions and tradeoffs
This section captures WHY choices were made, including rejected options.

Options considered
- option: add local polling loop in E2E
  description: wait until `textarea` count reaches 2 before selecting by index
  pros: quick, minimal UI changes
  cons / risks: introduces new timeouts, still order-based, not reusable
  decision: rejected
  rationale: requirement to avoid timeout increases and prefer reusable selectors

- option: add deterministic field selectors and shared helper
  description: use `data-testid="metadata-field-${fieldKey}-${docId}"` and add helper to target by docId
  pros: reusable, stable, no extra timeouts, aligns with existing selector contract
  cons / risks: requires helper change + test update; relies on testid contract continuity
  decision: accepted
  rationale: best long-term stability and reuse without adding timeouts

Key constraints influencing decisions
- No new timeouts without a dedicated timeout analysis
- One path only (no legacy/fallback selector behavior)
- Prefer general reusable code over one-off patches

Non-obvious context
- `HighlightedTextarea` wraps Draft.js; data-testid is on the wrapper, not the inner editable element.
- The UI already emits `metadata-field-${fieldKey}-${id}` testids; the E2E helper just did not target them in a row-specific way.

Workarounds
- None recommended; use deterministic selectors instead.

Known Error Record (what actually worked)

Root cause (best current understanding)
- E2E test used order-based `textarea` selection in plain-text mode; render timing variance meant the second field was sometimes not yet present, causing flake.

Permanent fix
1) Introduce a reusable selector builder in `e2e/utils/widget-edit/widgetEditorHelpers.js` that targets `data-testid="metadata-field-${fieldKey}-${docId}"` and works for both wrapper and nested editable elements.
2) Add `editableFieldLocatorById` helper to select fields by docId instead of DOM order.
3) Update `e2e/widget-edit-company-product.e2e.test.js` to use row id + `editableFieldLocatorById` for plain-text name/url fields and remove the polling loop.

Verification
How to confirm the fix:
  `yarn test:widgetEdit:companyProduct:full`
Expected result:
  Suite passes without relying on textarea count or timeouts; plain-text edits persist.

Prevention / guardrails
- Use `editableFieldLocatorById` for any multi-field row edits in E2E.
- Treat `metadata-field-${fieldKey}-${docId}` as the canonical selector contract for metadata fields.

----- END DOCUMENT CONTENT -----
