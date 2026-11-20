"""Build the evidence-based interim report using the bundled PDF runtime."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)
validation = json.loads((ROOT / "evidence/validation-results.json").read_text())
proposal = json.loads((ROOT / "evidence/validation-proposal-results.json").read_text())
state = json.loads((ROOT / "evidence/state/results.json").read_text())
designs = json.loads((ROOT / "evidence/designs-verified/summary.json").read_text())
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Cover", fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=colors.HexColor("#143042"), spaceAfter=14))
styles.add(ParagraphStyle(name="Deck", fontName="Helvetica", fontSize=12, leading=18, textColor=colors.HexColor("#455b68"), spaceAfter=12))
styles.add(ParagraphStyle(name="SmallCell", fontName="Helvetica", fontSize=8, leading=11, wordWrap="CJK"))
styles["BodyText"].fontSize = 10
styles["BodyText"].leading = 15
styles["BodyText"].spaceAfter = 8
styles["Heading2"].textColor = colors.HexColor("#143042")
styles["Heading2"].spaceBefore = 15
story = []


def p(text, style="BodyText"):
    return Paragraph(text, styles[style])


def add(text, style="BodyText"):
    story.append(p(text, style))


def table(rows, widths):
    data = [[p(escape(str(cell)), "SmallCell") for cell in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5eef2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), .7, colors.HexColor("#9bb0bd")),
        ("LINEBELOW", (0, 1), (-1, -1), .3, colors.HexColor("#dbe3e8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fa")]),
    ]))
    story.append(t)


add("FOSSEE WINTER INTERNSHIP 2026", "Deck")
add("OsdagBridge<br/>Software testing &amp;<br/>issue reporting", "Cover")
add("Testing evidence report | 20 November 2026", "Deck")
add("Prepared for Akshit Singh", "Heading2")
add("<b>Executed evidence:</b> 72 original validation checks, 21 layout checks, four backend design attempts and three consecutive desktop designs. The same desktop session was unlocked twice and rerun with 20, 25 and 30 m fixtures. Custom steel/concrete dialogs, CAD, structural plots and component summaries were observed. This report records both successful execution and reproducible mismatches.")
table([
    ["Executed suite", "Original source", "Fix proposal"],
    ["Validation: 72 checks", f"{validation['passed']} pass / {validation['failed']} fail", f"{proposal['passed']} pass / {proposal['failed']} fail"],
    [f"Layout and state: {len(state['cases'])} checks", f"{state['passed']} pass / {state['failed']} fail", "Not applied"],
    ["Full design attempts: 4", "3 completed / 1 error", "Original source"],
    ["Native CAD / structural plots", "3 models / 12 plots generated", "Desktop views inspected"],
    ["Consecutive desktop designs", "3 completed / 0 exceptions", "20 / 25 / 30 m"],
], [78*mm, 48*mm, 44*mm])
story.append(Spacer(1, 8*mm))
add("Scope and interpretation", "Heading2")
add("A failed check is a reproducible expectation mismatch, not a count of unique bugs. Observed defects overlap existing upstream issues. Completed calculations do not imply a passing engineering design: all custom cases report fatigue utilization above 100%. No independent structural-code verification or GUI crash is claimed. UI comparisons are sampled and their limits are stated explicitly.")
add("The separate validation proposal was tested temporarily against the real modules. Both upstream files were then restored byte-for-byte. Original failing evidence and proposal results are stored separately.")
story.append(PageBreak())

add("Environment and method", "Heading1")
add("Repository: <link href='https://github.com/Nidhikhare12/OsdagBridge'>Nidhikhare12/OsdagBridge</link>, branch <b>dev</b>.<br/>Commit: <font name='Courier' size='8'>d74f56dd7f22925fb8148cabf5740ed8d1e39ff3</font>.<br/>Executed validation/state checks: Windows, Python 3.12.5; actual upstream Python modules with no substitute validators or solver mocks.")
add("The empty example/placeholder tests were not used as evidence of application correctness. The added scripts record exact inputs, expectations, return values or exceptions, and generated dictionaries. No invalid non-finite values were sent into a native structural solver.")
add("Setup observations", "Heading2")
add("The runtime and package cache were placed under D:/Fossee-runtime because C: had little free space. After repeated download failures, all 211 solved Conda artifacts were downloaded and checked against their package hashes, then installed offline. PySide6 was pinned to 6.9.3, matching requirements.txt. The environment uses Python 3.12.13 and OpenSeesPy 3.8.0.0; all 14 import checks passed. Exact Conda metadata, pip versions and installation logs accompany the evidence.")
add("Fixtures", "Heading2")
add("State checks start with a 20 m span, 7.5 m carriageway, no median, no footpath, zero skew and Optimized mode. The expanded layout has four girders and 8.4 m overall width. A synthetic location dictionary is used only for these core fixtures; it is not a selected real project site. Deck and wearing-course overrides are 300 mm and 80 mm. Follow-up expansions change the span to 25 m and 30 m, then reduce the girder count to two.")
add("Evidence files", "Heading2")
table([
    ["File", "Purpose"],
    ["evidence/validation-results.json", "All 72 original validation observations, Python version and commit"],
    ["evidence/validation-proposal-results.json", "Same 72 checks against the proposed repair"],
    ["evidence/state/*.osi", "Exact baseline, custom before/after and successive-span input dictionaries (JSON is valid YAML)"],
    ["evidence/state/results.json; execution.log", "All layout checks and function output"],
    ["submission/fixes/validation-proposal.patch", "Reviewable proposal; not applied to the final working source"],
    ["evidence/designs-verified/", "Four full-design attempts, exact inputs, component outputs, plots and CAD checks"],
    ["tests/run_designs.py", "Executed full-design runner, protected by a Windows multiprocessing main guard"],
], [83*mm, 87*mm])
story.append(PageBreak())

add("Reproduced findings and repairs", "Heading1")
findings = [
    ("F01 - Non-finite and fractional numeric values", "Span NaN is accepted. Infinite girder counts raise OverflowError; 2.5 girders is accepted by integer truncation.", "validator.py: _to_float and _to_int. Require finite floats and integral counts before conversion. The proposal implements this.", "88, 130"),
    ("F02 - Material validation differs by member and entry route", "Negative or excessive steel yield strengths are accepted for cross-bracing and end-diaphragm keys. The OSI route also accepts tested out-of-range girder and deck properties.", "validator.py: validate_material_inputs; osi_validator.py: OsiInputValidator.validate. Reuse steel-property ranges for all steel members and run these validators on present OSI material properties. Implemented in the proposal.", "129, 96"),
    ("F03 - Default expansion overwrites custom thickness", "Deck thickness 300 becomes 250 mm; wearing-course thickness 80 becomes 50 mm.", "defaults.py: _update_typical_section_defaults uses unconditional input_dict.update. Insert defaults only for missing optional values; keep derived geometry recomputation separate. Audit save/load/design callers. Suggested only; no patch applied or tested for this finding.", "71"),
    ("F04 - Segment ends remain at the prior span", "After 20 -> 25 -> 30 m expansions, all four segment-table end values remain 20 m.", "defaults.py: _on_no_of_girders_changed initializes segment tables only if missing. Track auto-generated segments and refresh their endpoints on span changes; preserve and validate intentional multi-segment customizations. Do not blindly overwrite all user segments. Suggested only.", "125, 168"),
]
for title, observation, repair, issue_nums in findings:
    story.append(KeepTogether([p(title, "Heading2"), p(observation), p("<b>Cause / repair:</b> " + repair),
                               p("<b>Related existing issues:</b> " + ", ".join(f"<link href='https://github.com/Nidhikhare12/OsdagBridge/issues/{n.strip()}'>#{n.strip()}</link>" for n in issue_nums.split(",")))]))
add("Duplicate review", "Heading2")
add("Open and closed upstream issues were read on 20 November 2026. Links above identify overlap; no new issue or comment has been posted. The fractional-count result is retained as additional evidence, without asserting novelty.")
story.append(PageBreak())

add("Full design and native CAD results", "Heading1")
add("The unchanged upstream backend was exercised on one PlateGirderBridge instance. Each attempt received a freshly expanded input dictionary. The location is the bundled Bhopal (Bairagarh), Madhya Pradesh weather record. Carriageway width is 7.5 m, overall width 8.4 m, with four structural girders, no footpath, zero skew and Optimized mode. This is a backend sequence, not the desktop unlock/change/rerun workflow.")
rows = [["Case", "Span", "Execution", "Time", "Fatigue utilization"]]
for d in designs:
    rows.append([d["id"], str(d["span_m"]) + " m", d["execution_status"], str(d["elapsed_seconds"]) + " s", str(d.get("utilization", {}).get("util.fatigue", "N/A")) + ("%" if d.get("utilization") else "")])
table(rows, [45*mm, 17*mm, 35*mm, 25*mm, 48*mm])
add("Default material failure", "Heading2")
add("D01 uses the default E 350A steel and M40 concrete. Analysis reaches the design checks, which raise ValueError: Gs (shear modulus) is not set for grade 'E 350A'. This reproduces the condition already described in <link href='https://github.com/Nidhikhare12/OsdagBridge/issues/42'>issue #42</link>. The traceback and partial dictionaries are retained. The runtime import checks passed; this is not a missing solver installation.")
add("Custom material propagation", "Heading2")
add("D02-D04 use custom steel fy=355 MPa, fu=510 MPa, E=210 GPa, G=80.8 GPa, Poisson ratio=0.3, density=80 kN/m3 and thermal coefficient=12. Concrete inputs are fck=45 MPa, fctm=3.5 MPa, Ecm=35 GPa, density=24 kN/m3 and thermal coefficient=10. Exact named fields are in each input.osi.")
table([["Checked backend property", "Expected", "Actual"], ["Steel E / fy / fu", "210 GPa / 355 / 510 MPa", "Match in all three cases"], ["Steel weight density", "80,000 N/m3", "78,500 N/m3 in all three"], ["Concrete fck / fctm / Ecm", "45 MPa / 3.5 MPa / 35 GPa", "Match in all three cases"]], [64*mm, 53*mm, 53*mm])
add("Six of seven material-construction assertions pass per custom case. The steel density mismatch agrees with <link href='https://github.com/Nidhikhare12/OsdagBridge/issues/20'>issue #20</link>: _build_material_props uses its hardcoded fallback instead of material.girder.density. A repair should validate and convert that user field to N/m3, preserving the default only when no custom value exists. This check does not establish end-to-end propagation of every custom field or correct use of custom grades by all connection designers.")
story.append(PageBreak())
add("Outputs, geometry and limitations", "Heading1")
add("Each completed run retains the full output dictionary, deck results (55 top-level entries), cross-bracing results (3 entries) and end-diaphragm results (3 entries). These are dictionary-entry counts, not counts of physical parts. The output span matches the requested span in all three cases.")
add("For each completed run, the native CAD generator returned non-null shapes that pass OpenCascade BRepCheck_Analyzer in every recorded shape group. Each model has 12 girder plate shapes (four webs and eight flanges); stiffener, stud and cross-bracing entries include compounds. Overlapping groups must not be added to infer a total part count. The generated deck width and input overall width both equal 8400 mm.")
add("Grillage, bending-moment, shear-force and deflection PNGs were generated for each completed run. Bending and shear plots use Envelope ULS; deflection uses 1.0 LL. Plot data summaries and load-case names are saved. Visual inspection confirms nonblank diagrams and changing span axes, but labels overlap and are crowded in the exported views. Native topology validity and visible plot generation do not establish that dimensions, member locations or design calculations are correct.")
add("Desktop execution and recording method", "Heading2")
add("The genuine desktop was launched with an observer around the original design method. It records inputs and outputs without modifying results. All three GUI designs completed in one session (25.38, 28.08 and 33.81 seconds for the observed backend calls). Between runs the unlock confirmation was accepted and the next full OSI fixture was imported. This verifies unlock/import/rerun, rather than direct span editing with old segment tables. CAD visibly changed to 20.00, 25.00 and 30.00 m. The silent video is a labelled sequence of genuine desktop key-frame captures with pauses omitted; it is not a continuous real-time screencast.")
add("Evidence integrity", "Heading2")
add("An initial harness run lacked a Windows multiprocessing main guard, allowing child processes to re-enter the tests. That run was stopped and explicitly invalidated. Only the corrected, completed evidence in designs-verified is packaged. The upstream source checkout remains clean; neither the structural code nor the solver was replaced or patched for these runs.")
story.append(PageBreak())
add("Coverage and submission contents", "Heading1")
table([
    ["Requirement", "Current status / next action"],
    ["Desktop launch and input/output comparison", "Three GUI runs completed. Every compared material/basic-geometry fixture field matches the original design-call input; sampled deck and cross-bracing outputs match."],
    ["Custom materials", "Seven material-construction assertions executed per custom case; six pass, density fails. Full member/load propagation remains partly unverified."],
    ["At least three consecutive design runs", "Three desktop designs completed in one session with unlock/import changes, in addition to the separate backend sequence."],
    ["CAD and plots", "Three native models and 12 PNG plots generated; desktop bridge, girders/stiffeners, bracing and plot views inspected."],
    ["Component coverage", "Girder CAD, deck and transverse summaries sampled. End-diaphragm UI mismatch reproduced. Exhaustive member/code/report verification is outside the completed checks."],
    ["GitHub repository and issue evidence", "Evidence branch: Akshit-Singh-00/OsdagBridge, codex/fossee-screening-evidence. Existing issue links and reviewable repair proposal included; publication status is tracked separately."],
    ["Video and resume", "Silent key-frame walkthrough supplied. Original candidate resume is included only in the private submission ZIP."],
    ["PDF and supporting ZIP", "This report accompanies exact OSI files, dictionaries, screenshots, scripts, logs and checksums. Administrative submission status is separate from test outcomes."],
], [61*mm, 109*mm])
add("Reproduction commands", "Heading2")
for line in ["git clone --branch dev https://github.com/Nidhikhare12/OsdagBridge.git", "git -C OsdagBridge checkout d74f56dd7f22925fb8148cabf5740ed8d1e39ff3", "python tests/run_validation.py", "python tests/run_state_checks.py", "python tests/check_validation_proposal.py"]:
    add(escape(line), "Code")
add("Run from the package root, with the upstream checkout named OsdagBridge. The first two test scripts intentionally return exit code 1 when they reproduce original defects. The proposal runner restores its two source files in a finally block. Keep the pinned original version for evidence collection.")
add("For full tests, install the project environment, then use its Python to run tests/runtime_probe.py and tests/run_designs.py. The design script initializes the packaged Osdag section database as required by desktop startup, then records four attempts on the same backend. It does not operate the GUI or substitute for the demonstration video.")
story.append(PageBreak())
add("Desktop input/output comparisons", "Heading1")
add("The saved design-call inputs match every compared basic geometry and material field in the corresponding fixture, and all three output spans equal the UI span. Source: evidence/desktop/comparison.json. The explicit desktop material dialogs show steel 355/510 MPa, E 210 GPa, G 80.8 GPa and density 80 kN/m3; concrete 45/3.5 MPa, Ecm 35 GPa and density 24 kN/m3.")
table([["30 m desktop observation", "Original output dictionary", "Result"],
 ["Deck grade; thickness; overhang", "custom_concrete_45_3.5; 250 mm; 1050 mm", "Match"],
 ["Top rebar: 12 mm @195; area 580", "12; 195; 580 (deck_design_results)", "Match"],
 ["Bottom rebar: 12 mm @180; area 628", "12; 180; 628 (deck_design_results)", "Match"],
 ["Deck sagging / hogging / shear: 90/73/78%", "0.899 / 0.729 / 0.782, rounded to percent", "Match"],
 ["G1-G2 cross-brace utilization: .100/.460/.080/.380", "Same four Member.efficiency values", "Match"],
 ["End-diaphragm UI: same four ratios, PASS", "end_diaphragm_design_results G1-G2 is empty", "Mismatch"]], [66*mm,80*mm,24*mm])
add("The UI comparison script records 15 deck matches and four cross-bracing matches. Saved native accessibility captures preserve the visible values and component labels. The main dock initially selects G1/SW; its rounded values are not compared directly to the global envelope utilization, which represents a different selection.")
add("F05 - End-diaphragm result routing", "Heading2")
add("The End Diaphragm tab labels E1M1/E1M2 rows but repeats cross-bracing demands, capacities and ratios, despite empty own results. This supplies further evidence for <link href='https://github.com/Nidhikhare12/OsdagBridge/issues/72'>issue #72</link>. In src/osdagbridge/desktop/ui/dialogs/transverse_member_design.py, _try_load_data() (near lines 893-944), route the diaphragm tab only to end_diaphragm_design_results; display unavailable/error when that result is empty. Do not silently fall back to cross-bracing results. Suggested repair, not applied.")
add("Additional visual observations", "Heading2")
add("The initial imported location dialog had empty state/district controls; Bhopal was explicitly selected before running. Related UI-state report: <link href='https://github.com/Nidhikhare12/OsdagBridge/issues/105'>#105</link>. The diaphragm preview looks V-shaped while its field reads X-Bracing, and plot radio buttons lack visible text in this runtime. These are retained as observations without claiming new independently isolated bugs. Screenshots document the rendering context.")
story.append(PageBreak())
add("Selected desktop evidence", "Heading1")
for name,caption in [("14-cad30.png","Third consecutive GUI design: 30 m bridge CAD."),("17-enddiaphragm-summary.png","End-diaphragm display: tab, selected pair, fields and preview.")]:
    img=Image(str(ROOT/'evidence/desktop/screenshots'/name))
    ratio=min(170*mm/img.imageWidth,90*mm/img.imageHeight)
    img.drawWidth=img.imageWidth*ratio; img.drawHeight=img.imageHeight*ratio
    story.extend([img,p(caption),Spacer(1,4*mm)])
add("Evidence limits: no independent structural certification, exhaustive UI audit or generated LaTeX design-report comparison. The raw dictionaries retain warnings and failed engineering checks. This submission was prepared with AI-assisted scripting, desktop operation and documentation; the candidate should understand and review the findings.")
story.append(PageBreak())

add("Appendix A - All validation observations", "Heading1")
add("PASS means actual acceptance/rejection matched the stated expectation. An OSI draft with a blank required field is intentionally accepted by the importer; that case is treated as a passing draft-load contract. Required-field validation at Design remains a separate test.")
rows = [["Check / input", "Expected", "Original observation", "Result"]]
for r in validation["cases"]:
    actual = r["actual"]
    if actual is None:
        text = "Accepted (None)"
    elif isinstance(actual, dict):
        text = actual.get("exception", "Accepted" if actual.get("valid") else "Rejected")
        if "exception" in actual:
            text += ": " + actual["message"]
    else:
        text = "Rejected; correction=" + str(actual[0])
    rows.append([r["id"] + "\nvalue=" + r["value"], "Accept" if r["expected_valid"] else "Reject without exception", text, r["status"]])
table(rows, [73*mm, 28*mm, 52*mm, 17*mm])
story.append(PageBreak())
add("Appendix B - All layout/state observations", "Heading1")
add("These are consecutive calls into default/layout expansion, not completed structural designs. Full before/after dictionaries accompany the package.")
rows = [["Check", "Expected", "Actual", "Result"]]
for r in state["cases"]:
    rows.append([r["id"], str(r["expected"]), str(r["actual"]), r["status"]])
table(rows, [91*mm, 30*mm, 32*mm, 17*mm])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#c4d2da"))
    canvas.line(20*mm, 16*mm, 190*mm, 16*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#546b79"))
    canvas.drawString(20*mm, 11*mm, "AKSHIT SINGH  |  OSDAGBRIDGE  |  EXECUTED TESTING EVIDENCE")
    canvas.drawRightString(190*mm, 11*mm, str(doc.page))
    canvas.restoreState()


path = OUT / "OsdagBridge_Testing_Report.pdf"
doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                        topMargin=19*mm, bottomMargin=23*mm, title="OsdagBridge Testing Report", author="Akshit Singh")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(path)
