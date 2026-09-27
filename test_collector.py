from core.collector import fetch_source
from core.detector import analyze_text
from core.scorer import score_finding
from core.database import save_finding, findings_collection



for path in ["mock_data/paste_site_1.txt", "mock_data/paste_site_2.txt"]:
    result = fetch_source({"url": path, "type": "paste_site"})
    finding = analyze_text(result["source_url"], result["source_type"], result["text"])

    print(f"\n--- {path} ---")

    if finding is None:
        print("No watchlist match — skipping scoring.")
        continue

    finding = score_finding(finding)
    # after finding = score_finding(finding) for paste_site_1:
    result = save_finding(finding)
    print("Saved with ID:" if result else "Duplicate, not saved:", result)
    print(finding)


doc = findings_collection.find_one({"source_url": "mock_data/paste_site_4.txt"})
print(doc)