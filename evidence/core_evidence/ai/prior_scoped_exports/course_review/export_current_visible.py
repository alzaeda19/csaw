#!/usr/bin/env python3
"""Export bounded, authentic visible records for the 2026-11-10 material review."""
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
MARKER = 'okay so i have the entire meeting transcript and new documents to use to complete this project.'
AGENTS = {'/root/meeting_requirement_review', '/root/course_package_review'}
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
        # Earlier content is never decoded or parsed unless the exact marker bytes match.
        if MARKER.encode() not in raw:
            continue
        d = json.loads(raw)
        q = d.get('payload', {})
        if d.get('type') != 'response_item' or q.get('type') != 'message' or q.get('role') != 'user':
            continue
        body = text_content(q.get('content'))
        request = body.split('## My request:\n', 1)[-1].lstrip()
        if request.startswith(MARKER):
            hits.append((no, d['timestamp']))
    return hits

def export_one(label, lines, meta, first_line, minimum_timestamp, dest):
    events, gaps, delegation, models = [], [], [], []
    omitted, counts = Counter(), Counter()
    list_calls = set()
    folder = dest / label
    folder.mkdir()
    for no, raw in enumerate(lines, 1):
        if no < first_line:
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
                category = qt
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
                    gap('Agent-message body outside the two requested review-agent sessions excluded.')
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
        events.append({**ref, 'category': category, 'payload': payload, 'retained_field_source_locations': mappings})
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
            verified += 1
    readable = ['# Authentic visible records: ' + label, '', 'Native visible message fields only. Complete retained tool and command records are in visible_events.jsonl. Encrypted collaboration bodies are unavailable and are not reconstructed.', '']
    for event in saved:
        category = event['category']
        if category == 'user_message' or category.startswith('assistant_') or category == 'agent_message_readable_envelope':
            readable += ['', '## ' + category + ' — ' + event['timestamp'], 'Native source line ' + str(event['source_line']) + '.', '', text_content(event['payload'].get('content'))]
            if category == 'agent_message_readable_envelope' and not event['payload'].get('content'):
                readable += ['[Native collaboration body unavailable in readable form.]']
    integrity = {'pass': True, 'records_verified': len(saved), 'retained_fields_verified': verified, 'source_line_hashes_verified': True,
                 'method': 'Saved JSONL re-read; every retained field compared to the exact original native field or selected original list elements. SHA-256 verified against each full original source line, including newline.'}
    save(folder / 'VISIBLE_MESSAGES.md', '\n'.join(readable) + '\n', True)
    save(folder / 'source_line_index.json', [{k: e[k] for k in ['source_line', 'source_record_sha256', 'timestamp', 'category']} for e in saved])
    save(folder / 'omissions_and_gaps.json', gaps)
    save(folder / 'configured_model_records.json', {'note': 'Configured native model and effort labels do not authenticate serving weights or actual inference parameters.', 'turn_context_labels': models, 'delegation_activity_labels': delegation})
    save(folder / 'field_integrity_verification.json', integrity)
    manifest = {**meta, 'label': label, 'first_in_scope_line': first_line, 'minimum_timestamp': minimum_timestamp,
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
assert len(matches) == 1, 'No unique exact current-task user-message marker; refusing export.'
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
    meta['native_thread_id'] = native_id
    meta['root_delegation_agent_path'] = agent
    result, _ = export_one(agent.rsplit('/', 1)[1], lines, meta, 1, marker_timestamp, dest)
    results.append(result)

manifest = {'export_started_utc': started, 'export_finished_utc': now(), 'root_chat_id': ROOT_ID,
            'exact_user_marker': MARKER, 'root_marker_source_line': marker_line, 'root_marker_timestamp': marker_timestamp,
            'scope': 'Available visible records from the exact current user message onward, and the two review-agent sessions identified by scoped native delegation metadata.',
            'sessions': results, 'missing_sessions': missing,
            'gaps': ['Encrypted collaboration bodies were not decrypted or reconstructed.', 'Root final reply and all post-snapshot activity are outside this bounded export.', 'Earlier mixed history, reasoning, system/developer instructions, platform context, and compaction payloads are excluded.', 'Image-view paths and native tool records are retained; binary images are not copied into this transcript export.', 'The export-worker session is outside the requested two-review-agent export scope.'],
            'immutable_flags_used': False}
save(dest / 'SNAPSHOT_MANIFEST.json', manifest)
files = {str(p.relative_to(dest)): {'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in sorted(dest.rglob('*')) if p.is_file()}
save(dest / 'HASH_MANIFEST.json', {'algorithm': 'SHA-256', 'files': files, 'note': 'This hash manifest excludes itself; its hash is recorded in the stable export index.'})
index = {'format_version': 1, 'updated_utc': now(), 'current_snapshot': dest.name,
         'snapshot_manifest': str((dest / 'SNAPSHOT_MANIFEST.json').relative_to(BASE)),
         'snapshot_manifest_sha256': sha((dest / 'SNAPSHOT_MANIFEST.json').read_bytes()),
         'hash_manifest': str((dest / 'HASH_MANIFEST.json').relative_to(BASE)),
         'hash_manifest_sha256': sha((dest / 'HASH_MANIFEST.json').read_bytes()),
         'export_implementation_sha256': sha(Path(__file__).read_bytes()),
         'all_exported_field_and_raw_line_checks_passed': all(r['integrity']['pass'] for r in results),
         'exported_records': sum(r['exported_records'] for r in results), 'session_count': len(results)}
readme = '# Current course-review transcript export\n\n' + 'The stable entry point is `EXPORT_INDEX.json`. Current snapshot: `' + dest.name + '`.\n\n' + 'The root scope starts at native line ' + str(marker_line) + ' (' + marker_timestamp + '), the user message containing the exact marker:\n\n> ' + MARKER + '\n\n' + 'Each session contains readable visible messages, retained tool and command records, source-line hashes, exact-field integrity results, and omissions. The two review sessions were located using the root native SubAgentActivity thread IDs. Prior mixed history was not exported.\n\n' + 'This is a bounded snapshot, not a complete or immutable capture of the ongoing chat. Encrypted collaboration bodies are unavailable; none were decrypted or reconstructed. Root final reply and activity after each source snapshot are not captured. Reasoning, system/developer instructions, platform context, and compaction payloads are excluded. Image-view paths are recorded without copying image binaries.\n\n' + 'Every saved JSONL field was checked against the native source field, and every exported source-line hash was verified. SHA-256 manifests provide integrity references; no filesystem immutable flags were set. These hashes establish consistency with the captured sources, not independent authenticity or completeness.\n'
for name, content in [('EXPORT_INDEX.json', json.dumps(index, ensure_ascii=False, indent=2) + '\n'), ('README.md', readme)]:
    temp = BASE / ('.' + name + '.tmp')
    temp.write_text(content, encoding='utf-8')
    os.replace(temp, BASE / name)
print(json.dumps({'snapshot': str(dest), 'index': str(BASE / 'EXPORT_INDEX.json'), 'session_count': len(results), 'exported_records': index['exported_records'], 'sessions': [{'label': r['label'], 'records': r['exported_records'], 'fields_verified': r['integrity']['retained_fields_verified'], 'last_exported_timestamp': r['last_exported_timestamp']} for r in results], 'missing_sessions': missing, 'integrity_passed': index['all_exported_field_and_raw_line_checks_passed']}, indent=2))
