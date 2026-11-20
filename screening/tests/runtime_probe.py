"""Verify native dependencies without opening or controlling the desktop."""
import importlib
import importlib.metadata
import json
import os
import platform
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
results = {"python": sys.version, "prefix": sys.prefix, "platform": platform.platform(), "modules": {}}
for name in ("numpy", "scipy", "matplotlib", "pandas", "xarray", "yaml", "PySide6",
             "OCC.Core.BRep", "osdag_core", "openseespy.opensees", "opsvis", "navcube", "ifcopenshell", "fiona"):
    try:
        module = importlib.import_module(name)
        results["modules"][name] = {"status": "IMPORTED", "version": getattr(module, "__version__", None)}
    except Exception as exc:
        results["modules"][name] = {"status": "ERROR", "error": repr(exc)}
results["ready"] = all(v["status"] == "IMPORTED" for v in results["modules"].values())
(ROOT / "evidence/runtime-probe.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
sys.exit(0 if results["ready"] else 1)
