"""Self-contained course retrieval, adapted from the original Agent workshop.

Source and migration fingerprints: docs/SOURCE-PROVENANCE.md.
No import, checkout or installation of the original course is required.
"""
from __future__ import annotations

import json
from pathlib import Path

def validate_search_args(arguments: dict) -> dict:
    """Validate a small search contract; booleans are not numeric limits."""
    if not isinstance(arguments, dict):
        raise ValueError("Search parameters must be a JSON object")
    if set(arguments) - {"query", "limit"}:
        raise ValueError("Unexpected search parameter")
    query, limit = arguments.get("query"), arguments.get("limit", 2)
    if not isinstance(query, str) or not query.strip() or len(query) > 500:
        raise ValueError("query must be 1..500 nonblank characters")
    if type(limit) is not int or not 1 <= limit <= 3:
        raise ValueError("limit must be an integer between 1 and 3")
    return {"query": query.strip(), "limit": limit}


def search_notes(query: str, limit: int = 2) -> list[dict]:
    """Search controlled teaching notes. This is lexical retrieval, not vector RAG."""
    args = validate_search_args({"query": query, "limit": limit})
    notes = json.loads((Path(__file__).resolve().parent / "data" / "notes.json").read_text(encoding="utf-8"))
    terms = args["query"].lower().split()
    matches = [note for note in notes if any(term in note["topic"].lower() for term in terms)]
    return matches[:args["limit"]]


def build_report(evidence: list[dict]) -> str:
    if not evidence:
        return "资料不足：当前资料库没有匹配证据，请补充资料或调整问题。"
    return "\n".join(f"[{item['id']}] {item['text']}" for item in evidence)
