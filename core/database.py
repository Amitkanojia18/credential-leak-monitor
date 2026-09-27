import hashlib
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["credential_leak_monitor"]
findings_collection = db["findings"]


def generate_content_hash(finding):
    """
    Create a unique fingerprint for a finding based on its actual content,
    not on separately comparing fragile fields.
    """
    raw = (
        finding["source_url"]
        + "".join(sorted(finding["watchlist_matches"]))
        + "".join(sorted(finding["matched_keywords"]))
        + "".join(sorted(finding["emails_found"]))
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def finding_exists(content_hash):
    """Check if this exact finding was already stored."""
    return findings_collection.find_one({"content_hash": content_hash}) is not None


def save_finding(finding):
    """Save a finding to MongoDB, avoiding duplicates."""
    content_hash = generate_content_hash(finding)

    if finding_exists(content_hash):
        return None  # already stored, skip

    finding["content_hash"] = content_hash
    finding["detected_at"] = datetime.now(timezone.utc)

    result = findings_collection.insert_one(finding)
    return result.inserted_id