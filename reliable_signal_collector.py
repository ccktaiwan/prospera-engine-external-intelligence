"""
reliable_signal_collector.py | R4b | v1.1
Reliable signal collection using publicly accessible RSS/XML feeds.
Falls back gracefully to structured mock data.
"""
import urllib.request, json, datetime, os, re

# Publicly accessible feeds with better availability
RELIABLE_SOURCES = [
    {
        "name": "Taiwan Open Data - Government Subsidies",
        "url": "https://data.gov.tw/api/v2/rest/datastore/355000000A-000153-001?limit=5",
        "type": "json_api",
        "tags": ["subsidy", "government", "SME"],
        "timeout": 10
    },
    {
        "name": "ITRI News RSS",
        "url": "https://www.itri.org.tw/rss/NewsList_RSS.aspx",
        "type": "rss",
        "tags": ["technology", "innovation", "digital"],
        "timeout": 8
    },
    {
        "name": "NDC Open Data",
        "url": "https://www.ndc.gov.tw/Content_List.aspx?n=72&rss=1",
        "type": "rss",
        "tags": ["policy", "development", "economy"],
        "timeout": 8
    }
]

MOCK_SIGNALS = [
    {"name": "中小企業數位轉型補助計畫 2026", "deadline": "2026-07-31",
     "relevance_tags": ["health","consulting","digital","SME"], "source": "mock_structured",
     "source_name": "Structured Mock", "scraped_at": datetime.datetime.utcnow().isoformat()},
    {"name": "健康產業創新研發補助", "deadline": "2026-08-15",
     "relevance_tags": ["health","phoenix","aging"], "source": "mock_structured",
     "source_name": "Structured Mock", "scraped_at": datetime.datetime.utcnow().isoformat()},
    {"name": "企業 AI 導入輔導計畫", "deadline": "2026-09-30",
     "relevance_tags": ["AI","digital","consulting"], "source": "mock_structured",
     "source_name": "Structured Mock", "scraped_at": datetime.datetime.utcnow().isoformat()},
    {"name": "品牌行銷數位化補助", "deadline": "2026-10-31",
     "relevance_tags": ["brand","marketing","digital"], "source": "mock_structured",
     "source_name": "Structured Mock", "scraped_at": datetime.datetime.utcnow().isoformat()},
]

def try_fetch(source: dict) -> list:
    """Attempt to fetch from a source, return empty list on failure."""
    try:
        req = urllib.request.Request(
            source["url"],
            headers={"User-Agent": "Mozilla/5.0 (compatible; ProsperaBot/1.1)"},
        )
        with urllib.request.urlopen(req, timeout=source.get("timeout", 8)) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
        
        if source["type"] == "json_api":
            data = json.loads(content)
            results = data.get("result", {}).get("records", [])
            return [{"name": str(r)[:60], "source_name": source["name"],
                    "relevance_tags": source["tags"], "source": "real_json",
                    "deadline": (datetime.datetime.utcnow() + datetime.timedelta(days=60)).strftime("%Y-%m-%d"),
                    "scraped_at": datetime.datetime.utcnow().isoformat()} for r in results[:3]]
        
        elif source["type"] == "rss":
            items = re.findall(r"<item>(.*?)</item>", content, re.DOTALL)
            results = []
            for item in items[:5]:
                title = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", item)
                if title:
                    t = title.group(1).strip()
                    keywords = ["補助","計畫","申請","輔導","數位","AI","創新","grant"]
                    if any(kw in t for kw in keywords) and len(t) > 5:
                        results.append({"name": t[:60], "source_name": source["name"],
                            "relevance_tags": source["tags"], "source": "real_rss",
                            "deadline": (datetime.datetime.utcnow() + datetime.timedelta(days=60)).strftime("%Y-%m-%d"),
                            "scraped_at": datetime.datetime.utcnow().isoformat()})
            return results
    except Exception as e:
        return []

def collect_reliable_signals() -> tuple:
    """Try all sources, fallback to structured mock."""
    all_results = []
    for source in RELIABLE_SOURCES:
        results = try_fetch(source)
        all_results.extend(results)
    
    if all_results:
        return all_results, "real_feed"
    return MOCK_SIGNALS, "structured_mock"

if __name__ == "__main__":
    signals, source_type = collect_reliable_signals()
    print(f"Source: {source_type} | Count: {len(signals)}")
    for s in signals[:3]:
        print(f"  - {s['name'][:50]} ({s.get('source','?')})")
