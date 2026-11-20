"""Black-box checks of the actual upstream validator; no stubs or source extraction.

Run: python tests/run_validation.py
Exit 1 means a behavior under test violates the stated expectation. Each row
records that expectation and the actual return/exception, including known bugs.
"""
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "OsdagBridge" / "src"))
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.utils.osi_validator import validate_osi_inputs

validator = BridgeInputValidator()
rows = []
base = {"geometry.span": 25.0, "geometry.carriageway_width": 7.5,
        "geometry.skew_angle": 0.0, "geometry.include_median": "No",
        "geometry.design_mode": "Custom"}


def check(case_id, route, key, value, expected_valid, related_issues=()):
    inputs = {**base, key: value}
    row = {"id": case_id, "route": route, "key": key, "value": str(value),
           "expected_valid": expected_valid, "related_issues": list(related_issues)}
    try:
        if route == "osi":
            actual = validate_osi_inputs(inputs)
            valid = actual.is_valid
            row["actual"] = {"valid": valid, "errors": actual.errors,
                             "warnings": actual.warnings}
        else:
            actual = getattr(validator, "validate_" + route + "_inputs")(key, inputs)
            valid = actual is None
            row["actual"] = actual
        row["status"] = "PASS" if valid == expected_valid else "FAIL"
    except Exception as exc:
        row["actual"] = {"exception": type(exc).__name__, "message": str(exc)}
        row["status"] = "FAIL"
    rows.append(row)


for label, val, accepted in [
    ("lower", 20, True), ("upper", 45, True), ("ordinary", 25, True),
    ("numeric_string", "25", True), ("below", 19.9, False),
    ("above", 45.1, False), ("zero", 0, False), ("negative", -1, False),
    ("nonnumeric", "abc", False), ("blank", "", False),
    ("nan", float("nan"), False), ("inf", float("inf"), False),
]:
    for route in ("basic", "osi"):
        related = [88] if label == "nan" else ([67] if label == "blank" else [])
        # OSI deliberately permits incomplete drafts; Design validates required fields.
        route_accepted = True if route == "osi" and label == "blank" else accepted
        check(f"V-span-{route}-{label}", route, "geometry.span", val, route_accepted, related)

for member in ("girder", "cross_bracing", "end_diaphragm"):
    for label, val, accepted in [("ordinary", 350, True), ("negative", -10, False),
                                  ("above", 1500, False), ("nan", float("nan"), False)]:
        key = f"material.{member}.fy"
        check(f"V-material-{member}-{label}", "material", key, val, accepted,
              [129] if member != "girder" else [])
        check(f"V-osi-material-{member}-{label}", "osi", key, val, accepted, [96])

for key, valid_value, invalid_value in [
    ("material.deck.fck", 40, -1), ("material.deck.density", 24, 100),
    ("material.deck.ecm", 35, 1), ("material.girder.poisson", .3, .8),
    ("material.girder.density", 78.5, 1),
]:
    for label, val, accepted in [("ordinary", valid_value, True), ("invalid", invalid_value, False)]:
        check(f"V-{key}-{label}", "material", key, val, accepted)
        check(f"V-osi-{key}-{label}", "osi", key, val, accepted, [96])

for val in (float("inf"), float("-inf"), 2.5, 0):
    check("V-girders-" + str(val), "additional", "typical_section.no_of_girders", val, False, [130])

result = {
    "executed_at_utc": datetime.now(timezone.utc).isoformat(),
    "python": sys.version, "platform": platform.platform(),
    "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT / "OsdagBridge", text=True).strip(),
    "method": "Direct calls into unchanged upstream validator modules; no GUI actions",
    "passed": sum(r["status"] == "PASS" for r in rows),
    "failed": sum(r["status"] == "FAIL" for r in rows), "cases": rows,
}
path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "evidence" / "validation-results.json"
path.write_text(json.dumps(result, indent=2, ensure_ascii=True), encoding="utf-8")
print(f"{len(rows)} checks: {result['passed']} passed, {result['failed']} failed")
print(path)
for row in rows:
    if row["status"] == "FAIL":
        print(row["id"], json.dumps(row["actual"], ensure_ascii=True))
sys.exit(1 if result["failed"] else 0)
