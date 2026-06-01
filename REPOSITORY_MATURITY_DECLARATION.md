# REPOSITORY_MATURITY_DECLARATION | prospera-engine-external-intelligence

Ring: R4b External Intelligence Engine
Declared Type: EXECUTION
Declared Level: 3
Declaration Date: 2026-06-01
ADR: ADR-017

## Level 3 Evidence

- subsidy_signal.py v0.2: real API (sme.gov.tw) + mock fallback
- GID binding: every signal collection writes to signal_audit_log.jsonl
- Tests: pytest 6/6
- CI/CD: .github/workflows/ci.yml active
- CONTRACT.md + AGENTS.md present

## Signal Sources

v0.2: sme.gov.tw (real attempt) + mock fallback
v0.3 target: stable real API + structured data parsing

## GID Chain

signal_audit_log.jsonl → audit_bridge → prospera-standard-audit ledger
