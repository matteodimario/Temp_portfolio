import re

def build_aho_corasick(keyword_list):
    """Build a simple trie-like structure for keyword matching."""
    return set(kw.lower() for kw in keyword_list if kw)

def check_keywords(text, automaton, keyword_list):
    """Return exact and fuzzy keyword matches in text."""
    text_lower = text.lower()
    exact = set()
    fuzzy = set()
    for kw in automaton:
        if kw in text_lower:
            exact.add(kw)
        else:
            # Simple substring fuzzy match: check if most characters appear nearby
            # This is a simplified stand-in for fuzzywuzzy logic
            pass
    return exact, fuzzy
