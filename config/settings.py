WATCHLIST_DOMAINS = ["novashield.io", "brightforge.io"]
WATCHLIST_EMAILS = ["admin@novashield.io", "support@brightforge.io"]

# Threat keywords: words that make a watchlist match meaningful
THREAT_KEYWORDS = [
    "breach",
    "leak",
    "leaked",
    "dump",
    "credential",
    "credentials",
    "exposed",
    "password",
    "stealer",
]

# Sources to monitor, each tagged with a type
SOURCES = [
    {"url": "mock_data/paste_site_1.txt", "type": "paste_site"},
    {"url": "mock_data/paste_site_2.txt", "type": "paste_site"},
    {"url": "mock_data/paste_site_3.txt", "type": "paste_site"},
    {"url": "mock_data/paste_site_4.txt", "type": "paste_site"},
    {"url": "https://github.com/search?q=novashield.io+password&type=code", "type": "github"},
]

# --- Severity weight multiplier per source type ---
SOURCE_TYPE_WEIGHT = {
    "paste_site": 1.5,   # raw dumps — high signal
    "github": 1.2,       # accidental leaks — high signal
    "news": 0.5,         # just discussion — low signal
    "advisory": 0.3,     # official bulletins — lowest signal
}