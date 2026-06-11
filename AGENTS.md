<!-- Prospera SYSTEM HEADER (ADR-0032/SBOM) | 性質:doc | 設計:Kevin 架構 | 執行:AI 工具(claude.ai+Claude Code) | 驗證:無機制驗證 | IP:創造性歸 Kevin(發明人), AI 為執行工具 -->
# AGENTS.md | prospera-engine-external-intelligence

Ring: R4b External Intelligence Engine
Role: External Intelligence Signal Collector (ADR-017)

## Permitted Actions

PERMIT: collect_signals() / filter_by_client() / generate_insight() / write signals/
BLOCK: execute workflows / modify governance docs / call Task Agents directly
ESCALATE: adding new signal source requires J1 approval

## Signal Pipeline

World → collect_signals() → filter_by_client() → generate_insight() → Decision Layer
