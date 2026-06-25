from keyword_matching import *
from helper import *
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque, defaultdict
import sys
import time
import pprint

ALLOWED_DOMAINS = set()
ROBOTS_CACHE = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def crawler(seed_list, pos_keyword_list, neg_keyword_list, max_suburls):
    start_time = time.time()
    visited = {}
    output_pos = {}
    output_neg = {}
    queue = deque(seed_list)
    max_url = max_suburls * len(seed_list)

    while queue and sum(len(v) for v in visited.values()) < max_url:
        url = queue.popleft()
        url_domain = find_domain(url)

        if url_domain in visited and url in visited[url_domain]: 
            continue

        if not is_allowed_by_robots(url):
            print(f"{url} is not allowed by robots.txt")
            continue

        try:
            response = requests.get(url, headers=HEADERS, timeout=5)

            if response.status_code == 429:
                print(f"Skipping {url} due to persistent 429 errors.")
                continue
        
            if "text/html" not in response.headers["Content-Type"]:
                continue
            
            # if maxed out for that specific domain
            if url_domain in visited and len(visited[url_domain]) > max_suburls:
                queue = deque(link for link in queue if urlparse(link).netloc != url_domain)
                continue

            ## extracting keywords ###

            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
                tag.decompose()
            
            text = soup.get_text(separator="\n", strip=True)

            automaton_neg = build_aho_corasick(neg_keyword_list)
            automaton_pos = build_aho_corasick(pos_keyword_list)

            exact_neg, fuzzy_neg = check_keywords(text, automaton_neg, neg_keyword_list)
            negative = exact_neg.union(fuzzy_neg)
            exact_pos, fuzzy_pos = check_keywords(text, automaton_pos, pos_keyword_list)
            positive = exact_pos.union(fuzzy_pos)

            output_neg[url] = list(negative)[:len(neg_keyword_list)] + [''] * (len(neg_keyword_list) - len(negative))
            output_pos[url] = list(positive)[:len(pos_keyword_list)] + [''] * (len(pos_keyword_list) - len(positive))

            if url_domain not in visited:
                visited[url_domain] = set()
            visited[url_domain].add(normalize_url(url))

            ### extracting links ###

            for link in soup.find_all("a", href=True):
                full_link = urljoin(url, link["href"]) # constructs absolute url
                # checks if in domain
                if find_domain(full_link) not in ALLOWED_DOMAINS:
                    continue
                # checks link isn't explicitly a non html file, e.g .doc, .pdf, .jpg etc. 
                if not extension_filtering(full_link):
                    continue
                normalized_link = normalize_url(full_link)
                if find_domain(normalized_link) in visited and full_link in visited[find_domain(normalized_link)]:
                    continue

                queue.append(normalized_link)

        except requests.exceptions.RequestException:
            print(f"Failed to fetch {url}, skipping...")
            continue  
    return output_neg, output_pos
        

def main():
    if len(sys.argv) != 5:
        print("Usage: python crawler.py <seedURLs> <pos_keywords> <neg_keywords> <max_urls>")
        sys.exit(1)

    seed_filename = sys.argv[1]
    seed_list = []
    positive_keyword_filename = sys.argv[2]
    pos_keyword_list = []
    negative_keyword_filename = sys.argv[3]
    neg_keyword_list = []
    max_suburls = int(sys.argv[4])

    with open(seed_filename, "r") as f:
        for line in f:
            seed_url = line.strip()
            seed_list.append(normalize_url(seed_url))
            # create ALLOWED_DOMAINS list based on seed url domains
            ALLOWED_DOMAINS.add(urlparse(seed_url).netloc)

    with open(positive_keyword_filename, "r") as f:
        for line in f:
            pos_keyword_list.append(line.strip())

    with open(negative_keyword_filename, "r") as f:
        for line in f:
            neg_keyword_list.append(line.strip())
    
    output_neg, output_pos = crawler(seed_list, pos_keyword_list, neg_keyword_list, max_suburls)

    with open("output_pos.txt", "w") as f: 
        f.write("Positive output values:\n")
        for key, value_set in output_pos.items():
            f.write(f"{key}: {', '.join(value_set)}\n")  # Convert set to a comma-separated string

    with open("output_neg.txt", "w") as f:
        f.write("Negative output values:\n")
        for key, value_set in output_neg.items():
            f.write(f"{key}: {', '.join(value_set)}\n")

if __name__ == "__main__":
    main()