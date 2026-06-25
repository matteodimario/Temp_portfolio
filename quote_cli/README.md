# Quote CLI

A local command-line tool for scraping, managing, and displaying quote collections from any web page. Ships with a curated collection of quotes from the Italian TV series *Boris* as a built-in demo.

This is a personal project intended for local use only.

## Features

- **Scrape any site** – point the tool at a URL + CSS selector and build a local quote library.
- **Search & discover** – full-text search across all your collections.
- **Multiple output formats** – plain text, JSON, or rich terminal panels.
- **Offline-first** – collections are stored locally in `~/.local/share/quote_cli/`.
- **Respectful scraping** – checks `robots.txt` before fetching pages.

## Requirements

- Python 3.10+
- `requests`
- `beautifulsoup4`

Install dependencies if needed:

```bash
pip install requests beautifulsoup4
```

Optional rich terminal output:

```bash
pip install rich
```

## Quick Start

From the project directory:

```bash
# Random quote (defaults to built-in Boris collection once initialized)
python3 -m quote_cli random

# Search across all collections
python3 -m quote_cli search "Kubrick"

# List your collections
python3 -m quote_cli list

# Scrape a new collection from a web page
python3 -m quote_cli add-collection seinfeld \
  --url "https://example.com/seinfeld-quotes" \
  --selector "blockquote" \
  --title "Seinfeld Quotes"

# Re-scrape a collection later
python3 -m quote_cli sync seinfeld

# Stats
python3 -m quote_cli stats
python3 -m quote_cli stats boris

# Add a quote manually
python3 -m quote_cli add "No soup for you!" -c seinfeld --character "Soup Nazi"

# Remove a collection
python3 -m quote_cli remove-collection seinfeld
```

## Advanced Scraping

If a page embeds character attribution inside the same element, you can split it with a regex:

```bash
python3 -m quote_cli add-collection got \
  --url "https://example.com/got-quotes" \
  --selector "div.quote" \
  --regex '(?P<character>[A-Za-z\s]+):\s*"(?P<text>[^"]+)"'
```

The regex must use **named groups** `character` and `text`.

## Commands

| Command | Description |
|---|---|
| `python3 -m quote_cli random [-c NAME]` | Show a random quote |
| `python3 -m quote_cli search QUERY [-c NAME]` | Search by keyword |
| `python3 -m quote_cli list` | List all collections |
| `python3 -m quote_cli add-collection NAME --url URL --selector SELECTOR` | Scrape a new collection |
| `python3 -m quote_cli sync NAME` | Re-scrape an existing collection |
| `python3 -m quote_cli stats [NAME]` | Show statistics |
| `python3 -m quote_cli add TEXT -c NAME [--character CHAR]` | Add a quote manually |
| `python3 -m quote_cli remove-collection NAME` | Delete a collection |

## Data Storage

Collections are stored as JSON files in:

- **Linux/macOS**: `~/.local/share/quote_cli/collections/`
- **Windows**: `%LOCALAPPDATA%/quote_cli/collections/`

Built-in demo collections are copied there on first run.

## Example Output

```bash
$ python3 -m quote_cli random -c boris -f rich
┌─────────────────────────────────────────────────────────┐
│ René Ferretti                                           │
│                                                         │
│ "Aoh dai, c'hai mezz'ora! Non stamo a fà Kubrick!"     │
│                                                         │
│ — Boris                                                 │
└─────────────────────────────────────────────────────────┘
```

## License

MIT
