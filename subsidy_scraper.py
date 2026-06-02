"""
subsidy_scraper.py | R4b | v0.3
Structured scraping from Taiwan government subsidy sources.
Multiple sources with fallback chain. (ADR-017)
"""
import json
import datetime
import os

try:
    import requests
    from bs4 import BeautifulSoup
    _SCRAPE_AVAILABLE = True
except ImportError:
    _SCRAPE_AVAILABLE = False

SOURCES = [
    {"name": "SME Portal", "url": "https://www.sme.gov.tw/sme/index_en.jsp", "enabled": True},
    {"name": "MOEA News", "url": "https://www.moea.gov.tw/Mns/populace/news/News.aspx?kind=1", "enabled": True},
]

SUBSIDY_KEYWORDS = ["補助", "輔導", "申請", "計畫", "補貼", "補償", "資助", "獎勵"]


def scrape_source(source: dict) -> list:
    results = []
    if not _SCRAPE_AVAILABLE:
        return results
    try:
        resp = requests.get(
            source["url"],
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ProsperaBot/1.0)"},
        )
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in ["h2", "h3", "h4", "li", "a"]:
            items = soup.find_all(tag, limit=10)
            for item in items:
                text = item.get_text(strip=True)
                if len(text) > 10 and any(kw in text for kw in SUBSIDY_KEYWORDS):
                    results.append({
                        "name": text[:60],
                        "source_name": source["name"],
                        "source_url": source["url"],
                        "scraped_at": datetime.datetime.utcnow().isoformat(),
                        "deadline": "2026-12-31",
                        "relevance_tags": ["consulting", "digital", "health"],
                        "source": "real_scrape",
                    })
        return results[:3]
    except Exception:
        return []


def get_subsidies_with_fallback() -> tuple:
    """Returns (subsidies, source_type)"""
    from subsidy_signal import MOCK_SUBSIDIES
    all_real = []
    for source in SOURCES:
        if source["enabled"]:
            results = scrape_source(source)
            all_real.extend(results)
    if all_real:
        return all_real, "real_scrape"
    return MOCK_SUBSIDIES, "mock_fallback"


if __name__ == "__main__":
    subsidies, source_type = get_subsidies_with_fallback()
    print(f"Source: {source_type}")
    print(f"Count: {len(subsidies)}")
    for s in subsidies[:3]:
        print(f"  - {s['name'][:50]}")
