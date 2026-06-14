# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:無機制驗證 ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
"""
rss_signal_collector.py | R4b | v1.0
RSS/JSON based signal collection from Taiwan government sources.
More reliable than HTML scraping.
"""
import requests, json, datetime, os, urllib.parse

# 2026-06-14：原政府 RSS/JSON 端點全失效（ey.gov.tw SSL、sbir.org.tw 404、moea 回 HTML 非 JSON、皆無 <item>）。
# 改用 Google News RSS（免費、穩定、回真 <item>）作議題放大感測器來源——對應雙向生成 External S4「Google/Yahoo News 議題放大」。
def _gnews(query: str) -> str:
    q = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={q}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"

RSS_SOURCES = [
    {"name": "Google News｜中小企業補助", "url": _gnews("中小企業補助"),
     "type": "rss", "tags": ["subsidy", "SME", "policy"]},
    {"name": "Google News｜數位轉型補助", "url": _gnews("數位轉型 補助 計畫"),
     "type": "rss", "tags": ["digital", "transformation", "subsidy"]},
    {"name": "Google News｜SBIR 研發補助", "url": _gnews("SBIR 研發補助"),
     "type": "rss", "tags": ["innovation", "research", "startup"]},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
        for item in items[:12]:
            # CDATA 的 [ ] 需跳脫（原版 <![CDATA[...]]> 未跳脫→永遠抓空）；兼容純文字 title
            title_m = re.search(r"<title>\s*(?:<!\[CDATA\[(.*?)\]\]>|(.*?))\s*</title>", item, re.DOTALL)
            title = ((title_m.group(1) or title_m.group(2) or "").strip()) if title_m else ""
            if len(title) > 5:
                keywords = ["補助","輔導","計畫","申請","補貼","獎勵","研發","創新","貸款","grant","subsidy","數位","轉型","SBIR"]
                if any(kw in title for kw in keywords):
                    results.append({"title": title[:80], "source": "rss"})
        return results
    except Exception:
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
