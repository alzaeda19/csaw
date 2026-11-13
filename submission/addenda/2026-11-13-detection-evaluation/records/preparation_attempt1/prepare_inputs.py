"""Prepare fixed, identical analysis representations of frozen design inputs."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--suite',type=Path,required=True);a=p.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipts=[]
def run(cmd,cwd,label):
    start=time.monotonic()
    try:
        q=subprocess.run([str(x) for x in cmd],cwd=cwd,text=True,capture_output=True,timeout=180)
        code=q.returncode;out=q.stdout;err=q.stderr
    except subprocess.TimeoutExpired as x:
        code=124;out=x.stdout or b'';err=x.stderr or b''
        if isinstance(out,bytes):out=out.decode(errors='replace')
        if isinstance(err,bytes):err=err.decode(errors='replace')
        err+='\nTIMEOUT after180seconds\n'
    (cwd/(label+'.stdout')).write_text(out);(cwd/(label+'.stderr')).write_text(err)
    receipts.append({'command':[str(x) for x in cmd],'cwd':str(cwd),'exit_code':code,'elapsed_seconds':time.monotonic()-start,'label':label})
    (ROOT/'records/PREPARATION_COMMANDS.json').write_text(json.dumps(receipts,indent=2)+'\n')
    assert code==0,(label,code)
prep=ROOT/'analysis/preparation';prep.mkdir(exist_ok=False)
run([a.suite/'iverilog','-g2012','-E','-DNO_ICE40_DEFAULT_ASSIGNMENTS','-o',prep/'cells_preprocessed.v',ROOT/'sources/cells_sim.v'],prep,'primitive_preprocess')
cell_text=(prep/'cells_preprocessed.v').read_text();ram=re.search(r'(?m)^module SB_RAM40_4K\s*\(.*?^endmodule',cell_text,re.S)
assert ram
ram=ram.group(0)+'\n';(prep/'RAM_ONLY.v').write_text(ram)
results=[]
for name,wrapper in [('clean','baseline_protocol_dut.sv'),('modified','modified_protocol_dut.sv')]:
    rawdir=ROOT/'detectors'/('raw_'+name);rawdir.mkdir()
    wrapper_text,n=re.subn(r'\bmodule\s+protocol_dut\b','module top',(ROOT/'sources'/wrapper).read_text());assert n==1
    raw_text=wrapper_text+'\n'+(ROOT/'sources/baseline.v').read_text()+'\n'+ram
    # Explicit canonical top bypasses the supplied destructive underscore removal.
    rawfile=rawdir/'topModule.v';rawfile.write_text(raw_text)
    assert len(re.findall(r'(?m)^module\s+',raw_text))==3
    flatdir=ROOT/'detectors'/('flat_'+name);flatdir.mkdir()
    ys=ROOT/'synthesis'/f'{name}.ys'
    ys.write_text(f'''read_verilog -sv -DNO_ICE40_DEFAULT_ASSIGNMENTS sources/cells_sim.v sources/baseline.v sources/{wrapper}
hierarchy -check -top protocol_dut
flatten
proc
opt
memory
opt
check -assert
rename -top top
rename -unescape
write_verilog -noattr -nodec detectors/flat_{name}/topModule.v
write_json synthesis/{name}.json
tee -o synthesis/{name}_stats.json stat -json
''')
    run([a.suite/'yosys','-Q','-T','-s',ys],ROOT,f'synthesis/{name}')
    flatfile=flatdir/'topModule.v';net=json.loads((ROOT/'synthesis'/f'{name}.json').read_text());assert set(net['modules'])=={'top'}
    top=net['modules']['top'];assert all(c['type'].startswith('$') for c in top['cells'].values())
    assert not any(c['type'].startswith('$mem') for c in top['cells'].values())
    assert not top.get('memories')
    results.append({'design':name,'wrapper_sha256':sha(ROOT/'sources'/wrapper),'raw_file':str(rawfile.relative_to(ROOT)),'raw_sha256':sha(rawfile),'raw_modules':['top','chip','SB_RAM40_4K'],'flat_file':str(flatfile.relative_to(ROOT)),'flat_sha256':sha(flatfile),'flat_module_count':1,'flat_no_unresolved_hierarchy':True,'flat_memories_mapped_to_logic':True,'flat_cell_count':len(top['cells']),'ports':top['ports']})
report={'prepared_utc':datetime.now(timezone.utc).isoformat(),'identical_flow_for_both':True,'preprocessing_note':'topModule.v explicitly supplies the canonical top and bypasses HW2VEC global underscore stripping; detector backend and checkpoints unchanged. No classification outcome was used to choose representation.','behavioral_validation':'Separate Icarus representation comparison required before interpreting classifier results.','representations':results}
(ROOT/'analysis/REPRESENTATIONS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items() if k!='ports'} for x in results],indent=2))
