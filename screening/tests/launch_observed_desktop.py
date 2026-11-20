"""Launch the genuine desktop, observing design calls without altering their results.

All UI actions are performed separately with Computer Use. This observer only
saves input/output evidence around the original synchronous backend method.
"""
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "OsdagBridge/src"))
handles = []
if os.name == "nt":
    for suffix in ("Library/bin", "DLLs", ""):
        directory = Path(sys.prefix) / suffix
        if directory.is_dir():
            handles.append(os.add_dll_directory(str(directory)))
            os.environ["PATH"] = str(directory) + os.pathsep + os.environ.get("PATH", "")

import dataclasses
import json
import time
import traceback
from collections.abc import Mapping
from datetime import datetime, timezone
from osdagbridge.desktop import __main__ as desktop
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge

OUT = ROOT / "evidence/desktop"
OUT.mkdir(exist_ok=True)
original = PlateGirderBridge.design
counter = len(list(OUT.glob("run-*")))


def serialize(obj):
    if dataclasses.is_dataclass(obj):
        return serialize(dataclasses.asdict(obj))
    if isinstance(obj, Mapping):
        return {str(k): serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serialize(v) for v in obj]
    if hasattr(obj, "tolist"):
        return serialize(obj.tolist())
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def save(folder, name, value):
    try:
        (folder / name).write_text(json.dumps(serialize(value), indent=2), encoding="utf-8")
    except Exception as exc:
        print("Evidence observer could not save", name, repr(exc), file=sys.stderr)


def observed(self, *args, **kwargs):
    global counter
    counter += 1
    folder = OUT / f"run-{counter:02d}"
    folder.mkdir(exist_ok=True)
    metadata = {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                "method": "Unchanged backend called from the desktop; wrapper records before/after only"}
    started = time.monotonic()
    save(folder, "input-before.osi", self.input_dict)
    try:
        result = original(self, *args, **kwargs)
        metadata["status"] = "COMPLETED"
        save(folder, "output.json", self.output_dict)
        try:
            save(folder, "cad-parameters.json", self.get_3d_cad_parameters())
        except Exception:
            metadata["cad_observer_error"] = traceback.format_exc()
        return result
    except Exception:
        metadata["status"] = "ERROR"
        metadata["traceback"] = traceback.format_exc()
        save(folder, "output-at-error.json", self.output_dict)
        raise
    finally:
        metadata["seconds"] = round(time.monotonic() - started, 2)
        save(folder, "input-after.json", self.input_dict)
        save(folder, "metadata.json", metadata)


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    PlateGirderBridge.design = observed
    desktop.main()
