#!/usr/bin/env python3
"""Export only the authorized native task snapshot; never rewrite its source."""
from pathlib import Path
from datetime import datetime, timezone
import collections
import hashlib
import json
import re

SOURCE = Path('/Users/al-zayedal-hassan/.codex/sessions/2026/11/12/rollout-2026-11-12T19-12-19-01a1b0ad-f593-7f90-a689-b621984f7cb4_01a1d23f-7ed7-7fa1-9afd-64875b8a6cf8.jsonl')
DEST = Path(__file__).resolve().parent
CUTOFF_BYTES = 2371665
TURN_IDS = {'01a1d242-c430-7f82-b027-686debd939f6', '01a1d254-6a62-7ac2-8865-04c80eae105c'}
REQUEST = 'Have Qwen finish the missing modified RTL and testbench, then package the report and AI logs for submission. Keep my repo unchanged, don’t use solutions, and don’t program the board or recover the key.'
INSTRUCTION_OUTPUT = re.compile(r'AGENTS\.md|SKILL\.md|config/system_prompt\.txt|original_qualifier_README\.md')
OLD_DOCUMENT_OUTPUT = re.compile(r'TECHNICAL_HANDOFF\.md|AI_RECORDS_INDEX\.md')
THREAD_METADATA = re.compile(r'list_threads|read_thread|list_agents|ALL_TOOLS|submission_controller_(?:previous|parsed|snapshot)|current_threads_for_records')
SESSION_INVENTORY = re.compile(r'rg --files --hidden /Users/al-zayedal-hassan/\.codex/sessions')
ENCRYPTED = re.compile(r'gAAAA[A-Za-z0-9_=-]{70,}')
FORBIDDEN_KEYS = {'encrypted_content', 'internal_chat_message_metadata_passthrough', 'logprobs', 'annotations'}

def digest(b):
    return hashlib.sha256(b).hexdigest()

