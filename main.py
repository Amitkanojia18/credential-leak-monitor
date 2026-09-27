import logging
from config.settings import SOURCES
from core.collector import fetch_source
from core.detector import analyze_text
from core.scorer import score_finding
from core.database import save_finding

# --- Logging setup ---
logging.basicConfig(
    filename="logs/monitor.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def run_monitor():
    logging.info("Monitoring run started.")
    print("Starting credential leak monitor...\n")

    total_findings = 0

    for source in SOURCES:
        url = source["url"]
        print(f"Checking source: {url}")
        logging.info(f"Fetching source: {url}")

        result = fetch_source(source)

        if result is None:
            logging.warning(f"Could not fetch: {url}")
            continue

        finding = analyze_text(
            result["source_url"],
            result["source_type"],
            result["text"]
        )

        if finding is None:
            logging.info(f"No watchlist match: {url}")
            continue

        finding = score_finding(finding)
        saved_id = save_finding(finding)

        if saved_id:
            total_findings += 1
            print(f"  → New finding saved [{finding['severity']}] score={finding['score']}")
            logging.info(f"Saved finding from {url} | severity={finding['severity']} | score={finding['score']}")
        else:
            print(f"  → Duplicate, skipped.")
            logging.info(f"Duplicate skipped: {url}")

    print(f"\nRun complete. {total_findings} new finding(s) saved.")
    logging.info(f"Monitoring run finished. {total_findings} new finding(s) saved.")


if __name__ == "__main__":
    run_monitor()