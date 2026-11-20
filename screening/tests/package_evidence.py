"""Package only reviewable source, evidence and report; never runtime caches."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
paths = [ROOT / "README.md"]
for directory in ("tests", "submission", "evidence", "output/pdf"):
    paths += [p for p in (ROOT / directory).rglob("*") if p.is_file()
              and p.suffix not in (".zip", ".pyc") and "__pycache__" not in p.parts
              and p.name not in ("upstream-issues.json", "manifest.json", "full-design-execution.log", "task-brief.txt", "OsdagBridge_Interim_Testing_Report.pdf")
              and not p.relative_to(ROOT).as_posix().startswith("evidence/designs/")]
manifest = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}
manifest_path = ROOT / "submission/manifest.json"
manifest_path.write_text(json.dumps({"status": "executed_evidence_candidate_review", "sha256": manifest}, indent=2), encoding="utf-8")
paths.append(manifest_path)
out = ROOT / "output/OsdagBridge_Evidence.zip"
with ZipFile(out, "w", ZIP_DEFLATED) as z:
    for path in paths:
        z.write(path, path.relative_to(ROOT).as_posix())
with ZipFile(out) as z:
    assert z.testzip() is None
    for name, expected in manifest.items():
        assert hashlib.sha256(z.read(name)).hexdigest() == expected, name
print(f"Verified {len(paths)} files in {out} ({out.stat().st_size:,} bytes)")
