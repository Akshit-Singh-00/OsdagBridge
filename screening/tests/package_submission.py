"""Build a private submission draft; never copy this archive to the public fork."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
resume = ROOT / "private-submission/AkshitSingh_Resume.pdf"
public = ROOT / "output/OsdagBridge_Interim_Evidence.zip"
video = ROOT / "output/OsdagBridge_Demonstration.mp4"
out = ROOT / "output/OsdagBridge_Private_Submission_Draft.zip"
status = {"status": "draft_not_ready_for_final_submission", "resume_included": True,
          "video_included": video.exists(),
          "pending": ["Three desktop design runs and UI/output comparison",
                      "Verified silent demonstration video", "Collaborator invitation",
                      "Final review and screening submission"]}
manifest = {}
with ZipFile(out, "w", ZIP_DEFLATED) as target:
    with ZipFile(public) as source:
        for item in source.infolist():
            data = source.read(item)
            target.writestr(item.filename, data)
            manifest[item.filename] = hashlib.sha256(data).hexdigest()
    additions = {"candidate/AkshitSingh_Resume.pdf": resume.read_bytes(),
                 "submission/private-package-status.json": json.dumps(status, indent=2).encode()}
    if video.exists():
        additions["video/OsdagBridge_Demonstration.mp4"] = video.read_bytes()
    for name, data in additions.items():
        target.writestr(name, data)
        manifest[name] = hashlib.sha256(data).hexdigest()
    target.writestr("submission/private-manifest.json", json.dumps(manifest, indent=2))
with ZipFile(out) as target:
    assert target.testzip() is None
    for name, expected in manifest.items():
        assert hashlib.sha256(target.read(name)).hexdigest() == expected, name
print(f"Verified private draft: {out} ({out.stat().st_size:,} bytes)")
