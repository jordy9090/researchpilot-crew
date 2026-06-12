from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent


def resolve_project_path(path: str | Path) -> Path:
    target = Path(path)
    if target.is_absolute():
        return target
    return BASE_DIR / target


def ensure_output_dir(output_dir: str = "outputs") -> None:
    resolve_project_path(output_dir).mkdir(parents=True, exist_ok=True)


def load_json(path: str | Path, default: Any) -> Any:
    target = resolve_project_path(path)
    try:
        if not target.exists():
            return default
        with target.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default


def save_json(filename: str, data: dict[str, Any], output_dir: str = "outputs") -> str:
    ensure_output_dir(output_dir)
    path = resolve_project_path(output_dir) / filename
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    return str(path)


def save_markdown(filename: str, content: str, output_dir: str = "outputs") -> str:
    ensure_output_dir(output_dir)
    path = resolve_project_path(output_dir) / filename
    with path.open("w", encoding="utf-8") as file:
        file.write(content)
    return str(path)


def validate_required_keys(data: dict[str, Any], required_keys: list[str]) -> tuple[bool, list[str]]:
    missing = [key for key in required_keys if key not in data]
    return len(missing) == 0, missing


def score_priority(impact: int, urgency: int, feasibility: int) -> float:
    score = 0.45 * impact + 0.35 * urgency + 0.20 * feasibility
    return round(score, 2)


def _tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9:+-]+", text.lower()) if len(token) > 2]


def search_local_papers(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    papers = load_json("data/papers.json", [])
    query_terms = set(_tokens(query))
    if not query_terms:
        return []

    scored: list[tuple[int, dict[str, Any]]] = []
    for paper in papers:
        title = str(paper.get("title", "")).lower()
        abstract = str(paper.get("abstract", "")).lower()
        tags = " ".join(str(tag).lower() for tag in paper.get("tags", []))
        why = str(paper.get("why_relevant", "")).lower()

        score = 0
        for term in query_terms:
            if term in title:
                score += 4
            if term in tags:
                score += 3
            if term in abstract:
                score += 2
            if term in why:
                score += 1
        if score > 0:
            scored.append((score, paper))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [paper for _, paper in scored[:top_k]]


def detect_scope_creep(user_input: str, action_plan: dict[str, Any] | None = None) -> list[str]:
    warnings: list[str] = []
    lowered = user_input.lower()
    themes = ["paper", "startup", "marketing", "frontend", "backend", "professor", "exam", "mvp", "dataset"]
    hits = [theme for theme in themes if theme in lowered]
    if len(hits) >= 5:
        warnings.append("Scope risk detected: the plan was compressed to the top 3 actions for today.")
    if ("tonight" in lowered or "today" in lowered) and ("full paper" in lowered or "complete system" in lowered):
        warnings.append("Deadline risk detected: the requested scope is too large for the stated time window.")
    if action_plan:
        today = action_plan.get("today", [])
        if isinstance(today, list) and len(today) > 8:
            warnings.append("Too many TODOs detected: today's plan should be compressed before execution.")
    return warnings
