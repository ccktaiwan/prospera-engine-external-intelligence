# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:無機制驗證 ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
"""
rss_signal_collector.py | R4b | v1.0
RSS/JSON based signal collection from Taiwan government sources.
More reliable than HTML scraping.
"""
import requests, json, datetime, os

RSS_SOURCES = [
    {
        "name": "Executive Yuan News RSS",
        "url": "https://www.ey.gov.tw/Page/A1875BB00B09E424/rss",
        "type": "rss",
        "tags": ["policy", "government", "business"]
    },
    {
        "name": "MOEA Press Release",
        "url": "https://www.moea.gov.tw/MNS/populace/news/json_news.aspx",
        "type": "json",
        "tags": ["economy", "SME", "digital"]
    },
    {
        "name": "SBIR Taiwan",
        "url": "https://www.sbir.org.tw/api/v1/programs",
        "type": "json",
        "tags": ["startup", "innovation", "subsidy"]
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ProsperaBot/1.0)",
    "Accept": "application/rss+xml, application/json, text/xml, */*"
}

def fetch_rss(url: str) -> list:
    """Fetch and parse RSS feed."""
    try:
        resp = requests.get(url, timeout=8, headers=HEADERS)
        if resp.status_code != 200:
            return []
        # Simple RSS parsing without external lib
        import re
        items = re.findall(r"<item>(.*?)</item>", resp.text, re.DOTALL)
        results = []
        for item in items[:5]:
            title_m = re.search(r"<title><![CDATA[(.*?)]]></title>|<title>(.*?)</title>", item)
            title = (title_m.group(1) or title_m.group(2) or "").strip() if title_m else ""
            if len(title) > 5:
                keywords = ["補助","輔導","計畫","申請","補貼","grant","subsidy","數位"]
                if any(kw in title for kw in keywords):
                    results.append({"title": title[:60], "source": "rss"})
        return results
    except:
        return []

def fetch_json_api(url: str) -> list:
    """Fetch JSON API."""
    try:
        resp = requests.get(url, timeout=8, headers=HEADERS)
        if resp.status_code != 200:
            return []
        data = resp.json()
        if isinstance(data, list):
            return [{"title": str(item).get("title","")[:60] if isinstance(item, dict) else str(item)[:60], 
                    "source": "json_api"} for item in data[:5]]
        return []
    except:
        return []

def collect_all_signals() -> tuple:
    """Collect from all RSS/JSON sources."""
    all_results = []
    for source in RSS_SOURCES:
        if source["type"] == "rss":
            results = fetch_rss(source["url"])
        else:
            results = fetch_json_api(source["url"])
        
        for r in results:
            all_results.append({
                "name": r["title"],
                "source_name": source["name"],
                "relevance_tags": source["tags"],
                "source": f"real_{source['type']}",
                "deadline": (datetime.datetime.utcnow() + datetime.timedelta(days=60)).strftime("%Y-%m-%d"),
                "scraped_at": datetime.datetime.utcnow().isoformat()
            })
    
    if all_results:
        return all_results, "real_rss_json"
    return [], "no_data"

if __name__ == "__main__":
    results, source_type = collect_all_signals()
    print(f"Source: {source_type} | Count: {len(results)}")
    for r in results[:3]:
        print(f"  - {r['name'][:50]}")
