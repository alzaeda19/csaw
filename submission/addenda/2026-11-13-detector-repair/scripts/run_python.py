"""Use the existing native detector environment with isolated runtime directories."""
from pathlib import Path
import os,sys,subprocess,json,time
ROOT=Path(__file__).resolve().parents[1]
PYTHON=os.environ.get('CSAW_DETECTOR_PYTHON','/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runtime/venv/bin/python')
SUITE=os.environ.get('CSAW_TOOL_SUITE','/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/synthesis_fit_timing_2026-11-06/tooling/oss-cad-suite/bin')
label=sys.argv[1];args=sys.argv[2:];env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',PYTHONPATH=str(ROOT/'package/hw2vec'),PATH=SUITE+':'+env.get('PATH',''))
for key,sub in [('MPLCONFIGDIR','mpl'),('TMPDIR','tmp'),('XDG_CACHE_HOME','cache')]:
 p=ROOT/'runtime'/sub;p.mkdir(exist_ok=True);env[key]=str(p)
start=time.monotonic();cmd=[PYTHON,*args]
with (ROOT/'records'/f'{label}.stdout').open('w') as out,(ROOT/'records'/f'{label}.stderr').open('w') as err:
 q=subprocess.run(cmd,cwd=ROOT,env=env,stdout=out,stderr=err,timeout=240)
receipt={'command':cmd,'cwd':str(ROOT),'exit_code':q.returncode,'seconds':time.monotonic()-start}
(ROOT/'records'/f'{label}.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));raise SystemExit(q.returncode)
