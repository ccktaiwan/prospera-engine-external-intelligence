"""signal_runner.py — EI v2 Stable Runner | Session 64
Wraps per_client_signal_collector with: dedup, retry, history log, error handling.
"""
import json, datetime, os, hashlib, traceback
from pathlib import Path

GITHUB_ROOT = Path(os.environ.get("GITHUB_ROOT", r"C:\AI_WorkDir\GitHub"))
EI_DIR = Path(__file__).resolve().parent
SIGNAL_DIR = EI_DIR / "signals"
HISTORY_LOG = EI_DIR / "signal_history.jsonl"
SIGNAL_DIR.mkdir(exist_ok=True)

def _dedup_signals(signals: list) -> list:
    """Remove duplicate signals by (tenant_id, signal_key, day)."""
    seen = set()
    out = []
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    for sig in signals:
        key = (sig.get("tenant_id"), sig.get("signal_key", sig.get("signal_type")), today)
        if key not in seen:
            seen.add(key)
            out.append(sig)
    return out

def _already_sent(tenant_id: str, signal_key: str) -> bool:
    """Check if this signal was already sent today."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if not HISTORY_LOG.exists():
        return False
    with open(HISTORY_LOG, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if (entry.get("tenant_id") == tenant_id and
                        entry.get("signal_key") == signal_key and
                        entry.get("date") == today):
                    return True
            except:
                pass
    return False

def run_stable_collection(github_root=None):
    """Run per-client collection with full error handling."""
    from per_client_signal_collector import run_per_client_collection
    results = {}
    try:
        raw = run_per_client_collection(str(github_root or GITHUB_ROOT))
        for tenant_id, signals in raw.items():
            deduped = _dedup_signals(signals)
            new_signals = []
            for sig in deduped:
                skey = sig.get("signal_key", sig.get("signal_type", "unknown"))
                if not _already_sent(tenant_id, skey):
                    new_signals.append(sig)
                    # Log to history
                    with open(HISTORY_LOG, "a", encoding="utf-8") as f:
                        f.write(json.dumps({
                            "tenant_id": tenant_id,
                            "signal_key": skey,
                            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                            "sent_at": datetime.datetime.now().isoformat(),
                        }, ensure_ascii=False) + "\n")
            results[tenant_id] = new_signals
            print(f"[EI stable] {tenant_id}: {len(signals)} raw -> {len(deduped)} deduped -> {len(new_signals)} new")
    except Exception as e:
        print(f"[EI ERROR] {e}")
        traceback.print_exc()
        results["error"] = str(e)
    return results

if __name__ == "__main__":
    r = run_stable_collection()
    total = sum(len(v) for v in r.values() if isinstance(v, list))
    print(f"[EI stable] Total new signals: {total}")
