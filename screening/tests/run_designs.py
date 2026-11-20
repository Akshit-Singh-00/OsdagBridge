"""Run full upstream design pipelines and preserve inputs, outputs and plots.

This is a core integration test, NOT a claim that the desktop was exercised.
Run with the Osdag environment: python tests/run_designs.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "OsdagBridge" / "src"))
DLL_HANDLES = []
if os.name == "nt":
    for part in ("Library/bin", "DLLs", ""):
        folder = Path(sys.prefix) / part
        if folder.is_dir():
            DLL_HANDLES.append(os.add_dll_directory(str(folder)))
            os.environ["PATH"] = str(folder) + os.pathsep + os.environ.get("PATH", "")
os.environ.setdefault("MPLBACKEND", "Agg")

import contextlib
import copy
import dataclasses
import json
import time
import traceback
from collections.abc import Mapping
from datetime import datetime, timezone
import sqlite3
import matplotlib.pyplot as plt
from importlib.resources import files

# Same necessary database initialization as the desktop startup, without opening a GUI.
dbdir = files("osdag_core.data.ResourceFiles.Database")
db = Path(str(dbdir / "Intg_osdag.sqlite"))
with sqlite3.connect(db) as conn:
    if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' LIMIT 1").fetchone():
        conn.executescript((dbdir / "Intg_osdag.sql").read_text(encoding="utf-8"))

from osdagbridge.core.bridge_types.plate_girder.defaults import BASIC_INPUT_DICT, solve_extend_basic_input_dict
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
from osdagbridge.core.utils import common as C
from osdagbridge.core.bridge_types.plate_girder.ui_fields_project_location import get_weather

OUT = ROOT / "evidence" / "designs-verified"
OUT.mkdir(exist_ok=True)


def jsonable(obj):
    if dataclasses.is_dataclass(obj):
        return jsonable(dataclasses.asdict(obj))
    if isinstance(obj, Mapping):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if hasattr(obj, "tolist"):
        return jsonable(obj.tolist())
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def save(folder, name, obj):
    (folder / name).write_text(json.dumps(jsonable(obj), indent=2), encoding="utf-8")


def make_input(span, custom=False):
    inp = copy.deepcopy(BASIC_INPUT_DICT)
    location = {"method": "location_name", "data": {"state": "Madhya Pradesh", "district": "Bhopal (Bairagarh)"},
                "weather_data": get_weather("Madhya Pradesh", "Bhopal (Bairagarh)"),
                "display_text": "Bhopal (Bairagarh), Madhya Pradesh", "show_display": True}
    inp.update({C.KEY_SPAN: span, C.KEY_CARRIAGEWAY_WIDTH: 7.5, C.KEY_SKEW_ANGLE: 0,
                C.KEY_PROJECT_LOCATION: location,
                C.KEY_DESIGN_MODE: "Optimized"})
    solve_extend_basic_input_dict(inp)
    if custom:
        for member in ("girder", "cross_bracing", "end_diaphragm"):
            inp["material." + member] = "custom_steel_355_510"
            inp.update({f"material.{member}.{key}": value for key, value in {
                "fy": 355., "fu": 510., "e": 210., "g": 80.8,
                "poisson": .3, "density": 80., "thermal": 12.}.items()})
        inp[C.KEY_DECK_CONCRETE_GRADE_BASIC] = "custom_concrete_45_3.5"
        inp.update({"material.deck." + key: value for key, value in {
            "fck": 45., "fctm": 3.5, "ecm": 35., "density": 24., "thermal": 10.}.items()})
    return inp


def main():
    bridge = PlateGirderBridge()
    summary = []
    for name, span, custom in [("D01-baseline20", 20, False), ("D02-custom20", 20, True),
                               ("D03-custom25", 25, True), ("D04-custom30", 30, True)]:
        folder = OUT / name
        folder.mkdir(exist_ok=True)
        row = {"id": name, "span_m": span, "custom_materials": custom,
               "started_at_utc": datetime.now(timezone.utc).isoformat(),
               "method": "Same backend object; set_input followed by design; fresh expanded inputs each run"}
        started = time.monotonic()
        print("START", name, flush=True)
        with (folder / "execution.log").open("w", encoding="utf-8") as log:
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                try:
                    inputs = make_input(span, custom)
                    save(folder, "input.osi", inputs)
                    bridge.set_input(inputs)
                    material_props = bridge._build_material_props()
                    save(folder, "materials.json", material_props)
                    if custom:
                        material_expectations = [
                            ("steel_E_Pa", 210e9, material_props.steel_prop.E),
                            ("steel_Fy_Pa", 355e6, material_props.steel_prop.Fy),
                            ("steel_Fu_Pa", 510e6, material_props.steel_prop.Fu),
                            ("steel_weight_density_N_m3", 80000., material_props.steel_prop.rho),
                            ("concrete_fck_MPa", 45., material_props.concrete_prop.fck),
                            ("concrete_fctm_MPa", 3.5, material_props.concrete_prop.fctm),
                            ("concrete_Ecm_GPa", 35., material_props.concrete_prop.Ecm),
                        ]
                        save(folder, "material-checks.json", [
                            {"property": key, "expected": expected, "actual": actual,
                             "status": "PASS" if abs(expected - actual) < 1e-6 else "FAIL"}
                            for key, expected, actual in material_expectations])
                    bridge.design()
                    row["execution_status"] = "COMPLETED"
                    save(folder, "output.json", bridge.output_dict)
                    save(folder, "backend-input-after.json", bridge.input_dict)
                    save(folder, "cad-parameters.json", bridge.get_3d_cad_parameters())
                    save(folder, "deck-results.json", bridge.deck_design_results)
                    save(folder, "crossbracing-results.json", bridge.crossbracing_design_results)
                    save(folder, "end-diaphragm-results.json", bridge.end_diaphragm_design_results)
                    row["utilization"] = {k: jsonable(v) for k, v in bridge.output_dict.items() if k.startswith("util.")}
                    row["input_span_matches_output"] = bridge.output_dict.get(C.KEY_SPAN) == span
                    row["component_output_counts"] = {
                        "deck": len(bridge.deck_design_results or {}),
                        "crossbracing": len(bridge.crossbracing_design_results or {}),
                        "end_diaphragm": len(bridge.end_diaphragm_design_results or {}),
                    }
                    try:
                        fig = bridge.build_figure_grillage()
                        (folder / "grillage.png").write_bytes(bridge.figure_to_bytes(fig))
                        plt.close(fig)
                        row["grillage_plot"] = "GENERATED"
                    except Exception:
                        row["grillage_plot"] = traceback.format_exc()
                    # Use the same cached datasets and plotting functions as the desktop.
                    ds = bridge.grillage_model._deduplicated_results
                    save(folder, "load-cases.json", ds.coords["Loadcase"].values.tolist())
                    row["structural_plots"] = {}
                    for plot_name, case_name, build, component in [
                        ("bending-moment", "Envelope ULS", bridge.build_figure_bmd, "Mz"),
                        ("shear-force", "Envelope ULS", bridge.build_figure_sfd, "Fy"),
                        ("deflection", "1.0 LL", bridge.build_figure_deflection, "Dy"),
                    ]:
                        try:
                            fig, data = build(ds.sel(Loadcase=case_name), component)
                            (folder / (plot_name + ".png")).write_bytes(bridge.figure_to_bytes(fig))
                            save(folder, plot_name + "-summary.json", data)
                            plt.close(fig)
                            row["structural_plots"][plot_name] = "GENERATED"
                        except Exception:
                            row["structural_plots"][plot_name] = traceback.format_exc()
                    # Native CAD construction and shape checks supplement, not replace,
                    # visual inspection of the desktop model.
                    try:
                        from osdagbridge.core.bridge_types.plate_girder.cad_generator import PlateGirderCADGenerator
                        from OCC.Core.BRepCheck import BRepCheck_Analyzer
                        from OCC.Core.TopoDS import TopoDS_Shape
                        cad = PlateGirderCADGenerator()
                        model = cad.generate(bridge.get_3d_cad_parameters())
                        geometry = {}
                        for component, shapes in model.items():
                            if not isinstance(shapes, (list, tuple)):
                                continue
                            native_shapes = [s for s in shapes if isinstance(s, TopoDS_Shape)]
                            if native_shapes:
                                geometry[component] = {"count": len(native_shapes),
                                    "non_null": sum(not s.IsNull() for s in native_shapes),
                                    "valid": sum(BRepCheck_Analyzer(s).IsValid() for s in native_shapes if not s.IsNull())}
                        geometry["total_deck_width_mm"] = model.get("total_deck_width")
                        geometry["input_overall_width_mm"] = bridge.output_dict[C.KEY_TS_OVERALL_WIDTH] * 1000
                        save(folder, "cad-shape-checks.json", geometry)
                        row["cad_construction"] = "GENERATED"
                    except Exception:
                        row["cad_construction"] = traceback.format_exc()
                except Exception:
                    row["execution_status"] = "ERROR"
                    row["exception"] = traceback.format_exc()
                    print(row["exception"])
                    save(folder, "output-at-error.json", bridge.output_dict)
                    save(folder, "backend-input-at-error.json", bridge.input_dict)
        row["elapsed_seconds"] = round(time.monotonic() - started, 2)
        summary.append(row)
        save(OUT, "summary.json", summary)
        print("END", name, row["execution_status"], row["elapsed_seconds"], flush=True)
    bridge.reset()


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
