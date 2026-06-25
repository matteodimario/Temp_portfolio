"""Web scraping engine for extracting quotes from HTML pages."""

import re
import urllib.robotparser
from typing import Any
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    BeautifulSoup = None  # type: ignore


class ExtractorError(Exception):
    """Raised when extraction fails."""
    pass


def _check_dependencies() -> None:
    if requests is None:
        raise ExtractorError(
            "The 'requests' library is required for scraping. "
            "Install it with: pip install requests"
        )
    if BeautifulSoup is None:
        raise ExtractorError(
            "The 'beautifulsoup4' library is required for scraping. "
            "Install it with: pip install beautifulsoup4"
        )


def _fetch_robots_txt(url: str) -> urllib.robotparser.RobotFileParser | None:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp
    except Exception:
        return None


def fetch_html(url: str, timeout: int = 10, user_agent: str = "quote-cli/0.1.0") -> str:
    """Fetch raw HTML from *url*, respecting robots.txt."""
    _check_dependencies()
    rp = _fetch_robots_txt(url)
    if rp and not rp.can_fetch(user_agent, url):
        raise ExtractorError(f"robots.txt disallows fetching {url}")

    headers = {"User-Agent": user_agent}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ExtractorError(f"Failed to fetch {url}: {exc}") from exc

    content_type = resp.headers.get("Content-Type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        raise ExtractorError(f"Unexpected Content-Type: {content_type}")
    return resp.text


def extract_quotes(
    html: str,
    selector: str,
    regex: str | None = None,
    source_url: str | None = None,
) -> list[dict[str, Any]]:
    """Parse *html* and extract quotes matching *selector*.

    Parameters
    ----------
    html: str
        Raw HTML text.
    selector: str
        CSS selector (e.g. ``blockquote``, ``.quote``, ``div.tweet-text``).
    regex: str | None
        Optional regex with named groups ``character`` and ``text`` to split
        attribution from the raw element text.
    source_url: str | None
        URL the quotes were scraped from.

    Returns
    -------
    list[dict]
        Each dict has ``text``, ``character``, ``source``, and ``tags`` keys.
    """
    _check_dependencies()
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.select(selector)
    if not elements:
        raise ExtractorError(f"Selector '{selector}' matched 0 elements.")

    compiled = re.compile(regex, re.DOTALL) if regex else None
    quotes = []
    seen = set()

    for el in elements:
        raw = el.get_text(separator=" ", strip=True)
        if not raw or raw in seen:
            continue
        seen.add(raw)

        character = None
        text = raw

        if compiled:
            m = compiled.match(raw)
            if m:
                character = (m.group("character").strip() if "character" in m.groupdict() else None)
                text = (m.group("text").strip() if "text" in m.groupdict() else raw)

        quotes.append({
            "text": text,
            "character": character,
            "source": source_url or "scraped",
            "tags": [],
        })

    return quotes
