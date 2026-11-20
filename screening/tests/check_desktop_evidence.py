"""Compare actual desktop design-call dictionaries with the imported fixtures.

This checks the backend boundary. Screenshots and UI observations are separate
evidence; this script does not claim that every displayed value was inspected.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/desktop"
results = []
fixtures = {20: "D02-custom20", 25: "D03-custom25", 30: "D04-custom30"}
for folder in sorted(OUT.glob("run-*")):
    metadata_path = folder / "metadata.json"
    if not metadata_path.exists():
        continue
    metadata = json.loads(metadata_path.read_text())
    before = json.loads((folder / "input-before.osi").read_text())
    span = before.get("geometry.span")
    row = {"run": folder.name, "status": metadata["status"], "span_m": span}
    if span in fixtures:
        expected = json.loads((ROOT / "evidence/designs-verified" / fixtures[span] / "input.osi").read_text())
        keys = [k for k in expected if k.startswith("material.") or k in (
            "geometry.span", "geometry.carriageway_width", "geometry.skew_angle",
            "geometry.design_mode", "geometry.footpath", "geometry.include_median")]
        row["fixture_checks"] = [
            {"key": k, "expected": expected[k], "actual": before.get(k),
             "match": before.get(k) == expected[k]} for k in sorted(keys)]
    output_path = folder / "output.json"
    if output_path.exists():
        output = json.loads(output_path.read_text())
        row["output_span_matches_input"] = output.get("geometry.span") == span
        row["utilization"] = {k: v for k, v in output.items() if k.startswith("util.")}
    results.append(row)
report = {"method": "Actual desktop design-call input/output audit; no solver mocks",
          "runs": results, "completed": sum(r["status"] == "COMPLETED" for r in results)}
(OUT / "comparison.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({"runs": len(results), "completed": report["completed"]}))
