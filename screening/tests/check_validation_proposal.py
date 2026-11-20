"""Test a scoped proposal against actual modules and restore original bytes in finally.

Only the two listed files are temporarily modified. Failing upstream evidence is
preserved; candidate results are separate. Does not commit, push or post issues.
"""
import difflib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "OsdagBridge"
vpath = REPO / "src/osdagbridge/core/bridge_types/plate_girder/validator.py"
opath = REPO / "src/osdagbridge/core/utils/osi_validator.py"
originals = {p: p.read_bytes() for p in (vpath, opath)}


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError("Proposal context did not match exactly once")
    return text.replace(old, new, 1)


v = vpath.read_text(encoding="utf-8")
v = replace_once(v, "from math import isclose, floor, ceil", "from math import isclose, floor, ceil, isfinite")
v = replace_once(v, "        # ── Weight Density (kN/m³)", """        # All three steel member categories share the same property ranges.
        for prefix in ("material.cross_bracing.", "material.end_diaphragm."):
            if key.startswith(prefix):
                canonical = "material.girder." + key[len(prefix):]
                return self.validate_material_inputs(canonical, {canonical: inputs.get(key)})

        # ── Weight Density (kN/m³)""")
v = replace_once(v, """    def _to_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _to_int(self, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None""", """    def _to_float(self, value):
        try:
            number = float(value)
            return number if isfinite(number) else None
        except (TypeError, ValueError, OverflowError):
            return None

    def _to_int(self, value):
        number = self._to_float(value)
        if number is None or not number.is_integer():
            return None
        return int(number)""")
o = opath.read_text(encoding="utf-8")
o = replace_once(o, "        result.is_valid = len(result.errors) == 0", """        # OSI imports must apply the same material ranges as interactive editing.
        steel_fields = {"fy", "fu", "e", "g", "poisson", "thermal", "density"}
        deck_fields = {"fck", "fctm", "ecm", "thermal", "density"}
        for key, value in flat.items():
            parts = key.split(".")
            if len(parts) != 3 or parts[0] != "material" or self._is_missing(value):
                continue
            member, prop = parts[1:]
            is_steel = member in {"girder", "cross_bracing", "end_diaphragm"} and prop in steel_fields
            is_deck = member == "deck" and prop in deck_fields
            if is_steel or is_deck:
                self._run(self._bridge_validator.validate_material_inputs, key, flat, result)

        result.is_valid = len(result.errors) == 0""")
proposed = {vpath: v, opath: o}
fixdir = ROOT / "submission" / "fixes"
fixdir.mkdir(exist_ok=True)
patch = ""
for path, replacement in proposed.items():
    relative = path.relative_to(REPO).as_posix()
    patch += "".join(difflib.unified_diff(path.read_text(encoding="utf-8").splitlines(True),
                                        replacement.splitlines(True), fromfile="a/"+relative,
                                        tofile="b/"+relative))
(fixdir / "validation-proposal.patch").write_text(patch, encoding="utf-8")
try:
    for path, replacement in proposed.items():
        path.write_text(replacement, encoding="utf-8", newline="\n")
    run = subprocess.run([sys.executable, str(ROOT / "tests/run_validation.py"),
                          str(ROOT / "evidence/validation-proposal-results.json")])
finally:
    for path, content in originals.items():
        path.write_bytes(content)
print("Restored the original upstream files byte-for-byte.")
sys.exit(run.returncode)
