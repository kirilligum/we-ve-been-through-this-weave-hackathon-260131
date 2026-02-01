from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def deterministic_id(seed: int, prompt_id: str) -> str:
    raw = f"{seed}:{prompt_id}".encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    return f"run-{digest[:12]}"
