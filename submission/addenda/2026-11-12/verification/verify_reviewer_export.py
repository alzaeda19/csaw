#!/usr/bin/env python3
"""Check filtered reviewer artifacts without replaying any historical tool call."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / 'records/reviewer_recovery'
manifest = json.loads((EXPORT / 'EXPORT_MANIFEST.json').read_text())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def pointer(value, path):
    for token in path.lstrip('/').split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value

sources = {}
for item in manifest['snapshots']:
    with Path(item['source']).open('rb') as f:
        raw = f.read(item['prefix_bytes'])
    assert sha(raw) == item['prefix_sha256']
    lines = raw.splitlines(keepends=True)
    assert len(lines) == item['complete_lines']
    sources[item['reviewer']] = lines
rows = [json.loads(x) for x in (EXPORT / 'visible_reviewer_records.jsonl').read_text().splitlines()]
omitted = [json.loads(x) for x in (EXPORT / 'omitted_records.jsonl').read_text().splitlines()]
index = {(x['source']['reviewer'], x['source']['native_line']): x for x in rows}
assert len(index) == len(rows) == 74
seen = set()
for row in rows + omitted:
    origin = row['source']
    key = (origin['reviewer'], origin['native_line'])
    assert key not in seen
    seen.add(key)
    raw = sources[key[0]][key[1] - 1]
    assert sha(raw) == origin['native_line_sha256']
    assert len(raw) == origin['native_raw_line_bytes']
assert len(seen) == 305
checks = [json.loads(x) for x in (EXPORT / 'retained_field_verification.jsonl').read_text().splitlines()]
for check in checks:
    key = (check['reviewer'], check['native_line'])
    native = json.loads(sources[key[0]][key[1] - 1])
    actual = pointer(index[key], check['export_pointer'])
    original = pointer(native, check['native_pointer'])
    assert type(actual) is type(original) and actual == original
    canonical = json.dumps(actual, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    assert sha(canonical) == check['canonical_json_value_sha256']
assert len(checks) == 519
artifact_checks = 0
for name, item in manifest['files'].items():
    data = (EXPORT / name).read_bytes()
    assert len(data) == item['bytes'] and sha(data) == item['sha256'], name
    artifact_checks += 1
for p in EXPORT.iterdir():
    if p.is_file():
        assert not re.search(rb'gAAAA[A-Za-z0-9_=-]{70,}', p.read_bytes()), p.name
result = {
    'status': 'PASS', 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'native_source_prefixes': len(sources), 'raw_line_hashes': len(seen),
    'retained_records': len(rows), 'whole_record_omissions': len(omitted),
    'retained_field_values_checked': len(checks), 'artifact_hashes_checked': artifact_checks,
    'encrypted_payload_scan_clear': True,
    'limit': 'Authenticates retained native fields and exported file integrity; inaccessible prompt text remains inaccessible.'
}
(ROOT / 'verification/REVIEWER_EXPORT_VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
