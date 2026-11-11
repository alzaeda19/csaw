#!/usr/bin/env python3
"""Recover bounded visible detector tails. Logged commands are never executed."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib, json, os, re, stat

OUT = Path(__file__).resolve().parent
DOCS = Path('/Users/al-zayedal-hassan/Documents')
OLD = {'baseline': DOCS/'CSAW_2026_Detector_Baseline_2026-11-10_122045Z', 'clean_aes': DOCS/'CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z'}
ROOT_ID = '01a1b0ad-f593-7f90-a689-b621984f7cb4'
TEXT_TYPES = {'text', 'input_text', 'output_text'}
ALLOWED_AGENTS = {'/root', '/root/detector_environment', '/root/detector_input_audit', '/root/clean_aes_detector_review'}
SECRET_PATTERNS = [re.compile(x) for x in [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}', r'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}', r'\bBearer\s+[A-Za-z0-9._-]{24,}', r'\bAKIA[0-9A-Z]{16}\b']]

def now(): return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
def save(path, value, text=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f: f.write(value if text else json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def inventory(root):
    entries = {}
    for base, dirs, names in os.walk(root, followlinks=False):
        for name in sorted(dirs+names):
            path=Path(base)/name; s=path.lstat(); rel=str(path.relative_to(root))
            if stat.S_ISLNK(s.st_mode):
                target=os.readlink(path)
                entries[rel]={'kind':'symlink','target':target,'target_text_sha256':sha(os.fsencode(target))}
            elif stat.S_ISREG(s.st_mode):
                h=hashlib.sha256()
                with path.open('rb') as f:
                    while chunk:=f.read(1024*1024): h.update(chunk)
                entries[rel]={'kind':'file','bytes':s.st_size,'sha256':h.hexdigest()}
    return entries

def text_content(content):
    if isinstance(content,str): return content
    return '\n'.join(x.get('text','') for x in content or [] if isinstance(x,dict) and x.get('type') in TEXT_TYPES)

def resolve(native, location):
    cur=native
    for step in location: cur=[cur[i] for i in step] if isinstance(step,list) else cur[step]
    return cur

started=now()
before={name:inventory(root) for name,root in OLD.items()}
save(OUT/'preservation/old_files_before.json',{'captured_utc':now(),'roots':{k:str(v) for k,v in OLD.items()},'entries':before,'symlinks':'Link targets recorded without reading through symlinks; directory symlinks not traversed.'})
prior, all_prior_exported, snapshots, source_meta={},set(),{},{}
for exp,root in OLD.items():
    base=root/'records/current_task_transcripts'; ix=json.loads((base/'EXPORT_INDEX.json').read_text())
    mp=base/ix['snapshot_manifest']; manifest=json.loads(mp.read_text())
    prior[exp]={'manifest':manifest,'manifest_file':str(mp),'manifest_sha256':sha(mp.read_bytes())}
    for s in manifest['sessions']:
        if s['label']=='source_user_request_only': continue
        src=Path(s['source_file'])
        if str(src) not in snapshots:
            with src.open('rb') as f: raw=f.read(os.fstat(f.fileno()).st_size)
            lines=raw.splitlines(keepends=True)
            trailing=len(lines.pop()) if lines and not lines[-1].endswith(b'\n') else 0
            snapshots[str(src)]=(raw,lines)
            first=json.loads(lines[0]).get('payload',{})
            source_meta[str(src)]={'source_file':str(src),'source_snapshot_bytes':len(raw),'source_snapshot_sha256':sha(raw),'complete_source_lines':len(lines),'trailing_incomplete_bytes_omitted':trailing,'snapshot_read_utc':now(),'native_thread_id':first.get('id'),'parent_thread_id':first.get('parent_thread_id'),'agent_path':first.get('agent_path')}
        raw,lines=snapshots[str(src)]
        s['_prefix_verified']=sha(raw[:s['source_snapshot_bytes']])==s['source_snapshot_sha256']
        assert s['_prefix_verified'],('Prior source prefix changed',exp,s['label'])
        for event in json.loads((mp.parent/s['label']/'source_line_index.json').read_text()):
            all_prior_exported.add((str(src),event['source_line'],event['source_record_sha256']))

specs=[
 {'label':'baseline_root_completion','experiment':'baseline','first':1298,'last':1336,'end_reason':'Native assistant final_answer at line 1336; subsequent records excluded.'},
 {'label':'clean_aes_before_followup','experiment':'clean_aes','first':1528,'last':1543,'end_reason':'Ends immediately before incoming same-task coordinator delegation at line 1544.'},
 {'label':'clean_aes_completion_followup','experiment':'clean_aes','first':1544,'last':1605,'end_reason':'Begins at incoming same-task coordinator delegation and ends with native assistant final_answer at line 1605.'},
]
exported_keys=set(); results=[]
for spec in specs:
    old=prior[spec['experiment']]; original=next(s for s in old['manifest']['sessions'] if s['label']=='root_current_task')
    src=original['source_file']; raw,lines=snapshots[src]; first,last=spec['first'],spec['last']
    assert source_meta[src]['native_thread_id']==ROOT_ID and first>original['complete_source_lines'] and last<=len(lines)
    if spec['label']!='clean_aes_before_followup':
        final=json.loads(lines[last-1])['payload']
        assert final.get('type')=='message' and final.get('role')=='assistant' and final.get('phase')=='final_answer'
    events,omitted,metadata,all_lines=[],[],[],[]; counts,excluded=Counter(),Counter(); folder=OUT/spec['label']
    for no in range(first,last+1):
        line=lines[no-1]; d=json.loads(line); q=d.get('payload',{}); kind,typ=d.get('type'),q.get('type')
        ref={'source_file':src,'source_thread_id':ROOT_ID,'source_line':no,'source_record_sha256':sha(line),'timestamp':d.get('timestamp')}
        pm=q.get('internal_chat_message_metadata_passthrough',{})
        if isinstance(pm,dict) and 'turn_id' in pm:
            ref['source_turn_id']=pm['turn_id']; ref['source_turn_id_location']=['payload','internal_chat_message_metadata_passthrough','turn_id']
        if 'ordinal' in d: ref['source_ordinal']=d['ordinal']
        all_lines.append({**ref,'native_record_type':kind,'native_payload_type':typ})
        payload,mappings,category={},{},None
        def gap(reason,**extra): omitted.append({**ref,'reason':reason,**extra})
        def exclude(reason): excluded[reason]+=1; gap(reason)
        def keep(key,source=q,prefix=None):
            if key not in source: return
            value=source[key]
            if any(p.search(json.dumps(value,ensure_ascii=False)) for p in SECRET_PATTERNS):
                gap('Secret-pattern match: whole native field omitted without replacement.',omitted_field=key,source_field_location=(prefix or ['payload'])+[key],source_field_sha256=sha(canonical(value))); excluded['secret_field']+=1
            else: payload[key]=value; mappings[key]=(prefix or ['payload'])+[key]
        if kind=='response_item' and typ=='message':
            if q.get('role')=='assistant' and q.get('phase') in ['commentary','final_answer'] and q.get('channel')!='analysis':
                for key in ['type','id','role','content','phase','channel']: keep(key)
                category='assistant_'+q['phase']
            else: exclude('Nonvisible assistant, platform, system, developer, or out-of-scope message excluded in full.')
        elif kind=='response_item' and typ in ['function_call','custom_tool_call','function_call_output','custom_tool_call_output']:
            for key in ['type','id','status','call_id','name','namespace','arguments','input','output']: keep(key)
            if isinstance(q.get('output'),list):
                indices=list(range(len(q['output']))); removed=[]
                if no==1560:
                    assert 'exec tool declaration:' in q['output'][1].get('text','')
                    indices.remove(1); removed.append({'index':1,'reason':'Tool-discovery documentation excluded.'})
                if no==1577:
                    assert 'Warning: truncated output' in q['output'][1].get('text','')
                    indices.remove(1); removed.append({'index':1,'reason':'Entire native tool-output element excluded: combines a coordinator chat read containing mixed earlier history with other output. No embedded prior history copied; no words reconstructed.'})
                if removed:
                    payload['output']=[q['output'][i] for i in indices]; mappings['output']=['payload','output',indices]
                    gap('Selected original output list elements omitted.',omitted_output_elements=[{**r,'native_element_sha256':sha(canonical(q['output'][r['index']]))} for r in removed],original_output_element_count=len(q['output']),retained_output_indices=indices)
                    excluded['output_list_elements']+=len(removed)
            category='incoming_same_task_delegation' if no==1544 else typ
            if no==1544: assert '<codex_delegation>' in q.get('output','') and 'finish your existing report/preservation records' in q['output']
        elif kind=='response_item' and typ=='agent_message':
            if q.get('author') not in ALLOWED_AGENTS or q.get('recipient') not in ALLOWED_AGENTS:
                exclude('Exporter-worker or other child message outside the previously included detector/review child scope.')
            else:
                for key in ['type','id','author','recipient']: keep(key)
                content=q.get('content',[]); indices=[i for i,x in enumerate(content) if isinstance(x,dict) and x.get('type') in TEXT_TYPES]
                payload['content']=[content[i] for i in indices]; mappings['content']=['payload','content',indices]; category='agent_message_readable_envelope'
                if len(indices)!=len(content): gap('Encrypted/nontext collaboration content omitted; only exact readable envelope fields retained. No decryption or reconstruction.',omitted_content_indices=[i for i in range(len(content)) if i not in indices])
        elif kind=='event_msg' and typ=='item_completed' and q.get('item',{}).get('type') in ['CommandExecution','FileChange','ImageView']:
            item=q['item']; fields={'CommandExecution':['type','id','process_id','command','cwd','source','status','aggregated_output','exit_code','duration'],'FileChange':['type','id','changes','status','stdout','stderr'],'ImageView':['type','id','path']}[item['type']]
            for key in fields: keep(key,item,['payload','item'])
            for key in ['started_at_ms','completed_at_ms']: keep(key)
            category={'CommandExecution':'command_execution','FileChange':'file_change_record','ImageView':'image_view_record'}[item['type']]
        elif kind=='turn_context':
            selected={key:q[key] for key in ['turn_id','model','effort'] if key in q}
            metadata.append({**ref,'source_fields':selected,'source_field_locations':{key:['payload',key] for key in selected}})
            exclude('Turn context excluded except exact turn/model/effort labels in separate metadata; configured model does not authenticate serving weights.')
        elif kind=='compacted': exclude('Compaction and replacement history excluded in full.')
        else: exclude('Nonvisible, duplicate UI event, aggregate collaboration state, or out-of-scope record excluded in full.')
        if not category: continue
        key=(src,no,ref['source_record_sha256']); assert key not in all_prior_exported and key not in exported_keys; exported_keys.add(key)
        if 'truncated' in json.dumps(payload,ensure_ascii=False).lower(): gap('Native retained record contains a truncation indicator. Stored visible text retained exactly; unavailable omitted words not reconstructed.')
        events.append({**ref,'category':category,'payload':payload,'retained_field_source_locations':mappings,'retained_field_sha256':{k:sha(canonical(v)) for k,v in payload.items()}}); counts[category]+=1
    save(folder/'visible_events.jsonl',''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events),True)
    saved=[json.loads(x) for x in (folder/'visible_events.jsonl').read_text().splitlines()]; checked=0
    for e in saved:
        line=lines[e['source_line']-1]; native=json.loads(line); assert sha(line)==e['source_record_sha256']
        if 'source_turn_id' in e: assert e['source_turn_id']==resolve(native,e['source_turn_id_location'])
        for k,loc in e['retained_field_source_locations'].items():
            expected=resolve(native,loc); assert expected==e['payload'][k] and sha(canonical(expected))==e['retained_field_sha256'][k]; checked+=1
    for entry in metadata:
        native=json.loads(lines[entry['source_line']-1])
        for k,loc in entry['source_field_locations'].items(): assert entry['source_fields'][k]==resolve(native,loc)
    readable=['# Recovered visible detector tail: '+spec['label'],'','Exact native visible text; authored historical claims are preserved, not independently revalidated. Logged commands were not executed during recovery. Full retained tool/command fields are in visible_events.jsonl.','']
    for e in saved:
        if e['category'].startswith('assistant_') or e['category']=='agent_message_readable_envelope': body=text_content(e['payload'].get('content')) or '[No readable native collaboration body is available.]'
        elif e['category']=='incoming_same_task_delegation': body=e['payload']['output']
        else: continue
        readable.extend(['## '+e['category']+' — '+e['timestamp'],'','Source line '+str(e['source_line'])+'.','',body,''])
    save(folder/'VISIBLE_MESSAGES.md','\n'.join(readable)+'\n',True)
    save(folder/'source_line_index.json',[{k:e[k] for k in ['source_file','source_thread_id','source_line','source_record_sha256','timestamp','category','source_turn_id'] if k in e} for e in saved])
    save(folder/'bounded_source_line_inventory.json',all_lines); save(folder/'omissions_and_gaps.json',omitted)
    save(folder/'configured_model_records.json',{'note':'Native configured model/effort labels only, not authentication of serving weights or inference.','records':metadata})
    integrity={'pass':True,'records_verified':len(saved),'retained_fields_verified':checked,'raw_line_hashes_include_original_newline':True,'field_hash_algorithm':'SHA-256 of UTF-8 JSON, ensure_ascii=False, sort_keys=True, separators=(comma, colon)','duplicate_prior_source_lines_exported':0,'duplicate_recovery_source_lines_exported':0,'method':'Reread saved JSONL; compare each retained field to exact native field/selected original list elements and each raw source-line SHA-256. No detector execution or model/API calls.'}
    save(folder/'field_integrity_verification.json',integrity)
    result={**spec,**source_meta[src],'prior_snapshot_manifest':old['manifest_file'],'prior_snapshot_manifest_sha256':old['manifest_sha256'],'prior_complete_source_lines':original['complete_source_lines'],'prior_snapshot_prefix_sha256_verified':original['_prefix_verified'],'first_in_scope_timestamp':json.loads(lines[first-1]).get('timestamp'),'last_in_scope_timestamp':json.loads(lines[last-1]).get('timestamp'),'bounded_source_bytes':sum(len(x) for x in lines[first-1:last]),'bounded_source_sha256':sha(b''.join(lines[first-1:last])),'exported_records':len(saved),'exported_counts':dict(counts),'excluded_counts':dict(excluded),'omission_and_gap_entries':len(omitted),'integrity':integrity}
    save(folder/'export_manifest.json',result); results.append(result)

child_status=[]
for exp,old in prior.items():
    for s in old['manifest']['sessions']:
        if s['label'] in ['root_current_task','source_user_request_only']: continue
        raw,lines=snapshots[s['source_file']]; assert len(lines)==s['complete_source_lines'],'Child tail changed: reassess bounded export.'
        old_folder=Path(old['manifest_file']).parent/s['label']; records=[json.loads(x) for x in (old_folder/'visible_events.jsonl').read_text().splitlines()]
        finals=[{k:e[k] for k in ['source_line','source_record_sha256','timestamp']} for e in records if e['category']=='assistant_final_answer']
        child_status.append({'experiment':exp,'label':s['label'],**source_meta[s['source_file']],'prior_complete_source_lines':s['complete_source_lines'],'prior_snapshot_prefix_sha256_verified':s['_prefix_verified'],'new_complete_source_lines':0,'recovered_records':0,'prior_export_already_retained_final_records':finals,'status':'No post-snapshot lines available; prior child finals already exported and not duplicated.'})
save(OUT/'CHILD_CUTOFF_STATUS.json',child_status)
after={name:inventory(root) for name,root in OLD.items()}; changes={}
for name in OLD: changes[name]={'added':sorted(set(after[name])-set(before[name])),'removed':sorted(set(before[name])-set(after[name])),'changed':sorted(k for k in set(before[name])&set(after[name]) if before[name][k]!=after[name][k])}
assert all(not v for c in changes.values() for v in c.values()),changes
preservation={'pass':True,'verified_utc':now(),'roots':{k:str(v) for k,v in OLD.items()},'entries_verified':{k:len(v) for k,v in before.items()},'regular_files_verified':{k:sum(v['kind']=='file' for v in e.values()) for k,e in before.items()},'symlinks_verified':{k:sum(v['kind']=='symlink' for v in e.values()) for k,e in before.items()},'before_inventory_canonical_sha256':sha(canonical(before)),'after_inventory_canonical_sha256':sha(canonical(after)),'changes':changes,'method':'Full regular-file hashes and symlink targets inventoried before/after. No source directories modified; directory symlinks not traversed. Access times not checked.'}
save(OUT/'preservation/old_files_unchanged.json',preservation)
remaining=[
 'Encrypted/nontext collaboration bodies remain unavailable; none decrypted or reconstructed.',
 'No additional detector_environment, detector_input_audit, or clean_aes_detector_review child records exist beyond prior cutoffs; existing child finals are carried-forward references, not newly recovered records.',
 'Clean-AES source line 1577 output element 1 excluded in full because it contains mixed coordinator history; its native truncation indicator is documented and no missing text reconstructed. Separate native local command record at line 1575 retained.',
 'Exporter-worker sessions and their root message bodies remain outside the previously included detector/review child scope.',
 'Earlier root history, hidden reasoning, system/developer/platform context, compaction/replacement history, tool-discovery documentation, and records after each boundary excluded.',
 'Source-user coordinator history handled separately by parent recovery task; already exported single source-user request not duplicated.',
 'This is a local consistency-preserving recovery of available visible records, not independent authentication of historical claims, serving weights, missing logs, or complete task history.'
]
manifest={'format_version':1,'started_utc':started,'finished_utc':now(),'scope':'Only missing visible post-snapshot records for Nov10 baseline and clean-AES defensive detector tasks. No logged command executed; no new tests, detector/model/API calls, repository writes, or earlier-history path traversal.','source_root_thread_id':ROOT_ID,'segments':results,'children':child_status,'recovered_visible_records':sum(r['exported_records'] for r in results),'recovered_assistant_finals':sum(r['exported_counts'].get('assistant_final_answer',0) for r in results),'remaining_gaps':remaining,'preservation':preservation,'hash_limitations':'Raw-line hashes cover complete native line including newline, even when fields omitted. Source snapshot/prefix hashes cover excluded bytes without exporting/interpreting contents. Hashes establish local consistency, not independent authenticity.'}
save(OUT/'RECOVERY_MANIFEST.json',manifest)
readme='# Recovered detector transcript tails\n\n'+f"Recovered **{manifest['recovered_visible_records']} new visible records**, including **{manifest['recovered_assistant_finals']} root final answers**, in three bounded segments. Old experiment folders remain unchanged.\n\n"+'\n'.join(f"- `{r['label']}`: source lines {r['first']}–{r['last']}, {r['exported_records']} retained records. {r['end_reason']}" for r in results)+'\n\nEach segment provides exact retained native fields, source thread/turn IDs where present, complete original source-line hashes, canonical field hashes, readable visible messages, and exclusions. Prior snapshot prefixes match original hashes; no old exported source lines are duplicated.\n\nThe three included children have no post-snapshot records; their already exported finals are references in `CHILD_CUTOFF_STATUS.json`, not new records. The coordinator follow-up at line 1544 begins an explicit separate segment. Final answers retain historical snapshot-limited record counts verbatim.\n\n`RECOVERY_MANIFEST.json` and `RECOVERY_INDEX.json` record counts, boundaries and limitations. `preservation/old_files_unchanged.json` records content-hash comparisons. `HASH_MANIFEST.json` covers this folder except itself and the index; the index records its hash.\n\nRemaining gaps:\n\n'+'\n'.join('- '+x for x in remaining)+'\n'
save(OUT/'README.md',readme,True)
files={str(p.relative_to(OUT)):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(OUT.rglob('*')) if p.is_file()}
save(OUT/'HASH_MANIFEST.json',{'algorithm':'SHA-256','files':files,'exclusions':['HASH_MANIFEST.json','RECOVERY_INDEX.json'],'note':'Index records this manifest hash. Consistency hashes do not make files immutable.'})
index={'format_version':1,'finished_utc':now(),'manifest':'RECOVERY_MANIFEST.json','manifest_sha256':sha((OUT/'RECOVERY_MANIFEST.json').read_bytes()),'hash_manifest':'HASH_MANIFEST.json','hash_manifest_sha256':sha((OUT/'HASH_MANIFEST.json').read_bytes()),'recovered_visible_records':manifest['recovered_visible_records'],'recovered_assistant_finals':manifest['recovered_assistant_finals'],'segment_count':len(results),'no_additional_child_records':len(child_status),'all_retained_field_verifications_passed':all(r['integrity']['pass'] for r in results),'old_files_unchanged':preservation['pass'],'segments':[{'label':r['label'],'first_source_line':r['first'],'last_source_line':r['last'],'records':r['exported_records']} for r in results]}
save(OUT/'RECOVERY_INDEX.json',index); print(json.dumps(index,indent=2))
