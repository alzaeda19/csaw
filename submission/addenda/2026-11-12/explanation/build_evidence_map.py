#!/usr/bin/env python3
"""Index allowed original-baseline sources and static evidence; no HDL execution."""
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent
SUB=Path('/Users/al-zayedal-hassan/Documents/CSAW_Qwen_Submission_20261113T001822Z_9sj2k3k6/package/submission')
RESTART=Path('/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06')
EQUIV=RESTART/'baseline_bitstream_equivalence_2026-11-07_20261107T172039Z'
paths={
 'B':SUB/'rtl/baseline.v',
 'A':SUB/'reference/baseline_protocol_dut.sv',
 'T':SUB/'reference/paired_normal_tb.sv',
 'S':SUB/'evidence/original_materials/qualifier/ice40_cryptographic_IP.md',
 'H':SUB/'evidence/original_materials/qualifier/spi_ice40_crypto_ip_test.py',
 'R':SUB/'evidence/historical_recovery/REPORT.md',
 'P':SUB/'evidence/historical_recovery/PRIOR_TECHNICAL_BRIEF.txt',
 'Q':EQUIV/'REPORT.md',
 'J':EQUIV/'simulation/SUMMARY.json',
 'R_ORIGINAL':RESTART/'baseline_recovery_2026-11-06/REPORT.md',
}
sources={}
for name,path in paths.items():
 data=path.read_bytes()
 sources[name]={'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'line_count':len(data.decode().splitlines())}
for name,path in paths.items():
 if path.is_relative_to(SUB): sources[name]['original_package_relative_path']=str(path.relative_to(SUB))
sources['Q']['bundled_copy']='source_records/BASELINE_BITSTREAM_EQUIVALENCE_REPORT.md'
sources['J']['bundled_copy']='source_records/BASELINE_SIMULATION_SUMMARY.json'
sources['R_ORIGINAL']['reviewer_note']='External historical original; byte-identical to bundled original-package evidence/historical_recovery/REPORT.md if hash equality below holds.'
sources['R_ORIGINAL']['matches_packaged_recovery_report']=sources['R_ORIGINAL']['sha256']==sources['R']['sha256']
assert sources['B']['sha256']=='180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765'
static=json.loads((OUT/'STATIC_BASELINE_ANALYSIS.json').read_text())

def ref(source, *ranges):
 for start,end in ranges:
  assert 1<=start<=end<=sources[source]['line_count']
 return {'source_id':source,'sha256':sources[source]['sha256'],'line_ranges':[{'start':a,'end':b} for a,b in ranges]}

claims=[
 {'id':'E01','classification':['static_observation','proposed_interpretation','historical_report'],
  'claim':'Original-derived baseline identity and architecture-level table-assisted multi-cycle interpretation; no standard cipher identification.',
  'evidence':[ref('B',(3,3),(42766,42768),(42786,42797),(42901,42928),(44315,44331)),ref('R',(7,14)),ref('P',(3,9))],
  'limits':'Architecture interpretation combines the register/storage/data-selection observations below. It does not infer table contents or cipher identity.'},
 {'id':'E02','classification':['specification','original_host_source'],
  'claim':'32-bit, shared SCK, <=1 MHz, synchronous active-low reset, mode direction, transfer-launch-read sequence and MSB-first host.',
  'evidence':[ref('S',(4,24),(29,55)),ref('H',(14,21),(25,34),(41,48),(59,87),(96,137))]},
 {'id':'E03','classification':['static_observation','historical_inference'],
  'claim':'Functional roles and duplicated status, without physical package-pin validation.',
  'evidence':[ref('A',(1,9)),ref('B',(3,3),(30051,30051)),ref('R',(20,33))]},
 {'id':'E04','classification':['static_observation','boolean_substitution'],
  'claim':'32-bit serial path under CS low; MISO registers old n800; CS high selects other parallel data; no CS-triggered sequential block.',
  'evidence':[ref('B',(43628,43628),(45031,45031),(44269,44269),(45673,45673))]+
             [ref('B',(x['data_line'],x['data_line']),(x['ff_line'],x['ff_line'])) for x in static['serial_path_evidence'].values()],
  'derived_artifact':'STATIC_BASELINE_ANALYSIS.json:serial_path_MOSI_to_last_register, serial_path_evidence, state',
  'limits':'Serial identity obtained by CS=0 substitution, not an HDL simulation. Output sample timing follows nonblocking rising-edge register structure.'},
 {'id':'E05','classification':['static_inventory','structural_role_inference','historical_report'],
  'claim':'1404 LUT-tagged assignments, four RAM primitives, 71 rising-SCK registers partitioned into 32 serial, 32 working, four counter bits, qualifier, delayed BUSY and MISO.',
  'evidence':[ref('B',(42766,42768),(42800,42802),(42834,42836),(42868,42870),(42901,44304),(44305,45708)),ref('Q',(26,28))],
  'derived_artifact':'STATIC_BASELINE_ANALYSIS.json:counts, state, working_registers, qualification_bit_direct_lut_consumers',
  'limits':'LUT comment count is a recovered-text count, not a fresh mapped utilization estimate. Two-bit counter interpretation follows toggle/XOR D equations and the associated enables/resets.'},
 {'id':'E06','classification':['static_observation','inference_from_constant_wiring'],
  'claim':'Four fixed initialized lookup primitives: READ_MODE=1, eight nonconstant address signals and eight connected output bits each; SCK read clock, common gated read enable, disabled write clock and clock enable.',
  'evidence':[ref('B',(42766,42768),(42786,42796),(42800,42802),(42820,42830),(42834,42836),(42854,42864),(42868,42870),(42888,42898),(42901,42901),(43384,43384),(44787,44787),(45177,45177)),ref('R',(13,13))],
  'derived_artifact':'STATIC_BASELINE_ANALYSIS.json:memories, control_alias_chains.n5, control_alias_chains.n466',
  'limits':'64 INIT payload lines are excluded before parsing; no content values, addressing permutation, table identity or key interpretation is claimed.'},
 {'id':'E07','classification':['static_observation','proposed_interpretation','driver_source'],
  'claim':'Direction input feeds 32 LUT equations; representative selection n1779. Working bank and memory outputs feed Boolean datapath. Stable-mode driver use; no cipher family/round count inference.',
  'evidence':[ref('B',(43238,43238),(42913,42913),(43239,43239),(43667,43667),(42920,42920),(43276,43276),(44679,44679)),ref('T',(81,89),(108,119)),ref('R',(29,29),(73,74))],
  'derived_artifact':'STATIC_BASELINE_ANALYSIS.json:mode_direct_lut_consumers, working_registers, state.*.data_combinational_leaves, qualification_bit_direct_lut_consumers',
  'limits':'No algorithm name is inferred from the host comments. No assertion that encryption/decryption form a bijection for every input.'},
 {'id':'E08','classification':['static_observation','exhaustive_combinational_identity','timing_inference'],
  'claim':'BUSY combinational equation, serial-enable equation, delayed BUSY register, and next-CS-high-edge parallel loading after a BUSY fall.',
  'evidence':[ref('B',(43022,43022),(43089,43089),(43123,43123),(43410,43410),(43626,43626),(43764,43764),(43923,43923),(44093,44093),(44341,44341),(44492,44492),(44526,44526),(44813,44813),(45167,45167),(45327,45327),(45497,45497),(42938,42938),(44269,44269),(45673,45673))],
  'derived_artifact':'STATIC_BASELINE_ANALYSIS.json:control_boolean_identity_checks and control_alias_chains; 768 identities checked over 256 combinations.',
  'limits':'The result-load timing inference assumes normal launch/completion, reset released and chip-select held high for the loading edge; it is not a proof of arbitrary malformed schedules.'},
 {'id':'E09','classification':['historical_tested_evidence','original_host_source','static_timing_explanation'],
  'claim':'Launch-inclusive four-clock BUSY observation, seven additional host clocks, post-edge sampling qualification, known-answer host passes and retained immediate-read failures.',
  'evidence':[ref('R',(39,49),(57,67)),ref('H',(72,78),(118,124)),ref('Q',(16,20)),ref('J',(65,86))],
  'limits':'No simulation, hardware or formal tool rerun occurred for this addendum. Recorded rate labels describe behavioral simulation.'},
 {'id':'E10','classification':['original_host_source','historical_tested_evidence'],
  'claim':'Single supplied P/C pair and both directional historical passes; 352 transactions/model and 104468 checkpoints; arbitrary stimuli lack an independent cipher oracle.',
  'evidence':[ref('H',(33,34)),ref('R',(59,60),(74,74)),ref('T',(8,8),(81,89),(96,99),(108,119)),ref('Q',(16,20),(32,32))]},
 {'id':'E11','classification':['historical_formal_report','scope_limit'],
  'claim':'Historical baseline-versus-regenerated-binary equivalence covers 135 next-state bits/three outputs under state relation and each-mode all-payload prescribed transactions; preserves readiness failure.',
  'evidence':[ref('Q',(3,5),(12,20),(26,34),(65,71)),ref('P',(7,9))],
  'limits':'Formal results are historical report statements. No new proof or log rerun. Equality is not independent cipher correctness, universal inversion or original physical-binary recovery proof.'},
 {'id':'E12','classification':['scope_statement','explicit_unknowns'],
  'claim':'Provides architectural proposed explanation; algorithm/table/key semantics and cryptographic strength remain unknown, no key recovery attempted.',
  'evidence':[ref('R',(11,14),(73,74)),ref('P',(3,9))],
  'limits':'The statement about this being a proposal rather than an exhaustive proof describes the deliverable; it is not a claim that this task independently audited course grading requirements.'}
]
result={'schema_version':1,'source_policy':'Only enumerated original baseline, original interface/host, reference adapter/normal bench and permitted clean historical records. No links followed to other artifacts. No published solution or shared Claude/Jordan material used.','line_numbering':'1-based, inclusive, pinned by source SHA-256','sources':sources,'claims':claims,'static_analysis_artifacts':['static_baseline_analysis.py','STATIC_BASELINE_ANALYSIS.json','STATIC_ANALYSIS_STDOUT.json'],'fresh_execution_scope':'Python static text/connectivity parsing and combinational Boolean identity checks only. No HDL generation/modification/execution; no attack code or key recovery.'}
(OUT/'EVIDENCE_MAP.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'sources':len(sources),'claims':len(claims),'all_line_ranges_in_bounds':True,'baseline_hash_verified':True},indent=2))
