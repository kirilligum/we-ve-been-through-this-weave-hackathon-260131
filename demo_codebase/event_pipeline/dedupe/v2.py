"""New dedupe implementation (synthetic)."""


class DedupeV2:
    def run(self, events, pricing_context=None):
        # Simulate missing context error used in the demo.
        currency = pricing_context["currency"]  # raises if missing
        return _dedupe(events, currency)


def _dedupe(events, currency):
    # Placeholder: behaves correctly when currency provided.
    return list(dict.fromkeys(events))
