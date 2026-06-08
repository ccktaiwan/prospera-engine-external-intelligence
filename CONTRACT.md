# CONTRACT | prospera-engine-external-intelligence

Ring: R4b External Intelligence Engine
Version: v0.1 (CONTRACT架構版) / 代碼 subsidy_signal.py v0.2 / subsidy_scraper.py v0.4
Date: 2026-06-01
Governing: ADR-017

## 實作狀態（版本對齊事實，2026-06-08）
> CONTRACT 為 v0.1 架構契約，代碼版本 v0.2–v0.4（PoC mock 階段，data_source=mock）。
> GID 0% 驗證（所有 GID 為本地生成 UUID hex，未連接外部身分鏈）。
> signal_audit_log.jsonl 清理：4 筆 GID-TEST000001 已移至 signal_audit_log_test.jsonl（2026-06-08 T0-C）。
> ★ GID 驗證機制待實作（需 prospera-engine-token 連動，邏輯修改 = T0）。

## Role

First External Intelligence signal source.
Collects World Signals, filters by client relevance, generates actionable Insights.
Feeds Decision Layer with World Intent (What/Why).

## Input

`tenant_id: str` — client identifier

## Output

`{signal_type, source, urgency, recommended_action, suggested_workflow, insights[]}`

## Signal Sources (PoC)

Mock data → Real API Phase 2: sme.gov.tw subsidy database

## Boundary

PERMIT: collect signals / filter by client / generate insights / write to signals/
BLOCK: execute workflows / modify governance docs / call Task Agents directly
ESCALATE: new signal source addition requires J1
