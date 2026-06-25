"""Persistent JSON storage for quote collections."""

import json
import os
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_COLLECTIONS_DIR = Path(__file__).parent / "data" / "default_collections"


def _get_data_dir() -> Path:
    xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
    data_dir = Path(xdg_data) / "quote_cli"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _get_collections_dir() -> Path:
    collections_dir = _get_data_dir() / "collections"
    collections_dir.mkdir(parents=True, exist_ok=True)
    return collections_dir


def _collection_path(name: str) -> Path:
    safe = "".join(c for c in name if c.isalnum() or c in "-_").lower()
    return _get_collections_dir() / f"{safe}.json"


def init_defaults() -> None:
    """Copy built-in collections to user data directory on first run."""
    if not DEFAULT_COLLECTIONS_DIR.exists():
        return
    for src in DEFAULT_COLLECTIONS_DIR.glob("*.json"):
        dst = _collection_path(src.stem)
        if not dst.exists():
            shutil.copy2(src, dst)


def list_collections() -> list[dict[str, Any]]:
    """Return metadata for every stored collection."""
    init_defaults()
    collections = []
    for path in sorted(_get_collections_dir().glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        collections.append({
            "name": data.get("name", path.stem),
            "title": data.get("title", path.stem),
            "description": data.get("description", ""),
            "quote_count": len(data.get("quotes", [])),
            "last_synced": data.get("last_synced"),
            "source_url": data.get("source_url"),
        })
    return collections


def get_collection(name: str) -> dict[str, Any] | None:
    """Load a single collection by name."""
    init_defaults()
    path = _collection_path(name)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_collection(collection: dict[str, Any]) -> None:
    """Persist a collection to disk."""
    path = _collection_path(collection["name"])
    path.write_text(json.dumps(collection, indent=2, ensure_ascii=False), encoding="utf-8")


def delete_collection(name: str) -> bool:
    """Remove a collection. Returns True if it existed."""
    path = _collection_path(name)
    if path.exists():
        path.unlink()
        return True
    return False


def search_quotes(name: str, query: str) -> list[dict[str, Any]]:
    """Case-insensitive search across quote text and character fields."""
    collection = get_collection(name)
    if collection is None:
        return []
    q = query.lower()
    return [
        quote for quote in collection.get("quotes", [])
        if q in quote.get("text", "").lower()
        or q in (quote.get("character") or "").lower()
        or q in (quote.get("source") or "").lower()
    ]


def random_quote(name: str | None = None) -> dict[str, Any] | None:
    """Return a random quote from the named collection or any collection."""
    init_defaults()
    if name:
        collection = get_collection(name)
        if not collection:
            return None
        quotes = collection.get("quotes", [])
        return random.choice(quotes) if quotes else None

    all_quotes = []
    for path in _get_collections_dir().glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        for q in data.get("quotes", []):
            copied = dict(q)
            copied["_collection"] = data.get("name", path.stem)
            all_quotes.append(copied)
    return random.choice(all_quotes) if all_quotes else None


def get_stats(name: str | None = None) -> dict[str, Any]:
    """Compute statistics for one or all collections."""
    init_defaults()
    if name:
        collection = get_collection(name)
        if not collection:
            return {}
        quotes = collection.get("quotes", [])
        characters = {q.get("character") for q in quotes if q.get("character")}
        return {
            "name": collection.get("name"),
            "title": collection.get("title"),
            "quote_count": len(quotes),
            "character_count": len(characters),
            "last_synced": collection.get("last_synced"),
        }

    total_quotes = 0
    total_collections = 0
    for path in _get_collections_dir().glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        total_quotes += len(data.get("quotes", []))
        total_collections += 1
    return {
        "total_collections": total_collections,
        "total_quotes": total_quotes,
    }


def add_quote(name: str, text: str, character: str | None = None, source: str | None = None) -> bool:
    """Append a new quote to an existing collection."""
    collection = get_collection(name)
    if collection is None:
        return False
    quote = {
        "text": text,
        "character": character,
        "source": source or collection.get("title", name),
        "tags": [],
    }
    collection.setdefault("quotes", []).append(quote)
    collection["last_modified"] = datetime.now(timezone.utc).isoformat()
    save_collection(collection)
    return True
