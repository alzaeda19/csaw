#!/usr/bin/env python3
"""Read frozen reviewer records; write only this recovery directory. No replay."""
import collections
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

DEST = Path(__file__).resolve().parent
EXPECTED_DEST = Path('/Users/al-zayedal-hassan/Documents/ChatGPT/trojan/CSAW_records_explanation_20261113T011536Z_jj4i8v2x/records/reviewer_recovery')
assert DEST == EXPECTED_DEST
SESSION_DIR = Path('/Users/al-zayedal-hassan/.codex/sessions/2026/11/12')
APP_DIR = Path('/Users/al-zayedal-hassan/Documents/CSAW_Qwen_Submission_20261113T001822Z_9sj2k3k6/ai_logs')
SPECS = [
    {'reviewer': 'protocol_review', 'file': 'rollout-2026-11-12T19-18-29-01a1d245-26de-7730-8903-654a1eb4004d.jsonl',
     'bytes': 802897, 'lines': 190, 'sha256': 'ebda1cd30dedcbc83a67156f7ce2f1cab32de124c3f2ab8fd20b32ef504b4b8f',
     'agent_path': '/root/submission_protocol_review', 'tail_start': 105,
     'tail_label': 'original_generation_ai_record_packaging',
     'omit_output_lines': {114: 'Nested source-record identifier inventory; excluded as internal metadata.',
       121: 'Nested source-record schema and tool inventory; excluded as internal metadata.',
       128: 'Nested parent transcript and encrypted delegation fragments; entire output omitted.',
       142: 'Nested parent command and tool-event inventory; excluded as internal metadata.',
       149: 'Nested parent source/instruction-loading calls; entire output omitted.'}},
    {'reviewer': 'report_review', 'file': 'rollout-2026-11-12T19-18-34-01a1d245-3808-71b3-a696-a4f14fca0a76.jsonl',
     'bytes': 563576, 'lines': 115, 'sha256': 'd9ed9d6cbf10b34951194a8460f7e3fdc380ac26fff17af884c19b44dcd5856a',
     'agent_path': '/root/submission_report_review', 'tail_start': 93,
     'tail_label': 'original_generation_final_package_consistency_review',
     'omit_output_lines': {17: 'Original challenge instructions and inherited provenance documents; whole combined output omitted.',
       38: 'Historical baseline-recovery documents and derivation source; whole combined output omitted.'}},
]
ROOT_TURNS = {'01a1d242-c430-7f82-b027-686debd939f6', '01a1d254-6a62-7ac2-8865-04c80eae105c'}
ENCRYPTED = re.compile(r'gAAAA[A-Za-z0-9_=-]{70,}')
TRUNCATED = re.compile(r'Warning: truncated output \(original token count: \d+\)|[.…]{1,3}\d+ tokens truncated[.…]{1,3}')

def sha(b):
    return hashlib.sha256(b).hexdigest()

