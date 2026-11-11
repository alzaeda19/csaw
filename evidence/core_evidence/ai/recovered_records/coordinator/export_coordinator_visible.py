#!/usr/bin/env python3
"""Export bounded, authentic visible records for the 2026-11-10 defensive detector task."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import os
import re

BASE = Path(__file__).resolve().parent
SESSIONS = Path('/Users/al-zayedal-hassan/.codex/sessions')
ROOT_ID = '01a1b0ad-f593-7f90-a689-b621984f7cb4'
MARKER = 'User explicitly requests: work with trojan orchestrator to run four detectors on clean AES reference and compare existing baseline'
FALLBACK_MARKER = 'I’ll run the four detectors on a new isolated copy of the clean AES reference, including both dependency files'
SOURCE_ID = '01a1c563-aa79-7e12-ae2f-72d867d1e3da'
SOURCE_MARKER = 'now work with the trojan orchestrator to run the four detectors on the clean AES reference and compare with the existing baseline results. keep everything separate, no Trojan generation or published solutions.'
AGENTS = {'/root/readiness_review'}
TEXT_TYPES = {'text', 'input_text', 'output_text'}
HEADER = re.compile(rb'^\{"timestamp":"([^"\n]+)"')

def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def save(path, obj, plain=False):
    with path.open('x', encoding='utf-8') as f:
        f.write(obj if plain else json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def text_content(content):
    if isinstance(content, str):
        return content
    return '\n'.join(x.get('text', '') for x in content or []
                     if isinstance(x, dict) and x.get('type') in TEXT_TYPES)

def snapshot(path):
    started = now()
    with path.open('rb') as f:
        limit = os.fstat(f.fileno()).st_size
        raw = f.read(limit)
    lines = raw.splitlines(keepends=True)
    trailing = len(lines.pop()) if lines and not lines[-1].endswith(b'\n') else 0
    return lines, {'source_file': str(path), 'snapshot_read_started_utc': started,
                   'snapshot_read_finished_utc': now(), 'source_snapshot_bytes': len(raw),
                   'source_snapshot_sha256': sha(raw), 'complete_source_lines': len(lines),
                   'trailing_incomplete_bytes_not_parsed': trailing}

def marker_hits(lines):
    hits = []
    for no, raw in enumerate(lines, 1):
        if MARKER.encode() not in raw:
            continue
        d = json.loads(raw)
        q = d.get('payload', {})
        if (d.get('type') == 'response_item' and q.get('type') == 'function_call_output'
                and q.get('name') == 'send_message_to_thread'
                and isinstance(q.get('output'), str)
                and q['output'].startswith('<codex_delegation>')
                and '<source_thread_id>' + SOURCE_ID + '</source_thread_id>' in q['output']
                and '<input>' + MARKER in q['output']):
            hits.append((no, d['timestamp']))
    return hits


def field_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8'))

def export_one(label, lines, meta, first_line, minimum_timestamp, dest, last_line=None):
    events, gaps, delegation, models = [], [], [], []
    omitted, counts = Counter(), Counter()
    list_calls = set()
    folder = dest / label
    folder.mkdir()
    for no, raw in enumerate(lines, 1):
        if no < first_line or (last_line is not None and no > last_line):
            continue
        header = HEADER.match(raw)
        if not header or header[1].decode() < minimum_timestamp:
            continue
        d = json.loads(raw)
        if (meta['source_file'], no) in EXCLUDED_VISIBLE_LINES:
            gaps.append({'source_line':no,'source_record_sha256':sha(raw),'timestamp':d.get('timestamp'),'reason':EXCLUDED_VISIBLE_LINES[(meta['source_file'],no)]})
            omitted['scoped_sensitive_or_history_output'] += 1
            continue
        q = d.get('payload', {})
        kind, qt = d.get('type'), q.get('type')
        ref = {'source_line': no, 'source_record_sha256': sha(raw), 'timestamp': d['timestamp']}
        payload, mappings, category = {}, {}, None

        def keep(key, source=q, prefix='payload'):
            if key in source:
                payload[key] = source[key]
                mappings[key] = [prefix, key]

        def gap(reason, **extra):
            gaps.append({**ref, 'reason': reason, **extra})

        if kind == 'compacted':
            gap('Compaction payload and replacement history excluded in full.')
            omitted['compaction_payload'] += 1
            continue
        if kind == 'turn_context':
            models.append({**ref, 'source_fields': {k: q[k] for k in ['turn_id', 'model', 'effort'] if k in q}})
            omitted['turn_context_except_configured_model_labels'] += 1
            continue
        if kind == 'response_item':
            if qt == 'message' and q.get('role') in ['user', 'assistant']:
                if label == 'root_current_task' and q.get('phase') == 'final_answer':
                    gap('Parent final response excluded by export scope.')
                    omitted['parent_final_response'] += 1
                    continue
                if q['role'] == 'assistant' and (q.get('phase') not in ['commentary', 'final_answer'] or q.get('channel') == 'analysis'):
                    omitted['nonvisible_assistant_message'] += 1
                    continue
                if q['role'] == 'user' and text_content(q.get('content')).lstrip().startswith('<environment_context>'):
                    omitted['platform_environment_context'] += 1
                    continue
                for key in ['type', 'id', 'role', 'content', 'phase', 'channel']:
                    keep(key)
                category = 'user_message' if q['role'] == 'user' else 'assistant_' + q['phase']
            elif qt in ['function_call', 'custom_tool_call', 'function_call_output', 'custom_tool_call_output']:
                if qt in ['function_call', 'custom_tool_call'] and q.get('name') == 'list_agents':
                    list_calls.add(q.get('call_id'))
                if qt in ['function_call_output', 'custom_tool_call_output'] and q.get('call_id') in list_calls:
                    gap('Aggregate agent-list output excluded because it may contain unrelated prior-task reports.')
                    omitted['aggregate_agent_list_output'] += 1
                    continue
                for key in ['type', 'id', 'status', 'call_id', 'name', 'namespace', 'arguments', 'input', 'output']:
                    keep(key)
                if isinstance(q.get('output'), list):
                    output = q['output']
                    omitted_indices = [i for i, x in enumerate(output) if isinstance(x, dict)
                                       and 'exec tool declaration:' in x.get('text', '')
                                       and x.get('text', '').lstrip().startswith('[{"name":"mcp__')]
                    if omitted_indices:
                        indices = [i for i in range(len(output)) if i not in omitted_indices]
                        payload['output'] = [output[i] for i in indices]
                        mappings['output'] = ['payload', 'output', indices]
                        gap('Tool-discovery documentation omitted; other original output list elements retained exactly.', omitted_output_indices=omitted_indices)
                        omitted['tool_discovery_documentation_elements'] += len(omitted_indices)
                category = 'initiating_delegation' if label == 'root_current_task' and no == first_line else qt
                if q.get('namespace') == 'collaboration':
                    try:
                        args = json.loads(q.get('arguments', '{}'))
                    except (ValueError, TypeError):
                        args = {}
                    encrypted = [k for k, v in args.items() if isinstance(v, str) and v.startswith('gAAAAA')]
                    if encrypted:
                        payload.pop('arguments', None)
                        mappings.pop('arguments', None)
                        gap('Readable collaboration argument body unavailable. Encrypted argument field excluded; no decryption or reconstruction attempted.', encrypted_argument_fields=encrypted)
            elif qt == 'agent_message':
                if q.get('author') not in AGENTS | {'/root'} or q.get('recipient') not in AGENTS | {'/root'}:
                    gap('Agent-message body outside the requested clean-AES review session excluded.')
                    omitted['other_agent_message'] += 1
                    continue
                for key in ['type', 'id', 'author', 'recipient']:
                    keep(key)
                content = q.get('content', [])
                indices = [i for i, x in enumerate(content) if isinstance(x, dict) and x.get('type') in TEXT_TYPES]
                payload['content'] = [content[i] for i in indices]
                mappings['content'] = ['payload', 'content', indices]
                if len(indices) != len(content):
                    gap('Encrypted or nontext collaboration body unavailable; only native readable envelope retained. No decryption or reconstruction attempted.', omitted_content_indices=[i for i in range(len(content)) if i not in indices])
                category = 'agent_message_readable_envelope'
            else:
                omitted['response_item:' + str(qt)] += 1
                continue
        elif kind == 'event_msg' and qt == 'item_completed':
            item = q.get('item', {})
            itype = item.get('type')
            if itype in ['CommandExecution', 'ImageView', 'FileChange']:
                fields = {
                    'CommandExecution': ['type', 'id', 'process_id', 'command', 'cwd', 'source', 'status', 'aggregated_output', 'exit_code', 'duration'],
                    'ImageView': ['type', 'id', 'path'],
                    'FileChange': ['type', 'id', 'changes', 'status', 'stdout', 'stderr'],
                }[itype]
                for key in fields:
                    keep(key, item, 'payload.item')
                for key in ['started_at_ms', 'completed_at_ms']:
                    keep(key)
                category = {'CommandExecution': 'command_execution', 'ImageView': 'image_view_record', 'FileChange': 'file_change_record'}[itype]
            elif itype == 'SubAgentActivity' and item.get('agent_path') in AGENTS:
                delegation.append({**ref, 'source_fields': {k: item[k] for k in ['type', 'id', 'kind', 'agent_thread_id', 'agent_path', 'model', 'reasoning_effort'] if k in item}})
                continue
            elif itype == 'CollabAgentToolCall':
                gap('Aggregate collaboration activity excluded to avoid unrelated prior-agent states.')
                omitted['aggregate_collaboration_activity'] += 1
                continue
            else:
                omitted['event_item:' + str(itype)] += 1
                continue
        else:
            omitted[str(kind)] += 1
            continue
        events.append({**ref, 'category': category, 'payload': payload, 'retained_field_source_locations': mappings, 'retained_field_sha256': {key: field_sha(value) for key, value in payload.items()}})
        counts[category] += 1

    save(folder / 'visible_events.jsonl', ''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in events), True)
    # Re-read the saved export and compare each retained field to its exact native source.
    saved = [json.loads(line) for line in (folder / 'visible_events.jsonl').read_text().splitlines()]
    verified = 0
    for event in saved:
        raw = lines[event['source_line'] - 1]
        assert sha(raw) == event['source_record_sha256']
        native = json.loads(raw)['payload']
        for key, location in event['retained_field_source_locations'].items():
            source = native.get('item', {}) if location[0] == 'payload.item' else native
            expected = source[location[1]]
            if len(location) == 3:
                expected = [expected[i] for i in location[2]]
            assert event['payload'][key] == expected, (label, event['source_line'], key)
            assert event['retained_field_sha256'][key] == field_sha(expected)
            verified += 1
    readable = ['# Authentic visible records: ' + label, '', 'Native visible message fields only. Complete retained tool and command records are in visible_events.jsonl. Encrypted collaboration bodies are unavailable and are not reconstructed.', '']
    for event in saved:
        category = event['category']
        if category == 'initiating_delegation':
            readable += ['', '## initiating_delegation — ' + event['timestamp'], 'Native source line ' + str(event['source_line']) + '.', '', event['payload']['output']]
        if category == 'user_message' or category.startswith('assistant_') or category == 'agent_message_readable_envelope':
            readable += ['', '## ' + category + ' — ' + event['timestamp'], 'Native source line ' + str(event['source_line']) + '.', '', text_content(event['payload'].get('content'))]
            if category == 'agent_message_readable_envelope' and not event['payload'].get('content'):
                readable += ['[Native collaboration body unavailable in readable form.]']
    metadata_verified = 0
    for entry in models + delegation:
        raw = lines[entry['source_line'] - 1]
        assert sha(raw) == entry['source_record_sha256']
        native = json.loads(raw)['payload']
        native = native.get('item', native)
        entry['source_field_sha256'] = {key: field_sha(value) for key, value in entry['source_fields'].items()}
        for key, value in entry['source_fields'].items():
            assert native[key] == value
            metadata_verified += 1
    integrity = {'pass': True, 'metadata_fields_verified': metadata_verified, 'retained_field_hash_algorithm': 'SHA-256 of UTF-8 JSON with ensure_ascii=False, sort_keys=True, separators=(comma, colon)', 'records_verified': len(saved), 'retained_fields_verified': verified, 'source_line_hashes_verified': True,
                 'method': 'Saved JSONL re-read; every retained field compared to the exact original native field or selected original list elements. SHA-256 verified against each full original source line, including newline.'}
    save(folder / 'VISIBLE_MESSAGES.md', '\n'.join(readable) + '\n', True)
    save(folder / 'source_line_index.json', [{k: e[k] for k in ['source_line', 'source_record_sha256', 'timestamp', 'category']} for e in saved])
    save(folder / 'omissions_and_gaps.json', gaps)
    save(folder / 'configured_model_records.json', {'note': 'Configured native model and effort labels do not authenticate serving weights or actual inference parameters.', 'turn_context_labels': models, 'delegation_activity_labels': delegation})
    save(folder / 'field_integrity_verification.json', integrity)
    manifest = {**meta, 'label': label, 'first_in_scope_line': first_line, 'minimum_timestamp': minimum_timestamp, 'last_in_scope_source_line': last_line or len(lines), 'bounded_source_cutoff_timestamp': json.loads(lines[(last_line or len(lines))-1]).get('timestamp'),
                'exported_records': len(saved), 'exported_counts': dict(counts), 'excluded_counts': dict(omitted),
                'last_exported_timestamp': saved[-1]['timestamp'] if saved else None, 'integrity': integrity,
                'significant_omissions_and_gaps': len(gaps)}
    save(folder / 'export_manifest.json', manifest)
    return manifest, delegation

EXCLUDED_VISIBLE_LINES = {}

if __name__ == '__main__':
    source = Path('/Users/al-zayedal-hassan/.codex/sessions/2026/11/10/rollout-2026-11-10T07-16-45-01a1c563-aa79-7e12-ae2f-72d867d1e3da.jsonl')
    source_id = '01a1c563-aa79-7e12-ae2f-72d867d1e3da'
    lines, meta = snapshot(source)
    first = 168
    start = json.loads(lines[first-1])['timestamp']
    q = json.loads(lines[first-1])['payload']
    assert q['role'] == 'user' and text_content(q['content']).startswith(SOURCE_MARKER)
    unsafe_calls=set()
    credential=re.compile(r'(?:sk-(?:proj-)?[A-Za-z0-9_-]{25,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|xox[baprs]-[A-Za-z0-9-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    def configure_omissions(raw_lines, path, begin):
        unsafe=set()
        for no,raw in enumerate(raw_lines,1):
            if no<begin: continue
            d=json.loads(raw);q=d.get('payload',{})
            if d.get('type')!='response_item': continue
            if q.get('type') in ['custom_tool_call','function_call']:
                code=str(q.get('input',q.get('arguments','')))
                if 'mcp__codex_app__read_thread' in code or q.get('name')=='read_thread':
                    unsafe.add(q.get('call_id'))
            if q.get('type') in ['custom_tool_call_output','function_call_output'] and q.get('call_id') in unsafe:
                EXCLUDED_VISIBLE_LINES[(str(path),no)]='Entire chat-read result omitted because it may include mixed earlier chat history. Native line hash retained; no historical body copied.'
            if credential.search(json.dumps(q)):
                EXCLUDED_VISIBLE_LINES[(str(path),no)]='Entire visible record omitted after credential-pattern screening. Native line hash retained; suspected secret not copied.'
    configure_omissions(lines,source,first)
    dest=BASE/('snapshot_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));dest.mkdir()
    meta['native_thread_id']=source_id
    parent,activity=export_one('coordinator_current_clean_work',lines,meta,first,start,dest)
    results=[parent];snapshots=[(lines,meta,parent)]
    child_ids={x['source_fields']['agent_thread_id'] for x in activity if x['source_fields'].get('kind')=='started'}
    assert child_ids=={'01a1c574-9a3c-73d2-aa19-6b294a9719e1'}
    for child_id in sorted(child_ids):
        candidates=list(SESSIONS.rglob('*'+child_id+'.jsonl'));assert len(candidates)==1
        raw_lines,child_meta=snapshot(candidates[0]);sm=json.loads(raw_lines[0])['payload']
        assert sm.get('parent_thread_id')==source_id and sm.get('agent_path')=='/root/readiness_review'
        child_meta['native_thread_id']=child_id
        configure_omissions(raw_lines,candidates[0],1)
        child,_=export_one('coordinator_readiness_review',raw_lines,child_meta,1,start,dest)
        results.append(child);snapshots.append((raw_lines,child_meta,child))
    for raw_lines,sm,res in snapshots:
        turns={};turn=None
        for no,raw in enumerate(raw_lines,1):
            d=json.loads(raw);q=d.get('payload',{})
            if d.get('type')=='turn_context' and q.get('turn_id'):turn=q['turn_id']
            if d.get('type')=='event_msg' and q.get('type')=='task_started' and q.get('turn_id'):turn=q['turn_id']
            turns[no]=turn
        events=[json.loads(x) for x in (dest/res['label']/'visible_events.jsonl').read_text().splitlines()]
        save(dest/res['label']/'thread_turn_index.json',[{'source_line':e['source_line'],'source_record_sha256':e['source_record_sha256'],'native_thread_id':sm['native_thread_id'],'native_turn_id':turns.get(e['source_line']),'native_payload_id':e['payload'].get('id'),'category':e['category']} for e in events])
    total=sum(x['exported_records'] for x in results)
    report={'created_utc':now(),'scope':'Coordinator source chat from the verified clean AES detector/comparison user request through bounded current snapshot, plus its scoped readiness-review child. Earlier source history and chat-read output bodies omitted. Current recovery/submission task is still active, so later records/final remain outside cutoff.','sessions':results,'exported_records':total,'already_exported_records_carried_forward':1,'newly_exported_records_relative_to_known_AES_source_user_snapshot':total-1,'counts_are_visible_native_records_not_unique_conversational_turns':True,'known_prior_reference':str(Path('/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/records/current_task_transcripts/EXPORT_INDEX.json')),'limitations':['No claim that earlier course-package/clean-AES-reference work is fully exported: source lines before168 excluded.','Native collaboration bodies can be encrypted; unavailable portions excluded, no decryption/reconstruction.','Task is ongoing: messages/final after each snapshot cutoff excluded.','Tool output may already be truncated; truncation retained as observed, missing text not reconstructed.','Only local native source/field consistency verified; no global completeness or independent authenticity claim.']}
    save(dest/'RECOVERY_INDEX.json',report)
    files={str(f.relative_to(dest)):{'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in sorted(dest.rglob('*')) if f.is_file()}
    save(dest/'HASH_MANIFEST.json',{'files':files,'scope':'All snapshot files except this manifest.'})
    save(BASE/'RECOVERY_INDEX.json',{'snapshot':dest.name,'snapshot_index':str((dest/'RECOVERY_INDEX.json').relative_to(BASE)),'snapshot_index_sha256':sha((dest/'RECOVERY_INDEX.json').read_bytes()),'hash_manifest':str((dest/'HASH_MANIFEST.json').relative_to(BASE)),'hash_manifest_sha256':sha((dest/'HASH_MANIFEST.json').read_bytes()),'exported_records':total,'carried_forward_records':1,'new_records':total-1})
    print(json.dumps({'exported_records':total,'new_records':total-1,'sessions':[(x['label'],x['exported_records'],x['last_in_scope_source_line']) for x in results],'snapshot':str(dest)},indent=2))
