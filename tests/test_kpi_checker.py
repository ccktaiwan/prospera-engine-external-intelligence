# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:無機制驗證 ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kpi_checker import check_kpis

def test_kpi_checker_runs():
    result = check_kpis()
    assert "kpi_score" in result
    assert "status" in result
    assert result["status"] in ["HEALTHY", "DEGRADED"]

def test_kpi_score_positive():
    result = check_kpis()
    assert result["kpi_score"] >= 0

def test_kpi_log_created():
    check_kpis()
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kpi_history.jsonl")
    assert os.path.exists(log_path)
