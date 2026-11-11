#!/usr/bin/env python3
"""Copy and verify the already-exported 17 clean stages; never reconstruct content."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import re

DEST = Path(__file__).resolve().parent
ROOT = Path('/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06')
PRIOR = ROOT / 'mac_infrastructure_execution_2026-11-07_20261107T170940Z'
TRANSCRIPTS = PRIOR / 'records/transcripts'
VISIBLE = TRANSCRIPTS / 'clean_native_visible'
CLEAN_ID = '01a1b130-b28f-70c3-b80d-a7129910ee45'
SENDER_ID = '01a1b0ad-f593-7f90-a689-b621984f7cb4'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save_json(name, value):
    (DEST / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def body(payload):
    value = payload.get('content', [])
    if isinstance(value, str):
        return value
    return '\n'.join(x.get('text', '') for x in value
                     if isinstance(x, dict) and x.get('type') in ('text', 'input_text', 'output_text'))


def string_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from string_values(item)


prior_manifest = json.loads((VISIBLE / 'export_manifest.json').read_text())
prior_phases = json.loads((TRANSCRIPTS / 'phase_index.json').read_text())
source = Path(prior_manifest['source_file'])
input_files = sorted(set([source, *VISIBLE.rglob('*'), TRANSCRIPTS / 'phase_index.json',
                         PRIOR / 'records/source_thread_references.json',
                         PRIOR / 'export_clean_transcript.py', PRIOR / 'TRANSCRIPT_EXPORT_STATUS.md',
                         ROOT / 'handoff_and_records_index_2026-11-07/AI_RECORDS_INDEX.md']))
input_files = [p for p in input_files if p.is_file()]
before = {str(p): {'sha256': digest(p.read_bytes()), 'bytes': p.stat().st_size} for p in input_files}
source_data = source.read_bytes()
source_lines = source_data.splitlines(keepends=True)
assert digest(source_data) == prior_manifest['source_sha256']
assert len(source_lines) == prior_manifest['source_lines'] == 3558
assert prior_manifest['metadata']['id'] == CLEAN_ID

existing_record_texts = (VISIBLE / 'visible_events.jsonl').read_text().splitlines()
existing = [json.loads(line) for line in existing_record_texts]
existing_record_text_by_source_line = {event['source_line']: text for event, text in zip(existing, existing_record_texts)}
existing_counts = collections.Counter(x['category'] for x in existing)
assert dict(existing_counts) == prior_manifest['exported_counts']
allowed_turns = {p['turn_id'] for p in prior_phases}
assert len(allowed_turns) == 17
selected, exclusions = [], []
for event in existing:
    no = event['source_line']
    raw = source_lines[no - 1]
    native = json.loads(raw)
    payload = native['payload']
    assert digest(raw) == event['source_record_sha256']
    assert native['timestamp'] == event['timestamp']
    if event['category'] == 'command_execution':
        original = payload['item']
        assert event['payload']['type'] == 'command_execution'
        assert original['type'] == 'CommandExecution'
        for key, value in event['payload'].items():
            if key == 'type':
                continue
            assert value == (payload.get(key) if key in ('started_at_ms', 'completed_at_ms') else original[key])
    else:
        assert all(payload[key] == value for key, value in event['payload'].items())
    if event['category'] == 'user_role_message':
        exclusions.append({k: event[k] for k in ('source_line', 'source_record_sha256', 'timestamp', 'category')})
        exclusions[-1]['reason'] = 'Platform-supplied user-role context; body omitted from this new export.'
        continue
    assert event['turn_id'] in allowed_turns
    selected.append(event)

# Inspect only type/role/phase metadata to confirm the existing export did not miss
# an eligible visible record; excluded internal bodies are never exported.
candidate_lines = set()
role_counts = collections.Counter()
native_excluded = collections.Counter()
for no, raw in enumerate(source_lines, 1):
    native = json.loads(raw)
    payload = native.get('payload', {})
    kind, subtype = native.get('type'), payload.get('type')
    eligible = False
    if kind == 'response_item':
        if subtype == 'message':
            role_counts[(payload.get('role'), payload.get('phase'), payload.get('channel'))] += 1
            eligible = payload.get('role') == 'assistant' and payload.get('phase') in ('commentary', 'final_answer') and payload.get('channel') != 'analysis'
        elif subtype in ('function_call', 'custom_tool_call', 'function_call_output', 'custom_tool_call_output'):
            eligible = True
    elif kind == 'event_msg' and subtype == 'item_completed':
        eligible = payload.get('item', {}).get('type') == 'CommandExecution'
    if eligible:
        candidate_lines.add(no)
    else:
        key = kind + ':' + str(subtype)
        if kind == 'response_item' and subtype == 'message':
            key += ':' + str(payload.get('role'))
        native_excluded[key] += 1
assert candidate_lines == {e['source_line'] for e in selected}

screen_rules = {
    'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'openai_style_token': r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}',
    'github_token': r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',
    'aws_access_key': r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'slack_token': r'\bxox[baprs]-[A-Za-z0-9-]{20,}',
    'credential_assignment': r'''(?i)\b(?:password|secret|api_key|access_token|auth_token)\s*[:=]\s*["'][^"'\s]{8,}["']''',
    'system_developer_markup': r'<(?:system|developer)(?:>|\s)',
    'encrypted_reasoning_field': r'"encrypted_content"',
}
screen_findings = []
for event in selected:
    serialized = json.dumps(event['payload'], ensure_ascii=False)
    for name, pattern in screen_rules.items():
        if re.search(pattern, serialized):
            screen_findings.append({'source_line': event['source_line'], 'rule': name})
assert not screen_findings, 'Review candidate secrets/instructions before exporting.'

for dirname in ('prompts', 'finals'):
    (DEST / dirname).mkdir(exist_ok=True)
phases = []
for old in prior_phases:
    turn = old['turn_id']
    prompt = next(e for e in selected if e['turn_id'] == turn and e['category'] == 'delegated_task')
    final = next(e for e in selected if e['turn_id'] == turn and e['category'] == 'assistant_final_answer')
    prompt_text = prompt['payload']['output']
    final_text = body(final['payload'])
    sender = re.search(r'<source_thread_id>([^<]+)</source_thread_id>', prompt_text).group(1)
    assert sender == SENDER_ID
    assert (TRANSCRIPTS / old['prompt']).read_bytes() == prompt_text.encode()
    assert (TRANSCRIPTS / old['authentic_final']).read_bytes() == final_text.encode()
    phase = old['phase_directories'][0]
    assert phase in final_text, 'Phase mapping requires final response destination evidence.'
    prompt_name, final_name = f'prompts/{turn}.txt', f'finals/{turn}.txt'
    (DEST / prompt_name).write_bytes(prompt_text.encode())
    (DEST / final_name).write_bytes(final_text.encode())
    phases.append({
        'phase_directory': phase, 'clean_thread_id': CLEAN_ID, 'turn_id': turn,
        'envelope_source_thread_id': sender,
        'envelope_sender_scope': 'Mixed coordinating thread; history excluded. Envelope received by clean thread only.',
        'mapping_evidence': 'Prior phase_index.json and exact phase-directory destination in native final response.',
        'prompt': prompt_name, 'prompt_source_line': prompt['source_line'],
        'prompt_source_record_sha256': prompt['source_record_sha256'], 'prompt_timestamp': prompt['timestamp'],
        'final': final_name, 'final_source_line': final['source_line'],
        'final_source_record_sha256': final['source_record_sha256'], 'final_timestamp': final['timestamp'],
        'final_bytes': len(final_text.encode()), 'final_sha256': digest(final_text.encode()),
        'prior_final_file': str(TRANSCRIPTS / old['authentic_final']),
        'status': 'Already present in authentic 2026-11-07 export; reverified, not newly recovered.'})

assert all(json.dumps(e, ensure_ascii=False) == existing_record_text_by_source_line[e['source_line']] for e in selected)
(DEST / 'visible_events.jsonl').write_text(''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in selected))
save_json('phase_index.json', phases)
save_json('source_line_index.json', [dict(export_record=i + 1, **{k: e[k] for k in ('source_line', 'source_record_sha256', 'timestamp', 'turn_id', 'category')}) for i, e in enumerate(selected)])
message_lines = ['# Historical clean visible messages', '',
                 'Exact existing delegated requests and assistant responses; headings are added. No original body is reconstructed. Tool records are in visible_events.jsonl.', '']
for e in selected:
    if e['category'] not in ('delegated_task', 'assistant_commentary', 'assistant_final_answer'):
        continue
    value = e['payload']['output'] if e['category'] == 'delegated_task' else body(e['payload'])
    message_lines.extend([f"## {e['category']} — {e['timestamp']}", '',
                          f"Clean thread: {CLEAN_ID}; turn: {e['turn_id']}; native line: {e['source_line']}.", '', value, ''])
(DEST / 'VISIBLE_MESSAGES.md').write_text('\n'.join(message_lines) + '\n')

truncations = []
for e in selected:
    if e['category'] not in ('custom_tool_call_output', 'function_call_output', 'command_execution'):
        continue
    flags = set()
    for value in string_values(e['payload']):
        if 'Warning: truncated output' in value:
            flags.add('Original tool warning: truncated output')
        if 'command output truncated for persistence' in value:
            flags.add('Original persistence truncation marker')
    if flags:
        truncations.append({k: e[k] for k in ('source_line', 'source_record_sha256', 'turn_id', 'category')} | {'markers': sorted(flags), 'status': 'Original shortened output retained exactly; no missing bytes reconstructed.'})
gaps = {
    'scope': 'Only the 17 original clean stages in the unchanged known native source, lines 1–3558.',
    'coordinating_thread_excluded': {'thread_id': SENDER_ID, 'reason': 'Mixed/pre-clean or potentially solution-contaminated history. Not opened by this recovery task. Only sender IDs and envelopes already received in the clean thread retained.'},
    'platform_context_exclusions_relative_to_prior_export': exclusions,
    'native_excluded_record_metadata_counts': dict(native_excluded),
    'original_tool_truncations': truncations,
    'compactions': prior_manifest['compactions'],
    'cutoff': {'last_native_line': len(source_lines), 'last_native_timestamp': json.loads(source_lines[-1])['timestamp'], 'appended_native_lines_since_prior_export': 0, 'observed_completed_turns': 17, 'observed_finals': 17},
    'remaining_gaps': [
        'Original human prompts and broader conversation in the mixed coordinating thread are outside scope; received delegation envelopes are retained.',
        'Original tool truncations and persistence cutoff markers remain. This is not a promise of every tool byte ever generated.',
        'Internal reasoning, developer/system instructions, internal replacement context and opaque internal metadata are excluded.',
        'No plaintext is inferred from opaque/encrypted bodies, and no missing body is decrypted or reconstructed.',
        'Exact serving-model identity and undisclosed inference parameters are not authenticated by local logs.',
        'The absence of a final capture in older stage records is resolved by the already-existing Nov 7 clean export; those historical files remain untouched.'],
    'record_preservation_note': 'AGENTS.md/SKILL.md text encountered as ordinary visible tool-file output remains source evidence; raw developer-role and platform context payloads are omitted.',
    'redactions': {'body_redactions': 0, 'entire_platform_context_records_omitted': len(exclusions), 'secret_pattern_findings': 0, 'screen_scope': list(screen_rules), 'screen_limit': 'Pattern screening does not establish absence of every possible secret format.'}}
save_json('scope_and_gaps.json', gaps)

after = {str(p): {'sha256': digest(p.read_bytes()), 'bytes': p.stat().st_size} for p in input_files}
assert before == after
save_json('prior_artifact_hashes.json', {'all_inputs_unchanged': True, 'files': before})
counts = collections.Counter(e['category'] for e in selected)
manifest = {
    'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'purpose': 'Self-contained verified re-export of already-existing authentic clean historical records.',
    'source': {'path': str(source), 'thread_id': CLEAN_ID, 'bytes': len(source_data), 'lines': len(source_lines), 'sha256': digest(source_data)},
    'prior_export': {'path': str(VISIBLE), 'source_sha256_at_prior_export': prior_manifest['source_sha256'], 'native_source_unchanged': True, 'visible_events_sha256': before[str(VISIBLE / 'visible_events.jsonl')]['sha256'], 'counts': dict(existing_counts), 'total_events': len(existing)},
    'new_export': {'total_events': len(selected), 'counts': dict(counts), 'distinct_clean_turns': len(allowed_turns), 'newly_recovered_events': 0, 'already_exported_events_reverified_and_copied': len(selected), 'prior_platform_context_events_omitted': len(exclusions), 'newly_recovered_finals': 0, 'already_exported_finals_reverified_and_copied': 17},
    'counting_note': 'Counts are native record counts, including distinct command execution and tool-result records; not counts of unique logical commands.',
    'field_identity': 'Each retained JSONL record text exactly matches its corresponding prior-export JSONL record. All retained payload values equal their native source values except the explicitly normalized command type described below. Native source-line hashes retain original line ending bytes.',
    'export_schema_metadata': {
        'command_type_normalization': {'applies_to_category': 'command_execution', 'native_path': 'payload.item.type', 'native_value': 'CommandExecution', 'export_path': 'payload.type', 'export_value': 'command_execution', 'purpose': 'Prior exporter schema label; not a verbatim native type field.'},
        'command_field_layout': 'Command fields other than type are copied unchanged from native payload.item; started_at_ms and completed_at_ms are copied unchanged from the enclosing native payload. Layout is flattened by the prior exporter.',
        'record_wrapper': 'source_line, source_record_sha256, category and the association of turn_id are exporter index metadata; timestamp is copied from the native record.',
        'other_payload_value_normalizations_found': 0},
    'scope_and_gaps': 'scope_and_gaps.json', 'phase_index': 'phase_index.json',
    'prior_input_hashes': 'prior_artifact_hashes.json', 'all_source_and_prior_artifacts_unchanged': True,
    'legacy_index_gaps_satisfied_by_existing_2026_11_07_export': ['baseline_recovery final capture', 'baseline_followup final capture', 'protocol_harness final listed absent in table', 'source_intake final listed absent in table'],
    'limitations': ['A local matching hash establishes consistency, not independent provider attestation.', 'No original workspace record, source file, repository or CSAW artifact modified.', 'No experiment/test reruns and no model calls.']}
save_json('export_manifest.json', manifest)
save_json('field_integrity_verification.json', {'passed': True, 'prior_records_verified_against_native': len(existing), 'retained_records': len(selected), 'retained_record_texts_exactly_match_corresponding_prior_jsonl_records': True, 'native_payload_comparison': 'Every retained payload value matches its native source value except command_execution payload.type, which is prior-export schema metadata normalized from native payload.item.type = CommandExecution. Command timestamp fields are taken from the enclosing native event payload, while remaining command fields are taken from payload.item.', 'normalized_command_type_records': counts['command_execution'], 'other_payload_value_normalizations_found': 0, 'retained_final_files_equal_prior_files': 17, 'eligible_native_visible_lines_exactly_match_retained_lines': True, 'all_prior_hashes_unchanged': True, 'newly_recovered_events': 0})

index = ['# Historical clean log verification', '',
         '**Newly recovered events: 0. Newly recovered final responses: 0.** The Nov 7 export already contains all 17 delegated tasks, 81 assistant progress messages, 17 finals, and 1,190 tool/command records. This bundle re-verifies and copies 1,305 existing records. Four platform context messages from the prior export are omitted.', '',
         'The known clean native source remains byte-for-byte unchanged (3,558 lines; SHA-256 `' + digest(source_data) + '`). All source and prior-export hashes remained unchanged during this work.', '',
         'Each retained JSONL record exactly matches its corresponding prior-export record. Its payload values match native values except the prior exporter\'s command type label: native `payload.item.type = "CommandExecution"` is represented as export `payload.type = "command_execution"` for 388 records. This label is export schema metadata. Command fields are flattened from `payload.item`; command start/completion timestamps come from the enclosing native payload. No other payload-value normalization was found. Source-line hashes and record categories are provenance/index metadata.', '',
         'The `source_thread_id` in all 17 delegation envelopes identifies the mixed coordinator `' + SENDER_ID + '`, not the clean recipient. That coordinator history was not opened. The authentic clean conversation is `' + CLEAN_ID + '`.', '',
         'The older AI_RECORDS_INDEX.md gaps for **baseline_recovery** and **baseline_followup** are already satisfied by authentic final captures made on Nov 7. Its table also lacked final captures for **protocol_harness** and **source_intake**; those are present in that same existing export. No old record was overwritten.', '',
         '[Readable messages](VISIBLE_MESSAGES.md) · [Structured records](visible_events.jsonl) · [Manifest](export_manifest.json) · [Exact phase map](phase_index.json) · [Scope and gaps](scope_and_gaps.json) · [Preserved input hashes](prior_artifact_hashes.json)', '',
         '| Clean stage | Turn ID | Prompt / final native line | Authentic final |',
         '|---|---|---|---|']
for phase in phases:
    index.append(f"| {phase['phase_directory']} | `{phase['turn_id']}` | {phase['prompt_source_line']} / {phase['final_source_line']} | [Final]({phase['final']}) |")
index.extend(['', f"Remaining limits: {len(truncations)} native output records contain explicit original truncation markers; two compaction boundaries are recorded. Internal reasoning, native developer/system content and platform user-context bodies are excluded. Original received prompts and finals are present for every observed clean task, but this is a filtered visible export, not an unabridged session or proof that no other conversations existed.", '',
              'Tool outputs retain their historical text, including ordinary reads of local guidance documents. No opaque or missing body was decrypted or reconstructed. No experiment or test was rerun, and no model was called.', ''])
(DEST / 'INDEX.md').write_text('\n'.join(index))
save_json('OUTPUT_HASHES.json', {str(p.relative_to(DEST)): {'sha256': digest(p.read_bytes()), 'bytes': p.stat().st_size} for p in sorted(DEST.rglob('*')) if p.is_file() and p.name != 'OUTPUT_HASHES.json'})
print(json.dumps({'destination': str(DEST), 'existing_events': len(existing), 'retained_events': len(selected), 'newly_recovered_events': 0, 'finals': len(phases), 'original_truncation_records': len(truncations), 'all_inputs_unchanged': True}, indent=2))
