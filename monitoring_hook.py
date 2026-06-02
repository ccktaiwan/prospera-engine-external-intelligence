"""monitoring_hook.py | R4b | v1.0 | L5 for External Intelligence Engine"""
import os, subprocess, json, datetime, hashlib

MONITOR_PATH = r"C:\AI_WorkDir\GitHub\prospera-agent-orchestrator"
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "execution_log.jsonl")


def generate_gid(tenant_id: str, signal_type: str) -> str:
    raw = f"{tenant_id}:{signal_type}:{datetime.datetime.utcnow().isoformat()[:16]}"
    return "GID-" + hashlib.sha256(raw.encode()).hexdigest()[:12].upper()


def trigger_monitoring(context=None):
    gid = generate_gid(
        (context or {}).get("tenant_id", "unknown"),
        (context or {}).get("signal_type", "signal"),
    )
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "repo": "prospera-engine-external-intelligence",
        "gid": gid,
        "context": context or {},
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    try:
        subprocess.Popen(["python", "monitoring_agent.py"], cwd=MONITOR_PATH)
    except Exception:
        pass
    return gid
