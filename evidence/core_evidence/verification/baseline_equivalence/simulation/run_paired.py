#!/usr/bin/env python3
"""Independent simulations and unmasked nine-port trace comparisons; write only here."""
from pathlib import Path
import datetime, hashlib, json, platform, re, shutil, subprocess, sys

B=Path(__file__).resolve().parent
E=B.parent
R=E.parent
SUITE=R/'synthesis_fit_timing_2026-11-06/tooling/oss-cad-suite'
PORTS=['SCK','RST_N','MOSI','NORM_CS_N','START','ENC_DEC','MISO','BUSY','ICE_LED']
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ident(p):
    data=p.read_bytes()
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def save(p,data): p.write_text(json.dumps(data,indent=2)+'\n')
commands=[]
def run(argv,cwd,label,timeout=180):
    entry={'argv':[str(x) for x in argv],'cwd':str(cwd),'started_utc':now()}
    try:
        p=subprocess.run(entry['argv'],cwd=cwd,capture_output=True,timeout=timeout)
        entry.update(returncode=p.returncode)
        out,err=p.stdout,p.stderr
    except Exception as exc:
        entry.update(returncode=None,error=str(exc))
        out,err=b'',str(exc).encode()
    entry['finished_utc']=now()
    (cwd/(label+'.stdout')).write_bytes(out)
    (cwd/(label+'.stderr')).write_bytes(err)
    commands.append(entry)
    save(B/'records/commands.json',commands)
    return entry,out.decode(errors='replace')

def normalized_vcd(path):
    """Final values at each time step; retain x/z and all nine ports, no filtered window."""
    codes={};current={p:'x' for p in PORTS};rows=[];timestamp=0;started=False
    def append():
        row=[timestamp]+[current[p] for p in PORTS]
        if not rows or row[1:]!=rows[-1][1:]:rows.append(row)
    for raw in path.read_text().splitlines():
        line=raw.strip()
        if line.startswith('$var '):
            parts=line.split()
            if parts[4] in PORTS:
                if parts[2]!='1':raise ValueError('non-scalar IO declaration')
                codes[parts[3]]=parts[4]
        if line=='$enddefinitions $end':started=True;continue
        if not started:continue
        if line.startswith('#'):
            append();timestamp=int(line[1:])
        elif line and line[0] in '01xz' and line[1:] in codes:
            current[codes[line[1:]]]=line[0]
    append()
    assert set(codes.values())==set(PORTS),codes
    return rows

def compare_vcd(a,b):
    ia=ib=0;va=['x']*len(PORTS);vb=va.copy();mismatches=[];compared=0
    for t in sorted({x[0] for x in a}|{x[0] for x in b}):
        while ia<len(a) and a[ia][0]<=t:va=a[ia][1:];ia+=1
        while ib<len(b) and b[ib][0]<=t:vb=b[ib][1:];ib+=1
        compared+=1
        if va!=vb:mismatches.append({'time_ps':t,'baseline':dict(zip(PORTS,va)),'decoded':dict(zip(PORTS,vb))})
    return {'union_timestamps':compared,'mismatches':mismatches,'equal':not mismatches}

