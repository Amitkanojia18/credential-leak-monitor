# 🛡️ Credential Leak & Dark Web Mention Monitoring Tool

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![MongoDB Atlas](https://img.shields.io/badge/database-MongoDB%20Atlas-green.svg)](https://www.mongodb.com/atlas)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python-based monitoring system that scans public sources for mentions of
a target organization's domain/emails alongside credential-leak indicators,
scores the severity of each finding, stores it in MongoDB, and generates
digest reports for quick review.

Built to simulate a real-world threat intelligence workflow: **collect →
detect → score → store → report.**

---

## 📑 Table of Contents

1. [The Problem](#-the-problem)
2. [How It Works](#️-how-it-works)
3. [Project Structure](#️-project-structure)
4. [Module Breakdown](#-module-breakdown)
5. [Running It](#-running-it)
6. [Sample Output](#-sample-output)
7. [Key Design Decisions](#-key-design-decisions)
8. [Known Limitations](#️-known-limitations)
9. [Tech Stack](#️-tech-stack)

---

## 🎯 The Problem

Most simple "leak monitor" scripts just search pages for words like
`"breach"` or `"leak"` — which means a Wikipedia article or a random news
story about *any* company gets flagged just as loudly as an actual leaked
credential dump. That's noise, not intelligence.

This tool fixes that by requiring a **watchlist match** (a real mention of
the target's domain/email) *combined with* threat-keyword context before
anything is flagged — and weights severity differently depending on
*where* it was found (a raw paste dump is far more dangerous than a news
article using the same words).

---

## ⚙️ How It Works

````mermaid
flowchart LR
    A[Collector<br/>fetch pages<br/>URL or file] --> B[Detector<br/>watchlist +<br/>keyword scan]
    B --> C[Scorer<br/>severity by<br/>source type]
    C --> D[Database<br/>dedupe +<br/>store]
    D --> E[Summary<br/>digest report]

    style A fill:#4c6ef5,color:#fff
    style B fill:#12b886,color:#fff
    style C fill:#fa5252,color:#fff
    style D fill:#be4bdb,color:#fff
    style E fill:#f59f00,color:#fff
````

1. **Collector** fetches raw text from configured sources (web pages or local files)
2. **Detector** checks for watchlist matches (target domain/email) — if none found, the page is ignored *regardless* of keyword content
3. **Scorer** calculates a severity score, weighted by source type (paste site > GitHub > news)
4. **Database** stores the finding in MongoDB, using a content hash to prevent duplicate entries
5. **Summary** reads stored findings and generates a digest report

---

## 🗂️ Project Structure

````
credential-leak-monitor/
├── config/settings.py     # Watchlist, keywords, sources, scoring weights
├── core/
│   ├── collector.py       # Fetches pages (web or local mock files)
│   ├── detector.py        # Watchlist + keyword detection, context extraction
│   ├── scorer.py          # Severity scoring logic
│   ├── models.py          # Finding data structure
│   └── database.py        # MongoDB storage + hash-based deduplication
├── reports/summary.py     # Digest report generator
├── mock_data/             # Sample "leak" files for controlled testing
├── logs/monitor.log       # Timestamped run history
└── main.py                # Orchestrator — runs the full pipeline
````

---

## 🧩 Module Breakdown

| Module | Responsibility |
|---|---|
| `core/collector.py` | Routes each source to the right fetcher — `requests` + BeautifulSoup for URLs, direct file read for local mock data |
| `core/detector.py` | Normalizes obfuscated text (`domain[.]com` → `domain.com`), checks watchlist matches, extracts threat keywords/emails, builds a context snippet |
| `core/scorer.py` | Converts keyword/email findings into a numeric score, weighted by source type, then maps to a severity label |
| `core/database.py` | Generates a SHA-256 content hash per finding to prevent duplicate storage, saves to MongoDB Atlas |
| `reports/summary.py` | Queries stored findings over a time window and builds a severity/source/watchlist digest |
| `main.py` | Orchestrates the full pipeline across every configured source, with logging at each step |

---

## 🚀 Running It

**1. Install dependencies**
````bash
pip install -r requirements.txt
````

**2. Configure your watchlist** in `config/settings.py`:
````python
WATCHLIST_DOMAINS = ["yourcompany.com"]
WATCHLIST_EMAILS  = ["admin@yourcompany.com"]
````

**3. Add a `.env` file** with your MongoDB Atlas connection string:
````
MONGO_URI=your_connection_string_here
````

**4. Run a scan**
````bash
python main.py
````

**5. Generate a report**
````bash
python -m reports.summary
````

---

## 📊 Sample Output

**Running a scan (multi-target monitoring):**
````
Starting credential leak monitor...

Checking source: mock_data/paste_site_1.txt
  → New finding saved [Critical] score=188
Checking source: mock_data/paste_site_2.txt
Checking source: mock_data/paste_site_3.txt
  → New finding saved [Critical] score=128
Checking source: mock_data/paste_site_4.txt
  → New finding saved [Critical] score=165
Checking source: https://github.com/search?q=novashield.io+password&type=code
  → New finding saved [Medium] score=36

Run complete. 4 new finding(s) saved.
````

**Detecting an obfuscated mention:**
````
Input text: "Selling access: novashield[.]io admin panel + credential dump..."
Result: → New finding saved [Critical] score=165
watchlist_matches: ['novashield.io', 'brightforge.io']
````
This demonstrates the tool correctly normalized `novashield[.]io` → `novashield.io` before matching — a naive substring check would have missed this entirely.

**Generating a digest (across multiple targets):**
````
========================================
  CREDENTIAL LEAK MONITOR — DIGEST
  Last 7 day(s)
========================================
Total findings: 4

By severity:
  Critical  : 3
  High      : 0
  Medium    : 1
  Low       : 0

Top watchlist mentions:
  novashield.io             — 3 mention(s)
  admin@novashield.io       — 1 mention(s)
  brightforge.io            — 2 mention(s)
  support@brightforge.io    — 1 mention(s)

By source type:
  paste_site  : 3
  github      : 1
========================================
````

---

## 🧠 Key Design Decisions

| Decision | Why |
|---|---|
| **Watchlist-required detection** | Prevents false positives — a page mentioning "breach" in general is noise unless it's tied to your actual target |
| **Source-type severity weighting** | The same keyword means different things on a paste site vs. a news article |
| **Content-hash deduplication** | Avoids fragile field-by-field duplicate checks that silently break on minor data drift |
| **Context snippets stored** | A finding shows *evidence* (the surrounding text), not just a yes/no match |
| **Text normalization before matching** | Catches common obfuscation (`domain[.]com`, `p4ssw0rd`) that would otherwise slip past simple substring matching |
| **Config-driven sources/keywords** | Adding a new source, target, or keyword never requires touching logic code |

---

## ⚠️ Known Limitations

- The current GitHub source uses HTML scraping of search results, which can echo the search query itself as a false match. **Planned fix:** switch to GitHub's official Code Search API for structured, query-free results.
- Sources are checked sequentially, not in parallel — fine for a handful of sources, would need async fetching to scale.
- **Obfuscation handling is pattern-based, not exhaustive.** The detector normalizes common evasion tricks before matching, but a determined actor could invent new obfuscation the tool doesn't yet recognize (e.g., spaced-out characters, homoglyphs). A production system would use fuzzy/edit-distance matching or ML-based normalization instead of a fixed pattern list.
- This tool monitors **publicly accessible sources only** (paste sites, GitHub, news/advisories) — it does not access dark web marketplaces or anything requiring special access, by design.

---

## 🛠️ Tech Stack

`Python` · `Requests` · `BeautifulSoup4` · `MongoDB (Atlas)` · `PyMongo` · `python-dotenv`