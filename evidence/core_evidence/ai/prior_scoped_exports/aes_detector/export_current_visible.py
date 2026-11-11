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
AGENTS = {'/root/clean_aes_detector_review'}
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
                        gap('Readable collaboration argument body unavailable. Original argument string retained verbatim; no decryption or reconstruction attempted.', encrypted_argument_fields=encrypted)
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

started = now()
matches = []
for source in sorted(SESSIONS.rglob('*' + ROOT_ID + '*.jsonl')):
    lines, meta = snapshot(source)
    for no, timestamp in marker_hits(lines):
        matches.append((lines, meta, no, timestamp))
assert len(matches) == 1, 'No unique exact current-task native delegation; refusing export.'
root_lines, root_meta, marker_line, marker_timestamp = matches[0]
dest = BASE / ('snapshot_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
dest.mkdir()
root_result, delegation = export_one('root_current_task', root_lines, root_meta, marker_line, marker_timestamp, dest)
results, missing, child_ids = [root_result], [], {}
for entry in delegation:
    fields = entry['source_fields']
    if fields.get('kind') == 'started':
        child_ids[fields['agent_path']] = fields['agent_thread_id']
for agent in sorted(AGENTS):
    native_id = child_ids.get(agent)
    paths = list(SESSIONS.rglob('*' + native_id + '.jsonl')) if native_id else []
    if len(paths) != 1:
        missing.append({'agent': agent, 'native_thread_id': native_id, 'reason': 'No unique filename found from scoped root SubAgentActivity metadata.'})
        continue
    lines, meta = snapshot(paths[0])
    session = json.loads(lines[0]).get('payload', {})
    assert session.get('id') == native_id
    assert session.get('parent_thread_id') == ROOT_ID
    assert session.get('agent_path') == agent
    meta['native_thread_id'] = native_id
    meta['root_delegation_agent_path'] = agent
    result, _ = export_one(agent.rsplit('/', 1)[1], lines, meta, 1, marker_timestamp, dest)
    results.append(result)

source_matches = []
for source in sorted(SESSIONS.rglob('*' + SOURCE_ID + '*.jsonl')):
    lines, meta = snapshot(source)
    for no, raw in enumerate(lines, 1):
        if SOURCE_MARKER.encode() not in raw:
            continue
        d = json.loads(raw)
        q = d.get('payload', {})
        if (d.get('type') == 'response_item' and q.get('type') == 'message'
                and q.get('role') == 'user' and text_content(q.get('content')).startswith(SOURCE_MARKER)):
            source_matches.append((lines, meta, no, d['timestamp']))
assert len(source_matches) == 1, 'No unique exact source user message; refusing ambiguous export.'
lines, meta, source_line, source_timestamp = source_matches[0]
meta['native_thread_id'] = SOURCE_ID
result, _ = export_one('source_user_request_only', lines, meta, source_line, source_timestamp, dest, last_line=source_line)
results.append(result)

manifest = {'export_started_utc': started, 'export_finished_utc': now(), 'root_chat_id': ROOT_ID,
            'exact_delegation_input_prefix': MARKER, 'root_marker_source_line': marker_line, 'root_marker_timestamp': marker_timestamp,
            'initiation_body_available': True, 'fallback_commentary_boundary_used': False,
            'source_user_thread_id': SOURCE_ID, 'source_user_message_source_line': source_line,
            'scope': 'Visible records beginning with the authentic current-task native delegation; the clean-AES review child identified by scoped native SubAgentActivity metadata; and exactly one source user request record. Parent final response and exporter-worker session excluded.',
            'sessions': results, 'missing_sessions': missing,
            'gaps': ['Encrypted collaboration bodies were not decrypted or reconstructed.', 'Parent final reply, final report completion, checksum sealing, and all post-snapshot activity are outside this bounded export.', 'Earlier mixed history, reasoning, system/developer instructions, platform context, tool-discovery documentation, and compaction payloads are excluded.', 'Source user request is one complete original message, including its additional completion/Claude-review request; no other source-chat history is exported.', 'Image-view paths and native tool records are retained; binary images are not copied.', 'The export-worker session is outside the requested clean-AES root/review scope.'],
            'immutable_flags_used': False}
save(dest / 'SNAPSHOT_MANIFEST.json', manifest)
files = {str(p.relative_to(dest)): {'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in sorted(dest.rglob('*')) if p.is_file()}
save(dest / 'HASH_MANIFEST.json', {'algorithm': 'SHA-256', 'files': files, 'note': 'This hash manifest excludes itself; its hash is recorded in the stable export index.'})
index = {'format_version': 2, 'updated_utc': now(), 'current_snapshot': dest.name,
         'snapshot_manifest': str((dest / 'SNAPSHOT_MANIFEST.json').relative_to(BASE)),
         'snapshot_manifest_sha256': sha((dest / 'SNAPSHOT_MANIFEST.json').read_bytes()),
         'hash_manifest': str((dest / 'HASH_MANIFEST.json').relative_to(BASE)),
         'hash_manifest_sha256': sha((dest / 'HASH_MANIFEST.json').read_bytes()),
         'export_implementation_sha256': sha(Path(__file__).read_bytes()),
         'all_exported_field_and_raw_line_checks_passed': all(r['integrity']['pass'] for r in results),
         'exported_records': sum(r['exported_records'] for r in results), 'session_count': len(results)}
readme = f"""# Current clean-AES detector transcript export

The stable entry point is `EXPORT_INDEX.json`. Current snapshot: `{dest.name}`.

The root scope starts at native line {marker_line} ({marker_timestamp}), the original `send_message_to_thread` delegation from source chat `{SOURCE_ID}`. Its readable body is present and retained verbatim; the fallback commentary boundary was unnecessary.

Included are the root's current comparison records, the `/root/clean_aes_detector_review` session located through scoped native SubAgentActivity metadata, and exactly one authentic source user request (native line {source_line}). The complete source request also mentions project completion and Claude review. No earlier source conversation is included.

Each session contains readable visible messages, retained tool and command records, exact source-field mappings and canonical-JSON field hashes, raw source-line hashes including the original newline, integrity results, and explicit omissions. Saved JSONL is re-read and every retained field and raw-line hash is compared with its native source. Native model labels are configuration metadata only; they do not authenticate actual serving weights or inference parameters.

This is a bounded snapshot, not a complete or immutable capture. Per-session manifests state the native file, byte snapshot, complete-line cutoff and last in-scope timestamp. Encrypted collaboration bodies remain unavailable; none were decrypted or reconstructed. The parent final response, final report completion, checksum sealing, and activity after snapshots are excluded. Reasoning, system/developer instructions, platform context, tool-discovery documentation, compaction payloads and replacement history are excluded. Current tool outputs may contain pre-existing detector artifacts inspected for this comparison; those are current tool observations, not an export of prior chat history. The exporter-worker session is excluded. Image-view paths are recorded without copying image binaries.

SHA-256 manifests provide consistency references; no filesystem immutable flags were set. Hashes establish consistency with captured sources, not independent authenticity or completeness.
"""
for name, content in [('EXPORT_INDEX.json', json.dumps(index, ensure_ascii=False, indent=2) + '\n'), ('README.md', readme)]:
    temp = BASE / ('.' + name + '.tmp')
    temp.write_text(content, encoding='utf-8')
    os.replace(temp, BASE / name)
print(json.dumps({'snapshot': str(dest), 'index': str(BASE / 'EXPORT_INDEX.json'), 'session_count': len(results), 'exported_records': index['exported_records'], 'sessions': [{'label': r['label'], 'records': r['exported_records'], 'fields_verified': r['integrity']['retained_fields_verified'], 'last_exported_timestamp': r['last_exported_timestamp']} for r in results], 'missing_sessions': missing, 'integrity_passed': index['all_exported_field_and_raw_line_checks_passed']}, indent=2))
