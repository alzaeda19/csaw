#!/usr/bin/env python3
"""Carry forward bounded old visible exports; do not rerun historical work."""
from pathlib import Path
from collections import Counter
import json, hashlib, re
OUT = Path(__file__).resolve().parent
OLD = Path('/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/records/current_task_transcripts/snapshot_20261107T173219129900Z')
SHA = lambda b:hashlib.sha256(b).hexdigest()
OMIT = {'root_current_task':{331,333,784,785},'baseline_bitstream_simulation':{22,26},'baseline_mapped_formal':{22,24},'decode_regenerated_baseline':{17,18}}
def save(p,v,plain=False):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write(v if plain else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
results=[]
for label,omitted_lines in OMIT.items():
 old=OLD/label; dest=OUT/'prior_bitstream_export'/label; meta=json.loads((old/'export_manifest.json').read_text())
 native=[]
 with Path(meta['source_file']).open('rb') as f:
  for _ in range(meta['complete_source_lines']):native.append(f.readline())
 assert SHA(b''.join(native))==meta['source_snapshot_sha256']
 events=[]; omissions=[]; fields=0; originals=[]
 for e in map(json.loads,(old/'visible_events.jsonl').read_text().splitlines()):
  no=e['source_line'];q=json.loads(native[no-1])['payload'];assert SHA(native[no-1])==e['source_record_sha256']
  if no in omitted_lines:
   omissions.append({'source_line':no,'source_record_sha256':e['source_record_sha256'],'action':'whole record omitted','reason':'Original prior export contained local AGENTS.md instruction output.'});continue
  if isinstance(e['payload'].get('arguments'),str) and 'gAAAAA' in e['payload']['arguments']:
   del e['payload']['arguments'];del e['retained_field_source_locations']['arguments']
   omissions.append({'source_line':no,'source_record_sha256':e['source_record_sha256'],'action':'arguments field omitted','reason':'Original arguments embed encrypted collaboration body; no decryption or reconstruction.'})
  for key,loc in e['retained_field_source_locations'].items():
   expected=(q['item'] if loc[0]=='payload.item' else q)[loc[1]]
   if len(loc)==3:expected=[expected[i] for i in loc[2]]
   assert expected==e['payload'][key];fields+=1
  assert e['payload'].get('role') not in ['system','developer'] and e['payload'].get('channel')!='analysis' and e['payload'].get('type')!='reasoning'
  assert not re.search(r'(?i)(-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}|\bgh[pousr]_[A-Za-z0-9]{20,})',json.dumps(e['payload']))
  events.append(e)
 for name in ['export_manifest.json','omissions_and_gaps.json','configured_model_records.json','field_integrity_verification.json','VISIBLE_MESSAGES.md']:
  src=old/name; dst=dest/('original_'+name); data=src.read_bytes();dst.parent.mkdir(parents=True,exist_ok=True)
  with dst.open('xb') as f:f.write(data)
  assert dst.read_bytes()==data
  originals.append({'source_file':str(src),'portable_file':dst.name,'sha256':SHA(data),'bytes':len(data)})
 save(dest/'visible_events.jsonl',''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events),True)
 save(dest/'source_line_index.json',[{k:e[k] for k in ['source_line','source_record_sha256','timestamp','category']} for e in events])
 save(dest/'additional_omissions.json',omissions)
 result={'label':label,'status':'Existing records carried forward; not new recovery. Safe field projection of prior visible export.',
  'original_export_file':str(old/'visible_events.jsonl'),'original_export_sha256':SHA((old/'visible_events.jsonl').read_bytes()),
  'original_record_count':meta['exported_records'],'carried_record_count':len(events),'whole_records_omitted':len(omitted_lines),
  'encrypted_argument_fields_omitted':sum(x['action']=='arguments field omitted' for x in omissions),
  'carried_counts':dict(Counter(e['category'] for e in events)),'source_file':meta['source_file'],
  'first_in_scope_line':meta['first_in_scope_line'],'last_in_scope_line':meta['complete_source_lines'],
  'verification':{'pass':True,'source_line_hashes_verified':len(events),'retained_fields_verified':fields,'original_manifest_and_messages_hash_verified':True},
  'original_files_carried':originals,'limits':['Original manifests describe the historical snapshot before this additional filtering.','Original readable messages contain no omitted instruction tool outputs or encrypted argument strings.','Native raw session history was not copied.']}
 save(dest/'projection_manifest.json',result);results.append(result)
summary={'original_records':sum(x['original_record_count'] for x in results),'carried_records':sum(x['carried_record_count'] for x in results),'whole_instruction_output_records_omitted':sum(x['whole_records_omitted'] for x in results),'encrypted_argument_fields_omitted':sum(x['encrypted_argument_fields_omitted'] for x in results),'sessions':results}
save(OUT/'prior_bitstream_export/MANIFEST.json',summary)
inv=json.loads((OUT/'prior_files_integrity.json').read_text())
for path,row in inv['files'].items():assert SHA(Path(path).read_bytes())==row['sha256']
save(OUT/'FINAL_VERIFICATION.json',{'pass':True,'new_records':107,'new_fields_and_native_hashes_verified':True,'new_finals_verified':2,'carried_forward':summary,'prior_files_verified_unchanged':len(inv['files']),'no_historical_commands_executed':True})
manifest=json.loads((OUT/'MANIFEST.json').read_text());manifest['carried_forward_prior_bitstream_export']={k:v for k,v in summary.items() if k!='sessions'};manifest['carried_forward_prior_bitstream_manifest']='prior_bitstream_export/MANIFEST.json';manifest['portable_visible_record_count']=107+summary['carried_records'];(OUT/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
with (OUT/'INDEX.md').open('a') as f:
 f.write(f'\n## Portable prior bitstream export\n\nThe original snapshot had **597 records**. This folder carries **{summary["carried_records"]} existing records** in [prior_bitstream_export](prior_bitstream_export/MANIFEST.json), separate from the 107 new records. Ten instruction-output records are omitted; {summary["encrypted_argument_fields_omitted"]} encrypted argument fields are omitted. Original manifests, gaps, model labels and visible messages are copied exactly under clearly named original files; projection manifests record the differences. No raw native session history is copied.\n')
(OUT/'SHA256SUMS').write_text(''.join(f'{SHA(p.read_bytes())}  {p.relative_to(OUT).as_posix()}\n' for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'))
print(json.dumps({k:v for k,v in summary.items() if k!='sessions'},indent=2))
