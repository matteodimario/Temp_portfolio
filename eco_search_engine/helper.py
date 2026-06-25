from urllib.parse import urlparse
from urllib import robotparser
import os

ROBOTS_CACHE = {}

def find_domain(url):
    return urlparse(url).netloc

def normalize_url(url):
    parsed = urlparse(url)
    scheme = parsed.scheme or 'https'
    netloc = parsed.netloc.lower()
    path = parsed.path
    if not path.endswith('/'):
        path = path + '/'
    return f"{scheme}://{netloc}{path}"

def extension_filtering(url):
    excluded = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.mp4'}
    path = urlparse(url).path.lower()
    return not any(path.endswith(ext) for ext in excluded)

def is_allowed_by_robots(url):
    domain = find_domain(url)
    if domain not in ROBOTS_CACHE:
        rp = robotparser.RobotFileParser()
        rp.set_url(f"https://{domain}/robots.txt")
        try:
            rp.read()
        except Exception:
            pass
        ROBOTS_CACHE[domain] = rp
    return ROBOTS_CACHE[domain].can_fetch("*", url)
