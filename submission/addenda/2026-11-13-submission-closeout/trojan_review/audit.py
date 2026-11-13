"""Bounded recovery of two historical ordinary tool outputs; no model calls."""
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
KNOWN = Path('/Users/al-zayedal-hassan/Documents/Codex/2026-11-10/referenced-chatgpt-conversation-this-is-an/work/csaw-github/fresh-clone/submission/addenda/2026-11-12/records/reviewer_recovery')
sha = lambda b: hashlib.sha256(b).hexdigest()

def put_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def main():
    inputs = BASE / 'inputs'
    recovered = BASE / 'recovered'
    inputs.mkdir(exist_ok=True)
    recovered.mkdir(exist_ok=True)
    for name in ['PROMPT_GAPS.json', 'SOURCE_TRUNCATIONS.json']:
        target = inputs / name
        if not target.exists():
            target.write_bytes((KNOWN / name).read_bytes())
    gaps = json.loads((inputs / 'PROMPT_GAPS.json').read_text())
    truncs = json.loads((inputs / 'SOURCE_TRUNCATIONS.json').read_text())['retained_source_truncations']
    apis = [json.loads((BASE / n).read_text()) for n in ['api_protocol.json', 'api_report.json']]
    source_receipt_path = inputs / 'NATIVE_SOURCE_RECEIPT.json'
    if not source_receipt_path.exists():
        selected = {}
        for row in gaps['messages'] + truncs:
            s = row['source']
            selected.setdefault(s['native_source'], set()).add(s['native_line'])
        native = {}
        for name, lines in selected.items():
            with Path(name).open('rb') as stream:
                for n, raw in enumerate(stream, 1):
                    if n in lines:
                        native[(name, n)] = raw
                    if n >= max(lines):
                        break
        receipts = []
        for row in gaps['messages'] + truncs:
            s = row['source']
            raw = native[(s['native_source'], s['native_line'])]
            assert sha(raw) == s['native_line_sha256']
            assert len(raw) == s['native_raw_line_bytes']
            payload = json.loads(raw)['payload']
            record = {'source': s, 'raw_line_hash_matches': True, 'payload_type': payload['type'], 'id': payload.get('id')}
            if 'message_id' in row:
                assert payload['id'] == row['message_id']
                record['content_types'] = [b.get('type') for b in payload['content']]
                record['visible_wrapper'] = payload['content'][0]['text']
                assert record['content_types'] == ['input_text', 'encrypted_content']
                record['opaque_body_not_exported'] = True
            else:
                text = payload['output'][1]['text']
                assert len(text) == row['retained_string_characters']
                (inputs / f"native_line_{s['native_line']}_text.txt").write_text(text)
                record['call_id'] = payload.get('call_id')
                record['selected_text_sha256'] = sha(text.encode())
            receipts.append(record)
        put_json(source_receipt_path, {'scope': 'Exactly 12 known inbound message records and two known ordinary output records. No opaque payload exported or decoded.', 'records': receipts})
    native_receipt = json.loads(source_receipt_path.read_text())
    assert len(native_receipt['records']) == 14
    gapchecks = []
    for row in gaps['messages']:
        s = row['source']
        turns = [t for a in apis for t in a['turns'] if t['id'] == s['turn_id']]
        assert len(turns) == 1
        t = turns[0]
        assert t['userMessagePresent'] is False
        activity = [i for i in t['items'] if i['type'] == 'subAgentActivity']
        assert all(not any(k in i for k in ['prompt', 'message', 'body', 'content']) for i in activity)
        gapchecks.append({'message_id': row['message_id'], 'kind': row['kind'], 'source': s, 'turn_present_in_api': True, 'user_message_present': False, 'activity_contains_instruction_body': False, 'body_recovered': False})
    target_turn = apis[1]['turns'][0]
    assert target_turn['id'] == '01a1d25f-d0b3-78e2-8959-429ec689173c'
    commands = [i for i in target_turn['items'] if i['type'] == 'commandExecution']
    assert len(commands) == 2
    outputs = []
    for row, item in zip(truncs, commands):
        s = row['source']; line = s['native_line']
        raw_text = (inputs / f'native_line_{line}_text.txt').read_text()
        native_text = raw_text
        parsed_wrapper = native_text.startswith('{')
        if parsed_wrapper:
            native_text = json.loads(native_text)['output']
        api = item['output']['text']
        original = item['output']['originalChars']
        assert len(api) == 20000 and item['output']['truncated'] is True
        match = re.search(r'…\d+ tokens truncated…', native_text)
        assert match
        start = native_text.find(api[:100])
        assert start >= 0
        head = native_text[start:match.start()]
        tail = native_text[match.end():]
        assert api.startswith(head)
        tail_offset = original - len(tail)
        overlap = max(0, len(api) - tail_offset)
        if overlap:
            assert api[tail_offset:] == tail[:overlap]
            assert api.count(tail[:overlap]) == 1
            assembled = api + tail[overlap:]
            assert len(assembled) == original
            assert assembled.startswith(head) and assembled.endswith(tail)
            filename = f'recovered/report_line_{line}_stdout_assembled.txt'
            (BASE / filename).write_text(assembled)
            added = tail_offset - len(head)
            missing = 0
            derived = {'file': filename, 'characters': len(assembled), 'sha256': sha(assembled.encode()), 'segments': [{'source': 'api_report.json', 'item_id': item['id'], 'source_range': [0, len(api)], 'destination_range': [0, len(api)]}, {'source': f'inputs/native_line_{line}_text.txt', 'normalization': 'Parse ordinary JSON output wrapper; take text after original truncation marker.', 'source_tail_range': [overlap, len(tail)], 'destination_range': [len(api), original]}], 'label': 'Derived assembly from two authentic captures, not a newly retrieved complete raw transcript.'}
        else:
            added = len(api) - len(head)
            missing = tail_offset - len(api)
            filename = f'recovered/report_line_{line}_api_extra.txt'
            extra = api[len(head):]
            (BASE / filename).write_text(extra)
            derived = {'new_text_file': filename, 'new_text_sha256': sha(extra.encode()), 'missing_original_character_range': [len(api), tail_offset], 'retained_api_range': [0, len(api)], 'retained_native_tail_range': [tail_offset, original], 'label': 'Incomplete output; missing characters are not filled or guessed.'}
        outputs.append({'native_source': s, 'api_source': 'api_report.json', 'api_item_id': item['id'], 'api_command': item['command'], 'api_output_sha256': sha(api.encode()), 'original_character_count_reported_by_api': original, 'ordinary_json_wrapper_parsed': parsed_wrapper, 'native_stdout_header_offset': start, 'native_head_characters': len(head), 'native_tail_characters': len(tail), 'native_original_marker': match.group(), 'api_prefix_characters': len(api), 'tail_original_start_offset': tail_offset, 'exact_overlap_characters': overlap, 'newly_recovered_characters': added, 'remaining_missing_characters': missing, 'complete_stdout_coverage': missing == 0, 'derived': derived})
    assert [o['newly_recovered_characters'] for o in outputs] == [4, 10140]
    assert [o['remaining_missing_characters'] for o in outputs] == [6178, 0]
    result = {'scope': 'Bounded read-only audit of 12 known reviewer messages and 2 known truncated outputs; writes only in this isolated audit folder.', 'api_snapshots': [{'file': n, 'sha256': sha((BASE / n).read_bytes()), 'thread_id': a['thread']['id'], 'arguments': a['arguments'], 'page': a['page'], 'turn_count': len(a['turns'])} for n, a in zip(['api_protocol.json', 'api_report.json'], apis)], 'prompt_checks': gapchecks, 'output_checks': outputs, 'summary': {'prompt_bodies_recovered': 0, 'prompt_bodies_still_unavailable': 12, 'source_record_hashes_verified': 14, 'tool_outputs_now_fully_covered_by_authentic_fragments': 1, 'tool_outputs_still_incomplete': 1, 'new_output_characters_recovered': 10144, 'output_characters_still_missing': 6178}, 'limits': ['No claim of an unabridged generation/review transcript.', 'Character offsets are Unicode string offsets, not byte offsets or token counts.', 'Original source truncation markers and API truncation flags remain preserved unchanged.', 'No historical command was rerun. No ciphertext or internal payload was decoded. Ordinary JSON wrapper parsing is recorded explicitly.', 'Only saved normal-API projections were compared; no new API call or higher output-limit request was made in this resumed audit.', 'No repository, RTL, simulation or hardware change. No new tests. No solution material consulted.']}
    put_json(BASE / 'RECEIPT.json', result)
    print(json.dumps(result['summary']))

if __name__ == '__main__':
    main()