def jwrite(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def output_reason(command):
    if INSTRUCTION_OUTPUT.search(command):
        return 'Instruction-file output omitted; original command retained where available.'
    if OLD_DOCUMENT_OUTPUT.search(command):
        return 'Earlier provenance/handoff document output omitted; current command retained.'
    if THREAD_METADATA.search(command):
        return 'Thread/tool-catalog metadata or nested thread snapshot omitted, including any nested reasoning/context.'
    if SESSION_INVENTORY.search(command):
        return 'Session-file inventory metadata omitted; original search command retained.'
    return None

def sanitize(value, pointer, omitted):
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            p = pointer + '/' + key
            if key in FORBIDDEN_KEYS or 'encrypted' in key.lower():
                omitted.append({'field': p, 'reason': 'Encrypted payload or internal generation metadata omitted.'})
            else:
                out[key] = sanitize(child, p, omitted)
        return out
    if isinstance(value, list):
        out = []
        for index, child in enumerate(value):
            p = pointer + '/' + str(index)
            if isinstance(child, dict) and child.get('type') in ('encrypted_content', 'reasoning', 'reasoning_text'):
                omitted.append({'field': p, 'reason': 'Encrypted content or hidden reasoning block omitted.'})
            else:
                out.append(sanitize(child, p, omitted))
        return out
    if isinstance(value, str) and ENCRYPTED.search(value):
        raise ValueError('Encrypted string requires explicit field omission at ' + pointer)
    return value

with SOURCE.open('rb') as f:
    snapshot = f.read(CUTOFF_BYTES)
assert len(snapshot) == CUTOFF_BYTES and snapshot.endswith(b'\n'), 'Snapshot is unavailable or incomplete.'
raw_lines = snapshot.splitlines(keepends=True)
assert len(raw_lines) == 573

# First pass: identifiers only. Do not retrieve or export earlier payload contents.
active = None
eligible = []
turn_markers = []
for number, raw in enumerate(raw_lines, 1):
    r = json.loads(raw)
    q = r.get('payload') or {}
    if r.get('type') == 'turn_context' or (r.get('type') == 'event_msg' and q.get('type') == 'task_started'):
        active = q.get('turn_id', active)
        if active in TURN_IDS:
            turn_markers.append({'line': number, 'turn_id': active, 'record_type': r['type']})
    if active in TURN_IDS:
        eligible.append((number, active))
assert eligible[0][0] == 32 and eligible[-1][0] == 573
assert {turn for _, turn in eligible} == TURN_IDS
boundary = json.loads(raw_lines[33])
boundary_text = ''.join(c.get('text', '') for c in boundary['payload']['content'])
assert boundary['payload']['role'] == 'user' and boundary_text.rstrip('\n') == REQUEST

calls = {}
for number, _ in eligible:
    r = json.loads(raw_lines[number - 1]); q = r.get('payload') or {}
    if r.get('type') == 'response_item' and q.get('type') in ('function_call', 'custom_tool_call'):
        calls[q.get('call_id')] = {'line': number, 'name': q.get('name'), 'input': q.get('input', q.get('arguments', ''))}

records, omissions = [], []
def provenance(number, turn, r):
    return {'native_source': str(SOURCE), 'native_line': number, 'native_line_sha256': digest(raw_lines[number - 1]),
            'turn_id': turn, 'timestamp': r.get('timestamp'), 'ordinal': r.get('ordinal')}

for number, turn in eligible:
    r = json.loads(raw_lines[number - 1]); q = r.get('payload') or {}
    origin = provenance(number, turn, r)
    typ, subtype = r.get('type'), q.get('type')
    omitted, payload, reason = [], None, None
    if typ == 'response_item':
        if subtype == 'message':
            if q.get('role') not in ('user', 'assistant'):
                reason = 'System/developer or other non-visible message omitted.'
            elif q.get('phase') in ('analysis', 'reasoning'):
                reason = 'Hidden reasoning message omitted.'
            else:
                payload = {k: q[k] for k in ('type', 'id', 'role', 'phase', 'status', 'content') if k in q}
        elif subtype == 'agent_message':
            payload = {k: q[k] for k in ('type', 'id', 'author', 'recipient', 'content') if k in q}
        elif subtype in ('custom_tool_call', 'function_call'):
            if q.get('name') in ('list_agents', 'list_threads', 'list_archived_threads'):
                reason = 'Unrelated agent/sidebar/thread-list metadata call omitted.'
            else:
                payload = {k: q[k] for k in ('type', 'id', 'call_id', 'name', 'namespace', 'status', 'input', 'arguments') if k in q}
                for field in ('input', 'arguments'):
                    if isinstance(payload.get(field), str) and ENCRYPTED.search(payload[field]):
                        del payload[field]
                        omitted.append({'field': '/payload/' + field, 'reason': 'Original field contains encrypted delegation payload; no plaintext was reconstructed.'})
        elif subtype in ('custom_tool_call_output', 'function_call_output'):
            call = calls.get(q.get('call_id'))
            if call is None:
                reason = 'Tool output has no matched call within the authorized task snapshot.'
            else:
                reason = output_reason(call['input'])
                if call['name'] in ('list_agents', 'list_threads', 'list_archived_threads'):
                    reason = 'Unrelated agent/sidebar/thread-list metadata result omitted.'
                if reason is None:
                    payload = {k: q[k] for k in ('type', 'id', 'call_id', 'output') if k in q}
        else:
            reason = 'Hidden reasoning or unsupported non-visible response record omitted.'
    elif typ == 'event_msg' and subtype == 'item_completed':
        item = q.get('item') or {}
        if item.get('type') == 'CommandExecution':
            data = {k: item[k] for k in ('type', 'id', 'command', 'cwd', 'duration', 'exit_code', 'process_id', 'status', 'aggregated_output') if k in item}
            why = output_reason('\n'.join(item.get('command') or []))
            if why and 'aggregated_output' in data:
                del data['aggregated_output']
                omitted.append({'field': '/payload/item/aggregated_output', 'reason': why})
            payload = {'type': subtype, 'turn_id': q.get('turn_id'), 'item': data}
        elif item.get('type') == 'FileChange':
            payload = {'type': subtype, 'turn_id': q.get('turn_id'), 'item': {k: item[k] for k in ('type', 'id', 'changes', 'status', 'stdout', 'stderr') if k in item}}
        else:
            reason = 'Duplicate visible-message event, hidden reasoning, context compaction, or metadata event omitted.'
    else:
        reason = 'System/context/compaction/settings/usage/world-state or lifecycle metadata omitted.'
    if payload is not None:
        for key in q:
            if key not in payload and key not in ('item', 'type'):
                omitted.append({'field': '/payload/' + key, 'reason': 'Non-exported native metadata field; retained content fields are unchanged.'})
        payload = sanitize(payload, '/payload', omitted)
        entry = {'source': origin, 'record': {'type': typ, 'payload': payload}}
        if omitted:
            entry['omitted_fields'] = omitted
        records.append(entry)
    else:
        omissions.append({'source': origin, 'record_type': typ, 'payload_type': subtype, 'reason': reason})

assert len(records) + len(omissions) == len(eligible)
encoded = '\n'.join(json.dumps(r, ensure_ascii=False) for r in records) + '\n'
assert not ENCRYPTED.search(encoded), 'Encrypted payload leaked into export.'
assert all(r['source']['native_line'] >= 34 for r in records)
assert all(r['source']['turn_id'] in TURN_IDS for r in records)
assert all(r['record']['payload'].get('type') != 'reasoning' for r in records)
assert all(r['record']['payload'].get('role') not in ('system', 'developer') for r in records)
with SOURCE.open('rb') as f:
    assert digest(f.read(CUTOFF_BYTES)) == digest(snapshot), 'Source prefix changed while exporting.'

DEST.mkdir(parents=True, exist_ok=True)
(DEST / 'visible_task_records.jsonl').write_text(encoded)
(DEST / 'omitted_records.jsonl').write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in omissions) + '\n')
lines = ['# Bounded native record export', '',
         'This is a filtered snapshot of the current generation task, not a full chat history or a completion record.',
         'Original visible text, tool inputs, commands, diffs, and retained results are preserved as recorded. JSON formatting is normalized.',
         'The JSONL file is authoritative. Every retained entry links to its original native line and SHA-256 hash, including the original newline.',
         'Selected native execution events supplement tool calls/results and may duplicate evidence of the same action.',
         'Encrypted delegation payloads, hidden reasoning, context/compaction records, instruction-file outputs, and thread/sidebar metadata are omitted.',
         'Snapshot ends at native line 573; later work and the final user-facing completion reply are outside this export.', '']
