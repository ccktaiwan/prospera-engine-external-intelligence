# AGENTS.md | prospera-engine-external-intelligence

Ring: R4b External Intelligence Engine
Role: External Intelligence Signal Collector (ADR-017)

## Permitted Actions

PERMIT: collect_signals() / filter_by_client() / generate_insight() / write signals/
BLOCK: execute workflows / modify governance docs / call Task Agents directly
ESCALATE: adding new signal source requires J1 approval

## Signal Pipeline

World → collect_signals() → filter_by_client() → generate_insight() → Decision Layer
