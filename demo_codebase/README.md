WBTT Demo Codebase (Synthetic)

This is a minimal, synthetic codebase used only to make the demo prompts feel real.
It models a deduplication pipeline with a v2 implementation and a legacy fallback.

Key paths:
- event_pipeline/dedupe/entrypoint.py
- event_pipeline/dedupe/v2.py
- event_pipeline/dedupe/legacy.py
- tests/test_dedupe.py
- logs/pytest_artifact_excerpt.txt
