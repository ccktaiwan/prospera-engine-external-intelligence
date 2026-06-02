"""
subsidy_signal.py | R4b External Intelligence Engine | v0.2
ADR-017: Taiwan government subsidy signal collection.
v0.2: Real API attempt with fallback to mock data + GID audit log.
"""
import json
import datetime
import os
import hashlib

try:
    import requests
    from bs4 import BeautifulSoup
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signals")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "subsidy_signals.json")
GID_LOG_PATH = os.path.join(OUTPUT_DIR, "signal_audit_log.jsonl")

MOCK_SUBSIDIES = [
    {
        "name": "中小企業數位轉型補助計畫",
        "deadline": "2026-07-31",
        "target": ["中小企業", "數位轉型", "AI"],
        "amount": 100000,
        "relevance_tags": ["health", "consulting", "digital"],
        "source": "mock",
    },
    {
        "name": "健康產業創新研發補助",
        "deadline": "2026-08-15",
        "target": ["健康管理", "醫療", "銀髮族"],
        "amount": 200000,
        "relevance_tags": ["health", "phoenix", "aging"],
        "source": "mock",
    },
    {
        "name": "品牌形象升級輔導計畫",
        "deadline": "2026-09-30",
        "target": ["品牌", "中小企業", "行銷"],
        "amount": 50000,
        "relevance_tags": ["brand", "marketing", "consulting"],
        "source": "mock",
    },
]

CLIENT_PROFILES = {
    "phoenix":    {"industry": "health", "tags": ["health", "phoenix", "aging", "consulting"]},
    "exam":       {"industry": "education", "tags": ["education", "digital", "exam"]},
    "consulting": {"industry": "consulting", "tags": ["consulting", "brand", "marketing"]},
}


def fetch_real_subsidies() -> list:
    """Attempt to fetch real subsidies from SME portal. Returns empty list on failure."""
    if not _REQUESTS_AVAILABLE:
        return []
    try:
        resp = requests.get(
            "https://www.sme.gov.tw/sme/index_en.jsp",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ProsperaOS/1.0)"},
        )
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.find_all("a", limit=5)
            results = []
            for item in items:
                text = item.get_text(strip=True)
                if len(text) > 5:
                    results.append({
                        "name": text[:50],
                        "deadline": "2026-12-31",
                        "target": ["中小企業"],
                        "amount": 0,
                        "relevance_tags": ["consulting", "digital"],
                        "source": "real_sme_gov",
                    })
            if results:
                return results
    except Exception:
        pass
    return []



try:
    from rss_signal_collector import collect_all_signals as _collect_rss
    _RSS_AVAILABLE = True
except ImportError:
    _RSS_AVAILABLE = False

def collect_signals() -> list:
    if _RSS_AVAILABLE:
        rss, src = _collect_rss()
        if rss: return rss

    """Collect signals: try real API first, fallback to mock."""
    real = fetch_real_subsidies()
    return real if real else MOCK_SUBSIDIES


def filter_by_client(signals: list, tenant_id: str) -> list:
    profile = CLIENT_PROFILES.get(tenant_id, {"tags": []})
    relevant = []
    for s in signals:
        overlap = set(s.get("relevance_tags", [])) & set(profile["tags"])
        if overlap:
            try:
                days_left = (
                    datetime.datetime.strptime(s["deadline"], "%Y-%m-%d")
                    - datetime.datetime.utcnow()
                ).days
            except Exception:
                days_left = 90
            relevant.append({
                **s,
                "relevance_score": len(overlap),
                "days_until_deadline": days_left,
                "urgency": "HIGH" if days_left < 30 else ("MEDIUM" if days_left < 60 else "LOW"),
            })
    return sorted(relevant, key=lambda x: x["relevance_score"], reverse=True)


def generate_insight(signals: list, tenant_id: str) -> dict:
    filtered = filter_by_client(signals, tenant_id)
    base = {
        "signal_type": "subsidy",
        "source": "taiwan_government_subsidy",
        "tenant_id": tenant_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "data_source": signals[0].get("source", "mock") if signals else "none",
    }
    if not filtered:
        return {**base, "status": "NO_RELEVANT_SIGNAL", "insights": []}
    top = filtered[0]
    return {
        **base,
        "status": "SIGNAL_DETECTED",
        "top_signal": top["name"],
        "urgency": top["urgency"],
        "days_until_deadline": top["days_until_deadline"],
        "recommended_action": "立即申請" if top["urgency"] == "HIGH" else "評估申請",
        "suggested_workflow": "gengrant",
        "insights": filtered[:3],
    }


def log_signal_with_gid(insight: dict, gid: str = None) -> str:
    """Write signal collection event to audit log with GID."""
    if not gid:
        raw = f"{insight.get('tenant_id')}:subsidy:{insight.get('timestamp', '')[:16]}"
        gid = "GID-" + hashlib.sha256(raw.encode()).hexdigest()[:12].upper()
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "source": "external_intelligence",
        "signal_type": "subsidy",
        "tenant_id": insight.get("tenant_id"),
        "status": insight.get("status"),
        "gid": gid,
        "workflow_suggested": insight.get("suggested_workflow"),
        "data_source": insight.get("data_source", "mock"),
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(GID_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return gid


def run_signal_collection(tenant_id: str = "phoenix") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    signals = collect_signals()
    insight = generate_insight(signals, tenant_id)
    gid = log_signal_with_gid(insight)
    insight["gid"] = gid
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(insight, f, ensure_ascii=False, indent=2)
    return insight


if __name__ == "__main__":
    result = run_signal_collection("phoenix")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Data source: {result.get('data_source', 'mock')}")
    print(f"GID: {result.get('gid', 'NO_GID')}")