def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def write_json(name, value):
    (DEST / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def write_jsonl(name, values):
    (DEST / name).write_text(''.join(json.dumps(v, ensure_ascii=False) + '\n' for v in values), encoding='utf-8')

def esc(value):
    return str(value).replace('~', '~0').replace('/', '~1')

def leaves(value, path=''):
    if isinstance(value, dict) and value:
        for key, child in value.items():
            yield from leaves(child, path + '/' + esc(key))
    elif isinstance(value, list) and value:
        for index, child in enumerate(value):
            yield from leaves(child, path + '/' + str(index))
    else:
        yield path, value

def pointer(value, path):
    for token in path.split('/')[1:]:
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value

def app_string_fields(app):
    return [(p, v) for p, v in leaves(app) if isinstance(v, str)]

records, omissions, verification, gaps, comparisons, truncations, snapshots = [], [], [], [], [], [], []
source_cache = {}
app_refs = []
for spec in SPECS:
    source = SESSION_DIR / spec['file']
    with source.open('rb') as handle:
        frozen = handle.read(spec['bytes'])
    assert len(frozen) == spec['bytes'] and sha(frozen) == spec['sha256'] and frozen.endswith(b'\n')
    raw_lines = frozen.splitlines(keepends=True)
    assert len(raw_lines) == spec['lines']
    source_cache[spec['reviewer']] = (source, frozen, raw_lines)
    parsed = [json.loads(line) for line in raw_lines]
    session = parsed[0]['payload']
    assert session['source']['subagent']['thread_spawn']['agent_path'] == spec['agent_path']
    assert session['id'] in spec['file']
    app_path = APP_DIR / 'reviewer_exports' / (spec['reviewer'] + '.json')
    app_bytes = app_path.read_bytes()
    app = json.loads(app_bytes)
    assert app['source_thread_id'] == session['id']
    app_fields = app_string_fields(app)
    app_turns = {turn['id'] for turn in app['turns']}
    app_refs.append({'reviewer': spec['reviewer'], 'path': str(app_path), 'bytes': len(app_bytes),
                     'sha256': sha(app_bytes), 'turn_ids': sorted(app_turns)})
    active_turn = None
    turn_markers = []
    native_count_before = len(records)
    omitted_count_before = len(omissions)
    for number, (native, raw) in enumerate(zip(parsed, raw_lines), 1):
        q = native.get('payload') or {}
        typ, subtype = native.get('type'), q.get('type')
        if typ == 'event_msg' and subtype == 'task_started':
            assert q['root_turn_id'] in ROOT_TURNS
            active_turn = q['turn_id']
            turn_markers.append({'native_line': number, 'turn_id': active_turn,
                                 'root_turn_id': q['root_turn_id'], 'timestamp': native['timestamp'],
                                 'section': 'review_and_report_generation' if number < spec['tail_start'] else spec['tail_label']})
        origin = {'reviewer': spec['reviewer'], 'native_source': str(source), 'native_line': number,
                  'native_line_sha256': sha(raw), 'native_raw_line_bytes': len(raw),
                  'timestamp': native.get('timestamp'), 'turn_id': active_turn,
                  'section': 'review_and_report_generation' if number < spec['tail_start'] else spec['tail_label']}
        payload = None
        reason = None
        dropped = []
        mapping = []

        def keep(key):
            if key in q:
                payload[key] = q[key]
                for suffix, value in leaves(q[key]):
                    mapping.append(('/record/payload/' + esc(key) + suffix, '/payload/' + esc(key) + suffix))

        if number < 13:
            reason = 'Bootstrap environment, platform/developer instructions, or initial lifecycle/context metadata; no inherited content exported.'
        elif typ == 'response_item' and subtype in ('message', 'agent_message'):
            if subtype == 'message' and (q.get('role') != 'assistant' or q.get('phase') not in ('final_answer', 'commentary')):
                reason = 'Non-visible, instruction, or reasoning message omitted.'
            else:
                payload = {}
                for key in ('type', 'id', 'role', 'phase', 'status', 'author', 'recipient'):
                    keep(key)
                payload['content'] = []
                for index, block in enumerate(q.get('content', [])):
                    if block.get('type') not in ('input_text', 'output_text'):
                        dropped.append({'native_pointer': f'/payload/content/{index}', 'reason': 'Encrypted/unsupported block omitted in full; plaintext unavailable.'})
                        continue
                    retained_index = len(payload['content'])
                    text_block = {k: block[k] for k in ('type', 'text') if k in block}
                    assert not ENCRYPTED.search(dump(text_block))
                    payload['content'].append(text_block)
                    for key in text_block:
                        mapping.append((f'/record/payload/content/{retained_index}/{key}', f'/payload/content/{index}/{key}'))
                    for key in block:
                        if key not in text_block:
                            dropped.append({'native_pointer': f'/payload/content/{index}/{esc(key)}', 'reason': 'Annotations/logprobs/internal content metadata omitted.'})
                if subtype == 'agent_message':
                    assert q['author'] == '/root' and q['recipient'] == spec['agent_path']
                    plain = ''.join(block.get('text', '') for block in payload['content'])
                    has_payload = bool(plain.split('Payload:\n', 1)[-1]) if 'Payload:\n' in plain else bool(plain)
                    encrypted_blocks = sum(block.get('type') == 'encrypted_content' for block in q.get('content', []))
                    gaps.append({'source': origin, 'message_id': q.get('id'),
                                 'kind': 'NEW_TASK' if plain.startswith('Message Type: NEW_TASK\n') else 'MESSAGE',
                                 'visible_wrapper_retained': True, 'prompt_body_recovered': has_payload,
                                 'encrypted_payload_blocks': encrypted_blocks,
                                 'unavailable_native_pointers': [f'/payload/content/{i}' for i, b in enumerate(q['content']) if b.get('type') == 'encrypted_content'],
                                 'reason': 'Only routing wrapper is visible. Delegation/steering body is encrypted; no decryption or reconstruction attempted.'})
                    assert not has_payload and encrypted_blocks == 1
        elif typ == 'response_item' and subtype in ('custom_tool_call', 'function_call'):
            payload = {}
            for key in ('type', 'id', 'call_id', 'name', 'namespace', 'status', 'input', 'arguments'):
                if key in ('input', 'arguments') and isinstance(q.get(key), str) and ENCRYPTED.search(q[key]):
                    dropped.append({'native_pointer': '/payload/' + key, 'reason': 'Whole field contains encrypted delegation message; not exported or reconstructed.'})
                else:
                    keep(key)
        elif typ == 'response_item' and subtype in ('custom_tool_call_output', 'function_call_output'):
            if number in spec['omit_output_lines']:
                reason = spec['omit_output_lines'][number]
            else:
                payload = {}
                for key in ('type', 'id', 'call_id', 'output'):
                    keep(key)
                assert not ENCRYPTED.search(dump(payload))
        else:
            if subtype == 'reasoning':
                reason = 'Hidden reasoning omitted in full.'
            elif typ == 'event_msg' and subtype == 'item_completed':
                reason = 'Execution/message event duplicates the retained tool/message records, or contains hidden/internal event data; omitted.'
            else:
                reason = 'Lifecycle, context, world state, usage, communication-routing, or other internal metadata omitted.'

        if payload is None:
            omissions.append({'source': origin, 'record_type': typ, 'payload_type': subtype, 'reason': reason})
            continue
        retained_keys = set(payload)
        already_dropped = {d['native_pointer'] for d in dropped}
        for key in q:
            p = '/payload/' + esc(key)
            if key not in retained_keys and p not in already_dropped:
                dropped.append({'native_pointer': p, 'reason': 'Encrypted field omitted.' if 'encrypted' in key else 'Internal/non-visible metadata omitted.'})
        for key in native:
            if key not in ('type', 'payload'):
                dropped.append({'native_pointer': '/' + esc(key), 'reason': 'Native envelope metadata kept only as provenance where applicable; raw field omitted.'})
        entry = {'source': origin, 'record': {'type': typ, 'payload': payload}, 'omitted_fields': dropped}
        mapping.append(('/record/type', '/type'))
        for export_pointer, native_pointer in mapping:
            a, b = pointer(entry, export_pointer), pointer(native, native_pointer)
            assert type(a) is type(b) and a == b
            verification.append({'reviewer': spec['reviewer'], 'native_line': number,
                                 'export_pointer': export_pointer, 'native_pointer': native_pointer,
                                 'canonical_json_value_sha256': sha(dump(a).encode()), 'exactly_equal': True})
        assert len(mapping) == len(list(leaves(entry['record'])))
        records.append(entry)
        for p, value in leaves(payload):
            if not isinstance(value, str):
                continue
            hits = [{'start_character': m.start(), 'end_character': m.end(), 'exact_marker': m.group(0)} for m in TRUNCATED.finditer(value)]
            if hits:
                truncations.append({'source': origin, 'export_pointer': '/record/payload' + p,
                                    'retained_string_characters': len(value), 'markers': hits,
                                    'policy': 'Source truncation retained unchanged; no missing bytes inferred or restored.'})
        if subtype == 'message':
            for index, block in enumerate(payload.get('content', [])):
                text = block.get('text', '')
                matches = [p for p, value in app_fields if value == text]
                comparisons.append({'reviewer': spec['reviewer'], 'native_line': number, 'kind': 'assistant_final',
                                    'characters': len(text), 'app_exact_value_pointers': matches,
                                    'novelty': 'already_present_exact_text' if matches else 'new_visible_final_absent_from_saved_app_export'})
        elif subtype == 'custom_tool_call_output':
            output = payload.get('output')
            if isinstance(output, list):
                for index, block in enumerate(output):
                    if index == 0 or not isinstance(block, dict):
                        continue
                    text = block.get('text', '')
                    matches = [p for p, value in app_fields if value == text]
                    comparisons.append({'reviewer': spec['reviewer'], 'native_line': number,
                                        'kind': 'tool_output_text_block', 'native_block_index': index,
                                        'characters': len(text), 'app_exact_value_pointers': matches,
                                        'novelty': 'already_present_exact_text' if matches else 'native_tool_text_not_an_exact_saved_app_string',
                                        'note': 'A missing exact string match is not proof of new substantive information; formatting, wrappers, and diffs can differ.'})
    snapshots.append({'reviewer': spec['reviewer'], 'source': str(source), 'source_thread_id': session['id'],
                      'agent_path': spec['agent_path'], 'prefix_bytes': spec['bytes'], 'complete_lines': spec['lines'],
                      'prefix_sha256': spec['sha256'], 'last_timestamp': parsed[-1]['timestamp'],
                      'last_record_type': parsed[-1]['type'], 'last_payload_type': parsed[-1]['payload']['type'],
                      'bootstrap_lines_excluded': [1, 12], 'inherited_parent_history_exported': False,
                      'turn_markers': turn_markers, 'retained_records': len(records) - native_count_before,
                      'omitted_records': len(omissions) - omitted_count_before,
                      'source_prefix_unchanged_on_verification': False})

assert len(records) + len(omissions) == sum(spec['lines'] for spec in SPECS)
assert len(gaps) == 12 and not any(g['prompt_body_recovered'] for g in gaps)
assert len([v for v in comparisons if v['kind'] == 'assistant_final']) == 9
assert sum(v['kind'] == 'assistant_final' and bool(v['app_exact_value_pointers']) for v in comparisons) == 7
for spec, snapshot in zip(SPECS, snapshots):
    source, frozen, raw_lines = source_cache[spec['reviewer']]
    with source.open('rb') as handle:
        assert handle.read(spec['bytes']) == frozen
    snapshot['source_prefix_unchanged_on_verification'] = True
    relevant = [e for e in records + omissions if e['source']['reviewer'] == spec['reviewer']]
    assert sorted(e['source']['native_line'] for e in relevant) == list(range(1, spec['lines'] + 1))
    for entry in relevant:
        assert entry['source']['native_line_sha256'] == sha(raw_lines[entry['source']['native_line'] - 1])

original_refs = []
for rel in ('codex_current_task/EXPORT_MANIFEST.json', 'codex_current_task/omitted_records.jsonl'):
    path = APP_DIR / rel
    raw = path.read_bytes()
    original_refs.append({'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)})
    if rel.endswith('EXPORT_MANIFEST.json'):
        old_manifest = json.loads(raw)
    else:
        old_omissions = [json.loads(line) for line in raw.splitlines()]

record_comparisons = []
for spec in SPECS:
    reviewer = spec['reviewer']
    app = json.loads((APP_DIR / 'reviewer_exports' / (reviewer + '.json')).read_bytes())
    app_items = {item['id']: {'turn_id': turn['id'], 'type': item['type']} for turn in app['turns'] for item in turn['items']}
    native = [json.loads(line) for line in source_cache[reviewer][2]]
    calls = {d['payload']['call_id']: (n, d['payload']) for n, d in enumerate(native, 1)
             if d['type'] == 'response_item' and d['payload'].get('type') in ('custom_tool_call', 'function_call')}
    output_lines = {d['payload']['call_id']: n for n, d in enumerate(native, 1)
                    if d['type'] == 'response_item' and d['payload'].get('type') in ('custom_tool_call_output', 'function_call_output')}
    for entry in [r for r in records if r['source']['reviewer'] == reviewer]:
        q = entry['record']['payload']
        subtype = q['type']
        matching_ids = []
        if subtype == 'message':
            if q.get('id') in app_items:
                matching_ids.append(q['id'])
        elif subtype in ('function_call', 'function_call_output'):
            if q['call_id'] in app_items:
                matching_ids.append(q['call_id'])
        elif subtype in ('custom_tool_call', 'custom_tool_call_output'):
            start = calls[q['call_id']][0]
            end = output_lines[q['call_id']]
            for item_record in native[start:end - 1]:
                p = item_record.get('payload', {})
                item = p.get('item', {})
                if item_record['type'] == 'event_msg' and p.get('type') == 'item_completed' and item.get('id') in app_items:
                    matching_ids.append(item['id'])
        if matching_ids:
            category = 'overlaps_saved_app_final_exact_text' if subtype == 'message' else 'overlaps_saved_app_operation'
        elif subtype == 'agent_message':
            category = 'new_routing_wrapper_only_no_prompt_body'
        elif subtype == 'message':
            category = 'new_final_response'
        elif subtype == 'function_call':
            category = 'new_encrypted_call_metadata_only'
        elif subtype == 'function_call_output' and q.get('output') == '':
            category = 'new_empty_call_result_metadata_only'
        elif subtype == 'function_call_output':
            category = 'new_visible_dispatch_status'
        else:
            category = 'new_visible_tool_record'
        record_comparisons.append({'reviewer': reviewer, 'native_line': entry['source']['native_line'],
            'record_type': subtype, 'category': category, 'matching_saved_app_item_ids': matching_ids,
            'evidence': 'Stable item/call ID links native operation to saved app item; function wrappers may serialize differently.' if matching_ids and subtype != 'message'
                        else 'Exact final text and message ID agree.' if matching_ids else 'No matching item in saved app export.'})
novelty_counts = dict(collections.Counter(r['category'] for r in record_comparisons))
assert len(record_comparisons) == len(records)
assert sum(r['category'].startswith('overlaps_') for r in record_comparisons) == 39
assert sum(not r['category'].startswith('overlaps_') for r in record_comparisons) == 35

write_jsonl('visible_reviewer_records.jsonl', records)
write_jsonl('omitted_records.jsonl', omissions)
write_jsonl('retained_field_verification.jsonl', verification)
write_json('PROMPT_GAPS.json', {'recovered_prompt_bodies': 0, 'inbound_wrappers_retained': 12,
                              'new_task_bodies_unavailable': 9, 'followup_message_bodies_unavailable': 3,
                              'outbound_encrypted_tool_arguments_unavailable': sum(e['record']['payload']['type'] == 'function_call' and 'arguments' not in e['record']['payload'] for e in records),
                              'messages': gaps})
write_json('APP_EXPORT_COMPARISON.json', {'existing_exports': app_refs, 'comparisons': comparisons,
       'record_level_comparisons': record_comparisons,
       'summary': {'previously_exported_finals_exact_matches': 7, 'new_finals': 2, 'new_plaintext_delegation_bodies': 0,
                   'native_records_overlapping_saved_app_items': 39, 'native_records_without_saved_app_counterpart': 35,
                   'by_category': novelty_counts},
       'qualification': 'Exact-value comparison is definitive for final text. Native exec wrappers/provenance are additional format detail, not reconstructed delegation text.'})
write_json('SOURCE_TRUNCATIONS.json', {'exporter_added_truncation': False, 'retained_source_truncations': truncations,
       'omitted_truncated_source_outputs': [{'reviewer': 'protocol_review', 'native_line': 114,
           'reason': 'Whole nested identifier-inventory output omitted; native truncation is not repaired.'}],
       'unknown_missing_content': 'Counts in truncation markers are tool-reported token counts; missing source bytes cannot be determined from these records.'})

transcript = ['# Reviewer records recovered from frozen native sources', '',
    'This is an authentic filtered record export, not reconstructed dialogue. Source line hashes include the complete original JSONL line and its newline.',
    'The twelve inbound task/steering wrappers contain no visible prompt body. Their encrypted bodies are omitted. Seven finals duplicate the saved app exports; the final consistency review and original export-completion response are new.',
    'Tool calls below are historical text only. This recovery process did not execute them. Whole-record omissions are listed separately; source truncation remains unchanged.', '']
for entry in records:
    src, q = entry['source'], entry['record']['payload']
    transcript.extend([f"## {src['reviewer']} · native line {src['native_line']} · {q['type']}", '',
        f"Section: `{src['section']}`  ", f"Timestamp: {src['timestamp']}  ",
        f"Turn: `{src['turn_id']}`  ", f"Raw line SHA-256: `{src['native_line_sha256']}`", ''])
    if q['type'] in ('message', 'agent_message'):
        text_parts = [b['text'] for b in q.get('content', []) if 'text' in b]
    elif q['type'] in ('custom_tool_call', 'function_call'):
        text_parts = [q.get('input', q.get('arguments', '[Tool arguments unavailable; see exact omission ledger.]'))]
    elif isinstance(q.get('output'), list):
        text_parts = [b.get('text', '') for b in q['output'] if isinstance(b, dict)]
    else:
        text_parts = [q.get('output', '')]
    for content in text_parts:
        fence = '`' * max(4, 1 + max((len(x) for x in re.findall(r'`+', content)), default=0))
        transcript.extend([fence + 'text', content, fence, ''])
    if q['type'] == 'agent_message':
        transcript.extend(['**Prompt body unavailable:** only the original routing wrapper is visible; the encrypted body was omitted.', ''])
    if entry['omitted_fields']:
        transcript.extend(['Omitted field pointers: ' + ', '.join('`' + d['native_pointer'] + '`' for d in entry['omitted_fields']) + '.', ''])
(DEST / 'VISIBLE_REVIEWER_TRANSCRIPT.md').write_text('\n'.join(transcript), encoding='utf-8')

finals = [v for v in comparisons if v['kind'] == 'assistant_final']
by_reviewer = {spec['reviewer']: {'retained_records': sum(r['source']['reviewer'] == spec['reviewer'] for r in records),
    'omitted_records': sum(r['source']['reviewer'] == spec['reviewer'] for r in omissions),
    'inbound_wrappers': sum(g['source']['reviewer'] == spec['reviewer'] for g in gaps),
    'finals': sum(f['reviewer'] == spec['reviewer'] for f in finals)} for spec in SPECS}
readme = f'''# Reviewer record recovery

**No missing delegation prompt body was recovered.** Both native child sources store all 12 inbound bodies as encrypted content: nine task requests and three steering messages. Only their authentic routing wrappers are visible. No decryption or reconstruction was attempted. [PROMPT_GAPS.json](PROMPT_GAPS.json) identifies every unavailable body by source line and message ID. These are the same 12 parent-to-child exchanges identified by the parent export, not 12 additional missing requests. Eleven outgoing reviewer collaboration argument fields are also encrypted, including one call recorded as aborted before dispatch; that is a separate direction of communication.

Two visible final responses are newly added beyond the saved app exports:

- Report reviewer, native line 112: final package-consistency review (“No material inaccuracies found in the five reviewed files…”).
- Protocol reviewer, native line 187: completion of the original bounded transcript export. This is labeled original-generation AI-record packaging, separately from design review.

The other seven final responses exactly match existing reviewer app-export text. Previously covered review outputs are retained with native provenance where permitted; no missing prompt is inferred from those responses. Native execution wrappers and line hashes add provenance, not new dialogue.

Of the 74 retained native records, **39 overlap saved app items** by exact final text or stable operation IDs. **35 have no saved app counterpart:** 15 visible tool call/result records, two final responses, one dispatch-status result, 12 routing wrappers, three encrypted-call metadata records, and two empty-result metadata records. Thus 18 add visible text/tool records and 17 add only wrappers/metadata. Calls and results are counted as separate native records; these totals are not counts of independent substantive findings. [APP_EXPORT_COMPARISON.json](APP_EXPORT_COMPARISON.json) supplies the record-by-record mapping.

## Scope and files

The frozen snapshots contain protocol lines 1–190 and report lines 1–115, ending at the original child task completions. Both belong to the two authorized parent generation/packaging turns. Bootstrap lines 1–12 in each source are excluded; no inherited parent history is exported. Subsequent record-recovery work is outside this snapshot.

- [visible_reviewer_records.jsonl](visible_reviewer_records.jsonl): authoritative filtered content, {len(records)} native records.
- [VISIBLE_REVIEWER_TRANSCRIPT.md](VISIBLE_REVIEWER_TRANSCRIPT.md): readable rendering of those records.
- [omitted_records.jsonl](omitted_records.jsonl): all {len(omissions)} whole-record omissions; per-field omissions are on each retained record.
- [EXPORT_MANIFEST.json](EXPORT_MANIFEST.json): frozen byte/line cutoffs, source hashes, turn boundaries, counts, and file checksums.
- [retained_field_verification.jsonl](retained_field_verification.jsonl): {len(verification)} exact field-value comparisons, with original/export JSON pointers and value hashes.
- [APP_EXPORT_COMPARISON.json](APP_EXPORT_COMPARISON.json): exact comparison with the two earlier app exports.
- [PROMPT_GAPS.json](PROMPT_GAPS.json): 12 unrecoverable inbound bodies and the count of unavailable encrypted outbound tool arguments.
- [SOURCE_TRUNCATIONS.json](SOURCE_TRUNCATIONS.json): exact retained source truncation markers and character offsets.
- [export_reviewer_records.py](export_reviewer_records.py): record-processing script only; historical tool calls are never replayed.

Hidden reasoning, encrypted payloads, system/developer/platform instructions, bootstrap context, duplicate execution events, historical provenance-document outputs, and nested parent-record inventories are excluded. Two report-review tool outputs retain original truncation markers reporting 1,546 and 2,535 omitted tokens. The exporter adds no text truncation and cannot restore missing content.

## Integrity

Every retained/omitted record has its original 1-based line number and SHA-256 of the complete raw native line, including its newline. The manifest separately hashes each frozen source prefix. Every retained field was compared with the original field and is unchanged; JSON formatting is normalized. The source prefixes were reread read-only and verified unchanged. All {sum(spec['lines'] for spec in SPECS)} frozen lines are accounted for exactly once as retained or omitted. Raw encrypted payload values are absent from all output artifacts.

These files supplement the original export ending at parent line {old_manifest['snapshot']['complete_lines']} ({old_manifest['snapshot']['last_timestamp']}); they do not turn it into an unabridged transcript or repair earlier missing dialogue.
'''
(DEST / 'README.md').write_text(readme, encoding='utf-8')

for name in ('visible_reviewer_records.jsonl', 'omitted_records.jsonl', 'retained_field_verification.jsonl',
             'PROMPT_GAPS.json', 'APP_EXPORT_COMPARISON.json', 'SOURCE_TRUNCATIONS.json',
             'VISIBLE_REVIEWER_TRANSCRIPT.md', 'README.md', 'export_reviewer_records.py'):
    assert not ENCRYPTED.search((DEST / name).read_text(encoding='utf-8')), name
manifest = {'format': 'filtered_native_reviewer_records_v1', 'created_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Original current-generation reviewer and AI-record packaging turns only; frozen native sources, not unabridged chat history.',
    'source_open_mode': 'read-only binary; fixed prefix lengths', 'snapshots': snapshots,
    'existing_app_exports': app_refs, 'original_current_task_export_references': original_refs,
    'original_export_cutoff': old_manifest['snapshot'], 'original_omission_ledger_records': len(old_omissions),
    'counts': {'native_lines': sum(spec['lines'] for spec in SPECS), 'retained_records': len(records),
       'omitted_records': len(omissions), 'verified_retained_fields': len(verification), 'by_reviewer': by_reviewer,
       'recovered_delegation_prompt_bodies': 0, 'unavailable_inbound_prompt_bodies': 12,
       'visible_routing_wrappers': 12, 'previously_covered_finals': 7, 'new_finals': 2,
       'native_records_overlapping_saved_app_items': 39, 'native_records_without_saved_app_counterpart': 35,
       'novelty_by_category': novelty_counts},
    'verification': {'every_retained_field_exactly_equal_to_native': True, 'every_frozen_line_accounted_for_once': True,
       'raw_line_hash_includes_original_newline': True, 'original_prefixes_unchanged': True,
       'encrypted_payload_values_exported': False, 'decryption_attempted': False, 'prompt_reconstruction_attempted': False,
       'historical_calls_replayed': False, 'exporter_added_truncation': False,
       'value_hash_definition': 'SHA-256 of UTF-8 canonical JSON (sorted keys, separators comma/colon, ensure_ascii=False).'},
    'omission_policy': ['Hidden reasoning and encrypted values', 'System/developer/platform instructions and bootstrap/inherited context',
       'Historical provenance/challenge-instruction outputs', 'Nested parent-record inventories and transcript fragments',
       'Duplicate item-completed events and internal metadata'],
    'limitations': ['No inbound prompt body is visible in the allowed native sources.',
       'Final review statements remain historical reviewer statements, not fresh simulation or design verification.',
       'Two newly retained report tool outputs are source-truncated; missing content remains unavailable.',
       'Native tool wrappers and exact-value comparison differences do not by themselves establish new substantive information.'],
    'files': {}}
for name in ('visible_reviewer_records.jsonl', 'omitted_records.jsonl', 'retained_field_verification.jsonl',
             'PROMPT_GAPS.json', 'APP_EXPORT_COMPARISON.json', 'SOURCE_TRUNCATIONS.json',
             'VISIBLE_REVIEWER_TRANSCRIPT.md', 'README.md', 'export_reviewer_records.py'):
    raw = (DEST / name).read_bytes()
    manifest['files'][name] = {'bytes': len(raw), 'sha256': sha(raw)}
write_json('EXPORT_MANIFEST.json', manifest)
print(json.dumps({'status': 'PASS', 'destination': str(DEST), 'counts': manifest['counts'],
                  'snapshot_end_times': {s['reviewer']: s['last_timestamp'] for s in snapshots}}, indent=2))
