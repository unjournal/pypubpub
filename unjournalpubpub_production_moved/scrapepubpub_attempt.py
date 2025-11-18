 import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

# The page(s) to start scraping from
START_URLS = [
    "https://unjournal.pubpub.org/evaluation-summary-and-metrics"
]

# Regex to match links of the form:
# https://unjournal.pubpub.org/pub/<anything>/release/1
MATCH_PATTERN = re.compile(r"^https://unjournal\.pubpub\.org/pub/[^/]+/release/1$")

def get_all_links(url):
    """
    Fetch `url`, parse its HTML, and return a list of absolute URLs found in <a href="...">.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    found_links = []
    for link_tag in soup.find_all('a', href=True):
        href = link_tag['href']
        # Convert relative URLs to absolute
        absolute_url = urljoin(url, href)
        found_links.append(absolute_url)

    return found_links

def crawl_for_release_urls(start_urls, match_pattern, max_pages=50):
    """
    Perform a breadth-first crawl starting from `start_urls`.
    Collect all unique links matching `match_pattern`.
    By default, limit to visiting 50 pages total to prevent over-scraping.
    """
    to_visit = list(start_urls)
    visited = set()
    matched_urls = set()

    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue

        visited.add(current_url)
        all_links = get_all_links(current_url)

        for link in all_links:
            # If the link matches the "release/1" pattern, save it
            if match_pattern.match(link):
                matched_urls.add(link)

            # Optionally, add the link to to_visit if it’s within unjournal.pubpub.org
            # so you can keep crawling deeper pages if you want
            if "unjournal.pubpub.org" in link and link not in visited:
                to_visit.append(link)

    return matched_urls

def main():
    matched = crawl_for_release_urls(START_URLS, MATCH_PATTERN, max_pages=50)

    print("Found the following URLs with '/release/1':")
    for url in sorted(matched):
        print(url)
    print(f"Total: {len(matched)}")

if __name__ == "__main__":
    main()

