import pytest, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from subsidy_signal import (collect_signals, filter_by_client, generate_insight,
                             run_signal_collection, log_signal_with_gid)


def test_collect_signals():
    signals = collect_signals()
    assert isinstance(signals, list)
    assert len(signals) > 0


def test_filter_phoenix():
    signals = collect_signals()
    filtered = filter_by_client(signals, "phoenix")
    assert len(filtered) > 0
    assert all("urgency" in s for s in filtered)


def test_generate_insight():
    signals = collect_signals()
    insight = generate_insight(signals, "phoenix")
    assert "status" in insight
    assert "timestamp" in insight


def test_insight_has_gid_log():
    insight = {
        "tenant_id": "phoenix", "status": "SIGNAL_DETECTED",
        "timestamp": "2026-06-01T00:00:00", "suggested_workflow": "gengrant",
    }
    log_signal_with_gid(insight, gid="GID-TEST000001")
    log_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "signals", "signal_audit_log.jsonl"
    )
    assert os.path.exists(log_path)


def test_gid_in_audit_log():
    log_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "signals", "signal_audit_log.jsonl"
    )
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            lines = f.readlines()
        entry = json.loads(lines[-1].strip())
        assert "gid" in entry
        assert entry["gid"].startswith("GID-")


def test_run_collection():
    result = run_signal_collection("phoenix")
    assert result["tenant_id"] == "phoenix"
    assert "gid" in result
