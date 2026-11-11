#!/usr/bin/env python3
"""Preserve bounded native visible records; never evaluates or modifies detector work.

Run with --prepare to verify exact scope without creating a snapshot.
Run with --snapshot-after-results-ready ONLY after the parent supplies RESULTS_READY.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse
import hashlib
import json
import os
import re

BASE = Path(__file__).resolve().parent
SESSIONS = Path('/Users/al-zayedal-hassan/.codex/sessions')
ROOT_ID = '01a1b0ad-f593-7f90-a689-b621984f7cb4'
ROOT_PATH = SESSIONS / '2026/11/07/rollout-2026-11-07T12-02-34-01a1b0ad-f593-7f90-a689-b621984f7cb4_01a1b6f6-401f-7221-94ed-de4507c582f4.jsonl'
SOURCE_ID = '01a1c563-aa79-7e12-ae2f-72d867d1e3da'
MARKER = 'New direct user request in coordinating chat:'
MARKER_PHRASE = 'existing Trojan-infected and clean designs'
SOURCE_MARKER = 'While we wait for his reply, work with the trojan orchestrator to test the four detectors on the package’s existing Trojan-infected and clean designs. No new Trojan generation or published solutions.'
AGENTS = {'/root/existing_design_intake', '/root/existing_detector_method_review'}
ALLOWED_AUTHORS = AGENTS | {'/root'}
TEXT_TYPES = {'text', 'input_text', 'output_text'}
ENCRYPTED = re.compile(r'gAAAA[A-Za-z0-9_-]{60,}')
SECRET = re.compile(r'(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|Bearer\s+[A-Za-z0-9._~+/-]{30,})')
READ_THREAD_CALL = re.compile(r'\btools\.[A-Za-z0-9_]*read_thread\s*\(')

def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def field_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())

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

def ref(lines, no):
    d = json.loads(lines[no - 1])
    return {'source_line': no, 'source_record_sha256': sha(lines[no - 1]), 'timestamp': d.get('timestamp')}

def scope_lookup():
    lines, meta = snapshot(ROOT_PATH)
    matches = []
    for no, raw in enumerate(lines, 1):
        if MARKER.encode() not in raw or MARKER_PHRASE.encode() not in raw:
            continue
        d = json.loads(raw); q = d.get('payload', {})
        output = q.get('output')
        if (d.get('type') == 'response_item' and q.get('type') == 'function_call_output'
                and q.get('name') == 'send_message_to_thread' and isinstance(output, str)
                and output.startswith('<codex_delegation>')
                and '<source_thread_id>' + SOURCE_ID + '</source_thread_id>' in output
                and '<input>' + MARKER in output):
            matches.append((no, d['timestamp']))
    assert len(matches) == 1, 'No unique exact current native delegation; refusing export.'
    first, stamp = matches[0]
    activities = []
    ids = {}
    for no in range(first, len(lines) + 1):
        d = json.loads(lines[no - 1]); q = d.get('payload', {}); i = q.get('item', {})
        if d.get('type') == 'event_msg' and q.get('type') == 'item_completed' and i.get('type') == 'SubAgentActivity' and i.get('agent_path') in AGENTS:
            fields = {k: i[k] for k in ['type', 'id', 'kind', 'agent_thread_id', 'agent_path', 'model', 'reasoning_effort'] if k in i}
            activities.append({**ref(lines, no), 'source_fields': fields,
                               'source_field_sha256': {k: field_sha(v) for k, v in fields.items()}})
            if i.get('kind') == 'started':
                if i['agent_path'] in ids:
                    assert ids[i['agent_path']] == i['agent_thread_id']
                ids[i['agent_path']] = i['agent_thread_id']
    children = []
    for agent in sorted(AGENTS):
        sid = ids.get(agent)
        paths = list(SESSIONS.rglob('*' + sid + '.jsonl')) if sid else []
        assert len(paths) == 1, 'No unique current mapped child source: ' + agent
        child_lines, child_meta = snapshot(paths[0])
        session = json.loads(child_lines[0])['payload']
        assert session.get('id') == sid and session.get('parent_thread_id') == ROOT_ID and session.get('agent_path') == agent
        children.append((agent, sid, child_lines, child_meta))
    source_paths = list(SESSIONS.rglob('*' + SOURCE_ID + '*.jsonl'))
    source_matches = []
    for path in source_paths:
        source_lines, source_meta = snapshot(path)
        for no, raw in enumerate(source_lines, 1):
            if SOURCE_MARKER.encode() not in raw:
                continue
            d = json.loads(raw); q = d.get('payload', {})
            if d.get('type') == 'response_item' and q.get('type') == 'message' and q.get('role') == 'user' and text_content(q.get('content')).strip() == SOURCE_MARKER:
                source_matches.append((source_lines, source_meta, no, d['timestamp']))
    assert len(source_matches) == 1, 'No unique exact original human request.'
    return lines, meta, first, stamp, activities, children, source_matches[0]

def unsafe_reason(value):
    s = json.dumps(value, ensure_ascii=False)
    if ENCRYPTED.search(s):
        return 'Encrypted body excluded; no decryption or reconstruction attempted.'
    if SECRET.search(s):
        return 'Potential credential-bearing field excluded; value not retained.'
    return None

def get_path(root, path):
    for part in path:
        root = root[part]
    return root

def export_one(label, lines, meta, first_line, minimum_timestamp, dest, last_line=None):
    end = last_line or len(lines)
    session = json.loads(lines[0])['payload']
    sid = session['id']
    folder = dest / label
    folder.mkdir()
    events, gaps, metadata = [], [], []
    excluded, counts = Counter(), Counter()
    id_turn, line_turn = {}, {}
    current_turn = None
    # Metadata only: no earlier bodies are retained or used as a scope fallback.
    for no, raw in enumerate(lines, 1):
        d = json.loads(raw); q = d.get('payload', {})
        turn = q.get('turn_id')
        if turn:
            current_turn = (turn, no)
        line_turn[no] = current_turn
        i = q.get('item', {})
        if d.get('type') == 'event_msg' and q.get('type') == 'item_completed' and turn:
            if i.get('id'):
                id_turn[i['id']] = (turn, no)
    mixed_calls = set()
    blocked_calls = set()
    for no in range(first_line, end + 1):
        d = json.loads(lines[no - 1]); q = d.get('payload', {})
        if d.get('type') != 'response_item':
            continue
        if q.get('type') in ['function_call', 'custom_tool_call']:
            s = q.get('input', '') + q.get('arguments', '')
            if READ_THREAD_CALL.search(s) or q.get('name') == 'read_thread':
                mixed_calls.add(q.get('call_id'))
            if q.get('name') == 'list_agents':
                blocked_calls.add(q.get('call_id'))

    for no in range(first_line, end + 1):
        raw = lines[no - 1]; d = json.loads(raw); q = d.get('payload', {})
        if d.get('timestamp', '') < minimum_timestamp:
            excluded['before_current_delegation_timestamp'] += 1
            continue
        kind, qt = d.get('type'), q.get('type')
        source_ref = ref(lines, no)
        payload, maps = {}, {}
        category = None

        def gap(reason, **extra):
            gaps.append({**source_ref, 'reason': reason, **extra})

        def keep(key, path=None, indices=None):
            path = path or ['payload', key]
            try:
                value = get_path(d, path)
            except KeyError:
                return
            if indices is not None:
                value = [value[i] for i in indices]
            reason = unsafe_reason(value)
            if reason:
                gap(reason, omitted_field_path=path, omitted_indices=indices)
                excluded['encrypted_or_potential_credential_field'] += 1
                return
            payload[key] = value
            maps[key] = {'source_path': path, **({'selected_indices': indices} if indices is not None else {})}

        def keep_text_blocks():
            content = q.get('content', [])
            if not isinstance(content, list):
                gap('Non-list content excluded from visible-text selection.')
                return
            indices = [i for i, x in enumerate(content) if isinstance(x, dict) and x.get('type') in TEXT_TYPES and unsafe_reason(x) is None]
            keep('content', indices=indices)
            missing = [i for i in range(len(content)) if i not in indices]
            if missing:
                gap('Encrypted, nontext, or potential credential-bearing content blocks excluded; no decryption or reconstruction attempted.', omitted_content_indices=missing)
                excluded['nonvisible_content_blocks'] += len(missing)

        if kind == 'compacted':
            gap('Compaction payload and replacement history excluded in full.')
            excluded['compaction_payload'] += 1
            continue
        if kind == 'turn_context':
            # Only IDs/model configuration, never instructions or reasoning.
            values = {k: q[k] for k in ['turn_id', 'model', 'effort'] if k in q}
            metadata.append({**source_ref, 'source_fields': values, 'source_paths': {k: ['payload', k] for k in values}, 'source_field_sha256': {k: field_sha(v) for k, v in values.items()}})
            excluded['turn_context_except_selected_metadata'] += 1
            continue
        if kind == 'response_item':
            if qt == 'message' and q.get('role') in ['user', 'assistant']:
                if q['role'] == 'assistant' and (q.get('phase') not in ['commentary', 'final_answer'] or q.get('channel') == 'analysis'):
                    excluded['nonvisible_assistant_message'] += 1
                    continue
                if q['role'] == 'user' and text_content(q.get('content')).lstrip().startswith('<environment_context>'):
                    excluded['platform_environment_context'] += 1
                    continue
                for key in ['type', 'id', 'role', 'phase', 'channel']:
                    keep(key)
                keep_text_blocks()
                category = 'user_message' if q['role'] == 'user' else 'assistant_' + q['phase']
            elif qt in ['function_call', 'custom_tool_call', 'function_call_output', 'custom_tool_call_output']:
                for key in ['type', 'id', 'status', 'call_id', 'name', 'namespace', 'arguments', 'input']:
                    keep(key)
                if q.get('call_id') in mixed_calls and qt.endswith('_output'):
                    gap('Combined read_thread output excluded in full to prevent mixed prior-history retention; independently recorded command outputs remain eligible.')
                    excluded['read_thread_combined_output'] += 1
                elif q.get('call_id') in blocked_calls and qt.endswith('_output'):
                    gap('Aggregate agent-list output excluded because it can contain unrelated prior-task reports.')
                    excluded['aggregate_agent_list_output'] += 1
                elif isinstance(q.get('output'), list):
                    out = q['output']
                    indices = [i for i, x in enumerate(out) if not (isinstance(x, dict) and 'exec tool declaration:' in x.get('text', '') and x.get('text', '').lstrip().startswith('[{"name":"mcp__')) and unsafe_reason(x) is None]
                    keep('output', indices=indices)
                    missing = [i for i in range(len(out)) if i not in indices]
                    if missing:
                        gap('Tool-discovery documentation or encrypted/potential credential-bearing output elements excluded; other original elements retained exactly.', omitted_output_indices=missing)
                        excluded['excluded_output_elements'] += len(missing)
                else:
                    keep('output')
                category = 'initiating_delegation' if label == 'root_current_task' and no == first_line else qt
            elif qt == 'agent_message':
                if q.get('author') not in ALLOWED_AUTHORS or q.get('recipient') not in ALLOWED_AUTHORS:
                    gap('Agent-message body outside the current intake/method-review scope excluded, including export-worker traffic.')
                    excluded['out_of_scope_agent_message'] += 1
                    continue
                for key in ['type', 'id', 'author', 'recipient']:
                    keep(key)
                keep_text_blocks()
                category = 'agent_message_readable_envelope'
            else:
                excluded['response_item:' + str(qt)] += 1
                continue
        elif kind == 'event_msg' and qt == 'item_completed':
            item = q.get('item', {}); itype = item.get('type')
            fieldsets = {
                'CommandExecution': ['type', 'id', 'process_id', 'command', 'cwd', 'source', 'status', 'aggregated_output', 'exit_code', 'duration'],
                'ImageView': ['type', 'id', 'path'],
                'FileChange': ['type', 'id', 'changes', 'status', 'stdout', 'stderr'],
                'McpToolCall': ['type', 'id', 'server', 'tool', 'arguments', 'pluginId', 'status', 'result', 'duration'],
            }
            if itype in fieldsets:
                for key in fieldsets[itype]:
                    if itype == 'McpToolCall' and key == 'result' and item.get('tool', '').endswith('read_thread'):
                        gap('Full read_thread result excluded to prevent mixed earlier conversation export.')
                        excluded['read_thread_native_result'] += 1
                        continue
                    keep(key, ['payload', 'item', key])
                for key in ['thread_id', 'turn_id', 'started_at_ms', 'completed_at_ms']:
                    keep(key)
                category = {'CommandExecution': 'command_execution', 'ImageView': 'image_view_record', 'FileChange': 'file_change_record', 'McpToolCall': 'native_mcp_tool_record'}[itype]
            elif itype == 'SubAgentActivity' and item.get('agent_path') in AGENTS:
                values = {k: item[k] for k in ['type', 'id', 'kind', 'agent_thread_id', 'agent_path', 'model', 'reasoning_effort'] if k in item}
                metadata.append({**source_ref, 'source_fields': values, 'source_paths': {k: ['payload', 'item', k] for k in values}, 'source_field_sha256': {k: field_sha(v) for k, v in values.items()}})
                continue
            else:
                excluded['event_item:' + str(itype)] += 1
                continue
        else:
            excluded[str(kind)] += 1
            continue
        turn = id_turn.get(q.get('id')) or id_turn.get(q.get('call_id')) or line_turn.get(no)
        provenance = {'source_thread_id': sid, 'source_thread_id_reference': {**ref(lines, 1), 'source_path': ['payload', 'id']}}
        if turn:
            value, at = turn
            provenance.update({'source_turn_id': value, 'source_turn_id_reference': {**ref(lines, at), 'source_path': ['payload', 'turn_id']}, 'turn_association': 'matching native item/call ID when available; otherwise enclosing native turn metadata'})
        else:
            provenance.update({'source_turn_id': None, 'turn_association': 'No native turn ID available in captured source metadata.'})
        events.append({**source_ref, **provenance, 'category': category, 'payload': payload,
                       'retained_field_source_locations': maps,
                       'retained_field_sha256': {k: field_sha(v) for k, v in payload.items()}})
        counts[category] += 1

    save(folder / 'visible_events.jsonl', ''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in events), True)
    saved = [json.loads(s) for s in (folder / 'visible_events.jsonl').read_text().splitlines()]
    verified = 0; identities = 0; metadata_verified = 0
    for e in saved:
        native = json.loads(lines[e['source_line'] - 1])
        assert sha(lines[e['source_line'] - 1]) == e['source_record_sha256']
        for key, loc in e['retained_field_source_locations'].items():
            expected = get_path(native, loc['source_path'])
            if 'selected_indices' in loc:
                expected = [expected[i] for i in loc['selected_indices']]
            assert e['payload'][key] == expected
            assert e['retained_field_sha256'][key] == field_sha(expected)
            assert unsafe_reason(expected) is None
            verified += 1
        for value_key, ref_key in [('source_thread_id', 'source_thread_id_reference'), ('source_turn_id', 'source_turn_id_reference')]:
            if ref_key not in e:
                continue
            r = e[ref_key]; line = lines[r['source_line'] - 1]
            assert sha(line) == r['source_record_sha256']
            assert get_path(json.loads(line), r['source_path']) == e[value_key]
            identities += 1
    for e in metadata:
        line = lines[e['source_line'] - 1]
        assert sha(line) == e['source_record_sha256']
        for key, value in e['source_fields'].items():
            assert get_path(json.loads(line), e['source_paths'][key]) == value
            assert field_sha(value) == e['source_field_sha256'][key]
            metadata_verified += 1
    readable = ['# Authentic current visible records: ' + label, '', 'Native text fields are retained verbatim below. Full retained tool/command records and provenance are in visible_events.jsonl. Encrypted content is omitted, never reconstructed.', '']
    for e in saved:
        category = e['category']
        if category == 'initiating_delegation' or category == 'user_message' or category.startswith('assistant_') or category == 'agent_message_readable_envelope':
            readable += ['## ' + category + ' — ' + e['timestamp'], '', 'Native source line ' + str(e['source_line']) + '.', '', e['payload'].get('output', '') if category == 'initiating_delegation' else text_content(e['payload'].get('content')), '']
    integrity = {'pass': True, 'records_verified': len(saved), 'retained_fields_verified': verified,
                 'identity_values_verified': identities, 'metadata_fields_verified': metadata_verified,
                 'source_line_hashes_verified': True,
                 'method': 'Saved JSONL re-read; each retained value compared with its exact native field or selected original list elements; source identity references and original source-line SHA-256 including newline verified.',
                 'retained_field_hash_algorithm': 'SHA-256 of UTF-8 JSON, ensure_ascii=False, sort_keys=True, separators=(comma, colon)'}
    save(folder / 'VISIBLE_MESSAGES.md', '\n'.join(readable), True)
    save(folder / 'source_line_index.json', [{k: e[k] for k in ['source_line', 'source_record_sha256', 'timestamp', 'source_thread_id', 'source_turn_id', 'category']} for e in saved])
    save(folder / 'omissions_and_gaps.json', gaps)
    save(folder / 'selected_native_metadata.json', {'note': 'Only selected IDs, current delegation mapping and model configuration labels. Configured model labels do not authenticate serving weights or actual inference parameters.', 'records': metadata})
    save(folder / 'field_integrity_verification.json', integrity)
    manifest = {**meta, 'label': label, 'native_thread_id': sid, 'first_in_scope_line': first_line,
                'minimum_timestamp': minimum_timestamp, 'last_in_scope_source_line': end,
                'bounded_source_cutoff_timestamp': json.loads(lines[end - 1]).get('timestamp'),
                'last_exported_timestamp': saved[-1]['timestamp'] if saved else None,
                'exported_records': len(saved), 'exported_counts': dict(counts), 'excluded_counts': dict(excluded),
                'significant_omissions_and_gaps': len(gaps), 'integrity': integrity}
    save(folder / 'export_manifest.json', manifest)
    return manifest

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', action='store_true')
    group.add_argument('--snapshot-after-results-ready', action='store_true')
    args = parser.parse_args()
    started = now()
    root_lines, root_meta, first, stamp, activities, children, source = scope_lookup()
    source_lines, source_meta, source_no, source_stamp = source
    if args.prepare:
        print(json.dumps({'status': 'scope_verified_no_snapshot_created', 'exact_root_marker_line': first,
                          'root_marker_timestamp': stamp, 'source_user_line': source_no,
                          'children': [{'agent_path': a, 'native_thread_id': sid, 'source_file': m['source_file']} for a, sid, _, m in children]}, indent=2))
        return
    dest = BASE / ('snapshot_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    dest.mkdir()
    results = [export_one('root_current_task', root_lines, root_meta, first, stamp, dest)]
    for agent, sid, lines, meta in children:
        results.append(export_one(agent.rsplit('/', 1)[1], lines, meta, 1, stamp, dest))
    results.append(export_one('source_user_request_only', source_lines, source_meta, source_no, source_stamp, dest, source_no))
    gaps = [
        'Bounded non-atomic snapshots: each source has its own read time and complete-line cutoff; subsequent activity is excluded.',
        'Earlier root/source conversation bodies, hidden reasoning, system/developer instructions, platform context, internal metadata, tool discovery documentation, compaction and replacement history are excluded.',
        'Full read_thread result and combined output are excluded to prevent mixed earlier-history export.',
        'Encrypted bodies and any detected credential-bearing fields are excluded; nothing is decrypted or reconstructed.',
        'Only the mapped current intake and method-review child sessions are exported. Export-worker session, recursive recovery work and unrelated child sessions are excluded.',
        'The single original human request is one native response message; no surrounding source-chat history is included.',
        'Current tool observations may inspect existing detector artifacts; this does not export prior chat history.',
        'Image-view records retain paths only; binary images are not copied.',
        'Root final reply, later review, final report completion or checksum sealing are included only if already visible before their source cutoff; nothing is claimed complete beyond captured evidence.',
        'Hashes establish consistency with captured native sources, not independent authenticity or completeness; no immutable flags are set.',
    ]
    manifest = {'export_started_utc': started, 'export_finished_utc': now(), 'root_chat_id': ROOT_ID,
                'results_ready_gate': 'Invoked only after parent RESULTS_READY instruction.',
                'exact_delegation_input_prefix': MARKER, 'required_delegation_phrase': MARKER_PHRASE,
                'unique_exact_native_marker': True, 'root_marker_source_line': first, 'root_marker_timestamp': stamp,
                'fallback_boundary_used': False, 'source_user_thread_id': SOURCE_ID, 'source_user_message_source_line': source_no,
                'scope': 'Current root fixed-detector evaluation beginning at exact native delegation; current intake/method-review children mapped by in-scope native metadata; exactly one original coordinator human request.',
                'current_scope_delegation_mapping': activities, 'sessions': results, 'missing_sessions': [], 'gaps': gaps,
                'immutable_flags_used': False}
    save(dest / 'SNAPSHOT_MANIFEST.json', manifest)
    files = {str(p.relative_to(dest)): {'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in sorted(dest.rglob('*')) if p.is_file()}
    save(dest / 'HASH_MANIFEST.json', {'algorithm': 'SHA-256', 'files': files, 'note': 'Excludes itself; its hash is recorded in EXPORT_INDEX.json.'})
    index = {'format_version': 3, 'updated_utc': now(), 'current_snapshot': dest.name,
             'snapshot_manifest': str((dest / 'SNAPSHOT_MANIFEST.json').relative_to(BASE)), 'snapshot_manifest_sha256': sha((dest / 'SNAPSHOT_MANIFEST.json').read_bytes()),
             'hash_manifest': str((dest / 'HASH_MANIFEST.json').relative_to(BASE)), 'hash_manifest_sha256': sha((dest / 'HASH_MANIFEST.json').read_bytes()),
             'export_implementation_sha256': sha(Path(__file__).read_bytes()),
             'all_exported_field_and_raw_line_checks_passed': all(r['integrity']['pass'] for r in results),
             'exported_records': sum(r['exported_records'] for r in results), 'session_count': len(results)}
    readme = f'''# Current existing-design detector transcript export

The stable entry point is `EXPORT_INDEX.json`. Current snapshot: `{dest.name}`.

Root scope begins at native line {first} ({stamp}), the unique original delegation from coordinator chat `{SOURCE_ID}` whose input begins `{MARKER}` and contains `{MARKER_PHRASE}`. No broad earlier root history or fallback boundary is included. Exactly one original human request, coordinator native line {source_no}, is included.

Current `/root/existing_design_intake` and `/root/existing_detector_method_review` sessions are located from native SubAgentActivity records within the current root scope and checked against each child's native session IDs, parent ID and agent path. The exporter worker and unrelated sessions are excluded.

Each session has readable visible messages; exact retained tool/command fields; field locations and hashes; original native line hashes; source thread/turn IDs with native references; omission notes; and saved-file integrity verification. Selected metadata retains only identifiers and model configuration labels. Those labels do not authenticate serving weights or actual inference parameters.

Each source was captured once after RESULTS_READY. These are bounded, non-atomic snapshots with explicit byte/line/time cutoffs. Events after each cutoff, including the root's later final reply and final packaging if not yet captured, are outside the export. Encrypted bodies are excluded without decryption or reconstruction. Hidden reasoning, instructions, platform context, mixed history from read_thread, compaction and internal metadata are excluded. No earlier source conversation is exported. See SNAPSHOT_MANIFEST.json and per-session omissions_and_gaps.json for exact limits.

All retained fields and provenance references were compared to the original native sources after re-reading the saved JSONL. SHA-256 manifests support consistency checks; no immutable flags were used. Hashes do not independently prove authenticity or completeness.
'''
    for name, content in [('EXPORT_INDEX.json', json.dumps(index, ensure_ascii=False, indent=2) + '\n'), ('README.md', readme)]:
        temp = BASE / ('.' + name + '.tmp')
        temp.write_text(content, encoding='utf-8')
        os.replace(temp, BASE / name)
    # Re-read completed manifests and every listed artifact; this is export integrity, not a detector run.
    checked = json.loads((dest / 'HASH_MANIFEST.json').read_text())
    for name, expected in checked['files'].items():
        raw = (dest / name).read_bytes()
        assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256']
    assert index['hash_manifest_sha256'] == sha((dest / 'HASH_MANIFEST.json').read_bytes())
    print(json.dumps({'snapshot': str(dest), 'index': str(BASE / 'EXPORT_INDEX.json'), 'session_count': len(results), 'exported_records': index['exported_records'],
                      'sessions': [{'label': r['label'], 'records': r['exported_records'], 'fields_verified': r['integrity']['retained_fields_verified'], 'last_exported_timestamp': r['last_exported_timestamp']} for r in results],
                      'integrity_passed': True, 'missing_sessions': []}, indent=2))

if __name__ == '__main__':
    main()
