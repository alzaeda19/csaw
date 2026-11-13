"""Compare high-level reconstruction with untouched original RTL/primitive model."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess
import time
from baseline_model import Model, ROOT
from reconstruct_cipher import Reconstructed

parser=argparse.ArgumentParser()
parser.add_argument('--suite',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
model=Model();reconstruction=Reconstructed(model)
vectors=json.loads((ROOT/'verification/VECTORS.json').read_text())
rows=[]
for v in vectors:
    word=int(v['input'],16);f=d=word;phases=[]
    for _ in range(4):
        f=reconstruction.forward(f);d=reconstruction.inverse(d);phases += [f,d]
    rows.append(f"{word:08x} {v['mode']} {v['expected']} "+' '.join(f'{x:08x}' for x in phases)+'\n')
(out/'vectors.txt').write_text(''.join(rows))
forward=[None]*32
for (name,bit),dest in reconstruction.rom_to_word.items():forward[dest]=model.memories[name]['outputs'][2*bit]
forward_expression='{'+', '.join('dut.recovered.'+n for n in reversed(forward))+'}'
inverse_expression='{'+', '.join('dut.recovered.'+n for n in reversed(reconstruction.working))+'}'
bench='''`timescale 1ns/1ps
module tb;
reg SCK=0,RST_N=0,MOSI=0,NORM_CS_N=1,START=0,ENC_DEC=0;
wire MISO,BUSY,ICE_LED;
protocol_dut dut(.*);
wire [31:0] forward_state=FORWARD_EXPR;
wire [31:0] inverse_state=INVERSE_EXPR;
reg [31:0] input_word,expected,observed,fp[0:3],dp[0:3];
integer f,scan,mode,b,r,cases=0,checks=0,phase_checks=0;
task tick;begin #5;SCK=1;#5;SCK=0;#1;end endtask
initial begin
  f=$fopen("vectors.txt","r");if(!f)$fatal(1,"missing vectors");
  while(!$feof(f)) begin
    scan=$fscanf(f,"%h %d %h %h %h %h %h %h %h %h %h\\n",input_word,mode,expected,fp[0],dp[0],fp[1],dp[1],fp[2],dp[2],fp[3],dp[3]);
    if(scan!=11)$fatal(1,"invalid vector record %0d",scan);
    RST_N=0;START=0;NORM_CS_N=1;MOSI=0;ENC_DEC=mode;tick;tick;
    RST_N=1;NORM_CS_N=0;
    for(b=31;b>=0;b=b-1)begin MOSI=input_word[b];tick;end
    NORM_CS_N=1;MOSI=0;
    for(r=0;r<4;r=r+1)begin
      START=(r==0);tick;
      if(forward_state!==fp[r] || inverse_state!==dp[r])
        $fatal(1,"round mismatch case=%0d mode=%0d round=%0d forward=%h/%h inverse=%h/%h",cases,mode,r,forward_state,fp[r],inverse_state,dp[r]);
      phase_checks=phase_checks+2;
      if(BUSY!==(r<3))$fatal(1,"BUSY phase mismatch");
      checks=checks+1;
    end
    START=0;repeat(4)tick;
    NORM_CS_N=0;observed=0;
    for(b=0;b<32;b=b+1)begin tick;observed={observed[30:0],MISO};end
    if(observed!==expected)$fatal(1,"serial mismatch input=%h mode=%0d actual=%h expected=%h",input_word,mode,observed,expected);
    cases=cases+1;checks=checks+1;
  end
  $fclose(f);
  $display("PASS transactions=%0d phase_checks=%0d serial_and_busy_checks=%0d failures=0",cases,phase_checks,checks);
  $finish;
end
endmodule
'''.replace('FORWARD_EXPR',forward_expression).replace('INVERSE_EXPR',inverse_expression)
(out/'tb_original_reconstruction.sv').write_text(bench)
commands=[['iverilog','-g2012','-s','tb','-o','simulation.vvp',str(ROOT/'sources/baseline.v'),str(ROOT/'sources/cells_sim.v'),str(ROOT/'sources/baseline_protocol_dut.sv'),'tb_original_reconstruction.sv'],['vvp','simulation.vvp']]
receipt={'started_utc':datetime.now(timezone.utc).isoformat(),'original_sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'sources').iterdir() if p.is_file()},'steps':[]}
for index,cmd in enumerate(commands):
    cmd[0]=str(args.suite.resolve()/cmd[0]);start=time.monotonic()
    try:
        proc=subprocess.run(cmd,cwd=out,capture_output=True,text=True,timeout=240)
        stdout,stderr,code=proc.stdout,proc.stderr,proc.returncode
    except subprocess.TimeoutExpired as error:
        stdout=error.stdout or b'';stderr=error.stderr or b''
        if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
        if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
        stderr+='\nTIMEOUT after 240 seconds\n';code=124
    (out/f'{index}.stdout').write_text(stdout);(out/f'{index}.stderr').write_text(stderr)
    receipt['steps'].append({'command':cmd,'exit_code':code,'elapsed_seconds':round(time.monotonic()-start,3)})
    (out/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if code:raise SystemExit(code)
assert f'PASS transactions={len(vectors)} ' in (out/'1.stdout').read_text()
receipt.update(status='PASS',transactions=len(vectors),phase_checks=len(vectors)*8,serial_and_busy_checks=len(vectors)*5,failures=0,ended_utc=datetime.now(timezone.utc).isoformat())
(out/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('steps','original_sources')},indent=2))
