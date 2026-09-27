import re
from config.settings import WATCHLIST_DOMAINS, WATCHLIST_EMAILS, THREAT_KEYWORDS


def find_watchlist_matches(text):
    """Checking if any watchlist domain or email appears in the text."""
    text_lower = text.lower()
    matches = []

    for domain in WATCHLIST_DOMAINS:
        if domain.lower() in text_lower:
            matches.append(domain)

    for email in WATCHLIST_EMAILS:
        if email.lower() in text_lower:
            matches.append(email)

    return matches


def find_threat_keywords(text):
    """Find which threat keywords appear in the text."""
    text_lower = text.lower()
    found = [kw for kw in THREAT_KEYWORDS if kw in text_lower]
    return found


def find_emails(text):
    """Extract all email addresses found in the text."""
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    return re.findall(pattern, text)


def get_context_snippet(text, term, window=60):
    """Grab the surrounding text around the first occurrence of a term."""
    idx = text.lower().find(term.lower())
    if idx == -1:
        return ""

    start = max(0, idx - window)
    end = min(len(text), idx + len(term) + window)
    return text[start:end].strip()


def normalize_text(text):
    """
    Undo common obfuscation patterns used to dodge naive keyword filters.
    """
    text = text.lower()

    # Domain obfuscation: [.]  (dot)  {.}  -> .
    text = re.sub(r"\[\.\]|\(dot\)|\{\.\}", ".", text)

    # Leetspeak-style substitutions in keywords
    text = text.replace("p4ssw0rd", "password")
    text = text.replace("pa$$word", "password")
    text = text.replace("pa$$w0rd", "password")

    return text


def analyze_text(source_url, source_type, text):
    """
    Core detection logic. Returns None if no watchlist match found
    (this is the fix for the false-positive problem).
    """
    text = normalize_text(text) 

    watchlist_matches = find_watchlist_matches(text)

    if not watchlist_matches:
        # No mention of anything we care about — ignore, even if
        # threat keywords are present. This is the key fix.
        return None

    keywords = find_threat_keywords(text)
    emails = find_emails(text)

    # Context snippet anchored on the first watchlist match
    snippet = get_context_snippet(text, watchlist_matches[0])

    return {
        "source_url": source_url,
        "source_type": source_type,
        "watchlist_matches": watchlist_matches,
        "matched_keywords": keywords,
        "emails_found": emails,
        "context_snippet": snippet,
    }