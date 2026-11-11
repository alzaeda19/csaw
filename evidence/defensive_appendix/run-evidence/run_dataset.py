#!/usr/bin/env python3
"""Bounded one-pass controller; joins archive labels only after frozen inference."""
import os,sys,json,hashlib,subprocess,signal,time,datetime,csv,collections,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PYTHON=Path('/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runtime/venv/bin/python')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def group_rss_kib(pgid):
 p=subprocess.run(['/bin/ps','-axo','pgid=,rss='],capture_output=True,text=True,timeout=3)
 if p.returncode:raise RuntimeError('RSS monitor failed: '+p.stderr)
 return sum(int(s[1]) for l in p.stdout.splitlines() if len(s:=l.split())==2 and int(s[0])==pgid)
def one(row):
 ident=row['design_id'];out=ROOT/'records'/ident;out.mkdir()
 if not row['eligible']:
  return {'design_id':ident,'status':'unscored','reason':'static_screen_rejected','screen_reasons':row['rejection_reasons'],'exit_code':None,'per_model':{k:None for k in ['HT1','HT2','HT3','HT4']},'ensemble':None}
 env=os.environ.copy();env.pop('PYTHONNOUSERSITE',None);env.pop('PYTHONPATH',None)
 tmp=ROOT/'runtime/tmp'/ident;tmp.mkdir();mpl=ROOT/'runtime/matplotlib'/ident;mpl.mkdir();cache=ROOT/'runtime/cache'/ident;cache.mkdir()
 overrides={'PYTHONDONTWRITEBYTECODE':'1','MPLBACKEND':'Agg','MPLCONFIGDIR':str(mpl),'TMPDIR':str(tmp),'XDG_CACHE_HOME':str(cache),'PATH':str(PYTHON.parent)+':/opt/homebrew/bin:'+os.environ.get('PATH','')};env.update(overrides)
 argv=[str(PYTHON),str(ROOT/'evaluate_one.py'),ident];start=now();begin=time.monotonic();reason=None;peak=0;samples=0
 with (out/'stdout.txt').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
  process=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
  try:
   while process.poll() is None:
    rss=group_rss_kib(process.pid);peak=max(peak,rss);samples+=1
    if rss>2097152:reason='process_group_rss_exceeded_2_GiB';break
    if time.monotonic()-begin>75:reason='worker_wall_timeout_75_seconds';break
    time.sleep(.2)
  except BaseException as e:reason='parent_monitor_error:'+type(e).__name__+':'+str(e)
  finally:
   if reason:
    try:os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:pass
   exit_code=process.wait()
   try:os.killpg(process.pid,signal.SIGKILL)
   except ProcessLookupError:pass
 receipt={'design_id':ident,'argv':argv,'cwd':str(ROOT),'environment_overrides':overrides,'environment_removed':['PYTHONNOUSERSITE','PYTHONPATH'],'start_utc':start,'finish_utc':now(),'elapsed_seconds':time.monotonic()-begin,'exit_code':exit_code,'parent_failure_reason':reason,'peak_observed_process_group_rss_kib':peak,'rss_samples':samples,'rss_poll_seconds':.2,'worker_wall_limit_seconds':75,'graph_extraction_limit_seconds':30,'group_rss_limit_kib':2097152,'memory_limit_note':'Parent sampled process-group RSS guard; not a kernel-enforced address-space limit.','process_group_cleanup_attempted':True,'stdout_sha256':sha(out/'stdout.txt'),'stderr_sha256':sha(out/'stderr.txt'),'worker_sha256':sha(ROOT/'evaluate_one.py')};save(out/'command.json',receipt)
 result=ROOT/'runs'/ident/'RESULTS.json';failure=ROOT/'runs'/ident/'FAILURE.json'
 if exit_code==0 and reason is None and result.exists():
  data=json.loads(result.read_text());assert data['status']=='scored' and set(data['per_model'])=={'HT1','HT2','HT3','HT4'}
 else:
  data=json.loads(failure.read_text()) if failure.exists() else {'design_id':ident,'status':'unscored','error_type':reason or 'worker_nonzero_or_missing_result','error':'No complete valid four-model result'}
  data.update(status='unscored',per_model={k:None for k in ['HT1','HT2','HT3','HT4']},ensemble=None)
 data.update(command_receipt=str((out/'command.json').relative_to(ROOT)),exit_code=exit_code,parent_failure_reason=reason)
 save(out/'outcome.json',data);print('FINISHED',ident,data['status'],data.get('preprocessing',{}).get('route'),flush=True);return data
