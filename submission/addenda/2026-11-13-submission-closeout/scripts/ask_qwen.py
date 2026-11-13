"""Ask the existing local Qwen model for text only; preserve requests and replies."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('prompt_file', type=Path)
parser.add_argument('name')
args = parser.parse_args()
out = ROOT / 'ai_logs' / args.name
out.mkdir(exist_ok=False)
request = {
    'model': 'qwen3-csaw-agent:20261112234518',
    'messages': [
        {'role': 'system', 'content': 'You are an evidence-focused reviewer of an authorized local hardware project. Provide concise final conclusions with source references, uncertainty and verification checks. You have no tools or file-write permissions. Do not claim to have run tests. Do not create or improve malicious behavior, concealment, evasion or attack-generation systems. No published challenge solutions.'},
        {'role': 'user', 'content': args.prompt_file.read_text()},
    ],
    'think': False, 'stream': True,
    'options': {'temperature': 0.1, 'seed': 42, 'num_ctx': 16384, 'num_predict': 2000},
    'keep_alive': '10m',
}
(out / 'request.json').write_text(json.dumps(request, indent=2) + '\n')
started = time.monotonic()
receipt = {'started_utc': datetime.now(timezone.utc).isoformat(), 'endpoint': 'http://127.0.0.1:11434/api/chat', 'tools_granted': [], 'status': 'RUNNING'}
parts = []
try:
    req = urllib.request.Request(receipt['endpoint'], data=json.dumps(request).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as response, (out / 'received_stream.jsonl').open('w') as stream:
        for line in response:
            if time.monotonic() - started > 240:
                raise TimeoutError('240-second overall request limit')
            event = json.loads(line)
            if event.get('message', {}).get('thinking'):
                raise RuntimeError('Unexpected reasoning output despite think=false; not retained')
            stream.write(json.dumps(event) + '\n'); stream.flush()
            parts.append(event.get('message', {}).get('content', ''))
            if event.get('done'):
                receipt['completion'] = {k: v for k, v in event.items() if k != 'message'}
                receipt['status'] = 'COMPLETED'
        if receipt['status'] != 'COMPLETED':
            raise RuntimeError('Stream ended without a completion event')
except Exception as exc:
    receipt.update(status='ERROR', error=repr(exc))
finally:
    (out / 'response.txt').write_text(''.join(parts))
    receipt.update(ended_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=round(time.monotonic()-started, 3), response_characters=len(''.join(parts)))
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    (out / 'HASHES.json').write_text(json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name != 'HASHES.json'}, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
raise SystemExit(0 if receipt['status'] == 'COMPLETED' else 1)
