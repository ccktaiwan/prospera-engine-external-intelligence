"""
subsidy_signal.py | R4b External Intelligence Engine | v0.1 PoC
First External Intelligence signal: Taiwan government subsidies.
ADR-017: Start with government subsidy API, not Google Trends.
"""
import json
import datetime
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signals")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "subsidy_signals.json")

MOCK_SUBSIDIES = [
    {
        "name": "中小企業數位轉型補助計畫",
        "deadline": "2026-07-31",
        "target": ["中小企業", "數位轉型", "AI"],
        "amount": 100000,
        "relevance_tags": ["health", "consulting", "digital"],
    },
    {
        "name": "健康產業創新研發補助",
        "deadline": "2026-08-15",
        "target": ["健康管理", "醫療", "銀髮族"],
        "amount": 200000,
        "relevance_tags": ["health", "phoenix", "aging"],
    },
    {
        "name": "品牌形象升級輔導計畫",
        "deadline": "2026-09-30",
        "target": ["品牌", "中小企業", "行銷"],
        "amount": 50000,
        "relevance_tags": ["brand", "marketing", "consulting"],
    },
]

CLIENT_PROFILES = {
    "phoenix": {"industry": "health", "tags": ["health", "phoenix", "aging", "consulting"]},
    "exam": {"industry": "education", "tags": ["education", "digital", "exam"]},
    "consulting": {"industry": "consulting", "tags": ["consulting", "brand", "marketing"]},
}


def collect_signals() -> list:
    """Collect subsidy signals. Uses mock data for PoC (ADR-017 Phase 1)."""
    return MOCK_SUBSIDIES


def filter_by_client(signals: list, tenant_id: str) -> list:
    """Filter signals relevant to specific client."""
    profile = CLIENT_PROFILES.get(tenant_id, {"tags": []})
    relevant = []
    for s in signals:
        overlap = set(s["relevance_tags"]) & set(profile["tags"])
        if overlap:
            deadline_dt = datetime.datetime.strptime(s["deadline"], "%Y-%m-%d")
            days_left = (deadline_dt - datetime.datetime.utcnow()).days
            relevant.append({
                **s,
                "relevance_score": len(overlap),
                "days_until_deadline": days_left,
                "urgency": "HIGH" if days_left < 30 else ("MEDIUM" if days_left < 60 else "LOW"),
            })
    return sorted(relevant, key=lambda x: x["relevance_score"], reverse=True)


def generate_insight(signals: list, tenant_id: str) -> dict:
    """Convert filtered signals into actionable insight for Decision Layer."""
    filtered = filter_by_client(signals, tenant_id)
    if not filtered:
        return {
            "signal_type": "subsidy", "source": "taiwan_government_subsidy",
            "tenant_id": tenant_id, "timestamp": datetime.datetime.utcnow().isoformat(),
            "status": "NO_RELEVANT_SIGNAL", "insights": [],
        }
    top = filtered[0]
    return {
        "signal_type": "subsidy",
        "source": "taiwan_government_subsidy",
        "tenant_id": tenant_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "status": "SIGNAL_DETECTED",
        "top_signal": top["name"],
        "urgency": top["urgency"],
        "days_until_deadline": top["days_until_deadline"],
        "recommended_action": "立即申請" if top["urgency"] == "HIGH" else "評估申請",
        "suggested_workflow": "gengrant",
        "insights": filtered[:3],
    }


def run_signal_collection(tenant_id: str = "phoenix") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    signals = collect_signals()
    insight = generate_insight(signals, tenant_id)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(insight, f, ensure_ascii=False, indent=2)
    return insight


if __name__ == "__main__":
    result = run_signal_collection("phoenix")
    print(json.dumps(result, ensure_ascii=False, indent=2))
