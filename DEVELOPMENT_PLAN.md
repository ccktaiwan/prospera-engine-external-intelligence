<!-- Prospera SYSTEM HEADER (ADR-0032/SBOM) | 性質:idea | 設計:Kevin 架構 | 執行:AI 工具(claude.ai+Claude Code) | 驗證:無機制驗證 | IP:創造性歸 Kevin(發明人), AI 為執行工具 -->
# DEVELOPMENT_PLAN | prospera-engine-external-intelligence
Date: 2026-06-03
Type: ENGINE (EXTERNAL_SIGNAL)
Ring: R4b
Level: L5 (declared)

## Ecosystem Role
世界感知層。Prospera OS 的眼睛。收集政府補助 RSS、台灣開放資料、ITRI 新聞等外部訊號，
偵測機會（補助開放/截止期限）並輸出結構化 Signal 供 consulting + gengrant 消費。
ADR-017: 第一個 External Intelligence PoC 以政府補助 API 為主。

## Real Current Capability
- reliable_signal_collector.py: 3 real sources (Taiwan Open Data API, ITRI RSS, NDC RSS) + 4 mock fallback signals; graceful failure handling
- subsidy_scraper.py: scraper for additional subsidy data
- rss_signal_collector.py: general RSS feed collector
- subsidy_signal.py: signal processing and output formatting
- kpi_checker.py: signal freshness + relevance precision tracking
- monitoring_hook.py: L5 monitoring
- Output: signals/subsidy_signals.json (read by consulting_server.py and application_workflow.py)
- Tests: test_subsidy_signal.py, test_kpi_checker.py

## Gap Analysis
- BIGGEST GAP: No HTTP service endpoint — consuming repos (consulting, gengrant) read signal file directly via hardcoded relative path (brittle coupling)
- No self_evolution.py — cannot adjust source priority or filtering threshold based on relevance feedback
- Signal freshness only guaranteed for mock data — real RSS fetches can fail without detection
- No scheduled execution mechanism — signal collection only runs when manually triggered
- 3 real signal sources are sufficient for PoC but none are Taiwan government grant portals directly

## Next 3 Development Tasks

### Task 1: Add HTTP service endpoint
- What: Create signal_service.py (FastAPI, port 8083) with GET /signals (returns latest signals), POST /collect (triggers fresh collection), GET /health; replace file-path coupling in consulting + gengrant with HTTP call
- Acceptance: python signal_service.py starts on port 8083; GET /signals returns JSON list of current signals; collecting repos updated to call http://localhost:8083/signals
- Session: session_44

### Task 2: Add self_evolution.py for source priority adjustment
- What: Create self_evolution.py that reads signal_relevance_log.jsonl (consumer feedback on signal usefulness), calculates source relevance score, and updates source priority order in reliable_signal_collector.py's RELIABLE_SOURCES list
- Acceptance: After 5 signal usage records, self_evolution.py produces updated source priority order; most-used sources ranked higher
- Session: session_45

### Task 3: Signal freshness monitoring
- What: Add freshness_validator.py that checks each signal's scraped_at timestamp; marks signals older than 24h as STALE; updates signals/signal_health.json with freshness report; integrates with kpi_checker.py
- Acceptance: freshness_validator.py classifies mock signals as FRESH, real signals older than 24h as STALE; kpi_checker.py reports signal_freshness_rate
- Session: session_46
