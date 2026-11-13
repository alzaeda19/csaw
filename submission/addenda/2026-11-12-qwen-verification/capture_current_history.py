"""Export only this documentation turn's visible messages and tool inputs."""
from pathlib import Path
from datetime import datetime, timezone
import collections
import hashlib
import json

SOURCE = Path('/Users/al-zayedal-hassan/.codex/sessions/2026/11/11/rollout-2026-11-11T22-38-22-01a1c563-aa79-7e12-ae2f-72d867d1e3da_01a1cdd5-c9db-7581-b129-a9c84bd76091.jsonl')
OUT = Path(__file__).parent / 'ai_logs/codex_verification'
REQUEST = (Path(__file__).parent / 'records/USER_REQUEST.txt').read_text().strip()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    raw = SOURCE.read_bytes()
    lines = raw.splitlines(keepends=True)
    if lines and not lines[-1].endswith(b'\n'):
        lines.pop()
    retained, omitted = [], []
    started = False
    boundary = None
    for number, line in enumerate(lines, 1):
        record = json.loads(line)
        payload = record.get('payload', {})
        kind = record.get('type', '') + ':' + payload.get('type', '')
        if not started:
            if kind != 'response_item:message' or payload.get('role') != 'user':
                continue
            text = ''.join(b.get('text', '') for b in payload.get('content', []) if b.get('type') == 'input_text')
            if text.strip() != REQUEST:
                continue
            started, boundary = True, number
        selected = None
        if kind == 'response_item:message' and payload.get('role') in ('user', 'assistant') and payload.get('channel') not in ('analysis', 'summary'):
            blocks = [{'type': b['type'], 'text': b['text']}
                      for b in payload.get('content', [])
                      if b.get('type') in ('input_text', 'output_text') and isinstance(b.get('text'), str)]
            if blocks:
                selected = {'type': 'message', 'role': payload['role'], 'content': blocks}
        elif kind == 'response_item:custom_tool_call':
            selected = {k: payload[k] for k in ('type', 'call_id', 'name', 'input') if k in payload}
        if selected is not None:
            retained.append({'native_line': number, 'native_line_sha256': digest(line), 'timestamp': record.get('timestamp'), 'payload': selected})
        else:
            reason = ('tool outputs excluded to avoid inherited snapshots, hidden records and instruction-file contents; separate evidence receipts retain checked results'
                      if kind.endswith('tool_call_output') else 'hidden reasoning, duplicate events or internal metadata; not required visible dialogue')
            omitted.append({'native_line': number, 'kind': kind, 'reason': reason})
    assert boundary is not None
    OUT.mkdir(exist_ok=True)
    for name, rows in [('visible_messages_and_tool_inputs.jsonl', retained), ('omitted_records.jsonl', omitted)]:
        (OUT / name).write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    manifest = {
        'scope': 'Current Qwen-assisted verification turn only; includes visible verification code/tool inputs, not a reconstruction of original generation history.',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'source': str(SOURCE), 'first_native_line': boundary, 'last_native_line': len(lines),
        'source_snapshot_prefix_sha256': digest(b''.join(lines)),
        'source_snapshot_prefix_bytes': sum(map(len, lines)),
        'last_timestamp': json.loads(lines[-1]).get('timestamp'),
        'retained_records': len(retained), 'omitted_records': len(omitted),
        'visible_text_changed': False, 'hidden_reasoning_exported': False,
        'block_metadata_including_annotations_and_logprobs_excluded': True,
        'earlier_turns_exported': False,
        'limitations': ['Tool results are intentionally omitted; task journal and integrity/publication receipts document outcomes.', 'This snapshot predates the final push verification and user-facing completion message. It does not claim to contain future messages.'],
        'files': {p.name: {'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())} for p in sorted(OUT.glob('*.jsonl'))}
    }
    (OUT / 'EXPORT_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k:manifest[k] for k in ('first_native_line','last_native_line','retained_records','omitted_records')},indent=2))

if __name__ == '__main__':
    main()
