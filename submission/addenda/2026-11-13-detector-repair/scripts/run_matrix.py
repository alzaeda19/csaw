"""Bound all four predeclared representation attempts and preserve each result."""
from pathlib import Path
import os,json,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
PYTHON=os.environ.get('CSAW_DETECTOR_PYTHON','/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runtime/venv/bin/python')
SUITE=os.environ.get('CSAW_TOOL_SUITE','/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/synthesis_fit_timing_2026-11-06/tooling/oss-cad-suite/bin')
env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',PYTHONPATH=str(ROOT/'package/hw2vec'),PATH=SUITE+':'+env.get('PATH',''))
for key,sub in [('MPLCONFIGDIR','mpl'),('TMPDIR','tmp'),('XDG_CACHE_HOME','cache')]:
 p=ROOT/'runtime'/sub;p.mkdir(exist_ok=True);env[key]=str(p)
records=[]
for name in ['raw_clean','raw_modified','flat_clean','flat_modified']:
 cmd=[PYTHON,str(ROOT/'scripts/run_detectors.py'),name];start=time.monotonic()
 with (ROOT/'records'/f'{name}.stdout').open('wb') as out,(ROOT/'records'/f'{name}.stderr').open('wb') as err:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=out,stderr=err,start_new_session=True)
  try:code=proc.wait(timeout=165);status='completed' if code==0 else 'failed'
  except subprocess.TimeoutExpired:
   import signal
   os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   code=124;status='process_timeout'
 record={'candidate':name,'command':cmd,'exit_code':code,'status':status,'elapsed_seconds':time.monotonic()-start,'process_timeout_seconds':165}
 records.append(record);(ROOT/'records/DETECTOR_COMMANDS.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(record),flush=True)
