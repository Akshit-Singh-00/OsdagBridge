"""Compare recorded desktop observations with the captured original output."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / 'evidence/desktop'
out = json.loads((folder / 'run-03/output.json').read_text())
deck = out['deck_design_results']
observed = {'deck_grade':'custom_concrete_45_3.5', 'deck_thickness':'250',
            'deck_overhang':'1050', 'rebar_top_yield':'500', 'rebar_top_dia':'12',
            'rebar_top_spacing':'195','rebar_top_cover':'50','rebar_top_area':'580',
            'rebar_bottom_dia':'12','rebar_bottom_spacing':'180',
            'rebar_bottom_cover':'50','rebar_bottom_area':'628'}
checks = [{'field': k, 'ui': v, 'backend': deck.get(k), 'match': v == deck.get(k)}
          for k,v in observed.items()]
for key,ui in [('ur_bot_uls',90),('ur_top_uls',73),('ur_bot_shear',78)]:
    checks.append({'field':key,'ui_percent':ui,'backend_ratio':deck[key],
                   'match':ui==round(100*deck[key])})
cb = out['crossbracing_design_results']['G1-G2']
cross = []
for component,mode,ui in [('diagonal','tension',.1),('diagonal','compression',.46),
                           ('chord','tension',.08),('chord','compression',.38)]:
    val=cb[component][mode]['Member.efficiency']
    cross.append({'component':component,'mode':mode,'ui_ratio':ui,'backend':val,'match':ui==val})
report={'method':'Values transcribed from saved native accessibility observations and screenshots; sampled comparison only.',
        'run':'run-03','deck_checks':checks,'crossbracing_checks':cross,
        'end_diaphragm':{'backend_G1_G2':out['end_diaphragm_design_results']['G1-G2'],
          'ui_ratios':[.1,.46,.08,.38], 'ui_status':'PASS',
          'observation':'UI repeats cross-bracing ratios with E1M1/E1M2 labels despite empty own backend results.',
          'match':False,'related_issue':'https://github.com/Nidhikhare12/OsdagBridge/issues/72'},
        'visual_observations':[
          'All three completed CAD views show the requested 20/25/30 m span, 8.40 m width, 2.10 m spacing and 250 mm deck.',
          'Girder/stiffener and girder-plus-crossbracing geometry rendered in the 20 m CAD view.',
          'End Diaphragm preview looks V-shaped while its field reads X-Bracing; retained as an observation, not an independently established new defect.',
          'Plot radio buttons have no visible text labels in this runtime; selecting one changes the SW shear view to a displayed Tx moment view.',
          'Initial imported location dialog had empty selection controls; Bhopal was explicitly selected before Design. Related UI state issue #105.'],
        'limits':['No independent structural verification','Not an exhaustive UI/field comparison','No generated LaTeX report comparison'],
        'source_files':['screenshots/run03-deck-ax.txt','screenshots/run03-crossbracing-ax.txt','screenshots/run03-enddiaphragm-ax.txt','run-03/output.json']}
(folder/'ui-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'deck_matches':sum(c['match'] for c in checks),'deck_checks':len(checks),
                  'crossbracing_matches':sum(c['match'] for c in cross),'diaphragm_match':False}))
