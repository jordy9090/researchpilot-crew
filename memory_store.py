from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools import BASE_DIR, load_json


MEMORY_PATH = BASE_DIR / "data" / "project_memory.json"


def load_project_memory() -> dict[str, Any]:
    memory = load_json(MEMORY_PATH, {"memories": []})
    if not isinstance(memory, dict):
        return {"memories": []}
    if not isinstance(memory.get("memories"), list):
        memory["memories"] = []
    return memory


def save_project_memory(memory: dict[str, Any]) -> str:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_PATH.open("w", encoding="utf-8") as file:
        json.dump(memory, file, indent=2, ensure_ascii=False)
    return str(MEMORY_PATH)


def append_memory_entry(entry: dict[str, Any]) -> str:
    memory = load_project_memory()
    enriched = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **entry,
    }
    memory.setdefault("memories", []).append(enriched)
    return save_project_memory(memory)
