#!/usr/bin/env python3
"""Run only the four hash-verified professor-supplied clean AES source files."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import re
import subprocess

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / 'source-manifest.json').read_text())
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for entry in manifest['files']:
    if digest(ROOT / entry['path']) != entry['sha256']:
        raise SystemExit('Source integrity check failed: ' + entry['path'])

run = ROOT / 'runs' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
run.mkdir(parents=True)
# Deliberately do not inherit credentials, Python paths, or notebook configuration.
env = {'PATH': '/opt/homebrew/bin:/usr/bin:/bin', 'TMPDIR': str(run), 'LC_ALL': 'C'}
tools = {'iverilog': Path('/opt/homebrew/bin/iverilog'), 'vvp': Path('/opt/homebrew/bin/vvp')}
records = []
def command(label, args):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        p = subprocess.run(list(map(str, args)), cwd=run, env=env,
                           capture_output=True, text=True, timeout=30)
        code, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        code = 124
        out, err = exc.stdout or b'', exc.stderr or b''
        out = out.decode(errors='replace') if isinstance(out, bytes) else out
        err = err.decode(errors='replace') if isinstance(err, bytes) else err
    (run / (label + '.stdout')).write_text(out)
    (run / (label + '.stderr')).write_text(err)
    records.append({'label': label, 'argv': list(map(str, args)), 'cwd': str(run),
                    'start_utc': started, 'end_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'exit_code': code, 'stdout_sha256': digest(run / (label + '.stdout')),
                    'stderr_sha256': digest(run / (label + '.stderr'))})
    (run / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
    return code, out

tool_record = {name: {'path': str(path), 'resolved_path': str(path.resolve()), 'sha256': digest(path)}
               for name, path in tools.items()}
(run / 'environment.json').write_text(json.dumps({'host': platform.platform(), 'machine': platform.machine(),
    'tools': tool_record, 'environment': env}, indent=2) + '\n')
for name, path in tools.items():
    command(name + '_version', [path, '-V'])
design = ROOT / 'sources/designs/aes_128'
rc, _ = command('compile', [tools['iverilog'], '-g2012', '-s', 'test_aes_128', '-I', design,
    '-o', run / 'clean_aes.vvp', design / 'aes_128.v', ROOT / 'sources/testbenches/tb_aes_128.v'])
result = {'scope': 'Unmodified supplied clean AES functional testbench only', 'compile_exit': rc, 'pass': False}
if rc == 0:
    sim_rc, out = command('simulate', [tools['vvp'], run / 'clean_aes.vvp'])
    passes = re.findall(r'^\[PASS\] Test (\d+):', out, re.M)
    fails = re.findall(r'^\[FAIL\]', out, re.M)
    result.update({'simulation_exit': sim_rc, 'pass_count': len(passes), 'fail_count': len(fails)})
    result['pass'] = (sim_rc == 0 and passes == ['1', '2', '3', '4', '5'] and not fails
                      and 'PASSES: 5' in out and 'FAILS : 0' in out)
result['sources_unchanged'] = all(digest(ROOT / e['path']) == e['sha256'] for e in manifest['files'])
result['pass'] = result['pass'] and result['sources_unchanged']
(run / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'run': str(run), **result}, indent=2))
raise SystemExit(0 if result['pass'] else 1)
