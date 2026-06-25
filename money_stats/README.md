# Money Stats

A self-contained HTML dashboard visualizing statistics from Matt Levine's "Money Stuff" newsletter (2025 data).

## Files

- **index.html** — The dashboard. Open this file directly in a browser (no server needed). All data is embedded in the HTML so it works with the `file://` protocol.
- **newsletter_data.json** — The raw statistics data (also embedded in index.html).
- **parse_emails.py** — Python script that parses the `.mbox` email archive and generates `newsletter_data.json`.

## How to view

Simply open `index.html` in any web browser:

```bash
# macOS
open index.html

# Linux
xdg-open index.html
```

## Data pipeline

1. Export Matt Levine emails as an `.mbox` file (e.g. from Gmail Takeout)
2. Place it in this folder as `matt_levine_emails.mbox`
3. Run `python3 parse_emails.py` to regenerate `newsletter_data.json`
4. Copy the JSON contents into the `<script>` block of `index.html` (or use a local server if you prefer external JSON)

## Why embedded data?

Browsers block `fetch()` requests when opening HTML files directly via `file://` (CORS policy). Embedding the JSON as a JavaScript variable ensures the dashboard renders correctly without needing a local HTTP server.
