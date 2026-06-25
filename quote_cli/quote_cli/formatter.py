"""Output formatters for quotes and collections."""

import json
import shutil
from typing import Any


def _terminal_width() -> int:
    cols, _ = shutil.get_terminal_size(fallback=(80, 24))
    return cols


def _wrap(text: str, width: int) -> str:
    """Simple word-wrap for plain output."""
    lines = []
    current = []
    current_len = 0
    for word in text.split():
        if current_len + len(word) + 1 > width:
            lines.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += len(word) + (1 if current_len else 0)
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def format_quote(quote: dict[str, Any], style: str = "plain") -> str:
    """Render a single quote in the requested style."""
    if style == "json":
        return json.dumps(quote, indent=2, ensure_ascii=False)

    text = quote.get("text", "")
    character = quote.get("character")
    source = quote.get("source")
    collection = quote.pop("_collection", None) if "_collection" in quote else None

    if style == "rich":
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            console = Console()
            display = Text()
            if character:
                display.append(f"{character}\n", style="bold cyan")
            display.append(text, style="white")
            if source:
                display.append(f"\n\n— {source}", style="dim")
            if collection:
                display.append(f"  ({collection})", style="dim italic")
            # Capture the renderable output as string
            with console.capture() as capture:
                console.print(Panel(display, border_style="green"))
            return capture.get()
        except ImportError:
            style = "plain"

    # plain fallback
    width = _terminal_width() - 4
    parts = []
    if character:
        parts.append(f"  {character}")
        parts.append("")
    parts.append(_wrap(text, width))
    if source:
        parts.append(f"\n  — {source}")
    if collection:
        parts.append(f"  ({collection})")
    return "\n".join(parts)


def format_quotes(quotes: list[dict[str, Any]], style: str = "plain") -> str:
    """Render multiple quotes, separated by blank lines."""
    if not quotes:
        return "No quotes found."
    if style == "json":
        return json.dumps(quotes, indent=2, ensure_ascii=False)
    return "\n\n".join(format_quote(q, style) for q in quotes)


def format_collections(collections: list[dict[str, Any]], style: str = "plain") -> str:
    """Render a list of collection metadata."""
    if style == "json":
        return json.dumps(collections, indent=2, ensure_ascii=False)

    if not collections:
        return "No collections found."

    lines = []
    for c in collections:
        name = c.get("name", "?")
        title = c.get("title", name)
        desc = c.get("description", "")
        count = c.get("quote_count", 0)
        synced = c.get("last_synced") or "never"
        lines.append(f"  {title} ({name}) – {count} quotes")
        if desc:
            lines.append(f"    {desc}")
        lines.append(f"    Last synced: {synced}")
    return "\n".join(lines)


def format_stats(stats: dict[str, Any], style: str = "plain") -> str:
    """Render statistics."""
    if style == "json":
        return json.dumps(stats, indent=2, ensure_ascii=False)

    lines = []
    if "total_collections" in stats:
        lines.append(f"  Collections: {stats['total_collections']}")
        lines.append(f"  Total quotes: {stats['total_quotes']}")
    else:
        lines.append(f"  Collection: {stats.get('title', stats.get('name'))}")
        lines.append(f"  Quotes: {stats.get('quote_count', 0)}")
        lines.append(f"  Characters: {stats.get('character_count', 0)}")
        lines.append(f"  Last synced: {stats.get('last_synced') or 'never'}")
    return "\n".join(lines)