for entry in records:
    s, q = entry['source'], entry['record']['payload']
    kind = q.get('role') or q.get('type')
    if q.get('type') == 'agent_message':
        kind = 'agent message: ' + q.get('author', '')
    lines.extend(['## Native line ' + str(s['native_line']) + ' — ' + kind, '',
                  'Timestamp: ' + str(s['timestamp']) + '  ', 'Turn: `' + s['turn_id'] + '`  ',
                  'Native line SHA-256: `' + s['native_line_sha256'] + '`', ''])
    if q.get('type') in ('message', 'agent_message'):
        for block in q.get('content', []):
            if 'text' in block:
                text = block['text']; fence = '`' * max(4, max((len(x) for x in re.findall(r'`+', text)), default=0) + 1)
                lines.extend([fence + 'text', text, fence, ''])
    else:
        rendered = json.dumps(q, ensure_ascii=False, indent=2)
        fence = '`' * max(4, max((len(x) for x in re.findall(r'`+', rendered)), default=0) + 1)
        lines.extend([fence + 'json', rendered, fence, ''])
    if entry.get('omitted_fields'):
        lines.extend(['Omitted native fields: ' + '; '.join(x['field'] for x in entry['omitted_fields']) + '.', ''])
(DEST / 'VISIBLE_TASK_TRANSCRIPT.md').write_text('\n'.join(lines))
kind_counts = collections.Counter(r['record']['type'] + ':' + r['record']['payload']['type'] for r in records)
manifest = {
    'export_created_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Authorized current-generation task only, filtered native snapshot; not full history.',
    'source': str(SOURCE), 'source_open_mode': 'read-only binary',
    'snapshot': {'prefix_bytes': CUTOFF_BYTES, 'complete_lines': len(raw_lines), 'prefix_sha256': digest(snapshot),
                 'last_timestamp': json.loads(raw_lines[-1])['timestamp'], 'last_record': 'assistant commentary',
                 'includes_later_final_reply': False},
    'selected_turn_ids': sorted(TURN_IDS), 'turn_markers': turn_markers,
    'boundary': {'native_line': 34, 'user_request_matches_after_removing_trailing_newline': True,
                 'original_request_in_export_is_unaltered': True},
    'earlier_history': {'native_lines_excluded': [1, 31], 'contents_exported': False,
                        'processing': 'Only record type and turn identifiers were examined for boundary selection.'},
    'counts': {'eligible_native_records': len(eligible), 'retained_records': len(records),
               'omitted_records': len(omissions), 'retained_by_kind': dict(kind_counts)},
    'omission_policy': ['Hidden reasoning records and blocks', 'Encrypted payload fields, including encrypted text stored inside delegation arguments',
                        'System/developer/context/compaction/inherited context records', 'Skill and instruction-file outputs',
                        'Nested read_thread snapshots and thread/sidebar/list-agent metadata', 'Earlier provenance/handoff document outputs',
                        'Redundant visible-message events and internal metadata'],
    'authenticity': {'line_hash_definition': 'SHA-256 of the complete original native JSONL line bytes, including its trailing newline',
                     'retained_strings_changed': False, 'omitted_content_reconstructed': False,
                     'original_source_prefix_unchanged_at_completion': True,
                     'json_serialization_normalized': True,
                     'native_and_nested_tool_evidence_may_overlap': True},
    'limitations': ['This cutoff predates the final completion reply and any subsequent packaging work.',
                    'Encrypted delegation messages cannot be exported as plaintext from this native file; their fields are omitted.',
                    'Any truncation already present in native tool outputs remains unchanged.',
                    'No earlier session history or compacted inherited history is included.'],
    'files': {}
}
for name in ('visible_task_records.jsonl', 'omitted_records.jsonl', 'VISIBLE_TASK_TRANSCRIPT.md', 'export_bounded_native.py'):
    b = (DEST / name).read_bytes(); manifest['files'][name] = {'bytes': len(b), 'sha256': digest(b)}
jwrite(DEST / 'EXPORT_MANIFEST.json', manifest)
print(json.dumps({'destination': str(DEST), 'retained_records': len(records), 'omitted_records': len(omissions),
                  'cutoff_native_line': 573, 'prefix_sha256': digest(snapshot)}, indent=2))
