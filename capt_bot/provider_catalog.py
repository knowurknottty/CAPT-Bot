"""Safe display-only provider/model catalog from CAPT's local configured registry.

Never expose provider secrets, API keys, endpoints or auth references to the UI.
This is a *configured* model list; it does not assert live provider health.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_provider_catalog(path: Path | None = None) -> dict[str, Any]:
    source = path if path is not None else Path.home() / ".capt" / "ui" / "providers.json"
    try:
        if source.stat().st_size > 2_000_000:
            raise ValueError("PROVIDER_CATALOG_TOO_LARGE")
        doc = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("PROVIDER_CATALOG_UNAVAILABLE") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("providers"), list):
        raise ValueError("PROVIDER_CATALOG_MALFORMED")
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in doc["providers"]:
        if not isinstance(item, dict) or item.get("enabled") is False:
            continue
        provider_id = item.get("id")
        if not isinstance(provider_id, str) or not (1 <= len(provider_id) <= 120):
            continue
        if provider_id in seen:
            raise ValueError("PROVIDER_CATALOG_DUPLICATE_ID")
        seen.add(provider_id)
        raw_models = item.get("models")
        if not isinstance(raw_models, list):
            raw_models = []
        models = list(dict.fromkeys(
            model for model in raw_models
            if isinstance(model, str) and model and len(model) <= 1024
        ))
        if len(models) > 3000:
            raise ValueError("PROVIDER_MODEL_CATALOG_TOO_LARGE")
        name = item.get("name")
        kind = item.get("kind")
        items.append({
            "id": provider_id,
            "name": name.strip()[:120] if isinstance(name, str) and name.strip() else provider_id,
            "kind": kind if isinstance(kind, str) and kind in ("local", "cloud", "hybrid") else "unknown",
            "models": models,
        })
    if not items:
        raise ValueError("PROVIDER_CATALOG_EMPTY")
    return {
        "source": "CAPT configured providers",
        "availabilityVerified": False,
        "providers": items,
    }


def validate_provider_model(provider: str, model: str, catalog: dict[str, Any]) -> None:
    matched = next((p for p in catalog["providers"] if p["id"] == provider), None)
    if matched is None:
        raise ValueError("PROVIDER_NOT_CONFIGURED_OR_DISABLED")
    if model not in matched["models"]:
        raise ValueError("MODEL_NOT_CONFIGURED_FOR_PROVIDER")
