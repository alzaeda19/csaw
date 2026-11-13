"""Analyze one existing formal check and preserved full-core simulation evidence."""
from pathlib import Path
import csv
import hashlib
import json
import re
import traceback

ROOT = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()

def write(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + '\n')

raw_path = ROOT / 'formal/edge_control/counterexample.json'
raw = raw_path.read_text()
errors = []
try:
    json.loads(raw)
except json.JSONDecodeError as error:
    errors.append({'operation': 'Parse entire raw Yosys WaveJSON with strict JSON', 'exception': str(error), 'traceback': traceback.format_exc(), 'resolution': 'Raw output preserved unchanged. Parse only six original single-line signal objects whose names contain no invalid JSON escapes; record their original line numbers and hashes.'})
signals = {}; selected = []
wanted = {'word_a','word_b','mode_a','mode_b','miso','cycle'}
for line_number, line in enumerate(raw.splitlines(), 1):
    if re.search(r'"name": "(?:word_a|word_b|mode_a|mode_b|miso|cycle)"', line):
        obj = json.loads(line.strip().rstrip(','))
        assert obj['name'] not in signals
        signals[obj['name']] = obj
        selected.append({'source_line': line_number, 'exact_line_sha256_without_newline': sha(line.encode()), 'signal': obj})
assert set(signals) == wanted
write('records/SELECTED_WITNESS_SIGNALS.json', {'source': str(raw_path.relative_to(ROOT)), 'source_sha256': sha(raw_path.read_bytes()), 'selected': selected})
write('records/PARSING_ERRORS.json', errors)

def decode(signal):
    previous = None; data = iter(signal.get('data', [])); result = []
    for c in signal['wave']:
        if c == '.':
            result.append(previous); continue
        if c in '01xz': previous = c
        elif c in '=23456789': previous = next(data, '')
        else: raise ValueError('Unsupported WaveJSON symbol ' + c)
        result.append(previous)
    assert next(data, None) is None
    return result

decoded = {name: decode(signal) for name, signal in signals.items()}
assert all(len(values) == 326 for values in decoded.values())
def constant(name):
    values = {v for v in decoded[name] if v not in (None, '')}
    assert len(values) == 1
    return int(values.pop(), 2)
word_a, word_b, mode_a, mode_b = (constant(k) for k in ['word_a','word_b','mode_a','mode_b'])
different = [{'wave_index': i, 'cycle': int(decoded['cycle'][i], 2), 'abstract_miso': 1} for i, v in enumerate(decoded['miso']) if v == '1']
assert different and all(d['cycle'] == 43 for d in different)

harness = (ROOT / 'formal/edge_protocol_harness.sv').read_text()
script = (ROOT / 'formal/edge_control.ys').read_text()
assert '-DALLOW_DISCLOSED_FAULT_CASE' in script
inactive = re.search(r'`ifndef ALLOW_DISCLOSED_FAULT_CASE\n(.*?)`endif', harness, re.S)
assert inactive
active = harness[:inactive.start()] + harness[inactive.end():]
assumptions = re.findall(r'\bassume\((.*?)\);', active)
assert assumptions == ['SCK == formal_clock_phase']
assert '(* anyconst *) reg [31:0] word_a, word_b;' in active
assert '(* anyconst *) reg mode_a, mode_b;' in active
assert '(* anyseq *) reg extraction_mosi;' in active
assert not re.search(r'-set\s+(word_a|word_b|mode_a|mode_b)', script)

def connections(path):
    text = path.read_text()
    instance = re.search(r'\bchip\s+recovered\s*\((.*?)\);', text, re.S)
    assert instance
    return dict(re.findall(r'\.(io_\d+_\d+_\d)\((\w+)\)', instance.group(1)))
base = connections(ROOT / 'sources/baseline_protocol_dut.sv')
modified = connections(ROOT / 'sources/modified_protocol_dut.sv')
inputs = ['io_9_31_1','io_13_31_1','io_16_31_0','io_17_31_0','io_18_31_1','io_19_31_1']
assert all(base[k] == modified[k] for k in inputs)
assert all(base[k] == modified[k] for k in ['io_8_31_1','io_19_31_0'])
assert base['io_16_31_1'] == 'MISO' and modified['io_16_31_1'] == 'raw_miso'
mod_text = (ROOT / 'sources/modified_protocol_dut.sv').read_text()
miso_assignment = re.search(r'assign MISO = (.*?);', mod_text).group(1)
assert miso_assignment.startswith('raw_miso ^ ')

