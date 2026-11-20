"""Exercise unchanged layout/default expansion with saved before/after evidence."""
import contextlib
import copy
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "OsdagBridge" / "src"))
from osdagbridge.core.bridge_types.plate_girder.defaults import BASIC_INPUT_DICT, solve_extend_basic_input_dict
from osdagbridge.core.utils import common as C

OUT = ROOT / "evidence" / "state"
OUT.mkdir(exist_ok=True)
rows = []


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2), encoding="utf-8")


def result(case, expected, actual, issue=None):
    rows.append({"id": case, "expected": expected, "actual": actual,
                 "status": "PASS" if expected == actual else "FAIL",
                 "related_issue": issue})


inputs = copy.deepcopy(BASIC_INPUT_DICT)
inputs.update({C.KEY_SPAN: 20, C.KEY_CARRIAGEWAY_WIDTH: 7.5, C.KEY_SKEW_ANGLE: 0,
               C.KEY_PROJECT_LOCATION: {"name": "Test fixture", "weather_data": {"z_value": .10}}})
log = io.StringIO()
with contextlib.redirect_stdout(log):
    solve_extend_basic_input_dict(inputs)
    save("baseline-input.osi", inputs)
    n = inputs[C.KEY_TS_NO_OF_GIRDERS]
    width = inputs[C.KEY_TS_OVERALL_WIDTH]
    implied = (n - 1) * inputs[C.KEY_TS_GIRDER_SPACING] + 2 * inputs[C.KEY_TS_DECK_OVERHANG]
    result("S-layout-width-closure", round(width, 9), round(implied, 9))
    result("S-minimum-girders", True, n >= 2)

    # This operation is used by the application's save/recompute paths.
    overrides = {C.KEY_TS_DECK_THICKNESS: 300., C.KEY_WC_THICKNESS: 80.,
                 C.KEY_MATERIAL_GIRDER_E: 210., C.KEY_MATERIAL_GIRDER_FY: 355.,
                 C.KEY_MATERIAL_GIRDER_DENSITY: 80., C.KEY_MATERIAL_DECK_FCK: 45.,
                 C.KEY_MATERIAL_DECK_DENSITY: 24.}
    inputs.update(overrides)
    save("custom-before-expand.osi", inputs)
    solve_extend_basic_input_dict(inputs)
    save("custom-after-expand.osi", inputs)
    for key, value in overrides.items():
        result("S-preserve-" + key, value, inputs.get(key), 71 if key in (C.KEY_TS_DECK_THICKNESS, C.KEY_WC_THICKNESS) else None)

    # Actual layout expansions, not full design runs. The report must distinguish these.
    for span in (25., 30.):
        inputs[C.KEY_SPAN] = span
        solve_extend_basic_input_dict(inputs)
        save(f"span-{int(span)}-after-expand.osi", inputs)
        for gi in range(1, n + 1):
            segments = inputs[C.KEY_MP_GD_SEGMENT_TABLE + f".G{gi}"]
            result(f"S-span-{int(span)}-G{gi}-end", span, segments[-1]["end"], 125)

    # Shrinking the girder count should remove inactive component keys consistently.
    inputs[C.KEY_TS_NO_OF_GIRDERS] = 2
    solve_extend_basic_input_dict(inputs)
    save("two-girders-after-expand.osi", inputs)
    for component in ("girder_details", "stiffener_details", "cross_bracing_details", "end_diaphragm_details"):
        stale = [k for k in inputs if k.startswith("member_properties." + component + ".")
                 and any(f"G{i}" in k for i in range(3, n + 1))]
        result("S-remove-inactive-" + component, [], stale)

(OUT / "execution.log").write_text(log.getvalue(), encoding="utf-8")
save("results.json", {"method": "Direct calls into unchanged default/layout module, not full analysis or GUI",
                       "passed": sum(r["status"] == "PASS" for r in rows),
                       "failed": sum(r["status"] == "FAIL" for r in rows), "cases": rows})
for r in rows:
    print(r["status"], r["id"], "expected=", r["expected"], "actual=", r["actual"])
sys.exit(1 if any(r["status"] == "FAIL" for r in rows) else 0)
