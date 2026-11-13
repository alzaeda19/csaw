"""Replay original-only reconstruction in a new folder; no model/network calls."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil,subprocess,sys,time

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--suite',type=Path,required=True,help='Directory containing Icarus and VVP')
p.add_argument('--output',type=Path,required=True,help='New directory, must not exist')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
for directory in ['sources','scripts']:
    shutil.copytree(ROOT/directory,out/directory,ignore=shutil.ignore_patterns('__pycache__'))
for directory in ['analysis','verification']: (out/directory).mkdir()
steps=[['baseline_model.py'],['reconstruct_cipher.py'],['verify_icarus.py','--suite',str(a.suite.resolve()),'--output',str(out/'verification/icarus_run')]]
receipt={'started_utc':datetime.now(timezone.utc).isoformat(),'network_accessed':False,'model_called':False,'modified_RTL_used':False,'steps':[]}
for index,parts in enumerate(steps):
    command=[sys.executable,str(out/'scripts'/parts[0]),*parts[1:]];start=time.monotonic()
    try:
        r=subprocess.run(command,capture_output=True,text=True,timeout=300)
        code=r.returncode;stdout=r.stdout;stderr=r.stderr
    except subprocess.TimeoutExpired as error:
        code=124;stdout=error.stdout or b'';stderr=error.stderr or b''
        if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
        if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
        stderr+='\nTIMEOUT after 300 seconds\n'
    (out/f'{index}.stdout').write_text(stdout);(out/f'{index}.stderr').write_text(stderr)
    receipt['steps'].append({'command':command,'exit_code':code,'elapsed_seconds':round(time.monotonic()-start,3)})
    (out/'REPRODUCTION_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if code:raise SystemExit(code)
expected=['analysis/INITIAL_MODEL_TRACE.json','analysis/RECONSTRUCTION_RESULTS.json','verification/VECTORS.json','verification/vectors.txt']
receipt['result_matches']={name:(out/name).read_bytes()==(ROOT/name).read_bytes() for name in expected}
assert all(receipt['result_matches'].values())
receipt.update(status='PASS',ended_utc=datetime.now(timezone.utc).isoformat())
(out/'REPRODUCTION_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