if __name__=='__main__':
 lock=ROOT/'records/EVALUATION_STARTED.json'
 with lock.open('x') as f:json.dump({'start_utc':now(),'controller_sha256':sha(Path(__file__)),'worker_sha256':sha(ROOT/'evaluate_one.py'),'policy_sha256':sha(ROOT/'records/EVALUATION_POLICY.json')},f,indent=2)
 inputs=json.loads((ROOT/'records/inference_inputs.json').read_text())['inputs'];assert len(inputs)==23 and len({r['design_id'] for r in inputs})==23
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:outcomes=list(pool.map(one,inputs))
 labels={r['design_id']:r['target'] for r in json.loads((ROOT/'records/truth_labels.json').read_text())['labels']}
 designs={r['design_id']:r for r in json.loads((ROOT/'records/dataset_manifest.json').read_text())['designs']}
 assert collections.Counter(labels.values())=={0:9,1:14}
 rows=[]
 for outcome in outcomes:
  outcome['truth']=labels[outcome['design_id']];outcome['archive_metadata']=designs[outcome['design_id']]
  for model in ['HT1','HT2','HT3','HT4']:
   value=outcome['per_model'][model]
   rows.append({'design_id':outcome['design_id'],'truth':outcome['truth'],'model':model,'status':outcome['status'],'prediction':value['prediction'] if value else None,'prob_clean':value['prob_clean'] if value else None,'prob_trojan':value['prob_trojan'] if value else None,'graph_route':outcome.get('preprocessing',{}).get('route'),'exit_code':outcome.get('exit_code')})
 scored=[r for r in outcomes if r['status']=='scored'];metrics={}
 for model in ['HT1','HT2','HT3','HT4','ensemble']:
  tp=fn=fp=tn=0
  for r in scored:
   pred=r['ensemble']['prediction'] if model=='ensemble' else r['per_model'][model]['prediction'];truth=r['truth']
   tp+=truth==1 and pred==1;fn+=truth==1 and pred==0;fp+=truth==0 and pred==1;tn+=truth==0 and pred==0
  metrics[model]={'TP':tp,'FN':fn,'FP':fp,'TN':tn,'scored_designs':len(scored),'total_designs':23,'scored_positive_denominator':tp+fn,'total_positive_designs':14,'scored_negative_denominator':fp+tn,'total_negative_designs':9,'recall_on_scored':tp/(tp+fn) if tp+fn else None,'false_positive_rate_on_scored':fp/(fp+tn) if fp+tn else None,'unscored_positive':14-tp-fn,'unscored_negative':9-fp-tn}
 routes=dict(collections.Counter(r['preprocessing']['route'] for r in scored));statuses=collections.Counter()
 for r in outcomes:
  p=ROOT/'runs'/r['design_id']/'exact_extraction.json'
  statuses[json.loads(p.read_text())['status'] if p.exists() else 'not_reached']+=1
 results={'completed_utc':now(),'designs':outcomes,'coverage':{'total':23,'scored':len(scored),'unscored':23-len(scored),'model_rows':len(rows),'scored_model_rows':4*len(scored),'scored_routes':routes,'exact_extraction_status_counts':dict(statuses)},'metrics':metrics,'limits':['Directory labels are supplied dataset annotations, not independently validated behavior.','Repeated families and unknown checkpoint training overlap; not held-out accuracy.','Heuristic scores, if present, have reduced semantic coverage.','No payload simulation, generation, model training, threshold tuning or retry.','Previous AES/CSAW examples excluded from all23-design denominators.']};save(ROOT/'RESULTS.json',results);save(ROOT/'METRICS.json',{'coverage':results['coverage'],'metrics':metrics})
 with (ROOT/'per_design_model.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print('DATASET_COMPLETE',json.dumps(results['coverage']),flush=True)
