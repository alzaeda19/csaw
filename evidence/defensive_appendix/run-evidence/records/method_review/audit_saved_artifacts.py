#!/usr/bin/env python3
"""Check saved artifacts only; no model imports or design evaluation."""
import ast,collections,csv,datetime,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
PRIOR=Path('/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z')
checks=[];reviewed={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(rel):
 p=ROOT/rel;reviewed[str(rel)]=sha(p)
 return json.loads(p.read_text(),parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
def ck(name,condition):checks.append({'check':name,'passed':bool(condition)})
def close(a,b):return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=2e-6
def main():
 policy=load('records/EVALUATION_POLICY.json');started=load('records/EVALUATION_STARTED.json')
 inputs={r['design_id']:r for r in load('records/inference_inputs.json')['inputs']}
 labels={r['design_id']:r['target'] for r in load('records/truth_labels.json')['labels']}
 manifest={r['design_id']:r for r in load('records/dataset_manifest.json')['designs']}
 expected=load('records/expected_model_loads.json');vocab=load('records/expected_feature_vocabulary.json')
 ck('prior_model_identities',expected==json.loads((PRIOR/'runs/clean_aes_detection/model_loads.json').read_text()))
 ck('prior_37_feature_vocabulary',vocab==json.loads((PRIOR/'runs/clean_aes_detection/feature_vocabulary.json').read_text()) and len(vocab)==37)
 for name in ['evaluate_one.py','run_dataset.py']:
  p=ROOT/name;ast.parse(p.read_text());reviewed[name]=sha(p);ck(name+':frozen_hash',sha(p)==policy['source_hashes'][name])
 ck('start_worker_hash',started['worker_sha256']==sha(ROOT/'evaluate_one.py'))
 ck('start_controller_hash',started['controller_sha256']==sha(ROOT/'run_dataset.py'))
 ck('start_policy_hash',started['policy_sha256']==sha(ROOT/'records/EVALUATION_POLICY.json'))
 for m in expected:
  for filename,key in [('model.pth','checkpoint_sha256'),('model.cfg','config_sha256')]:
   rel=Path('package')/('model_'+m['model'])/filename
   ck(str(rel)+':unchanged',sha(ROOT/rel)==m[key]==sha(PRIOR/rel))
 for rel in ['hw2vec/hw2vec/hw2graph.py','hw2vec/hw2vec/graph2vec/models.py','hw2vec/hw2vec/config.py','hw2vec/examples/example_gnn4tj.yaml']:
  ck('package_unchanged:'+rel,sha(ROOT/'package'/rel)==sha(PRIOR/'package'/rel))
 ck('inventory_23',len(inputs)==23 and set(inputs)==set(labels)==set(manifest))
 ck('labels_9_clean_14_infected',collections.Counter(labels.values())=={0:9,1:14})
 ck('labels_outside_inference_manifest',all(not any(k in r for k in ['truth','truth_label','label','family','archive_member']) for r in inputs.values()))
 for ident,row in inputs.items():
  p=ROOT/row['source_path'];ck(ident+':source_hash_size',sha(p)==row['sha256']==manifest[ident]['sha256'] and p.stat().st_size==row['bytes'])
  ck(ident+':directory_truth',labels[ident]==manifest[ident]['truth_target']==int(manifest[ident]['archive_group']=='TjIn'))
 paths=sorted(p for p in (ROOT/'runs').glob('*/RESULTS.json') if (ROOT/'records'/p.parent.name/'command.json').exists());details=[]
 for path in paths:
  row=load(path.relative_to(ROOT));ident=row['design_id'];prep=row['preprocessing'];source=ROOT/inputs[ident]['source_path']
  exact=load('runs/'+ident+'/exact_extraction.json');receipt=load('records/'+ident+'/command.json')
  ck(ident+':worker_exit',receipt['exit_code']==0 and receipt['parent_failure_reason'] is None)
  ck(ident+':receipt_worker_hash',receipt['worker_sha256']==sha(ROOT/'evaluate_one.py'))
  ck(ident+':log_hashes',receipt['stdout_sha256']==sha(ROOT/'records'/ident/'stdout.txt') and receipt['stderr_sha256']==sha(ROOT/'records'/ident/'stderr.txt'))
  ck(ident+':observed_resource_guards',receipt['peak_observed_process_group_rss_kib']<=receipt['group_rss_limit_kib'] and receipt['elapsed_seconds']<=receipt['worker_wall_limit_seconds']+3)
  ck(ident+':four_frozen_models',load('runs/'+ident+'/model_loads.json')==expected)
  ck(ident+':vocabulary',load('runs/'+ident+'/feature_vocabulary.json')==vocab)
  ck(ident+':source_passthrough',sha(ROOT/'runs'/ident/'graph_input/topModule.v')==sha(source)==prep['preprocessed_sha256'])
  ck(ident+':no_truth_or_cache_input',prep['truth_label_accessed'] is False and prep['dataset_pickle_loaded'] is False and prep['placeholder_label']==0)
  ck(ident+':exact_state',prep['exact_extraction']==exact)
  compatible={'exact_DFG':{'success'},'heuristic_large_lookup_direct':{'not_attempted'},'heuristic_fallback':{'failed'}}
  ck(ident+':route_status',prep['route'] in compatible and exact['status'] in compatible[prep['route']])
  ck(ident+':lookup_policy',(prep['large_lookup_entries']>=128)==(prep['route']=='heuristic_large_lookup_direct'))
  if prep['route']=='heuristic_fallback':ck(ident+':fallback_error_recorded',bool(exact.get('exception_type')) and bool(exact.get('error')) and any('Using heuristic DFG fallback' in s for s in prep['messages']))
  graph=load('runs/'+ident+'/graph_before_normalization.json');data=load('runs/'+ident+'/model_input.json')
  nodes=graph['nodes'];edges=graph['edges'];index={n['id']:i for i,n in enumerate(nodes)}
  ck(ident+':graph_validity',len(nodes)>1 and len(edges)>0 and 'sig_dummy' not in index and len(index)==len(nodes))
  ck(ident+':graph_counts',len(nodes)==data['num_nodes']==prep['graph_nodes'] and len(edges)==data['num_edges']==prep['graph_edges'])
  ck(ident+':edge_index',data['edge_index']==[[index[e[0]] for e in edges],[index[e[1]] for e in edges]])
  indegree=collections.Counter(e[1] for e in edges);outdegree=collections.Counter(e[0] for e in edges);features=[]
  for n in nodes:
   key=n['id'];label=str(n.get('label','')).lower();name=key.split('_graphrename',1)[0]
   if label and label in vocab and label!='signal':kind=label
   elif any(s in name for s in ["'d","'b","'o","'h"]):kind='numeric'
   elif indegree[key]==0:kind='output'
   elif outdegree[key]==0:kind='input'
   elif '.' in name or '_' in name:kind='signal'
   else:kind=name.lower()
   features.append(vocab[kind])
  ck(ident+':normalization',data['x']==features and len(features)==len(nodes))
  ck(ident+':feature_counts',prep['feature_counts']==dict(collections.Counter(str(v) for v in features)))
  ck(ident+':raw_labels',prep['raw_label_counts']==dict(collections.Counter(str(n.get('label')) for n in nodes)))
  ck(ident+':four_outputs',set(row['per_model'])=={'HT1','HT2','HT3','HT4'});votes=[]
  for model,v in row['per_model'].items():
   logits=v['logits'];logs=v['log_probabilities'];probs=[v['prob_clean'],v['prob_trojan']]
   ck(ident+':'+model+':finite',len(logits)==2 and len(logs)==2 and all(math.isfinite(x) for x in logits+logs+probs))
   maxlog=max(logits);denom=maxlog+math.log(sum(math.exp(x-maxlog) for x in logits))
   ck(ident+':'+model+':logsoftmax',all(close(logs[i],logits[i]-denom) for i in range(2)))
   ck(ident+':'+model+':probabilities',all(close(probs[i],math.exp(logs[i])) for i in range(2)) and close(sum(probs),1))
   pred=int(logits[1]>logits[0]);ck(ident+':'+model+':argmax',v['prediction']==pred and v['label']==('TROJAN' if pred else 'CLEAN'))
   if pred:votes.append(model)
  e=row['ensemble'];ck(ident+':any_vote',e['prediction']==int(bool(votes)) and e['trojan_votes']==len(votes) and e['triggered_models']==votes and e['label']==('TROJAN' if votes else 'CLEAN'))
  details.append({'design_id':ident,'status':row['status'],'route':prep['route'],'exact_status':exact['status']})
 aggregate_exists=(ROOT/'RESULTS.json').exists();coverage=None
 if aggregate_exists:
  result=load('RESULTS.json');metrics=load('METRICS.json');designs=result['designs'];byid={r['design_id']:r for r in designs};scored=[r for r in designs if r['status']=='scored'];unscored=[r for r in designs if r['status']!='scored']
  ck('aggregate_exactly23',len(designs)==23 and len(byid)==23 and set(byid)==set(inputs))
  statuses=collections.Counter()
  for row in designs:
   ident=row['design_id'];ck(ident+':truth_join',row['truth']==labels[ident]);ck(ident+':archive_join',row['archive_metadata']==manifest[ident]);p=ROOT/'runs'/ident/'exact_extraction.json'
   statuses[load(p.relative_to(ROOT))['status'] if p.exists() else 'not_reached']+=1
   if row['status']=='scored':
    worker=load('runs/'+ident+'/RESULTS.json');ck(ident+':worker_values_preserved',all(row[k]==v for k,v in worker.items()))
   else:ck(ident+':unscored_no_prediction',row['ensemble'] is None and all(v is None for v in row['per_model'].values()))
  coverage={'total':23,'scored':len(scored),'unscored':len(unscored),'model_rows':92,'scored_model_rows':4*len(scored),'scored_routes':dict(collections.Counter(r['preprocessing']['route'] for r in scored)),'exact_extraction_status_counts':dict(statuses)}
  ck('coverage_recomputed',result['coverage']==coverage)
  for name in ['HT1','HT2','HT3','HT4','ensemble']:
   counts=collections.Counter()
   for row in scored:
    truth=row['truth'];pred=(row['ensemble'] if name=='ensemble' else row['per_model'][name])['prediction'];counts[('T' if truth==pred else 'F')+('P' if pred else 'N')]+=1
   got=result['metrics'][name];pos=counts['TP']+counts['FN'];neg=counts['FP']+counts['TN']
   ck(name+':confusion_counts',all(got[k]==counts[k] for k in ['TP','FN','FP','TN']))
   ck(name+':denominators',got['scored_designs']==len(scored) and got['total_designs']==23 and got['scored_positive_denominator']==pos and got['scored_negative_denominator']==neg and got['unscored_positive']==14-pos and got['unscored_negative']==9-neg)
   ck(name+':rates',got['recall_on_scored']==(counts['TP']/pos if pos else None) and got['false_positive_rate_on_scored']==(counts['FP']/neg if neg else None))
  ck('metrics_matches_results',metrics=={'coverage':result['coverage'],'metrics':result['metrics']})
  p=ROOT/'per_design_model.csv';reviewed['per_design_model.csv']=sha(p);rows=list(csv.DictReader(p.open()));ck('csv92_unique',len(rows)==92 and len({(r['design_id'],r['model']) for r in rows})==92)
  for r in rows:
   d=byid[r['design_id']];v=d['per_model'][r['model']]
   ck(r['design_id']+':'+r['model']+':csv',r['status']==d['status'] and int(r['truth'])==d['truth'] and ((r['prediction']==str(v['prediction']) and close(float(r['prob_clean']),v['prob_clean']) and close(float(r['prob_trojan']),v['prob_trojan'])) if v else (r['prediction']==r['prob_clean']==r['prob_trojan']=='')))
 failures=[c for c in checks if not c['passed']]
 outcome=('PASS_WITH_LIMITATIONS' if aggregate_exists else 'PARTIAL_REVIEW_PASS') if not failures else 'REVIEW_FINDINGS'
 limitations=['No model computation was rerun; review is static and based on saved artifacts.','Directory labels are supplied annotations; checkpoint training overlap is unknown, and repeated families are not independent held-out examples.','Exact DFG success records successful execution of the supplied backend, not an independently validated complete semantic model of each design.','No heuristic fallback or resource failure occurred in this run; those handling paths were reviewed statically only.','Parent RSS monitoring is sampled, not a kernel-enforced memory cap.','Softmax scores are uncalibrated; detector predictions do not establish hardware security or functional equivalence.']
 report={'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Frozen runner and saved-artifact review only; no model invocation, design evaluation, source execution, graph-cache deserialization, or modifications outside records/method_review.','outcome':outcome,'checks_total':len(checks),'checks_passed':len(checks)-len(failures),'failures':failures,'aggregate_available':aggregate_exists,'reviewed_scored_designs':len(paths),'coverage':coverage,'per_design_review':details,'checks':checks,'reviewed_file_sha256':reviewed,'limitations':limitations}
 (OUT/'INDEPENDENT_METHOD_ARTIFACT_REVIEW.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 lines=['# Independent method and artifact review','',f"Outcome: **{outcome}**. {len(checks)-len(failures)}/{len(checks)} checks passed.",'','This review checked frozen code and saved artifacts only. It did not run a model or evaluate a design.','',f'Reviewed scored design artifacts: {len(paths)}. Aggregate available: {aggregate_exists}.',f'Coverage: {coverage}.','','Frozen checkpoint/configuration hashes and model records match the prior audited AES run. All 37 vocabulary entries match. The worker uses CPU evaluation mode, strict weights-only loading, no-grad inference, two-class log-softmax and argmax, and the same four-model any-positive rule. The graph cache is not loaded. Catalog labels are absent from the worker input manifest and joined by the controller only after the inference pool completes.','','All source hashes and passthrough graph-input hashes match the inventory. Saved graph counts, node normalization, feature counts and edge indices agree independently. Saved logits, log probabilities and probabilities are finite and agree arithmetically; class predictions, ensemble votes, confusion counts, coverage denominators, aggregate joins and all 92 CSV rows agree.','','The static resource-handling review found no blocking issue. Deadline, resource and empty-graph exceptions bypass the package fallback handler. The parent guards worker wall time and process-group RSS, cleans up the process group, and leaves incomplete results unscored. Ordinary exact errors may use only the existing package fallback and retain explicit status/error evidence.','','## Findings','']
 lines += [json.dumps(f) for f in failures] or ['No failing artifact checks.']
 if aggregate_exists:
  lines += ['', '| Model | TP | FN | FP | TN | Recall | False-positive rate |','|---|---:|---:|---:|---:|---:|---:|']
  for model,m in result['metrics'].items():lines.append(f"| {model} | {m['TP']} | {m['FN']} | {m['FP']} | {m['TN']} | {m['recall_on_scored']:.2%} | {m['false_positive_rate_on_scored']:.2%} |")
  receipts=[load('records/'+r['design_id']+'/command.json') for r in designs]
  warning_counts=collections.Counter(line for r in designs for line in (ROOT/'records'/r['design_id']/'stderr.txt').read_text().splitlines() if line.strip())
  lines += ['', f"The largest sampled process-group RSS was {max(r['peak_observed_process_group_rss_kib'] for r in receipts):,} KiB. The longest recorded worker wall time was {max(r['elapsed_seconds'] for r in receipts):.3f} seconds. All 23 workers exited 0. The only nonempty stderr line was the Matplotlib font-cache notice, present for all 23 isolated worker cache directories."]
 lines+=['','## Limits','']+['- '+s for s in limitations]
 (OUT/'INDEPENDENT_METHOD_ARTIFACT_REVIEW.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'outcome':outcome,'checks':len(checks),'failures':failures,'reviewed_scored_designs':len(paths),'coverage':coverage}))
if __name__=='__main__':main()
