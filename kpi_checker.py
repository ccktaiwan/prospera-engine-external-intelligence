"""
kpi_checker.py | prospera-engine-external-intelligence | v1.0
KPI monitoring for engine-external-intelligence
Runs after each execution to verify health against defined KPIs.
"""
import os, json, datetime

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
KPI_LOG = os.path.join(REPO_ROOT, "kpi_history.jsonl")
AUDIT_LOG = os.path.join(REPO_ROOT, "signals/signal_audit_log.jsonl")

def check_kpis() -> dict:
    results = []
    passed = 0
    total = 0
    
    # Check 1: audit log exists and has entries
    total += 1
    if os.path.exists(AUDIT_LOG):
        lines = open(AUDIT_LOG, encoding="utf-8").readlines()
        if lines:
            results.append({"check": "audit_log_active", "status": "PASS", "value": len(lines)})
            passed += 1
        else:
            results.append({"check": "audit_log_active", "status": "FAIL", "value": 0})
    else:
        results.append({"check": "audit_log_exists", "status": "WARN", "value": "not found"})
    
    # Check 2: ECOSYSTEM_ROLE.md exists
    total += 1
    role_file = os.path.join(REPO_ROOT, "ECOSYSTEM_ROLE.md")
    if os.path.exists(role_file):
        results.append({"check": "ecosystem_role_defined", "status": "PASS"})
        passed += 1
    else:
        results.append({"check": "ecosystem_role_defined", "status": "FAIL"})
    
    # Check 3: REPOSITORY_MATURITY_DECLARATION level
    total += 1
    decl_file = os.path.join(REPO_ROOT, "REPOSITORY_MATURITY_DECLARATION.md")
    if os.path.exists(decl_file):
        content = open(decl_file, encoding="utf-8").read()
        import re
        m = re.search(r"Declared Level:\s*(\d+)", content)
        level = int(m.group(1)) if m else 0
        if level >= 5:
            results.append({"check": "maturity_level", "status": "PASS", "value": level})
            passed += 1
        else:
            results.append({"check": "maturity_level", "status": "FAIL", "value": level})
    else:
        results.append({"check": "maturity_declared", "status": "FAIL"})
    
    # Check 4: CONTRACT.md exists
    total += 1
    if os.path.exists(os.path.join(REPO_ROOT, "CONTRACT.md")):
        results.append({"check": "contract_defined", "status": "PASS"})
        passed += 1
    else:
        results.append({"check": "contract_defined", "status": "WARN"})

    score = round(passed / total * 100, 1) if total else 0
    report = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "repo": "prospera-engine-external-intelligence",
        "kpi_score": score,
        "passed": passed,
        "total": total,
        "status": "HEALTHY" if score >= 75 else "DEGRADED",
        "checks": results
    }
    
    os.makedirs(os.path.dirname(KPI_LOG), exist_ok=True) if os.path.dirname(KPI_LOG) else None
    with open(KPI_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False) + "\n")
    
    return report

if __name__ == "__main__":
    result = check_kpis()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"KPI Score: {result['kpi_score']}% - {result['status']}")
