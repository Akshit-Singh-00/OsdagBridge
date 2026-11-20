> Publication status: interim evidence. Desktop sequence, video, mentor invitation and final submission remain incomplete. The resume is held privately.

# OsdagBridge screening work

Prepared for Akshit Singh, FOSSEE Winter Internship 2026, 20 November 2026.

**In progress: this is not a complete screening submission.**

## Verified progress

- Upstream `Nidhikhare12/OsdagBridge`, `dev`, commit `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`.
- 72 actual validator checks: 46 pass, 26 fail on the original code.
- 21 actual layout/state checks: 11 pass, 10 fail on the original code.
- Separate validation repair proposal: all 72 validator checks pass.
- Runtime installed: 211 Conda packages verified; all 14 dependency import checks pass.
- Four full-design attempts: the default E350A baseline fails on missing shear modulus; custom 20 m, 25 m and 30 m designs complete on the same backend object.
- Three native CAD models pass the recorded shape-validity checks; 12 plots were generated and inspected. Exported plot labels are crowded.
- Custom steel density is ignored: entered 80 kN/m3 becomes 78.5 kN/m3 in material construction. Six other checked material properties match.
- All three completed designs report fatigue utilization above 100%; completion is not an engineering pass.
- The two temporarily modified upstream files were restored byte-for-byte; `git -C OsdagBridge status --short` is clean.
- Failures overlap existing issues; they are not 36 distinct new bugs. No issues/comments have been posted and nothing has been submitted.

## Files

- `output/pdf/OsdagBridge_Interim_Testing_Report.pdf`: updated report with executed checks and remaining requirements.
- `evidence/validation-results.json`: original validator observations.
- `evidence/validation-proposal-results.json`: separate proposed-fix observations.
- `evidence/state/`: full before/after input dictionaries, results and log.
- `submission/fixes/validation-proposal.patch`: proposed repair to finite/integer conversion, steel-member validation and OSI material validation.
- `submission/issue-comment-drafts.json`: draft additional evidence for existing issues, not posted.
- `evidence/designs-verified/`: completed full-design evidence, inputs, component outputs, plots and CAD checks.
- `tests/run_designs.py`: executed full-design runner. It does not automate the desktop or replace GUI evidence.
- `evidence/environment-install-*.log`: setup attempts and package-download failures.

## Reproduce completed checks

This directory is a standalone evidence package. Copy it outside this repository before running the commands below; they create the pinned source checkout inside the package. Application source is unchanged.

Place this package beside a checkout called `OsdagBridge`, or clone that checkout into the package root:

```powershell
git clone --branch dev https://github.com/Nidhikhare12/OsdagBridge.git OsdagBridge
git -C OsdagBridge checkout d74f56dd7f22925fb8148cabf5740ed8d1e39ff3
python tests/run_validation.py
python tests/run_state_checks.py
python tests/check_validation_proposal.py
```

The first two scripts intentionally exit 1 when they reproduce the original defects. The proposal runner temporarily edits two known files, saves candidate evidence separately, then restores the original bytes in a `finally` block. Use a clean checkout and do not edit those files while this script runs.

These checks ran with Python 3.12.5 on Windows. They exercise real upstream functions, without mocked solvers. They do not certify bridge-design accuracy or structural safety. Blank required values are intentionally allowed in draft OSI import; required-field handling at Design is still pending.

## Runtime setup progress

C: had only approximately 400 MB free, so runtime installation was moved to `D:\Fossee-runtime`. Micromamba lives in `.tools\Library\bin\micromamba.exe` in the working workspace (not included in the evidence ZIP).

The initial environment downloads repeatedly timed out. A compatibility retry pinned `pyside6=6.9.3` per `requirements.txt`. The resumed setup downloaded all 211 Conda packages, checked their hashes against the solved package metadata, and installed them offline. OpenSeesPy 3.8.0.0, opsvis 1.3.8 and the editable project were then installed. All 14 checks in `evidence/runtime-probe.json` pass. The runtime uses Python 3.12.13.

To reproduce setup on another machine, from `OsdagBridge` (adjust the paths):

```powershell
$env:TEMP = 'D:\Fossee-runtime\tmp'
$env:TMP = 'D:\Fossee-runtime\tmp'
$env:PIP_CACHE_DIR = 'D:\Fossee-runtime\pip-cache'
& '..\.tools\Library\bin\micromamba.exe' create --yes --no-rc --root-prefix 'D:\Fossee-runtime\mamba' --prefix 'D:\Fossee-runtime\env' -f environment.yml 'pyside6=6.9.3'
```

Use that environment's Python for `tests/runtime_probe.py`, `tests/run_designs.py` and `tests/launch_observed_desktop.py`. The full-design runner uses the bundled weather record for Bhopal (Bairagarh), Madhya Pradesh. The earlier layout-only checks use a synthetic location fixture. An initial design run without a Windows multiprocessing guard was invalidated and excluded from the ZIP; only `designs-verified` contains accepted design evidence.

The candidate's fork is available at https://github.com/Akshit-Singh-00/OsdagBridge. It is configured as `origin`; the original repository is `upstream`. Interim evidence is published on branch `codex/fossee-screening-evidence`; collaborator invitation remains pending.

## Remaining work

1. Start Windows recording manually: desktop control is restored and the custom 20 m input is imported, but automated activation dismisses the recording selector.
2. Observe desktop unlock/change/rerun behavior; compare UI inputs, internal dictionaries, component results and reports. No GUI design run is claimed.
3. Visually inspect the desktop 3D model and record the requested demonstration video. Native shape checks and generated plots do not replace this.
4. Update the published interim evidence with desktop results and complete the collaborator invitation. Issue comments remain drafts.
5. The candidate resume has been received privately. Add the completed recording, produce the final report/ZIP, and submit by 23 November 2026.

## Official references

- Internship: https://fossee.in/winter-internship/2026
- Task brief: https://docs.google.com/document/d/1eJAVX6PR0Za40EkdbZvILJI1vuF-uvA0/edit
- Repository: https://github.com/Nidhikhare12/OsdagBridge

The report distinguishes executed evidence, source-derived repair suggestions, and pending requirements. Review and understand the results before presenting them as your screening work.
