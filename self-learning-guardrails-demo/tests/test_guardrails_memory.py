from slg_demo.guardrails import extract_guardrails, validate_guardrails_schema


# TEST-001

def test_extract_guardrails():
    corrections = [
        "Remove fallback paths; single deterministic path only.",
        "Eliminate duplicated steps or sections.",
        "Add fail-fast checks for missing configuration.",
    ]
    memory = extract_guardrails(corrections)
    memory_dict = memory.to_dict()
    validate_guardrails_schema(memory_dict)
    assert "hard_constraints" in memory_dict
    assert len(memory_dict["hard_constraints"]) >= 3
    assert "clarifying_triggers" in memory_dict
    assert len(memory_dict["clarifying_triggers"]) >= 1
