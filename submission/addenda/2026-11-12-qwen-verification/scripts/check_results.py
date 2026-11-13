"""Validate scoped proof outcomes, source coupling, memory controls and source preservation."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
source_manifest=json.loads((ROOT/'records/SOURCE_MANIFEST.json').read_text())
for name,entry in source_manifest.items():
    data=(ROOT/'sources'/name).read_bytes()
    assert hashlib.sha256(data).hexdigest()==entry['sha256'] and len(data)==entry['bytes'],name
wrappers={name:(ROOT/'sources'/name).read_text() for name in ['baseline_protocol_dut.sv','modified_protocol_dut.sv']}
ports={name:dict(re.findall(r'\.(io_\d+_\d+_\d+)\((\w+)\)',text)) for name,text in wrappers.items()}
original=ports['baseline_protocol_dut.sv'];modified=ports['modified_protocol_dut.sv']
inputs=['io_9_31_1','io_13_31_1','io_16_31_0','io_17_31_0','io_18_31_1','io_19_31_1']
assert all(original[p]==modified[p] for p in inputs)
assert original['io_8_31_1']==modified['io_8_31_1']=='BUSY'
assert original['io_19_31_0']==modified['io_19_31_0']=='ICE_LED'
assert original['io_16_31_1']=='MISO' and modified['io_16_31_1']=='raw_miso'
assert re.search(r'assign\s+MISO\s*=\s*raw_miso\s*\^',wrappers['modified_protocol_dut.sv'])
proofs={}
for name,expected in [('normal','SUCCESS!'),('control_allow_fault','FAIL!'),('control_trace','FAIL!'),('edge_normal','SUCCESS!'),('edge_control','FAIL!'),('cyclic_control','FAIL!')]:
    out=ROOT/'formal'/name
    receipt=json.loads((out/'receipt.json').read_text());assert receipt['exit_code']==0,name
    marker=[l.strip() for l in (out/'stdout.log').read_text().splitlines() if l.startswith('SAT proof finished')]
    assert len(marker)==1 and marker[0].endswith(expected),(name,marker)
    proofs[name]={'expected':expected,'actual':marker[0],'pass':True}
induction=ROOT/'formal/cyclic_induction'
assert json.loads((induction/'receipt.json').read_text())['exit_code']==0
induction_log=(induction/'stdout.log').read_text()
assert 'Base case for induction length 100 proven.' in induction_log
assert 'Induction step proven: SUCCESS!' in induction_log
proofs['cyclic_induction']={'expected':'inductive proof success','actual':'Base case and induction step proved at length 100','pass':True,'scope':'Unbounded cyclic normal transactions in the synchronous/async2sync model, with fresh arbitrary allowed payload/mode for each transaction.'}
text=(ROOT/'formal/edge_control/stdout.log').read_text()
trace={}
for line in text.splitlines():
    m=re.match(r'\s*(\d+)\s+\\(word_a|word_b|mode_a|mode_b|cycle|miso)\s+(-?\d+)\s+\S+\s+([01]+)\s*$',line)
    if m:trace.setdefault(int(m[1]),{})[m[2]]=int(m[4],2)
faults=[{'step':t,**v} for t,v in trace.items() if v.get('miso')==1]
assert faults and all(v.get('cycle') in (43,123) for v in faults),faults[:3]
for v in faults:
    suffix='a' if v['cycle']==43 else 'b'
    assert v['word_'+suffix]==0xC5A02026 and v['mode_'+suffix]==0
ram_controls=[]
for kind in ['baseline','modified']:
    netlist=json.loads((ROOT/'synthesis'/kind/'netlist.json').read_text())['modules']['protocol_dut']
    for name,cell in netlist['cells'].items():
        if cell['type']=='SB_RAM40_4K':
            c=cell['connections'];assert c['WCLK']==c['WCLKE']==['0'] and c['WE']==['1']
            ram_controls.append({'design':kind,'instance':name,'WCLK':0,'WCLKE':0,'WE':1})
result={'status':'PASS','preserved_source_files':len(source_manifest),'core_input_connections_identical':True,'core_inputs':inputs,'BUSY_LED_connections_identical':True,'MISO_difference_is_XOR_mask':True,'proofs':proofs,'explicit_edge_control_fault_samples':faults,'ram_controls':ram_controls,'quantification':'Bounded two-transaction models and an unbounded cyclic synchronous protocol model; arbitrary allowed stable 32-bit word/mode per transaction plus arbitrary extraction MOSI. Only the disclosed encryption-word case is excluded.','compositional_argument':'No XOR mask under these conditions plus unchanged inputs to the same recovered core implies equal sampled outputs for coupled core state. The core itself is abstracted, not cryptographically verified.','limits':['Explicit-edge model is bounded to 325 global samples; unbounded cyclic proof uses the synchronous async2sync model.','Reset, full frames, stable mode, prescribed launch/readout sequence are assumptions.','No claim for malformed frames, arbitrary clock/control glitches, metastability, real board timing, or cipher identity.','Negative controls intentionally permit existing disclosed fault behavior; no new behavior is generated.']}
(ROOT/'analysis/VERIFICATION_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','sources_preserved':len(source_manifest),'proof_checks':len(proofs),'explicit_edge_fault_samples':len(faults)},indent=2))
