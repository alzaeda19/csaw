"""Same protocol traces on frozen originals and predeclared detector representations."""
from pathlib import Path
import subprocess,json,hashlib,random,time,os
ROOT=Path(__file__).resolve().parents[1]
SUITE=Path(os.environ.get('CSAW_TOOL_SUITE','/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/synthesis_fit_timing_2026-11-06/tooling/oss-cad-suite/bin'))
OUT=ROOT/'analysis/representation_validation';OUT.mkdir()
BIN=ROOT/'runtime/sim';BIN.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rng=random.Random(20261113)
words=list(dict.fromkeys([0,0xffffffff,0x59c359c3,0x9cd84392,0xc5a02026,0xaaaaaaaa,0x55555555]+[1<<i for i in range(32)]+[0xffffffff^(1<<i) for i in range(32)]+[rng.getrandbits(32) for _ in range(64)]))
vectors=[(w,m) for w in words for m in [0,1]]
(OUT/'vectors.txt').write_text(''.join(f'{w:08x} {m}\n' for w,m in vectors))
(OUT/'VECTOR_PLAN.json').write_text(json.dumps({'seed':20261113,'vectors':len(vectors),'words':len(words),'construction':'seven declared cases, walking ones/zeros, 64 seeded pseudorandom words; both modes; fixed before these simulations','positive_control':'Existing disclosed fault word in mode 0 included as a declared positive control, not independently discovered','reset':'Two synchronous reset clocks before each transaction','scope':'Fixed legal protocol only; finite representation validation, not universal equivalence or stealth'},indent=2)+'\n')
bench='''`timescale 1ns/1ps
module tb;
reg SCK=0,RST_N=0,MOSI=0,NORM_CS_N=1,START=0,ENC_DEC=0;
wire MISO,BUSY,ICE_LED;
DUT_MODULE dut(.*);
integer f,scan,mode,b,r,case_no=0,sample_no=0;
reg active=0;reg [31:0] word_in,observed;
task observe;begin
 if(active)begin
  $display("T %0d %0d %b%b%b",case_no,sample_no,MISO,BUSY,ICE_LED);
  if((^{MISO,BUSY,ICE_LED})===1'bx)$fatal(1,"unknown observed output");
  sample_no=sample_no+1;
 end
end endtask
task tick;begin #5;SCK=1;#1;observe;#4;SCK=0;#1;observe;end endtask
initial begin
 f=$fopen("vectors.txt","r");if(!f)$fatal(1,"missing vectors");
 while(!$feof(f))begin
  scan=$fscanf(f,"%h %d\\n",word_in,mode);if(scan!=2)$fatal(1,"bad vector");
  active=0;RST_N=0;START=0;NORM_CS_N=1;MOSI=0;ENC_DEC=mode;tick;tick;
  active=1;RST_N=1;NORM_CS_N=0;#1;observe;
  for(b=31;b>=0;b=b-1)begin MOSI=word_in[b];tick;end
  NORM_CS_N=1;MOSI=0;#1;observe;
  START=1;tick;START=0;repeat(7)tick;
  NORM_CS_N=0;#1;observe;observed=0;
  for(b=0;b<32;b=b+1)begin MOSI=(b%2);tick;observed={observed[30:0],MISO};end
  NORM_CS_N=1;#1;observe;
  $display("R %0d %08h %0d %08h",case_no,word_in,mode,observed);
  case_no=case_no+1;
 end
 $fclose(f);$display("PASS cases=%0d observed_samples=%0d",case_no,sample_no);$finish;
end
endmodule
'''
receipts=[];traces={};results={}
def run(cmd,label,timeout):
 start=time.monotonic()
 with (OUT/(label+'.stdout')).open('wb') as out,(OUT/(label+'.stderr')).open('wb') as err:
  q=subprocess.run([str(x) for x in cmd],cwd=OUT,stdout=out,stderr=err,timeout=timeout)
 receipts.append({'label':label,'command':[str(x) for x in cmd],'cwd':str(OUT),'exit_code':q.returncode,'seconds':time.monotonic()-start})
 (OUT/'COMMANDS.json').write_text(json.dumps(receipts,indent=2)+'\n')
 assert q.returncode==0,label
for kind,wrapper in [('clean','baseline_protocol_dut.sv'),('modified','modified_protocol_dut.sv')]:
 for form in ['original','raw','flat']:
  label=form+'_'+kind;tb=OUT/(label+'_tb.sv');tb.write_text(bench.replace('DUT_MODULE','protocol_dut' if form=='original' else 'top'))
  sources=[ROOT/'sources/cells_sim.v',ROOT/'sources/baseline.v',ROOT/'sources'/wrapper] if form=='original' else [ROOT/'detectors'/label/'topModule.v']
  binary=BIN/(label+'.vvp')
  run([SUITE/'iverilog','-g2012','-DNO_ICE40_DEFAULT_ASSIGNMENTS','-s','tb','-o',binary,*sources,tb],label+'_compile',60)
  run([SUITE/'vvp',binary],label+'_simulate',90)
  lines=(OUT/(label+'_simulate.stdout')).read_text().splitlines()
  traces[label]=[x for x in lines if x.startswith('T ')];results[label]=[x for x in lines if x.startswith('R ')]
  assert len(results[label])==len(vectors)
  assert any(x.startswith('PASS ') for x in lines)
checks=[]
for kind in ['clean','modified']:
 for form in ['raw','flat']:
  label=form+'_'+kind;original='original_'+kind
  mismatches=[i for i,(a,b) in enumerate(zip(traces[label],traces[original])) if a!=b]
  ok=not mismatches and len(traces[label])==len(traces[original]) and results[label]==results[original]
  checks.append({'candidate':label,'reference':original,'exact_observed_trace_match':ok,'samples':len(traces[label]),'transactions':len(vectors),'first_mismatches':mismatches[:10]})
  assert ok,label
differences=[]
for a,b in zip(results['original_clean'],results['original_modified']):
 if a!=b:
  x,y=a.split(),b.split();differences.append({'case':int(x[1]),'word':x[2],'mode':int(x[3]),'clean':x[4],'modified':y[4],'xor':f'{int(x[4],16)^int(y[4],16):08x}'})
assert len(differences)==1 and differences[0]['word'].lower()=='c5a02026' and differences[0]['mode']==0 and differences[0]['xor']=='80000000'
report={'status':'PASS','representation_comparisons':checks,'simulator_runs':6,'transactions_per_run':len(vectors),'full_core_positive_control':differences,'ordinary_transactions_without_serial_difference':len(vectors)-1,'outputs_checked':['MISO','BUSY','ICE_LED'],'observations':'After rising/falling edges and chip-select changes, after two reset edges; unknowns rejected','scope_limit':'Finite exact trace validation under listed reset/transaction schedule. Not universal HDL equivalence, timing analysis, or stealth evidence. Formal witness timing not replayed exactly.','output_hashes':{p.name:sha(p) for p in sorted(OUT.glob('*.stdout'))}}
(OUT/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
