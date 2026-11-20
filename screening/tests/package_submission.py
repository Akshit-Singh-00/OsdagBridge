"""Build a private submission draft; never copy this archive to the public fork."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
resume = ROOT / "private-submission/AkshitSingh_Resume.pdf"
public = ROOT / "output/OsdagBridge_Evidence.zip"
video = Path("D:/Fossee-runtime/submission/OsdagBridge_Demonstration.mp4")
out = Path("D:/Fossee-runtime/submission/OsdagBridge_Private_Submission.zip")
status = {"status": "prepared_for_candidate_review_and_submission", "resume_included": True,
          "video_included": video.exists(),
          "video_format": "Silent walkthrough of genuine desktop key frames, pauses omitted; not a continuous screencast",
          "pending": ["Final candidate review and screening form submission"]}
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