rows = list(csv.DictReader((ROOT / 'historical/simulation/demo_trace.csv').open()))
case = 'trigger_no_gap'
matching = [r for r in rows if r['case'] == case]
ingress = [r for r in matching if r['phase'] == 'ingest']
extraction = [r for r in matching if r['phase'] == 'extract']
assert len(ingress) == len(extraction) == 32
sim_word = int(''.join(r['MOSI'] for r in ingress), 2)
sim_mode = {int(r['ENC_DEC']) for r in matching}
assert sim_word == word_a and sim_mode == {mode_a}
base_word = int(''.join(r['REF_MISO'] for r in extraction), 2)
mod_word = int(''.join(r['MISO'] for r in extraction), 2)
differences = [i for i,r in enumerate(extraction) if r['MISO'] != r['REF_MISO']]
assert differences == [0] and base_word ^ mod_word == 0x80000000
assert all(r['BUSY'] == r['REF_BUSY'] and r['LED'] == r['REF_LED'] for r in matching)
sim_result = json.loads((ROOT / 'historical/simulation/RESULT.json').read_text())
assert sim_result['simulate']['returncode'] == sim_result['compile']['returncode'] == 0
for name in ['baseline.v','modified_protocol_dut.sv','cells_sim.v']:
    assert sha((ROOT / 'sources' / name).read_bytes()) == sim_result['source_hashes'][name]
assert sha((ROOT / 'historical/simulation/sources/demo_tb.sv').read_bytes()) == sim_result['source_hashes']['demo_tb.sv']
write('records/MATCHING_SIMULATION_CASE.json', {'case':case,'rows':matching,'coverage':'Historical full-core simulation with the same frozen sources and discovered input/mode. Not a fresh replay of the exact entire formal trace; idle/reset spacing differs.'})

stdout = (ROOT / 'formal/edge_control/stdout.log').read_text()
receipt = json.loads((ROOT / 'formal/edge_control/receipt.json').read_text())
assert receipt['exit_code'] == 0
assert 'SAT proof finished - model found: FAIL!' in stdout
result = {
    'check':'One fresh run of unchanged edge_control.ys / edge_protocol_harness.sv',
    'result':'Modification flagged: output-equality assertion has a counterexample.',
    'tool_exit_code':0,
    'assertion_result':'FAIL: counterexample found, not a tool execution failure.',
    'elapsed_seconds':receipt['elapsed_seconds'],
    'bound_global_steps':325,
    'transaction_slots':2,
    'active_assumptions':assumptions,
    'word_and_mode_constraints':'No data/mode restriction or supplied trigger assumption. Two arbitrary 32-bit words and two arbitrary stable direction bits; extraction MOSI arbitrary.',
    'genericity_limit':'The tool has white-box access to the unchanged modified RTL. Reviewers know the disclosed design. This is not a blind detector benchmark.',
    'witness':{'word_a_hex':f'{word_a:08x}','mode_a':mode_a,'word_b_hex':f'{word_b:08x}','mode_b':mode_b,'different_samples':different},
    'source_coupling':{'six_core_inputs_identical':True,'busy_and_led_direct_identical_connections':True,'miso_relation':miso_assignment,'underlying_baseline_sha256':sha((ROOT/'sources/baseline.v').read_bytes())},
    'abstraction':'The existing harness substitutes a zero-output chip. The result detects the XOR mask. Since actual core inputs are unchanged and mask logic does not depend on core outputs, a mask-one event implies a different sampled MISO for a coupled determinate core output. This is compositional evidence, not a fresh full-crypto RTL miter.',
    'historical_full_core_corroboration':{'case':case,'input_hex':f'{sim_word:08x}','mode':mode_a,'baseline_result_hex':f'{base_word:08x}','modified_result_hex':f'{mod_word:08x}','xor_hex':f'{base_word^mod_word:08x}','differing_extraction_indices':differences,'same_frozen_source_hashes':True,'historical_simulation_failures':sim_result['counts']['failures'],'fresh_simulation':False,'exact_formal_trace_replayed':False},
    'limits':['Protocol schedule is prescribed, with a reset and two transaction slots; clock phases are explicit.','Normal protocol here means legal framing/timing; all data includes the disclosed exceptional case excluded by earlier normal-operation proofs.','No arbitrary-protocol, physical timing, board, power, statistical stealth or all-detector claim.','One counterexample is enough to refute equality in this check, but does not measure detector recall or a universal stealth score.','No frozen source/harness changes; no generation, concealment or optimization. No published solutions. No Qwen call in this independently run subtask.'],
    'preserved_analysis_error_count':len(errors)
}
write('ANALYSIS.json',result)
print(json.dumps({k:result[k] for k in ['result','tool_exit_code','elapsed_seconds','witness','historical_full_core_corroboration','preserved_analysis_error_count']},indent=2))
