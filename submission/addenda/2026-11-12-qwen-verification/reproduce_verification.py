"""Reproduce analysis of existing frozen designs in a fresh directory; no AI generation or network."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

SOURCE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--yosys',type=Path,required=True,help='Path to a compatible installed Yosys executable')
parser.add_argument('--output',type=Path,help='New, nonexistent output directory; defaults to a temporary directory')
args=parser.parse_args()
assert args.yosys.is_file()
out=args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='csaw-verification-'))
if args.output:out.mkdir(parents=True,exist_ok=False)
for name in ['sources','scripts']:
    shutil.copytree(SOURCE/name,out/name)
for name in ['formal','synthesis','analysis','records']:(out/name).mkdir()
shutil.copyfile(SOURCE/'records/SOURCE_MANIFEST.json',out/'records/SOURCE_MANIFEST.json')
for name in ['formal','synthesis']:
    for p in (SOURCE/name).iterdir():
        if p.is_file() and p.suffix in ('.ys','.sv'):shutil.copyfile(p,out/name/p.name)
commands=[]
def run(argv):
    p=subprocess.run(argv,cwd=out,text=True,capture_output=True,timeout=240)
    commands.append({'argv':argv,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    (out/'records/REPRODUCTION_COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    if p.returncode:raise RuntimeError('Verification step failed; see '+str(out/'records/REPRODUCTION_COMMANDS.json'))
for kind in ['baseline','modified']:
    run([sys.executable,str(out/'scripts/run_yosys.py'),str(out/'synthesis'/f'{kind}.ys'),str(out/'synthesis'/kind),'--yosys',str(args.yosys.resolve())])
for script in ['audit_memory_and_overhead.py','compare_standard_substitution.py']:
    run([sys.executable,str(out/'scripts'/script)])
for kind in ['normal','control_allow_fault','control_trace','edge_normal','edge_control','cyclic_induction','cyclic_control']:
    run([sys.executable,str(out/'scripts/run_yosys.py'),str(out/'formal'/f'{kind}.ys'),str(out/'formal'/kind),'--yosys',str(args.yosys.resolve()),'--timeout','120'])
run([sys.executable,str(out/'scripts/check_results.py')])
report={'status':'PASS','finished_utc':datetime.now(timezone.utc).isoformat(),'output':str(out),'steps':len(commands),'generation_performed':False,'network_used':False,'new_model_calls':False,'scope':'Reproducible synthesis/resource accounting, original table properties and bounded edge-explicit and unbounded synchronous cyclic compositional checks of existing files; not an automated historical generation pipeline.'}
(out/'records/REPRODUCTION_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
