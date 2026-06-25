"""Command-line interface for quote_cli."""

import argparse
import sys
from datetime import datetime, timezone
from typing import Any

from quote_cli import __version__
from quote_cli import storage
from quote_cli.extractor import ExtractorError, extract_quotes, fetch_html
from quote_cli.formatter import (
    format_collections,
    format_quote,
    format_quotes,
    format_stats,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quotes",
        description="Universal quote scraper and manager.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  quotes random                          # random quote\n"
            '  quotes search "Kubrick"                # search across all collections\n'
            "  quotes random -c boris                 # random Boris quote\n"
            "  quotes add-collection seinfeld \\\n"
            "    --url https://example.com/quotes \\\n"
            "    --selector blockquote                # scrape a new collection\n"
            "  quotes sync seinfeld                   # re-scrape a collection\n"
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # random
    rand = sub.add_parser("random", help="Show a random quote")
    rand.add_argument("-c", "--collection", help="Collection name")
    rand.add_argument("-f", "--format", choices=["plain", "json", "rich"], default="plain")

    # search
    srch = sub.add_parser("search", help="Search quotes by keyword")
    srch.add_argument("query", help="Search string")
    srch.add_argument("-c", "--collection", help="Limit to a specific collection")
    srch.add_argument("-f", "--format", choices=["plain", "json", "rich"], default="plain")

    # list
    sub.add_parser("list", help="List all collections")

    # add-collection
    add_col = sub.add_parser("add-collection", help="Create a collection from a URL")
    add_col.add_argument("name", help="Unique collection identifier")
    add_col.add_argument("--url", required=True, help="Page to scrape")
    add_col.add_argument("--selector", required=True, help="CSS selector for quote elements")
    add_col.add_argument("--regex", help="Optional regex with named groups 'character' and 'text'")
    add_col.add_argument("--title", help="Human-readable title")
    add_col.add_argument("--description", help="Short description")

    # sync
    sync = sub.add_parser("sync", help="Re-scrape an existing collection")
    sync.add_argument("name", help="Collection name")

    # stats
    stats = sub.add_parser("stats", help="Show statistics")
    stats.add_argument("name", nargs="?", help="Collection name (omit for global stats)")
    stats.add_argument("-f", "--format", choices=["plain", "json"], default="plain")

    # add
    add = sub.add_parser("add", help="Add a quote manually")
    add.add_argument("text", help="Quote text")
    add.add_argument("-c", "--collection", required=True, help="Target collection")
    add.add_argument("--character", help="Attributed character")
    add.add_argument("--source", help="Source attribution")

    # remove-collection
    rm = sub.add_parser("remove-collection", help="Delete a collection")
    rm.add_argument("name", help="Collection name")

    return parser


def _cmd_random(args: argparse.Namespace) -> int:
    quote = storage.random_quote(args.collection)
    if not quote:
        print("No quotes found.", file=sys.stderr)
        return 1
    print(format_quote(quote, args.format))
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    if args.collection:
        quotes = storage.search_quotes(args.collection, args.query)
    else:
        storage.init_defaults()
        quotes = []
        for meta in storage.list_collections():
            quotes.extend(storage.search_quotes(meta["name"], args.query))
    print(format_quotes(quotes, args.format))
    return 0


def _cmd_list(_args: argparse.Namespace) -> int:
    cols = storage.list_collections()
    print(format_collections(cols))
    return 0


def _cmd_add_collection(args: argparse.Namespace) -> int:
    try:
        html = fetch_html(args.url)
        quotes = extract_quotes(html, args.selector, args.regex, args.url)
    except ExtractorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not quotes:
        print("No quotes extracted.", file=sys.stderr)
        return 1

    collection = {
        "name": args.name,
        "title": args.title or args.name,
        "description": args.description or "",
        "source_url": args.url,
        "selector": args.selector,
        "regex": args.regex,
        "last_synced": datetime.now(timezone.utc).isoformat(),
        "quotes": quotes,
    }
    storage.save_collection(collection)
    print(f"Saved '{args.name}' with {len(quotes)} quotes.")
    return 0


def _cmd_sync(args: argparse.Namespace) -> int:
    collection = storage.get_collection(args.name)
    if not collection:
        print(f"Collection '{args.name}' not found.", file=sys.stderr)
        return 1

    url = collection.get("source_url")
    selector = collection.get("selector")
    regex = collection.get("regex")

    if not url or not selector:
        print("Collection is missing source_url or selector.", file=sys.stderr)
        return 1

    try:
        html = fetch_html(url)
        quotes = extract_quotes(html, selector, regex, url)
    except ExtractorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    collection["quotes"] = quotes
    collection["last_synced"] = datetime.now(timezone.utc).isoformat()
    storage.save_collection(collection)
    print(f"Synced '{args.name}' – now {len(quotes)} quotes.")
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    stats = storage.get_stats(args.name)
    if not stats:
        print(f"Collection '{args.name}' not found.", file=sys.stderr)
        return 1
    print(format_stats(stats, args.format))
    return 0


def _cmd_add(args: argparse.Namespace) -> int:
    ok = storage.add_quote(args.collection, args.text, args.character, args.source)
    if not ok:
        print(f"Collection '{args.collection}' not found.", file=sys.stderr)
        return 1
    print("Quote added.")
    return 0


def _cmd_remove_collection(args: argparse.Namespace) -> int:
    if storage.delete_collection(args.name):
        print(f"Removed collection '{args.name}'.")
        return 0
    print(f"Collection '{args.name}' not found.", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    dispatch = {
        "random": _cmd_random,
        "search": _cmd_search,
        "list": _cmd_list,
        "add-collection": _cmd_add_collection,
        "sync": _cmd_sync,
        "stats": _cmd_stats,
        "add": _cmd_add,
        "remove-collection": _cmd_remove_collection,
    }

    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