def main():
    started=now()
    src=B/'sources'
    mapping={
      'baseline.v':E/'inputs/baseline.v',
      'baseline_protocol_dut.sv':E/'inputs/protocol_dut.sv',
      'regenerated_compatible.v':E/'decode/regenerated_compatible.v',
      'regenerated_protocol_dut.sv':E/'decode/regenerated_protocol_dut.sv',
      'cells_sim.v':SUITE/'share/yosys/ice40/cells_sim.v',
      'reference_normal_tb.sv':R/'baseline_confirmation_2026-11-06/tb/normal_tb.sv',
      'original_host.py':R/'original_materials/qualifier/spi_ice40_crypto_ip_test.py',
      'original_interface.md':R/'original_materials/qualifier/ice40_cryptographic_IP.md',
      'original_source_receipt.json':R/'original_materials/SOURCE_RECEIPT.json'}
    before={}
    for name,p in mapping.items():
        before[str(p)]=ident(p)
        shutil.copyfile(p,src/name)
    save(B/'records/source_manifest.json',{'copied_utc':now(),'files':{name:{'source':str(p),**ident(src/name)} for name,p in mapping.items()},'bench':ident(src/'paired_normal_tb.sv')})
    save(B/'records/environment.json',{'python':sys.version,'platform':platform.platform(),'started_utc':started,'no_hardware':True,'stimulus_classification':'original P/C known-answer only; arbitrary words are equivalence stimulus, not cipher oracle'})
    for tool in ['iverilog','vvp']:
        entry,_=run([SUITE/'bin'/tool,'-V'],B/'records',tool+'_version')
        if entry['returncode']!=0:raise RuntimeError('version command failed')
    for model in ['baseline','decoded']:
        d=B/'runs'/model;d.mkdir()
        sources=['baseline.v','baseline_protocol_dut.sv'] if model=='baseline' else ['regenerated_compatible.v','regenerated_protocol_dut.sv']
        entry,_=run([SUITE/'bin/iverilog','-g2012','-DNO_ICE40_DEFAULT_ASSIGNMENTS','-Wall','-s','paired_normal_tb','-o',d/'sim.vvp',src/'paired_normal_tb.sv',*[src/x for x in sources],src/'cells_sim.v'],d,'compile')
        if entry['returncode']!=0:raise RuntimeError(model+' compile failed')
    cases=[('host_50khz',10000000,0,0),('host_1mhz',500000,0,0),('paused_host_1mhz',500000,0,1),('immediate_read_1mhz',500000,1,0)]
    results=[]
    for name,half,immediate,pauses in cases:
        case={'case':name,'half_ps':half,'sample_ps':1000,'immediate':immediate,'pauses':pauses,'models':{}}
        for model in ['baseline','decoded']:
            d=B/'runs'/model/name;d.mkdir()
            entry,text=run([SUITE/'bin/vvp','-n',d.parent/'sim.vvp',f'+half_ps={half}','+sample_ps=1000',f'+immediate={immediate}',f'+pauses={pauses}'],d,'simulate')
            m={'returncode':entry['returncode'],'completion':re.findall(r'^COMPLETE .*$',text,re.M),'failed_checks':re.findall(r'^CHECK .* FAIL .*$',text,re.M),'latencies':re.findall(r'^LATENCY .*$',text,re.M),'values':re.findall(r'^VALUE .*$',text,re.M)}
            m['known_match_count']=len(re.findall(r'^VALUE .*known=1 .*known_match=1 ',text,re.M))
            m['known_mismatch_count']=len(re.findall(r'^VALUE .*known=1 .*known_match=0 ',text,re.M))
            if (d/'pins.vcd').exists():
                normalized=normalized_vcd(d/'pins.vcd')
                (d/'pins_normalized.csv').write_text(','.join(['time_ps']+PORTS)+'\n'+''.join(','.join(map(str,row))+'\n' for row in normalized))
            case['models'][model]=m
            save(d/'result.json',m)
        a=B/'runs/baseline'/name;b=B/'runs/decoded'/name
        at=(a/'io_trace.csv').read_text().splitlines();bt=(b/'io_trace.csv').read_text().splitlines()
        mismatches=[{'line':i+1,'baseline':at[i] if i<len(at) else None,'decoded':bt[i] if i<len(bt) else None} for i in range(max(len(at),len(bt))) if i>=len(at) or i>=len(bt) or at[i]!=bt[i]]
        vcd=compare_vcd(normalized_vcd(a/'pins.vcd'),normalized_vcd(b/'pins.vcd'))
        case['settled_checkpoint_comparison']={'baseline_rows':len(at)-1,'decoded_rows':len(bt)-1,'equal':not mismatches,'mismatch_count':len(mismatches)}
        case['full_pin_trace_comparison']={k:v for k,v in vcd.items() if k!='mismatches'}
        case['full_pin_trace_comparison']['mismatch_count']=len(vcd['mismatches'])
        case['latencies_equal']=case['models']['baseline']['latencies']==case['models']['decoded']['latencies']
        case['values_equal']=case['models']['baseline']['values']==case['models']['decoded']['values']
        save(B/'records'/(name+'_checkpoint_mismatches.json'),mismatches)
        save(B/'records'/(name+'_full_pin_mismatches.json'),vcd['mismatches'])
        case['pass']=not mismatches and vcd['equal'] and all(m['returncode']==0 and m['completion'] and not m['failed_checks'] for m in case['models'].values())
        results.append(case)
        save(B/'records/case_results.json',results)
        print(name,case['pass'],'checkpoint mismatches',len(mismatches),'full pin mismatches',len(vcd['mismatches']),flush=True)
    after={str(p):ident(p) for p in mapping.values()}
    save(B/'records/input_preservation.json',{'before':before,'after':after,'unchanged':before==after})
    summary={'started_utc':started,'finished_utc':now(),'all_cases_pass':all(c['pass'] for c in results),'input_sources_unchanged':before==after,'cases':[{'name':c['case'],'pass':c['pass'],'checkpoints':c['settled_checkpoint_comparison'],'full_pin_trace':c['full_pin_trace_comparison'],'values_equal':c['values_equal'],'latencies_equal':c['latencies_equal'],'known_matches_baseline':c['models']['baseline']['known_match_count'],'known_mismatches_baseline':c['models']['baseline']['known_mismatch_count']} for c in results],
      'scope':'Finite nine-functional-port behavioral regression of baseline RTL against decoded regenerated baseline bitstream. Not formal equivalence, independent cipher validation, or board validation.',
      'trace_policy':'All nine ports from time zero through completion. Checkpoints before/after rising/falling clocks, CS/START transitions and pauses. Full VCD compared after delta-cycle settling at every union timestamp, retaining x/z with no masks or ignored initialization window.',
      'primitive_model':'Unmodified OSS CAD Suite Yosys cells_sim.v; real SB_RAM40_4K INIT/address/RE/RCLKE/RCLK semantics. NO_ICE40_DEFAULT_ASSIGNMENTS permits Icarus syntax; no functional cells replaced.'}
    save(B/'SUMMARY.json',summary)
    hashes={str(p.relative_to(B)):ident(p) for p in sorted(B.rglob('*')) if p.is_file() and p.name!='output_hashes.json'}
    save(B/'records/output_hashes.json',hashes)
    print(json.dumps(summary,indent=2))
    return 0 if summary['all_cases_pass'] and before==after else 1
if __name__=='__main__':sys.exit(main())
