"""Export exact visible scalar fields for this audit's known native interval."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
SOURCE = Path('/Users/al-zayedal-hassan/.codex/sessions/2026/11/12/rollout-2026-11-12T19-12-19-01a1b0ad-f593-7f90-a689-b621984f7cb4_01a1d23f-7ed7-7fa1-9afd-64875b8a6cf8.jsonl')
FIRST = 2276
sha = lambda b: hashlib.sha256(b).hexdigest()
ALLOW = {'type','id','name','namespace','call_id','role','phase','status','content','input','arguments','output','author','recipient'}
raw = SOURCE.read_bytes()
lines = raw.splitlines(keepends=True)
records = []; omitted = []; verified_fields = 0

def leaves(value, pointer, fields, exclusions):
    if isinstance(value, dict):
        if value.get('type') in {'encrypted_content','reasoning','reasoning_text','analysis'}:
            exclusions.append({'pointer':pointer,'reason':'Opaque/internal block; not exported or decoded.'}); return
        for k,v in value.items():
            p = pointer + '/' + k.replace('~','~0').replace('/','~1')
            if k in {'encrypted_content','internal_chat_message_metadata_passthrough'}:
                exclusions.append({'pointer':p,'reason':'Opaque/internal field excluded.'})
            else: leaves(v,p,fields,exclusions)
    elif isinstance(value,list):
        for i,v in enumerate(value): leaves(v,pointer+'/'+str(i),fields,exclusions)
    elif isinstance(value,str) and (re.search(r'gAAAA[A-Za-z0-9_=-]{32,}',value) or re.search(r'"encrypted_content"\s*:',value)):
        exclusions.append({'pointer':pointer,'reason':'String may contain an embedded opaque payload; whole field excluded without decoding.'})
    else:
        fields.append({'pointer':pointer,'value':value})

def pointer_value(obj,pointer):
    for token in pointer.split('/')[1:]:
        token=token.replace('~1','/').replace('~0','~')
        obj=obj[int(token)] if isinstance(obj,list) else obj[token]
    return obj

for n,line in enumerate(lines,1):
    if n<FIRST: continue
    d=json.loads(line); p=d.get('payload',{})
    identity={'native_line':n,'native_line_sha256':sha(line),'native_raw_line_bytes':len(line),'timestamp':d.get('timestamp'),'payload_type':p.get('type')}
    if d.get('type')!='response_item' or p.get('type')=='reasoning' or p.get('role') in {'developer','system'} or p.get('phase')=='analysis':
        omitted.append({**identity,'reason':'Internal/context/event/duplicate record excluded.'}); continue
    if p.get('type') not in {'message','agent_message','custom_tool_call','custom_tool_call_output','function_call','function_call_output'}:
        omitted.append({**identity,'reason':'Not a selected visible message/tool record.'}); continue
    fields=[]; exclusions=[]
    for k,v in p.items():
        if k in ALLOW: leaves(v,'/payload/'+k,fields,exclusions)
    for field in fields:
        assert pointer_value(d,field['pointer'])==field['value']
        verified_fields+=1
    records.append({'source':identity,'fields':fields,'excluded_fields':exclusions})

dest=BASE/'ai_records';dest.mkdir(exist_ok=True)
for name,data in [('visible_exact_fields.jsonl',records),('omitted_records.jsonl',omitted)]:
    (dest/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in data))
receipt={'source_thread_id':'01a1b0ad-f593-7f90-a689-b621984f7cb4','native_source':str(SOURCE),'source_interval':[FIRST,len(lines)],'source_prefix_sha256':sha(raw),'source_prefix_bytes':len(raw),'snapshot_last_timestamp':json.loads(lines[-1]).get('timestamp'),'retained_records':len(records),'omitted_records':len(omitted),'exact_scalar_fields_verified':verified_fields,'policy':'Exact ordinary fields only. Opaque payloads are not decoded. Hidden reasoning, platform/context records and event duplicates excluded. Snapshot excludes future sealing/handoff messages. Does not restore historical missing dialogue.'}
(dest/'EXPORT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
