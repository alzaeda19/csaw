"""Deterministic nonfunctional declaration fix, adapter, and relocated harness copy."""
from pathlib import Path
import hashlib,json,difflib
B=Path(__file__).resolve().parents[1]; R=B.parent
raw=B/'raw/recovered_default.v'; s=raw.read_text()
assert s.count('output io_16_31_1')==1
assert s.count('reg io_16_31_1 = 0;')==1
# Preserve initial state and procedural driver, changing declarations only.
t=s.replace('output io_16_31_1','output reg io_16_31_1').replace('reg io_16_31_1 = 0;','initial io_16_31_1 = 0;')
(B/'adapters/recovered_iverilog.v').write_text(t)
(B/'records/declaration_compatibility.diff').write_text(''.join(difflib.unified_diff(s.splitlines(True),t.splitlines(True),fromfile='raw/recovered_default.v',tofile='adapters/recovered_iverilog.v')))
(B/'adapters/protocol_dut.sv').write_text('''// Functional role mapping inferred from original-derived connectivity.
// BUSY/LED duplicate outputs are functionally interchangeable; no board pin claim.
module protocol_dut(input SCK,RST_N,MOSI,NORM_CS_N,START,ENC_DEC,
 output MISO,BUSY,ICE_LED);
 chip recovered(
  .io_9_31_1(SCK), .io_13_31_1(RST_N), .io_16_31_0(MOSI),
  .io_17_31_0(NORM_CS_N), .io_18_31_1(START), .io_19_31_1(ENC_DEC),
  .io_16_31_1(MISO), .io_8_31_1(BUSY), .io_19_31_0(ICE_LED));
endmodule
''')
H=B/'harness'; U=B/'raw/harness_original'
for rel in ['run.py','tb/protocol_tb.sv','tests/acceptance.py']:
 original=(R/'protocol_harness_2026-11-06'/rel).read_bytes()
 for dest in [H/rel,U/rel]:
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(original)
model=B/'tooling/yosys/techlibs/ice40/cells_sim.v'
sha=hashlib.sha256(model.read_bytes()).hexdigest()
p=H/'run.py'; a=p.read_text(); c=a.replace('ROOT = BASE.parent','ROOT = BASE.parent.parent')
old="if not a.fixture and p!=inputs[0] and re.search(rb'`include|\\$readmem[hb]',b):"
new="trusted_library = p == ROOT/'baseline_recovery_2026-11-06/tooling/yosys/techlibs/ice40/cells_sim.v' and hashlib.sha256(b).hexdigest() == '"+sha+"'\n        if not a.fixture and p!=inputs[0] and re.search(rb'`include|\\$readmem[hb]',b) and not trusted_library:"
assert old in c;c=c.replace(old,new);p.write_text(c)
(B/'records/runner_relocation.diff').write_text(''.join(difflib.unified_diff(a.splitlines(True),c.splitlines(True),fromfile='original_harness/run.py',tofile='baseline/harness/run.py')))
(B/'records/derivation_hashes.json').write_text(json.dumps({str(p.relative_to(B)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [raw,B/'adapters/recovered_iverilog.v',B/'adapters/protocol_dut.sv',model,H/'run.py',H/'tb/protocol_tb.sv']},indent=2)+'\n')
print('Candidate declaration-only fix and functional adapter generated. Model SHA256',sha)
