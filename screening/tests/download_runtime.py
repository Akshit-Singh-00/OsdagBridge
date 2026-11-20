"""Download the solved Conda artifacts in resumable, checksum-verified parts.

Uses only URLs from Micromamba's package plan, with the documented conda-forge
mirror substitution. It does not install packages or execute downloaded code.
"""
import argparse
import concurrent.futures as futures
import hashlib
import json
import os
from pathlib import Path
import threading
import time
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--plan", default="evidence/runtime-plan.json")
parser.add_argument("--directory", default="D:/Fossee-runtime/downloads")
parser.add_argument("--workers", type=int, default=12)
args = parser.parse_args()
plan = json.loads(Path(args.plan).read_text(encoding="utf-8-sig"))
records = plan["actions"].get("LINK", plan["actions"].get("FETCH", []))
target = Path(args.directory)
target.mkdir(parents=True, exist_ok=True)
partdir = target / "parts"
partdir.mkdir(exist_ok=True)
CHUNK = 2 * 1024 * 1024
print_lock = threading.Lock()
stats_lock = threading.Lock()
completed_bytes = 0


def say(message):
    with print_lock:
        print(message, flush=True)


def digest(path, algorithm):
    h = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for buf in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()


def matches(path, rec):
    if not path.exists() or path.stat().st_size != rec["size"]:
        return False
    alg = "sha256" if rec.get("sha256") else "md5"
    return digest(path, alg) == rec[alg]


def fetch_part(rec, url, start, end):
    global completed_bytes
    filename = rec.get("fn") or rec["filename"]
    path = partdir / (filename + f".{start:012d}.part")
    length = end - start + 1
    if path.exists() and path.stat().st_size == length:
        return path
    last_error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}", "User-Agent": "FOSSEE-runtime-setup/1.0"})
            with urllib.request.urlopen(request, timeout=45) as response:
                cr = response.headers.get("Content-Range", "")
                expected = f"bytes {start}-{end}/{rec['size']}"
                if response.status == 206 and cr != expected:
                    raise ValueError(f"Unexpected range: {cr!r}, expected {expected!r}")
                if response.status != 206 and not (start == 0 and end + 1 == rec["size"] and response.status == 200):
                    raise ValueError(f"Server did not honor range: HTTP {response.status}")
                data = response.read(length + 1)
            if len(data) != length:
                raise ValueError(f"Short/oversize part: {len(data)} instead of {length}")
            tmp = path.with_suffix(".tmp")
            tmp.write_bytes(data)
            tmp.replace(path)
            with stats_lock:
                completed_bytes += length
            return path
        except Exception as exc:
            last_error = exc
            time.sleep(attempt + 1)
    raise RuntimeError(f"{filename} bytes {start}-{end}: {last_error}")


package_jobs = []
downloaded = []
cache = Path("D:/Fossee-runtime/mamba/pkgs/https")
cache_files = {p.name: p for p in cache.rglob("*") if p.is_file() and p.name.endswith((".conda", ".tar.bz2"))}
with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
    for rec in records:
        filename = rec.get("fn") or rec.get("filename")
        if not filename or Path(filename).name != filename or not filename.endswith((".conda", ".tar.bz2")):
            raise ValueError(f"Unexpected package filename: {filename}")
        rec["fn"] = filename
        if not rec.get("sha256") and not rec.get("md5"):
            raise ValueError(f"Missing expected hash for {filename}")
        destination = target / filename
        if matches(destination, rec):
            downloaded.append((destination, rec))
            continue
        cached = cache_files.get(filename)
        if cached and matches(cached, rec):
            import shutil
            shutil.copy2(cached, destination)
            downloaded.append((destination, rec))
            say("VERIFIED CACHE " + filename)
            continue
        url = rec.get("url") or rec.get("package_url")
        if not url:
            raise ValueError(f"Missing source URL for {filename}")
        url = url.replace("https://conda.anaconda.org/conda-forge/", "https://prefix.dev/conda-forge/")
        jobs = [pool.submit(fetch_part, rec, url, start, min(start + CHUNK, rec["size"]) - 1)
                for start in range(0, rec["size"], CHUNK)]
        package_jobs.append((rec, destination, jobs))
    say(f"QUEUED {len(package_jobs)} packages; {len(downloaded)} already verified")
    remaining = list(package_jobs)
    errors = []
    last_progress = time.monotonic()
    while remaining:
        for item in remaining[:]:
            rec, destination, jobs = item
            if not all(job.done() for job in jobs):
                continue
            try:
                parts = [job.result() for job in jobs]
                with destination.open("wb") as output:
                    for part in parts:
                        output.write(part.read_bytes())
                if not matches(destination, rec):
                    raise ValueError("Final package checksum mismatch")
                downloaded.append((destination, rec))
                say("VERIFIED " + rec["fn"])
            except Exception as exc:
                errors.append(str(exc))
                say("ERROR " + str(exc))
            remaining.remove(item)
        if time.monotonic() - last_progress >= 20:
            say(f"PROGRESS {completed_bytes / 1048576:.1f} MiB transferred; {len(downloaded)}/{len(records)} verified")
            last_progress = time.monotonic()
        if remaining:
            time.sleep(1)

report = {"verified": len(downloaded), "required": len(records), "errors": errors}
Path("evidence/runtime-download-results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
if errors or len(downloaded) != len(records):
    raise SystemExit(1)
explicit = ["@EXPLICIT"]
for path, rec in downloaded:
    hashpart = rec.get("md5")
    explicit.append(path.resolve().as_uri() + ("#" + hashpart if hashpart else ""))
Path("evidence/runtime-explicit.txt").write_text("\n".join(explicit) + "\n", encoding="utf-8")
say("ALL PACKAGES VERIFIED")
