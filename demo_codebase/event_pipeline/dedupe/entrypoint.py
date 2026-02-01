"""Entrypoint for dedupe pipeline selection (synthetic)."""
from .v2 import DedupeV2
from .legacy import DedupeLegacy


class DedupeEntrypoint:
    """Select v2 unless env missing or v2 throws; fallback to legacy."""

    def __init__(self, env: dict):
        self.env = env
        self.v2 = DedupeV2()
        self.legacy = DedupeLegacy()

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

    def _log_selected(self, pipeline):
        # This line is mirrored in pytest artifacts for the demo.
        print(f"[INFO] selected_pipeline={pipeline}")
