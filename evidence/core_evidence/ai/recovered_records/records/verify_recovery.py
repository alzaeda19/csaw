from pathlib import Path
import json,hashlib,re,datetime,subprocess,os
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def fh(p):return sha(Path(p).read_bytes())
cache={};sessions=[];record_ids=set();fields=0;total=0;finals=0
for f in sorted(R.rglob('visible_events.jsonl')):
 rows=[json.loads(x) for x in f.read_text().splitlines()]
 if not rows:continue
 if (f.parent/'projection_manifest.json').exists():m=read(f.parent/'projection_manifest.json')
 else:m=read(f.parent/'export_manifest.json')
 source=m.get('source_file') or m.get('source',{}).get('path') or rows[0].get('source_file')
 assert source,(f,list(m))
 if source not in cache:cache[source]=Path(source).read_bytes().splitlines(keepends=True)
 lines=cache[source]
 for e in rows:
  raw=lines[e['source_line']-1];assert sha(raw)==e['source_record_sha256'],(f,e['source_line'])
  native=json.loads(raw);q=native['payload'];value=e['payload']
  assert value.get('role') not in ['system','developer']
  assert not (value.get('role')=='assistant' and value.get('channel')=='analysis')
  if 'retained_field_source_locations' in e:
   for k,loc in e['retained_field_source_locations'].items():
    obj=native
    for part in loc:
     if part=='payload.item':obj=native['payload']['item']
     elif isinstance(part,list):obj=[obj[i] for i in part]
     else:obj=obj[part]
    assert value[k]==obj,(f,e['source_line'],k)
    if 'retained_field_sha256' in e:assert e['retained_field_sha256'][k]==sha(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
    fields+=1
  else:
   for k,v in value.items():
    expected=q.get('item',{}).get(k,q.get(k)) if e['category']=='command_execution' else q[k]
    if e['category']=='command_execution' and k=='type':
     assert v=='command_execution' and expected=='CommandExecution'
    else:assert v==expected,(f,e['source_line'],k)
    fields+=1
  ident=(source,e['source_line']);assert ident not in record_ids,('duplicate native event',ident);record_ids.add(ident)
  total+=1;finals+=e['category']=='assistant_final_answer'
 sessions.append({'path':str(f.relative_to(R)),'source_file':source,'records':len(rows),'finals':sum(e['category']=='assistant_final_answer' for e in rows),'first_native_line':min(e['source_line'] for e in rows),'last_native_line':max(e['source_line'] for e in rows)})
# Verify each sub-bundle's checksum manifest without executing any historical command.
manifest_checks=0
for mf in [R/'historical_clean/OUTPUT_HASHES.json',R/'detector_tails/HASH_MANIFEST.json']+list((R/'coordinator').rglob('HASH_MANIFEST.json')):
 d=read(mf);rows=d.get('files',d)
 if isinstance(rows,dict):items=rows.items()
 else:items=[(x['path'],x) for x in rows]
 for rel,h in items:
  if not isinstance(h,dict) or 'sha256' not in h:continue
  p=mf.parent/rel;assert fh(p)==h['sha256'],p
  if 'bytes' in h:assert p.stat().st_size==h['bytes']
  manifest_checks+=1
for line in (R/'bitstream_and_mac/SHA256SUMS').read_text().splitlines():
 if not line:continue
 h,rel=line.split('  ',1);assert fh(R/'bitstream_and_mac'/rel)==h;manifest_checks+=1
# Independently verify the unchanged detector evidence manifests and original source receipts.
prior_checks=0
for name in ['CSAW_2026_Detector_Baseline_2026-11-10_122045Z','CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z']:
 p=Path('/Users/al-zayedal-hassan/Documents')/name
 for x in read(p/'OUTPUT_HASHES.json')['files']:
  assert fh(p/x['path'])==x['sha256'];prior_checks+=1
base=Path('/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z')
for x in read(base/'records/preservation_check.json')['checks']:
 assert fh(x['path'])==x['sha256'];prior_checks+=1
env=os.environ.copy();env['GIT_OPTIONAL_LOCKS']='0';repo=Path('/Users/al-zayedal-hassan/Documents/llm4chipdesign-hw')
def git(args):
 p=subprocess.run(['git','-C',str(repo)]+args,capture_output=True,text=True,env=env);return {'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
after={'status':git(['status','--porcelain=v1']),'head':git(['rev-parse','HEAD'])}
assert after==read(base/'records/repository_before.json')
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_pass':True,'visible_records_verified':total,'unique_native_record_ids':len(record_ids),'retained_fields_verified':fields,'final_answer_records':finals,'source_files':len(cache),'sessions':sessions,'sub_bundle_file_hashes_verified':manifest_checks,'prior_detector_evidence_and_source_hash_checks':prior_checks,'repository_unchanged':True,'repository_after':after,'limitations':'Checks validate retained local fields, hashes and scope; not global conversation completeness or provider attestation. No tests/inference/historical commands executed.'}
(R/'records/FINAL_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['sessions','repository_after']},indent=2))
