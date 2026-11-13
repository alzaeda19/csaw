"""Run an explicitly provided Yosys verification/synthesis script and save evidence."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
YOSYS = Path('/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/synthesis_fit_timing_2026-11-06/tooling/oss-cad-suite/bin/yosys')
parser = argparse.ArgumentParser()
parser.add_argument('script', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--timeout', type=int, default=180)
parser.add_argument('--yosys', type=Path, default=YOSYS)
args = parser.parse_args()
out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
script = args.script.resolve()
cmd = [str(args.yosys.resolve()), '-T', '-s', str(script)]
receipt = {'argv': cmd, 'cwd': str(ROOT), 'started_utc': datetime.now(timezone.utc).isoformat(), 'script_sha256': hashlib.sha256(script.read_bytes()).hexdigest(), 'timeout_seconds': args.timeout}
started = time.monotonic()
try:
    with (out/'stdout.log').open('w') as stdout, (out/'stderr.log').open('w') as stderr:
        result = subprocess.run(cmd, cwd=ROOT, stdout=stdout, stderr=stderr, timeout=args.timeout)
    receipt['exit_code'] = result.returncode
except subprocess.TimeoutExpired:
    receipt.update(exit_code=124, error='Process exceeded time limit')
finally:
    receipt.update(ended_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=round(time.monotonic()-started, 3))
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt, indent=2))
raise SystemExit(receipt['exit_code'])
