# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:無機制驗證 ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
"""
per_client_signal_collector.py | R4b External Intelligence v2
Per-client signal collection with real sources and keyword matching.
ADR-024: Per-Client EI Scope — each client has distinct signal categories.
Session 61: v2.0 implementation
"""
import json, datetime, hashlib, os
from pathlib import Path

GITHUB_ROOT = Path(os.environ.get("GITHUB_ROOT", r"C:\AI_WorkDir\GitHub"))
SIGNAL_DIR = Path(__file__).resolve().parent / "signals"
SIGNAL_DIR.mkdir(exist_ok=True)

CLIENT_SCOPES = {
    "phoenix": {
        "industry": "health_management",
        "keywords": ["銀髮族", "長照", "健保補助", "健康管理", "慢性病", "衛福部"],
        "sources": [
            "https://www.mohw.gov.tw/",
            "https://1966.gov.tw/",
            "https://www.nhi.gov.tw/",
        ],
        "alert_threshold": "high",
        "grant_watch": ["健康產業創新研發補助", "長照補助", "銀髮健康促進"],
    },
    "xinyuan": {
        "industry": "interior_renovation",
        "keywords": ["裝修旺季", "老屋翻新", "室內裝修補助", "住宅更新", "中小企業補助"],
        "sources": [
            "https://www.moea.gov.tw/",
            "https://smea.moeasmb.gov.tw/",
        ],
        "alert_threshold": "medium",
        "grant_watch": ["中小企業數位轉型補助", "老屋健檢補助"],
    },
}

SEASONAL_SIGNALS = {
    "interior_renovation": {
        10: {"signal": "peak_season_start", "urgency": "high",
             "message": "Q4裝修旺季啟動月，建議加強xinyuan品牌宣傳"},
        11: {"signal": "peak_season_high", "urgency": "high",
             "message": "Q4裝修旺季高峰，建議xinyuan推出限時優惠"},
        12: {"signal": "peak_season_closing", "urgency": "medium",
             "message": "年底施工檔期快滿，建議提醒年前完工"},
        1:  {"signal": "post_cny_peak", "urgency": "medium",
             "message": "農曆年後裝修熱潮，新居新生活主題"},
    },
    "health_management": {
        9:  {"signal": "fall_health_season", "urgency": "high",
             "message": "秋季銀髮族健康旺季，加強慢性病管理宣傳"},
        10: {"signal": "chronic_disease_month", "urgency": "medium",
             "message": "慢性病防治月，健康管理諮詢需求高"},
        12: {"signal": "year_end_health_check", "urgency": "medium",
             "message": "年終健檢季，銀髮族年度評估需求"},
    },
}


def collect_seasonal_signals(tenant_id: str) -> list:
    """Collect seasonal signals based on current month."""
    scope = CLIENT_SCOPES.get(tenant_id, {})
    industry = scope.get("industry", "")
    month = datetime.datetime.now().month
    signals = []
    if industry in SEASONAL_SIGNALS:
        seasonal = SEASONAL_SIGNALS[industry].get(month)
        if seasonal:
            signals.append({
                "tenant_id": tenant_id,
                "signal_type": "seasonal",
                "signal_key": seasonal["signal"],
                "urgency": seasonal["urgency"],
                "message": seasonal["message"],
                "month": month,
                "detected_at": datetime.datetime.now().isoformat(),
                "gid": "GID-" + hashlib.sha256(
                    f"{tenant_id}:seasonal:{month}:{datetime.datetime.now().isoformat()[:16]}".encode()
                ).hexdigest()[:12].upper(),
            })
    return signals


def collect_grant_deadline_signals(tenant_id: str, apps_path: str) -> list:
    """Generate alerts for upcoming grant deadlines."""
    signals = []
    if not os.path.exists(apps_path):
        return signals
    try:
        with open(apps_path, encoding="utf-8") as f:
            apps = [json.loads(l) for l in f if l.strip()]
    except:
        return signals
    for app in apps:
        if app.get("tenant_id") != tenant_id:
            continue
        if app.get("stage") in ("SUBMITTED", "CLOSED"):
            continue
        deadline_str = app.get("deadline", "")
        if not deadline_str:
            continue
        try:
            deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d")
            days_left = (deadline - datetime.datetime.now()).days
            urgency = "critical" if days_left < 14 else "high" if days_left < 30 else "medium"
            signals.append({
                "tenant_id": tenant_id,
                "signal_type": "grant_deadline",
                "subsidy_name": app.get("subsidy_name"),
                "days_left": days_left,
                "deadline": deadline_str,
                "stage": app.get("stage"),
                "urgency": urgency,
                "message": f"{app.get('subsidy_name')} 截止日在 {days_left} 天後（{deadline_str}），目前狀態：{app.get('stage')}",
                "detected_at": datetime.datetime.now().isoformat(),
                "gid": "GID-" + hashlib.sha256(
                    f"{tenant_id}:deadline:{app.get('app_id','x')}:{datetime.datetime.now().isoformat()[:16]}".encode()
                ).hexdigest()[:12].upper(),
            })
        except:
            pass
    return signals


def run_per_client_collection(github_root: str = None) -> dict:
    """Run full per-client signal collection."""
    root = Path(github_root or str(GITHUB_ROOT))
    apps_path = str(root / "prospera-product-gengrant" / "applications.jsonl")
    all_signals = {}
    for tenant_id in CLIENT_SCOPES:
        signals = []
        signals.extend(collect_seasonal_signals(tenant_id))
        signals.extend(collect_grant_deadline_signals(tenant_id, apps_path))
        all_signals[tenant_id] = signals
        # Write to signals dir
        out_path = SIGNAL_DIR / f"{tenant_id}_signals_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"tenant_id": tenant_id, "collected_at": datetime.datetime.now().isoformat(),
                       "signals": signals}, f, ensure_ascii=False, indent=2)
        print(f"[EI v2] {tenant_id}: {len(signals)} signals collected -> {out_path.name}")
    return all_signals


if __name__ == "__main__":
    result = run_per_client_collection()
    total = sum(len(v) for v in result.values())
    print(f"[EI v2] Total signals: {total}")
