from pathlib import Path
import json, hashlib, datetime

OUT = Path(__file__).resolve().parent / 'ai_records'
OUT.mkdir(exist_ok=True)
SOURCES = [
    ('audit', Path('/Users/al-zayedal-hassan/.codex/sessions/2026/11/12/rollout-2026-11-12T19-12-19-01a1b0ad-f593-7f90-a689-b621984f7cb4_01a1d23f-7ed7-7fa1-9afd-64875b8a6cf8.jsonl'), 1824),
    ('peer', Path('/Users/al-zayedal-hassan/.codex/sessions/2026/11/12/rollout-2026-11-12T21-33-19-01a1d2c0-9947-77a3-befe-8f8eadc57345.jsonl'), 1),
]
sha = lambda b: hashlib.sha256(b).hexdigest()
allowed = {'message', 'agent_message', 'custom_tool_call', 'custom_tool_call_output', 'function_call', 'function_call_output'}
indexes = []
for label, source, first in SOURCES:
    raw = source.read_bytes()
    lines = raw.splitlines()
    retained, omissions = [], []
    verified = 0
    for number, line in enumerate(lines, 1):
        if number < first:
            continue
        record = json.loads(line)
        p = record.get('payload', {})
        kind = p.get('type')
        if record.get('type') != 'response_item' or kind not in allowed:
            omissions.append({'line': number, 'reason': 'Non-visible event, internal context/reasoning, or duplicate bookkeeping', 'sha256': sha(line)})
            continue
        if kind == 'message' and (p.get('role') not in {'user', 'assistant'} or p.get('phase') == 'analysis'):
            omissions.append({'line': number, 'reason': 'Platform instruction or internal reasoning', 'sha256': sha(line)})
            continue
        serialized = json.dumps(p, ensure_ascii=False)
        if kind == 'message' and p.get('role') == 'user' and '<environment_context>' in serialized:
            omissions.append({'line': number, 'reason': 'Environment inventory, not an audit request', 'sha256': sha(line)})
            continue
        if kind in {'custom_tool_call_output', 'function_call_output'} and (
            ('base_instructions' in serialized and 'creator_account_id' in serialized)
            or ('corrected_csaw_requirements' in serialized and 'agent_status' in serialized)
            or ('# PDF Skill' in serialized and 'Tools + Contract Requirements' in serialized)
            or 'gAAAAA' in serialized
        ):
            omissions.append({'line': number, 'reason': 'Mixed platform-instruction, historical-agent-inventory or encrypted-body diagnostic output excluded in full; no missing design-generation answer inferred', 'sha256': sha(line)})
            continue
        fields = {}
        removed = []
        def visit(value, path):
            nonlocal_unused = None
            if isinstance(value, dict):
                if value.get('type') in {'encrypted_content', 'input_image', 'image', 'image_url'}:
                    removed.append({'path': path, 'reason': 'Encrypted content or binary media; media is separately preserved where generated', 'sha256': sha(json.dumps(value, sort_keys=True).encode())})
                    return
                for key, val in value.items():
                    pointer = path + '/' + key.replace('~', '~0').replace('/', '~1')
                    if key in {'internal_chat_message_metadata_passthrough', 'encrypted_content', 'logprobs', 'annotations'}:
                        removed.append({'path': pointer, 'reason': 'Internal metadata or opaque encrypted content', 'sha256': sha(json.dumps(val, sort_keys=True).encode())})
                    elif key == 'arguments' and isinstance(val, str) and 'gAAAAA' in val:
                        removed.append({'path': pointer, 'reason': 'Arguments contain encrypted ordinary message body; plaintext unavailable in this export', 'sha256': sha(val.encode())})
                    else:
                        visit(val, pointer)
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    visit(val, path + '/' + str(i))
            elif isinstance(value, str) and value.startswith('gAAAAA'):
                removed.append({'path': path, 'reason': 'Opaque encrypted body', 'sha256': sha(value.encode())})
            else:
                fields[path] = value
        visit(p, '/payload')
        for pointer, value in fields.items():
            original = record
            for token in pointer.strip('/').split('/'):
                token = token.replace('~1', '/').replace('~0', '~')
                original = original[int(token)] if isinstance(original, list) else original[token]
            assert original == value
            verified += 1
        retained.append({'native_line': number, 'native_line_sha256': sha(line), 'timestamp': record.get('timestamp'), 'visible_fields': fields, 'omitted_fields': removed})
    dest = OUT / (label + '_visible_fields.jsonl')
    dest.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in retained))
    index = {'source': str(source), 'first_line': first, 'last_line': len(lines), 'source_snapshot_sha256': sha(raw), 'cutoff_timestamp': json.loads(lines[-1]).get('timestamp'), 'retained_records': len(retained), 'verified_exact_scalar_fields': verified, 'whole_record_omissions': omissions, 'output': dest.name, 'output_sha256': sha(dest.read_bytes())}
    indexes.append(index)
(OUT / 'EXPORT_MANIFEST.json').write_text(json.dumps({'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'format': 'Explicit JSON-pointer field projection retaining exact scalar values, not a full native transcript', 'sources': indexes}, indent=2) + '\n')
print(json.dumps([{'source': x['source'], 'records': x['retained_records'], 'exact_fields': x['verified_exact_scalar_fields'], 'cutoff': x['cutoff_timestamp']} for x in indexes], indent=2))
