# OsdagBridge screening evidence — Akshit Singh

FOSSEE Winter Internship 2026, Software Testing & Issue Reporting.
Original source: `Nidhikhare12/OsdagBridge`, `dev` at `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`.

## Executed work

- Original validation: 72 checks, 46 pass / 26 expectation mismatches.
- Layout/state: 21 checks, 11 pass / 10 mismatches.
- Separate proposed validation repair: 72/72 pass; original source restored byte for byte.
- Four original-backend design attempts: default E350A raises missing Gs; custom 20/25/30 m designs complete.
- Three consecutive **desktop** designs in one session, with unlock and fresh changed-span OSI import: all complete and CAD shows 20/25/30 m.
- Every compared basic-geometry/material fixture field matches the captured desktop design-call input.
- Sampled desktop comparison: 15 deck matches, four cross-bracing matches; End Diaphragm incorrectly displays cross-bracing results despite empty own backend results (existing issue #72).
- Native CAD topology checks and 12 exported structural plots; actual desktop CAD/component/plot captures.

Completed calculation does not mean structural design pass. Fatigue utilization exceeds 100%; no independent structural certification is claimed. Input fixtures were imported freshly between GUI runs; direct span editing with stale segment tables is covered separately by the state checks.

## Main artifacts

- `output/pdf/OsdagBridge_Testing_Report.pdf`: 13-page report, exact cases, comparisons, failures, repair suggestions and limitations.
- `evidence/desktop/`: three original design-call input/output records, comparison JSON, screenshots and native accessibility observations.
- `evidence/designs-verified/`: separate backend attempts, component dictionaries, CAD checks and plots.
- `submission/fixes/validation-proposal.patch`: tested proposed repair, not applied to upstream source.
- `submission/issue-comment-drafts.json`: unposted draft follow-up evidence. Existing issue URLs in the report identify duplicates; no claim of new unique bugs.
- `video/OsdagBridge_Demonstration.mp4`: silent 2-minute walkthrough of genuine captured desktop key frames, with pauses omitted. It is explicitly labelled and is not a continuous real-time screencast.

Resume and private submission ZIP are intentionally excluded from this public repository.

## Reproduction

Copy this screening folder outside the repository, then clone the pinned source as its child `OsdagBridge`:

```powershell
git clone --branch dev https://github.com/Nidhikhare12/OsdagBridge.git OsdagBridge
git -C OsdagBridge checkout d74f56dd7f22925fb8148cabf5740ed8d1e39ff3
python tests/run_validation.py
python tests/run_state_checks.py
python tests/check_validation_proposal.py
```

The first two scripts intentionally return exit code 1 for reproduced expectation mismatches. The proposal runner temporarily edits two files and restores original bytes in `finally`. Do not concurrently edit those files.

For full designs, install the official project environment with PySide6 6.9.3 and use its Python for `tests/runtime_probe.py` and `tests/run_designs.py`. Our runtime uses Python 3.12.13; all 14 dependency imports pass. Exact environment/package versions accompany the evidence. `tests/launch_observed_desktop.py` launches the genuine UI with a before/after observer; UI operation was separate. An initial unguarded multiprocessing run was invalidated and excluded. Accepted full-design evidence is only in `designs-verified`.

## Scope and review

This is AI-assisted test scripting, desktop operation and documentation prepared for the candidate to review and understand. UI comparisons are sampled, not exhaustive. No independent engineering verification or generated LaTeX report comparison was completed. Displayed component PASS labels and engineering warnings are preserved as observed rather than endorsed.

Official internship: https://fossee.in/winter-internship/2026

Task brief: https://docs.google.com/document/d/1eJAVX6PR0Za40EkdbZvILJI1vuF-uvA0/edit

Live additional-evidence comment: https://github.com/Nidhikhare12/OsdagBridge/issues/72#issuecomment-7040686132

Mentor Nidhikhare12 was invited as a collaborator with write permission; acceptance is pending.
