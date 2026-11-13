#!/usr/bin/env python3
"""Read-only independent checks of exported visible fields and native provenance."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / 'records/generation_tail'
OLD = Path('/Users/al-zayedal-hassan/Documents/CSAW_Qwen_Submission_20261113T001822Z_9sj2k3k6/ai_logs/codex_current_task')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def subset(actual, native):
    """Retained mappings are subsets; filtered arrays retain source order."""
    if isinstance(actual, dict):
        if not isinstance(native, dict):
            return False, 0
        count = 0
        for key, value in actual.items():
            if key not in native:
                return False, 0
            okay, leaves = subset(value, native[key])
            if not okay:
                return False, 0
            count += leaves
        return True, count
    if isinstance(actual, list):
        if not isinstance(native, list):
            return False, 0
        position, count = 0, 0
        for value in actual:
            found = False
            while position < len(native):
                okay, leaves = subset(value, native[position])
                position += 1
                if okay:
                    count += leaves
                    found = True
                    break
            if not found:
                return False, 0
        return True, count
    return type(actual) is type(native) and actual == native, 1


manifest = json.loads((EXPORT / 'EXPORT_MANIFEST.json').read_text())
prior_manifest = json.loads((OLD / 'EXPORT_MANIFEST.json').read_text())
source = Path(manifest['source'])
with source.open('rb') as f:
    raw = f.read(manifest['snapshot']['prefix_bytes'])
assert sha(raw) == manifest['snapshot']['prefix_sha256']
assert sha(raw[:prior_manifest['snapshot']['prefix_bytes']]) == prior_manifest['snapshot']['prefix_sha256']
lines = raw.splitlines(keepends=True)
assert len(lines) == 697
rows = [json.loads(line) for line in (EXPORT / 'visible_task_records.jsonl').read_text().splitlines()]
omissions = [json.loads(line) for line in (EXPORT / 'omitted_records.jsonl').read_text().splitlines()]
prior = [json.loads(line) for line in (OLD / 'visible_task_records.jsonl').read_text().splitlines()]
by_line = {row['source']['native_line']: row for row in rows}
assert len(by_line) == len(rows) == 199
assert all(by_line[row['source']['native_line']] == row for row in prior)
assert len(prior) == 155
assert set(by_line) | {r['source']['native_line'] for r in omissions} == set(range(32, 698))
assert not (set(by_line) & {r['source']['native_line'] for r in omissions})
leaf_checks = 0
for row in rows + omissions:
    origin = row['source']
    line = lines[origin['native_line'] - 1]
    native = json.loads(line)
    assert sha(line) == origin['native_line_sha256']
    assert origin['native_source'] == str(source)
    assert origin['timestamp'] == native['timestamp']
    if 'record' in row:
        assert row['record']['type'] == native['type']
        okay, count = subset(row['record']['payload'], native['payload'])
        assert okay, ('Changed retained payload', origin['native_line'])
        leaf_checks += count
serialized = (EXPORT / 'visible_task_records.jsonl').read_text()
assert not re.search(r'gAAAA[A-Za-z0-9_=-]{70,}', serialized)
assert by_line[694]['record']['payload']['phase'] == 'final_answer'
end = json.loads(lines[696])
assert end['payload']['type'] == 'task_complete'
assert end['payload']['turn_id'] == '01a1d254-6a62-7ac2-8865-04c80eae105c'
for name, item in manifest['files'].items():
    data = (EXPORT / name).read_bytes()
    assert len(data) == item['bytes'] and sha(data) == item['sha256']
with source.open('rb') as f:
    assert sha(f.read(len(raw))) == sha(raw)
result = {
    'status': 'PASS', 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'retained_records': len(rows), 'omitted_records': len(omissions),
    'prior_records_exactly_preserved': len(prior), 'new_records': len(rows) - len(prior),
    'retained_leaf_values_checked': leaf_checks,
    'native_line_hashes_checked': len(rows) + len(omissions),
    'native_coverage_first_line': 32, 'native_coverage_last_line': 697,
    'final_reply_present_at_line': 694,
    'new_and_old_source_prefix_hashes_match': True,
    'export_manifest_files_match': True, 'source_prefix_unchanged': True,
    'encrypted_payload_scan_clear': True,
    'limits': 'Checks authenticity of retained fields and documented coverage. Does not recover encrypted prompts or certify that every omitted item is required or irrelevant to a grading rubric.'
}
(ROOT / 'verification/GENERATION_EXPORT_VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
