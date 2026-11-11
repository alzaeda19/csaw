from pathlib import Path
import json,math,hashlib,csv,collections,os,subprocess,datetime
R=Path(__file__).resolve().parent
def rd(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=rd(R/'RESULTS.json');labels={r['design_id']:r['target'] for r in rd(R/'records/truth_labels.json')['labels']};inputs=rd(R/'records/inference_inputs.json')['inputs'];models=rd(R/'records/expected_model_loads.json');vocab=rd(R/'records/expected_feature_vocabulary.json')
assert len(results['designs'])==23 and collections.Counter(labels.values())=={0:9,1:14}
assert len({d['design_id'] for d in results['designs']})==23
checks=[];confusions={k:{x:0 for x in ['TP','FN','FP','TN']} for k in ['HT1','HT2','HT3','HT4','ensemble']};scored=0
for d in results['designs']:
 ident=d['design_id'];run=R/'runs'/ident;receipt=rd(R/d['command_receipt']);row=next(i for i in inputs if i['design_id']==ident)
 assert d['truth']==labels[ident] and sha(R/row['source_path'])==row['sha256'] and receipt['worker_sha256']==sha(R/'evaluate_one.py')
 for stream in ['stdout','stderr']:assert sha(R/'records'/ident/(stream+'.txt'))==receipt[stream+'_sha256']
 if d['status']!='scored':
  assert d['ensemble'] is None and all(v is None for v in d['per_model'].values());checks.append({'design_id':ident,'status':'unscored','failures_preserved':True});continue
 scored+=1;assert receipt['exit_code']==0 and receipt['parent_failure_reason'] is None
 assert rd(run/'model_loads.json')==models and rd(run/'feature_vocabulary.json')==vocab and sha(run/'graph_input/topModule.v')==row['sha256']
 mi=rd(run/'model_input.json');g=rd(run/'graph_before_normalization.json');prep=d['preprocessing']
 assert len(g['nodes'])==prep['graph_nodes']==mi['num_nodes']==len(mi['x']) and len(g['edges'])==prep['graph_edges']==mi['num_edges']
 assert len(g['nodes'])>1 and len(g['edges'])>0 and all(0<=x<37 for x in mi['x'])
 assert all(0<=n<mi['num_nodes'] for a in mi['edge_index'] for n in a)
 for name,p in d['per_model'].items():
  logits=p['logits'];offset=max(logits);e=[math.exp(x-offset) for x in logits];probs=[x/sum(e) for x in e]
  assert all(math.isfinite(x) for x in logits+p['log_probabilities']+[p['prob_clean'],p['prob_trojan']])
  assert abs(probs[0]-p['prob_clean'])<1e-6 and abs(probs[1]-p['prob_trojan'])<1e-6
  assert all(abs(math.exp(x)-q)<1e-6 for x,q in zip(p['log_probabilities'],[p['prob_clean'],p['prob_trojan']]))
  assert p['prediction']==max(range(2),key=lambda k:logits[k])
 assert d['ensemble']['prediction']==int(any(x['prediction']==1 for x in d['per_model'].values())) and d['ensemble']['trojan_votes']==sum(x['prediction'] for x in d['per_model'].values())
 for name in confusions:
  pred=d['ensemble']['prediction'] if name=='ensemble' else d['per_model'][name]['prediction'];key=('T' if pred==d['truth'] else 'F')+('P' if pred else 'N');confusions[name][key]+=1
 checks.append({'design_id':ident,'status':'scored','all_checks_pass':True,'route':prep['route']})
for name,c in confusions.items():
 m=results['metrics'][name];assert all(m[k]==v for k,v in c.items());assert m['scored_designs']==scored
 assert m['scored_positive_denominator']==c['TP']+c['FN'] and m['scored_negative_denominator']==c['FP']+c['TN']
 if c['TP']+c['FN']:assert abs(m['recall_on_scored']-c['TP']/(c['TP']+c['FN']))<1e-12
 if c['FP']+c['TN']:assert abs(m['false_positive_rate_on_scored']-c['FP']/(c['FP']+c['TN']))<1e-12
assert results['coverage']['scored']==scored and results['coverage']['unscored']==23-scored
csvrows=list(csv.DictReader((R/'per_design_model.csv').open()));assert len(csvrows)==92 and len({(x['design_id'],x['model']) for x in csvrows})==92
preserve=[]
for r in rd(R/'records/package_manifest.json'):
 for p in [Path(r['source']),R/r['copy']]:assert sha(p)==r['sha256'];preserve.append({'path':str(p),'sha256':r['sha256'],'unchanged':True})
for r in inputs:preserve.append({'path':str(R/r['source_path']),'sha256':sha(R/r['source_path']),'unchanged':sha(R/r['source_path'])==r['sha256']})
outer=Path('/Users/al-zayedal-hassan/Downloads/TrojanGYM_AES_Course_Package.zip');assert sha(outer)=='3912fd8e7afca470b57132c5af34215967c1b0e579ef2c0bc345de6a448c2832';preserve.append({'path':str(outer),'sha256':sha(outer),'unchanged':True})
env=os.environ.copy();env['GIT_OPTIONAL_LOCKS']='0'
def git(a):
 p=subprocess.run(['git','-C','/Users/al-zayedal-hassan/Documents/llm4chipdesign-hw']+a,capture_output=True,text=True,env=env);return {'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
repo={'status':git(['status','--porcelain=v1']),'head':git(['rev-parse','HEAD'])};assert repo==rd(R/'records/repository_before.json')
policy=rd(R/'records/EVALUATION_POLICY.json');assert all(sha(R/n)==h for n,h in policy['source_hashes'].items())
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_pass':True,'design_checks':checks,'model_rows':92,'scored_designs':scored,'recomputed_confusions':confusions,'preservation_checks':len(preserve),'repository_unchanged':True,'frozen_runner_hashes_match':True,'no_inference_rerun':True}
(R/'records/RESULT_VERIFICATION.json').write_text(json.dumps(record,indent=2)+'\n');(R/'records/preservation_check.json').write_text(json.dumps({'utc':record['utc'],'checks':preserve,'repository_after':repo,'all_match':True},indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='design_checks'},indent=2))
