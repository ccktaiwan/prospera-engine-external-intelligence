# CONTRACT | prospera-engine-external-intelligence

Ring: R4b External Intelligence Engine
Version: v0.1 (PoC)
Date: 2026-06-01
Governing: ADR-017

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
