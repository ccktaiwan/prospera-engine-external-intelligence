import pytest, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from subsidy_signal import collect_signals, filter_by_client, generate_insight, run_signal_collection


def test_collect_signals():
    signals = collect_signals()
    assert isinstance(signals, list)
    assert len(signals) > 0
    assert "name" in signals[0]
    assert "deadline" in signals[0]


def test_filter_by_client_phoenix():
    signals = collect_signals()
    filtered = filter_by_client(signals, "phoenix")
    assert len(filtered) > 0
    assert all("relevance_score" in s for s in filtered)
    assert all("urgency" in s for s in filtered)


def test_generate_insight_structure():
    signals = collect_signals()
    insight = generate_insight(signals, "phoenix")
    assert "signal_type" in insight
    assert "status" in insight
    assert "suggested_workflow" in insight


def test_insight_triggers_gengrant():
    signals = collect_signals()
    insight = generate_insight(signals, "phoenix")
    if insight["status"] == "SIGNAL_DETECTED":
        assert insight["suggested_workflow"] == "gengrant"


def test_run_signal_collection():
    result = run_signal_collection("phoenix")
    assert result["tenant_id"] == "phoenix"
    signal_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "signals", "subsidy_signals.json"
    )
    assert os.path.exists(signal_path)
