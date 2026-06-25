# Author

### imports
import sys
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import deque
import time

start = time.time()

### header to avoid 403 requests
headers = {'User-agent': 'Mozilla/5.0'}

### normalize url
def normalize_url(url):
    parsed = urlparse(url)
    # normalize scheme and domain to lowercase, remove fragment and query
    parsed = parsed._replace(scheme='https', fragment='', query='')
    normalized = parsed.geturl().lower()
    # ensure http is replaced with https
    if normalized.startswith('http://'):
        normalized = normalized.replace('http://', 'https://', 1)
    return normalized

### identify allowed domain
def is_allowed_domain(url, allowed_domains):
    domain = urlparse(url).netloc
    return domain in allowed_domains

### crawler function
def crawler(seed_file, max_urls):
    ## set-up the crawling
    # allowed domains
    allowed_domains = {'eecs.umich.edu', 'eecs.engin.umich.edu', 'ece.engin.umich.edu', 'cse.engin.umich.edu'}
    # open file with urls
    with open(seed_file, 'r') as f:
        seed_urls = [normalize_url(line.strip()) for line in f]
    # initialize variables
    queue = deque(seed_urls)
    identified = set()
    visited = set()
    links = []
    # initialize identified set with seed URLs
    for url in seed_urls:
        # if you want to restrict to certain domains
        # if is_allowed_domain(url, allowed_domains):
        identified.add(url)
    # check urls do not exceed max_urls
    if len(identified) > max_urls:
        identified = set(list(identified)[:max_urls])
        queue = deque()
    ## main crawling algorithm
    # open output files
    with open('crawler.output', 'w') as crawler_out, open('links.output', 'w') as links_out:
        crawler_out.write("Author \n \n")
        # write seed URLs to crawler.output first
        for url in seed_urls:
            if url in identified:
                crawler_out.write(url + '\n')
        # loop until the required number of urls is met or the queue runs out of urls
        while queue and len(identified) < max_urls:
            current_url = queue.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)
            try:
                # store response
                response = requests.get(current_url, allow_redirects=True, timeout=10, headers=headers)
                final_url = normalize_url(response.url)
                # check if it is an allowed domain
                if not is_allowed_domain(final_url, allowed_domains):
                    continue
                # check if final url should be added
                if final_url not in identified:
                    identified.add(final_url)
                    crawler_out.write(final_url + '\n')
                    if len(identified) >= max_urls:
                        break
                # process only if HTML
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    continue
                ## use BeautifulSoup to parse
                soup = BeautifulSoup(response.text, 'html.parser')
                # find outgoing links in the current url
                for link in soup.find_all('a', href=True):
                    # normalize the url link
                    href = link['href']
                    absolute_url = urljoin(final_url, href)
                    normalized_link = normalize_url(absolute_url)
                    # check if link is in the allowed domain
                    if not is_allowed_domain(normalized_link, allowed_domains):
                        continue
                    # add link
                    links.append((final_url, normalized_link))
                    # write pair of links to links.output
                    links_out.write(f'({final_url}, {normalized_link})\n')
                    # check if link has to be added to crawler.output
                    if normalized_link not in identified and normalized_link not in queue:
                        # check if the max number of url has been reached
                        if len(identified) < max_urls:
                            # add link to queue and identified, and write to crawler.output
                            identified.add(normalized_link)
                            crawler_out.write(normalized_link + '\n')
                            queue.append(normalized_link)
                        else:
                            break
            # error check
            except Exception as e:
                print(f"Error fetching {current_url}: {e}")
            # check if max_urls has been reached
            if len(identified) >= max_urls:
                break
    end = time.time()
    elapsed_time = end - start
    print(elapsed_time)

### main
if __name__ == "__main__":
    # check for an error in the command line
    if len(sys.argv) != 3:
        print("The command line does not have the correct number of arguments")
        sys.exit(1)
    seed_name = sys.argv[1]
    max_urls = int(sys.argv[2])
    seed_file = seed_name
    # main function for the crawling
    crawler(seed_file, max_urls)