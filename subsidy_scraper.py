"""
subsidy_scraper.py | R4b | v0.4
Multiple Taiwan government subsidy sources with structured output.
"""
import requests, json, datetime, os, re
from bs4 import BeautifulSoup

SOURCES = [
    {
        "name": "MOEA SME Portal",
        "url": "https://www.sme.gov.tw/sme/newslist_en.aspx",
        "enabled": True,
        "tags": ["SME", "digital", "consulting"]
    },
    {
        "name": "Taiwan Government e-service",
        "url": "https://www.gov.tw/News.aspx?n=9&sms=582",
        "enabled": True,
        "tags": ["general", "business"]
    },
    {
        "name": "NSTC Grant",
        "url": "https://www.nstc.gov.tw/base/a/link",
        "enabled": False,
        "tags": ["technology", "research"]
    }
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ProsperaBot/0.4; +https://prospera.ai)"}

def scrape_source(source: dict) -> list:
    if not source.get("enabled"): return []
    results = []
    try:
        resp = requests.get(source["url"], timeout=8, headers=HEADERS)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, "html.parser")
        keywords = ["補助", "輔導", "申請", "計畫", "補貼", "獎勵", "grant", "subsidy"]
        for tag in ["h2", "h3", "h4", "li", "a", "td"]:
            for item in soup.find_all(tag, limit=20):
                text = item.get_text(strip=True)
                if len(text) > 8 and any(kw in text for kw in keywords):
                    results.append({
                        "name": text[:60],
                        "source_name": source["name"],
                        "source_url": source["url"],
                        "scraped_at": datetime.datetime.utcnow().isoformat(),
                        "deadline": estimate_deadline(text),
                        "relevance_tags": source["tags"],
                        "source": "real_scrape"
                    })
        return results[:5]
    except Exception as e:
        return []

def estimate_deadline(text: str) -> str:
    """Try to extract deadline from text, fallback to 90 days."""
    patterns = [
        r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",
        r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
        r"(\d{1,2})月(\d{1,2})日"
    ]
    for p in patterns:
        m = re.search(p, text)
        if m: 
            try:
                g = m.groups()
                if len(g[0]) == 4:
                    return f"{g[0]}-{int(g[1]):02d}-{int(g[2]):02d}"
                else:
                    return f"2026-{int(g[0]):02d}-{int(g[1]):02d}"
            except: pass
    default = datetime.datetime.utcnow() + datetime.timedelta(days=90)
    return default.strftime("%Y-%m-%d")

def get_subsidies_with_fallback() -> tuple:
    """Returns (subsidies, source_type)"""
    all_real = []
    for source in SOURCES:
        if source.get("enabled"):
            results = scrape_source(source)
            all_real.extend(results)
    if all_real:
        return all_real, "real_scrape"
    # Mock fallback
    mock = [
        {"name": "中小企業數位轉型補助計畫", "deadline": "2026-07-31",
         "relevance_tags": ["health","consulting","digital"], "source": "mock",
         "source_name": "Mock", "source_url": "", "scraped_at": datetime.datetime.utcnow().isoformat()},
        {"name": "健康產業創新研發補助", "deadline": "2026-08-15",
         "relevance_tags": ["health","phoenix","aging"], "source": "mock",
         "source_name": "Mock", "source_url": "", "scraped_at": datetime.datetime.utcnow().isoformat()},
    ]
    return mock, "mock_fallback"

if __name__ == "__main__":
    subsidies, source_type = get_subsidies_with_fallback()
    print(f"Source: {source_type} | Count: {len(subsidies)}")
    for s in subsidies[:3]:
        print(f"  - {s['name'][:50]} | deadline: {s['deadline']}")
