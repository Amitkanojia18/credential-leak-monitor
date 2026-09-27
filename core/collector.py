import requests
from bs4 import BeautifulSoup


def fetch_from_url(url):
    """Fetch and parse a real web page."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    return text


def fetch_from_file(path):
    """Read a local mock text file (simulates a paste-site dump)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return text
    except FileNotFoundError:
        print(f"File not found: {path}")
        return None


def fetch_source(source):
    """
    Decide how to fetch based on the source's URL.
    source = {"url": ..., "type": ...} from config.SOURCES
    """
    url = source["url"]

    if url.startswith("http://") or url.startswith("https://"):
        text = fetch_from_url(url)
    else:
        text = fetch_from_file(url)

    if text is None:
        return None

    return {
        "source_url": url,
        "source_type": source["type"],
        "text": text
    }