"""Basic tests for quote_cli components."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from quote_cli import storage
from quote_cli.extractor import extract_quotes
from quote_cli.formatter import format_quote, format_stats


@pytest.fixture(autouse=True)
def _isolate_data_dir(monkeypatch):
    """Use a temporary directory for all test data."""
    with tempfile.TemporaryDirectory() as tmp:
        monkeypatch.setenv("XDG_DATA_HOME", tmp)
        yield


@pytest.fixture
def sample_collection():
    return {
        "name": "test",
        "title": "Test Collection",
        "description": "A test collection.",
        "source_url": "https://example.com",
        "selector": "blockquote",
        "last_synced": None,
        "quotes": [
            {"text": "Hello world", "character": "Alice", "source": "Test", "tags": []},
            {"text": "Goodbye world", "character": "Bob", "source": "Test", "tags": []},
        ],
    }


def test_save_and_get_collection(sample_collection):
    storage.save_collection(sample_collection)
    loaded = storage.get_collection("test")
    assert loaded["title"] == "Test Collection"
    assert len(loaded["quotes"]) == 2


def test_search_quotes(sample_collection):
    storage.save_collection(sample_collection)
    results = storage.search_quotes("test", "hello")
    assert len(results) == 1
    assert results[0]["character"] == "Alice"


def test_random_quote(sample_collection):
    storage.save_collection(sample_collection)
    quote = storage.random_quote("test")
    assert quote["text"] in ["Hello world", "Goodbye world"]


def test_random_quote_any(sample_collection):
    storage.save_collection(sample_collection)
    quote = storage.random_quote()
    assert "_collection" in quote
    assert isinstance(quote["_collection"], str)
    # Ensure original data is not mutated
    loaded = storage.get_collection("test")
    assert "_collection" not in loaded["quotes"][0]


def test_stats(sample_collection):
    storage.save_collection(sample_collection)
    stats = storage.get_stats("test")
    assert stats["quote_count"] == 2
    assert stats["character_count"] == 2


def test_extract_quotes():
    html = """
    <html><body>
    <blockquote>Alice: "Hello world"</blockquote>
    <blockquote>Bob: "Goodbye world"</blockquote>
    </body></html>
    """
    regex = r'(?P<character>[A-Za-z\s]+):\s*"(?P<text>[^"]+)"'
    quotes = extract_quotes(html, "blockquote", regex)
    assert len(quotes) == 2
    assert quotes[0]["character"] == "Alice"
    assert quotes[0]["text"] == "Hello world"


def test_format_quote_plain():
    quote = {"text": "Hello", "character": "Alice", "source": "Test", "tags": []}
    out = format_quote(quote, "plain")
    assert "Hello" in out
    assert "Alice" in out


def test_format_quote_json():
    quote = {"text": "Hello", "character": "Alice", "source": "Test", "tags": []}
    out = format_quote(quote, "json")
    data = json.loads(out)
    assert data["text"] == "Hello"
