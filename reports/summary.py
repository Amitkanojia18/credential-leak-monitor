from collections import Counter
from datetime import datetime, timedelta, timezone
from core.database import findings_collection


def generate_summary(days=7):
    """
    Generate a digest of findings from the last `days` days.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    findings = list(findings_collection.find({"detected_at": {"$gte": since}}))

    total = len(findings)

    severity_counts = Counter(f["severity"] for f in findings)

    # Flatten all watchlist matches across findings to find top mentioned domains/emails
    all_matches = []
    for f in findings:
        all_matches.extend(f.get("watchlist_matches", []))
    top_matches = Counter(all_matches).most_common(5)

    # Which sources triggered findings
    source_types = Counter(f["source_type"] for f in findings)

    return {
        "period_days": days,
        "total_findings": total,
        "by_severity": dict(severity_counts),
        "top_watchlist_matches": top_matches,
        "by_source_type": dict(source_types),
    }


def print_summary(summary):
    print("=" * 40)
    print(f"  CREDENTIAL LEAK MONITOR — DIGEST")
    print(f"  Last {summary['period_days']} day(s)")
    print("=" * 40)
    print(f"Total findings: {summary['total_findings']}")
    print("\nBy severity:")
    for sev in ["Critical", "High", "Medium", "Low"]:
        count = summary["by_severity"].get(sev, 0)
        print(f"  {sev:<10}: {count}")

    print("\nTop watchlist mentions:")
    if summary["top_watchlist_matches"]:
        for term, count in summary["top_watchlist_matches"]:
            print(f"  {term:<25} — {count} mention(s)")
    else:
        print("  None")

    print("\nBy source type:")
    for src_type, count in summary["by_source_type"].items():
        print(f"  {src_type:<12}: {count}")
    print("=" * 40)


if __name__ == "__main__":
    summary = generate_summary(days=7)
    print_summary(summary)