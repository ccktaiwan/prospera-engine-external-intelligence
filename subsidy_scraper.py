# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:無機制驗證 ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
"""
subsidy_scraper.py | R4b | v0.4
Multiple Taiwan government subsidy sources with structured output.
"""
import requests, json, datetime, os, re
from bs4 import BeautifulSoup

# 2026-06-14：sme.gov.tw 改版，舊 newslist_en.aspx 已 404；改用現行輔導/補助頁（靜態 HTML，瀏覽器 UA 200）。
SOURCES = [
    {
        "name": "MOEA SME 中小企業輔導計畫",
        "url": "https://www.sme.gov.tw/counseling-tw-2874",
        "enabled": True,
        "tags": ["SME", "digital", "consulting"]
    },
    {
        "name": "MOEA SME 輔導計畫(研發創新)",
        "url": "https://www.sme.gov.tw/counseling-tw-2875",
        "enabled": True,
        "tags": ["innovation", "research", "SME"]
    },
    {
        "name": "NSTC Grant",
        "url": "https://www.nstc.gov.tw/base/a/link",
        "enabled": False,
        "tags": ["technology", "research"]
    }
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def scrape_source(source: dict) -> list:
    if not source.get("enabled"): return []
    results = []
    try:
        resp = requests.get(source["url"], timeout=8, headers=HEADERS)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, "html.parser")
        keywords = ["補助", "輔導", "申請", "計畫", "補貼", "獎勵", "研發", "創新", "貸款", "grant", "subsidy"]
        seen = set()
        for tag in ["h2", "h3", "h4", "li", "a", "td"]:
            for item in soup.find_all(tag, limit=40):
                text = item.get_text(strip=True)
                # 過濾過長 nav 串接（真補助標題多 8-40 字）+ 去重
                if not (8 < len(text) < 40):
                    continue
                hit = [kw for kw in keywords if kw in text]
                # 真補助標題含 1-3 個關鍵字；含 ≥4 個＝導覽選單串接（如「輔導主軸數位轉型研發創新…」），跳過
                if not hit or len(hit) >= 4:
                    continue
                if text in seen:
                    continue
                seen.add(text)
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
