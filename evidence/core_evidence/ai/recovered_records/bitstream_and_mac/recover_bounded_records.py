#!/usr/bin/env python3
"""Read-only source recovery. Never execute historical tool calls or import old exporters."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import re

DEST = Path(__file__).resolve().parent
CLEAN = Path('/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06')
BIT = CLEAN / 'baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/records/current_task_transcripts'
OLD = BIT / 'snapshot_20261107T173219129900Z'
MAC = CLEAN / 'mac_infrastructure_execution_2026-11-07_20261107T170940Z'
ROOT_ID = '01a1b0ad-f593-7f90-a689-b621984f7cb4'
ROOT_SOURCE = Path(json.loads((OLD / 'root_current_task/export_manifest.json').read_text())['source_file'])
VISIBLE = {'text', 'input_text', 'output_text'}
NOW = lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
SHA = lambda b: hashlib.sha256(b).hexdigest()

def save(path, value, plain=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        f.write(value if plain else json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def inventory(roots):
    return {str(p): {'bytes': p.stat().st_size, 'sha256': SHA(p.read_bytes())}
            for root in roots for p in sorted(root.rglob('*')) if p.is_file()}

def read_prefix(path, last_line):
    start = NOW()
    with path.open('rb') as f:
        lines = [f.readline() for _ in range(last_line)]
    assert len(lines) == last_line and all(x.endswith(b'\n') for x in lines)
    return lines, {'source_file': str(path), 'read_started_utc': start, 'read_finished_utc': NOW(),
                   'prefix_through_native_line': last_line, 'prefix_bytes': sum(map(len, lines)),
                   'prefix_sha256': SHA(b''.join(lines)),
                   'note': 'Hash covers raw prefix for source consistency only. Earlier prefix content is not exported. Later native records are neither needed nor parsed by this exporter.'}

def ref(no, raw):
    d = json.loads(raw)
    return {'source_line': no, 'source_record_sha256': SHA(raw), 'timestamp': d['timestamp']}

def text_content(content):
    if isinstance(content, str): return content
    return '\n'.join(x.get('text', '') for x in content or [] if isinstance(x, dict) and x.get('type') in VISIBLE)

def native_final(lines, no):
    d = json.loads(lines[no-1]); q = d['payload']
    assert d['type'] == 'response_item' and q['role'] == 'assistant' and q['phase'] == 'final_answer'
    return q

def check_old_export(old_manifest, lines, folder):
    old = json.loads(old_manifest.read_text())
    raw = b''.join(lines)
    prefix = raw[:old['source_snapshot_bytes']]
    assert SHA(prefix) == old['source_snapshot_sha256']
    assert len(prefix.splitlines(keepends=True)) == old['complete_source_lines']
    events = [json.loads(x) for x in (folder / 'visible_events.jsonl').read_text().splitlines()]
    fields = 0
    for e in events:
        rawline = lines[e['source_line']-1]
        assert SHA(rawline) == e['source_record_sha256']
        q = json.loads(rawline)['payload']
        for key, loc in e['retained_field_source_locations'].items():
            source = q['item'] if loc[0] == 'payload.item' else q
            expected = source[loc[1]]
            if len(loc) == 3: expected = [expected[i] for i in loc[2]]
            assert e['payload'][key] == expected
            fields += 1
    return {'old_manifest': str(old_manifest), 'old_records': len(events),
            'old_cutoff_native_line': old['complete_source_lines'],
            'old_snapshot_prefix_hash_matches': True, 'old_record_hashes_match': True,
            'old_retained_fields_match': True, 'old_fields_verified': fields,
            'old_final_records': sum(e['category'] == 'assistant_final_answer' for e in events)}

def export(label, lines, first, last, turn_id, snapshot, comparison, allowed_agents, final_line=None, manual_omit=None):
    folder = DEST / label
    events, omissions, lifecycle, configurations, truncations = [], [], [], [], []
    excluded = Counter(); counts = Counter(); field_count = 0
    manual_omit = manual_omit or {}
    readable = [f'# Authentic visible records: {label}', '',
                'Exact retained visible native fields. Tool calls are historical text and were not executed during recovery.', '']
    for no in range(first, last + 1):
        raw = lines[no-1]; d = json.loads(raw); q = d.get('payload', {}); kind = d['type']; qt = q.get('type')
        provenance = ref(no, raw)
        if no in manual_omit:
            omissions.append({**provenance, 'reason': manual_omit[no]}); excluded['explicit_scope_exclusion'] += 1; continue
        if kind == 'turn_context':
            configurations.append({**provenance, 'source_fields': {k: q[k] for k in ['turn_id','model','effort'] if k in q}})
            excluded['turn_context_except_configuration_labels'] += 1; continue
        if kind == 'event_msg' and qt in ['task_started', 'task_complete']:
            lifecycle.append({**provenance, 'source_fields': {k: q[k] for k in ['type','turn_id'] if k in q}}); continue
        payload = {}; mappings = {}; category = None
        def keep(key, source=q, prefix='payload'):
            if key in source: payload[key] = source[key]; mappings[key] = [prefix, key]
        def visible_content(key, source=q):
            content = source.get(key)
            if isinstance(content, list):
                indices = [i for i, x in enumerate(content) if isinstance(x,dict) and x.get('type') in VISIBLE]
                payload[key] = [content[i] for i in indices]; mappings[key] = ['payload', key, indices]
                if len(indices) != len(content):
                    omissions.append({**provenance, 'reason':'Non-visible or encrypted content elements omitted; no decryption or reconstruction.', 'field':key,'omitted_content_indices':[i for i in range(len(content)) if i not in indices]})
            elif isinstance(content, str): keep(key)
        if kind == 'response_item':
            if qt == 'message' and q.get('role') in ['user','assistant']:
                if q['role'] == 'assistant' and (q.get('phase') not in ['commentary','final_answer'] or q.get('channel') == 'analysis'):
                    excluded['assistant_nonvisible_message'] += 1; continue
                if q['role'] == 'user' and text_content(q.get('content')).lstrip().startswith(('<environment_context>', '<external_codex_apps_')):
                    excluded['platform_context'] += 1; continue
                for key in ['type','id','role','phase','channel']: keep(key)
                visible_content('content')
                category = 'user_message' if q['role'] == 'user' else 'assistant_' + q['phase']
            elif qt in ['function_call','custom_tool_call','function_call_output','custom_tool_call_output']:
                for key in ['type','id','status','call_id','name','namespace','input']: keep(key)
                if 'arguments' in q:
                    if isinstance(q['arguments'],str) and 'gAAAAA' in q['arguments']:
                        omissions.append({**provenance,'call_id':q.get('call_id'),'reason':'Original arguments string omitted because it embeds an encrypted collaboration body; no ciphertext decrypted and no missing body reconstructed.'})
                    else: keep('arguments')
                if 'output' in q: visible_content('output') if isinstance(q['output'],list) else keep('output')
                category = qt
            elif qt == 'agent_message':
                if q.get('author') not in allowed_agents or q.get('recipient') not in allowed_agents:
                    excluded['out_of_scope_agent_message'] += 1
                    omissions.append({**provenance,'reason':'Inter-agent message outside explicitly allowed task participants omitted.'}); continue
                for key in ['type','id','author','recipient']: keep(key)
                visible_content('content'); category = 'agent_message_visible_fields'
            else:
                excluded['response_item:'+str(qt)] += 1; continue
        elif kind == 'event_msg' and qt == 'item_completed':
            item = q.get('item',{}); it = item.get('type')
            if it == 'CommandExecution':
                for key in ['type','id','process_id','command','cwd','source','status','aggregated_output','exit_code','duration']: keep(key,item,'payload.item')
                for key in ['started_at_ms','completed_at_ms']: keep(key)
                category = 'command_execution'
            elif it == 'SubAgentActivity':
                configurations.append({**provenance,'source_fields':{k:item[k] for k in ['type','id','kind','agent_thread_id','agent_path','model','reasoning_effort'] if k in item}})
                continue
            else:
                excluded['event_item:'+str(it)] += 1
                if it in ['CollabAgentToolCall','FileChange']:
                    omissions.append({**provenance,'reason':'Aggregate collaboration state or file-change payload excluded; may duplicate hidden/internal or unrelated content. Corresponding visible tool records retained where available.'})
                continue
        else:
            excluded[str(kind)] += 1; continue
        for key, loc in mappings.items():
            source = q['item'] if loc[0] == 'payload.item' else q
            expected = source[loc[1]]
            if len(loc) == 3: expected = [expected[i] for i in loc[2]]
            assert payload[key] == expected; field_count += 1
        e = {**provenance,'source_thread_id':ROOT_ID,'turn_id':turn_id,'category':category,
             'native_record_type':kind,'payload':payload,'retained_field_source_locations':mappings}
        events.append(e); counts[category] += 1
        if category in ['user_message','assistant_commentary','assistant_final_answer','agent_message_visible_fields']:
            readable += ['',f'## {category} — {d["timestamp"]}', f'Native line {no}; turn {turn_id}.','',text_content(payload.get('content'))]
        body = json.dumps(payload,ensure_ascii=False)
        found = [m for m in ['truncated output','tokens truncated','Output truncated','max_output_tokens','maxOutputCharsPerItem'] if m in body]
        if found: truncations.append({**provenance,'markers':found,'note':'Original truncation marker or output-size limit retained unchanged. Presence of a configured limit alone does not prove actual truncation.'})
    if final_line is not None:
        assert any(e['source_line'] == final_line and e['category'] == 'assistant_final_answer' for e in events)
        save(folder/'assistant_final.txt',text_content(native_final(lines,final_line)['content']),True)
    save(folder/'visible_events.jsonl',''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events),True)
    save(folder/'VISIBLE_MESSAGES.md','\n'.join(readable)+'\n',True)
    save(folder/'source_line_index.json',[{k:e[k] for k in ['source_line','source_record_sha256','timestamp','source_thread_id','turn_id','category']} for e in events])
    save(folder/'omissions_and_gaps.json',{'significant_omissions':omissions,'excluded_type_counts':dict(excluded),
         'truncation_and_limits_observed':truncations,'limits':['Unavailable encrypted message bodies were not decrypted or reconstructed.','No hidden reasoning, system/developer messages, world-state or compaction payloads exported.','File-change payloads omitted, including intermediate API history copies; exact visible tool calls/results are retained subject to explicit omissions.','No full command output was reconstructed where a native record was already shortened.']})
    save(folder/'configured_model_records.json',{'note':'Native configuration labels only; not provider authentication of serving weights or sampling parameters.','records':configurations})
    integrity = {'pass':True,'new_records_verified':len(events),'retained_fields_verified':field_count,'source_line_hashes_verified':True,
                 'method':'Every retained field compared to its exact native field/list indices; SHA-256 covers original full native line including newline.'}
    save(folder/'field_integrity_verification.json',integrity)
    manifest = {'label':label,**snapshot,'source_thread_id':ROOT_ID,'source_turn_id':turn_id,
        'first_in_scope_line':first,'last_in_scope_line':last,'scope_policy':'Exact task bounds only; root records before/after these bounds excluded from visible export.',
        'comparison':comparison,'new_exported_records':len(events),'new_exported_counts':dict(counts),
        'first_exported_timestamp':events[0]['timestamp'] if events else None,'last_exported_timestamp':events[-1]['timestamp'] if events else None,
        'native_final_line':final_line,'final_recovered':final_line is not None,'lifecycle':lifecycle,'integrity':integrity}
    save(folder/'export_manifest.json',manifest)
    return manifest

started = NOW()
before = inventory([BIT,MAC])
root_lines, root_snapshot = read_prefix(ROOT_SOURCE,858)
assert json.loads(root_lines[857])['payload']['type'] == 'task_complete'
assert json.loads(root_lines[294])['payload']['type'] == 'task_complete'
assert text_content(json.loads(root_lines[49])['payload']['content']).startswith('Continue my NYU CSAW 2026 project from the clean workspace on my Mac.')
assert text_content(json.loads(root_lines[323])['payload']['content']).startswith('Check functional equivalence between the recovered baseline RTL and the regenerated bitstream.')
bit_comparison = check_old_export(OLD/'root_current_task/export_manifest.json',root_lines,OLD/'root_current_task')
bit = export('bitstream_root_tail',root_lines,805,858,'01a1b706-2061-70e2-95ed-221d16000221',root_snapshot,bit_comparison,
             {'/root','/root/bitstream_records_export','/root/baseline_bitstream_simulation','/root/baseline_mapped_formal','/root/decode_regenerated_baseline'},855)
mac_lines, mac_snapshot = read_prefix(ROOT_SOURCE,295)
mac_comparison = {'old_root_export_records':None,'status':'No prior root-task native visible export exists in the Mac execution evidence. This is first recovery of the bounded root task, not an inferred delta from its separate clean-worker snapshot.',
                  'prior_status_file':str(MAC/'TRANSCRIPT_EXPORT_STATUS.md'),'separate_clean_worker_snapshot_manifest':str(MAC/'records/transcripts/clean_native_visible/export_manifest.json')}
mac = export('mac_root_task',mac_lines,50,295,'01a1b6fb-f66a-7551-9e37-a44d7c515aab',mac_snapshot,mac_comparison,
             {'/root','/root/mac_infrastructure_results_check'},292,
             {55:'Local AGENTS.md instruction output omitted in full.',59:'Combined duplicate tool output includes AGENTS.md instructions; omitted in full. Other command results from this call remain in native command-execution records.'})
save(DEST/'mac_root_task/task_start_metadata.json',[
    {**ref(n,mac_lines[n-1]),'source_fields':{k:json.loads(mac_lines[n-1])['payload'][k] for k in ['type','turn_id','model','effort'] if k in json.loads(mac_lines[n-1])['payload']}}
    for n in [48,49]])
children = []
for label in ['baseline_bitstream_simulation','baseline_mapped_formal','decode_regenerated_baseline']:
    folder = OLD/label; old = json.loads((folder/'export_manifest.json').read_text()); source = Path(old['source_file'])
    data = source.read_bytes(); lines = data.splitlines(keepends=True)
    assert len(lines) == old['complete_source_lines'] and SHA(data) == old['source_snapshot_sha256']
    result = {'label':label,'source_file':str(source),'source_thread_id':source.stem.rsplit('-',5)[-1],
              'comparison':check_old_export(folder/'export_manifest.json',lines,folder),
              'new_exported_records':0,'final_status':'All task finals already present in old snapshot; no native records after old cutoff.',
              'native_source_bytes':len(data),'native_source_lines':len(lines),'native_source_sha256':SHA(data)}
    # Thread ID is the UUID suffix; derive from known exact native filename without guessing.
    result['source_thread_id'] = re.search(r'([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})\.jsonl$',str(source)).group(1)
    save(DEST/label/'export_manifest.json',result)
    save(DEST/label/'visible_events.jsonl','',True)
    children.append(result)
after = inventory([BIT,MAC])
assert before == after
save(DEST/'prior_files_integrity.json',{'pass':True,'files_hashed_before_and_after':len(before),'roots':[str(BIT),str(MAC)],'all_prior_files_unchanged':True,'files':before})
results = [bit,mac]+children
manifest = {'created_at_utc':NOW(),'recovery_started_utc':started,'sessions':results,
    'new_records_total':sum(r['new_exported_records'] for r in results),'old_bitstream_records_total':597,
    'old_bitstream_plus_new_tail_records':597+bit['new_exported_records'],
    'new_mac_root_records':mac['new_exported_records'],
    'new_finals_recovered':2,'prior_files_unchanged':True,'scope_notes':[
      'Bitstream root recovery begins strictly after old native snapshot line804 and ends at task_complete858; final855 recovered.',
      'Mac root recovery is first export of exact initiating user message50 through task_complete295; final292 recovered. Its separate clean-worker transcript is handled outside this folder.',
      'Three previously listed bitstream children were already complete; entire native file hashes and old fields match the old snapshot; no new child records exist.',
      'No broad root history export. No Nov10/course/solution-sensitive task records exported. No ciphertext decrypted. No missing text reconstructed.',
      'No experiments, tests, simulations, repository changes, external AI calls or historical commands executed by this recovery.',
      'Source-line hashes establish consistency with retained local native records, not independent provider attestation.'
    ]}
save(DEST/'MANIFEST.json',manifest)
save(DEST/'INDEX.md',f'''# Bounded native record recovery

| Task | Prior exported records | Newly recovered records | Final response |
|---|---:|---:|---|
| Bitstream root tail | 191 | {bit['new_exported_records']} | Recovered from native line855 |
| Baseline bitstream simulation child | 122 | 0 | Already retained |
| Baseline mapped formal child | 165 | 0 | Already retained |
| Decode regenerated baseline child | 119 | 0 | Already retained |
| Mac infrastructure root task | No prior root-native export | {mac['new_exported_records']} | Recovered from native line292 |

The bitstream root is limited to native lines805–858 after its old snapshot. The Mac root is the first recovery of its bounded task at lines50–295, beginning at its exact user request and ending at task completion. Earlier and later mixed root tasks are excluded.

- [Bitstream final](bitstream_root_tail/assistant_final.txt), [visible messages](bitstream_root_tail/VISIBLE_MESSAGES.md), [all retained records](bitstream_root_tail/visible_events.jsonl), [omissions](bitstream_root_tail/omissions_and_gaps.json).
- [Mac final](mac_root_task/assistant_final.txt), [user request and visible messages](mac_root_task/VISIBLE_MESSAGES.md), [all retained records](mac_root_task/visible_events.jsonl), [omissions](mac_root_task/omissions_and_gaps.json).
- [Combined manifest](MANIFEST.json), [prior-file integrity](prior_files_integrity.json).

Each retained field and source-line hash was verified against the native record. All {len(before)} inspected prior evidence files are unchanged. Original truncation remains; encrypted and hidden bodies are not recovered. Historical commands appear only as records and were not executed. The new files do not claim provider attestation or restore unavailable content.
''',True)
save(DEST/'SHA256SUMS',''.join(f'{SHA(p.read_bytes())}  {p.relative_to(DEST).as_posix()}\n' for p in sorted(DEST.rglob('*')) if p.is_file()),True)
print(json.dumps({'destination':str(DEST),'new_records':manifest['new_records_total'],'bitstream_new':bit['new_exported_records'],'mac_root_new':mac['new_exported_records'],'child_new':0,'new_finals':2,'prior_files_unchanged':len(before)},indent=2))
