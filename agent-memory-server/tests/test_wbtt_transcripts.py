# TEST-007
from pathlib import Path

import pytest


@pytest.mark.parametrize("case_id", [pytest.param("case", id="TEST-007")])
def test_transcripts_memory_on_off(case_id):
    # TEST-007
    base = Path(__file__).parent / "fixtures" / "wbtt" / "transcripts"
    memory_on = (base / "memory_on.txt").read_text(encoding="utf-8")
    memory_off = (base / "memory_off.txt").read_text(encoding="utf-8")

    on_turns = _count_turns(memory_on)
    off_turns = _count_turns(memory_off)

    assert on_turns <= 2
    assert off_turns >= 8


def _count_turns(text: str) -> int:
    return sum(1 for line in text.splitlines() if _is_turn_line(line))


def _is_turn_line(line: str) -> bool:
    stripped = line.strip()
    return len(stripped) > 2 and stripped[0].isdigit() and stripped[1] == " "
