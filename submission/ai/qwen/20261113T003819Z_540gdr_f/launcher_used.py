#!/usr/bin/env python3
"""Project-local Qwen coding interface, with restricted file tools and durable logs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parent
WORK = ROOT / 'work'
CONFIG = json.loads((ROOT / 'config/agent.json').read_text())


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def inventory():
    return {str(p.relative_to(WORK)): {'bytes': p.stat().st_size, 'sha256': sha(p)}
            for p in sorted(WORK.rglob('*')) if p.is_file() and not p.is_symlink()}


def save(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.replace(path)


def run_turn(prompt, session_id, resume=False, timeout=600):
    turn = Path(tempfile.mkdtemp(prefix=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ_'),
                                 dir=ROOT / 'ai_logs'))
    (turn / 'prompt.txt').write_text(prompt + '\n')
    for name in ['agent.json', 'agent.sb', 'settings.json', 'empty-mcp.json', 'system_prompt.txt', 'Modelfile']:
        shutil.copyfile(ROOT / 'config' / name, turn / name)
    shutil.copyfile(Path(__file__).resolve(), turn / 'launcher_used.py')
    system = (ROOT / 'config/system_prompt.txt').read_text()
    debug = ROOT / 'runtime' / (turn.name + '.debug.log')
    live = ROOT / 'runtime' / turn.name
    live.mkdir()
    env = {
        'HOME': os.environ['HOME'],
        'USER': os.environ.get('USER', 'al-zayedal-hassan'),
        'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',
        'LANG': 'en_US.UTF-8',
        'TMPDIR': str(ROOT / 'runtime/tmp'),
        'ANTHROPIC_BASE_URL': CONFIG['endpoint'],
        'ANTHROPIC_API_KEY': 'ollama',
        'ANTHROPIC_AUTH_TOKEN': 'ollama',
        'ANTHROPIC_DEFAULT_SONNET_MODEL': CONFIG['model'],
        'ANTHROPIC_DEFAULT_OPUS_MODEL': CONFIG['model'],
        'ANTHROPIC_DEFAULT_HAIKU_MODEL': CONFIG['model'],
        'CLAUDE_CONFIG_DIR': str(ROOT / 'runtime/native-config'),
        'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC': '1',
        'DISABLE_AUTOUPDATER': '1',
        'CLAUDE_CODE_MAX_OUTPUT_TOKENS': '8192',
        'MAX_THINKING_TOKENS': '0',
        'NO_PROXY': '127.0.0.1,localhost',
    }
    argv = ['/usr/bin/sandbox-exec', '-f', str(ROOT / 'config/agent.sb'),
            CONFIG['claude'], '--safe-mode', '--setting-sources', '',
            '--settings', str(ROOT / 'config/settings.json'),
            '--strict-mcp-config', '--mcp-config', str(ROOT / 'config/empty-mcp.json'),
            '--disable-slash-commands', '--no-chrome',
            '--tools', 'Read,Edit,Write,Glob,Grep', '--permission-mode', 'dontAsk',
            '--allowedTools', *[name + '(/' + str(WORK) + '/**)'
                                 for name in ['Read', 'Edit', 'Write', 'Glob', 'Grep']],
            '--system-prompt', system, '--model', CONFIG['model'],
            '--resume' if resume else '--session-id', session_id,
            '--print', '--verbose', '--output-format', 'stream-json',
            '--include-partial-messages', '--debug-file', str(debug)]
    record = {'start_utc': now(), 'status': 'RUNNING', 'session_id': session_id,
              'resume': resume, 'model': CONFIG['model'], 'cwd': str(WORK),
              'argv': argv, 'environment': env, 'before': inventory(),
              'timeout_seconds': timeout, 'process_returncode': None}
    save(turn / 'receipt.json', record)
    print('\nQwen working folder: ' + str(WORK), flush=True)
    print('Interaction logs: ' + str(turn), flush=True)
    started = time.monotonic()
    exit_code = 1
    process = None
    try:
        # Bun inspects stdout during startup; its live descriptors must lie within
        # the child's allowed runtime area. The parent snapshots them into ai_logs.
        with (live / 'stdout.stream.jsonl').open('xb') as out, (live / 'stderr.log').open('xb') as err:
            process = subprocess.Popen(argv, cwd=WORK, env=env, stdin=subprocess.PIPE,
                                       stdout=out, stderr=err, start_new_session=True)
            try:
                process.communicate(input=(prompt + '\n').encode(), timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
                record['status'] = 'TIMEOUT' if isinstance(exc, subprocess.TimeoutExpired) else 'INTERRUPTED'
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                exit_code = 124 if record['status'] == 'TIMEOUT' else 130
            record['process_returncode'] = process.returncode
        for name in ['stdout.stream.jsonl', 'stderr.log']:
            shutil.copyfile(live / name, turn / name)
        events, malformed = [], 0
        for line in (turn / 'stdout.stream.jsonl').read_text(errors='replace').splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                malformed += 1
        results = [e for e in events if e.get('type') == 'result']
        calls = []
        tool_errors = []
        for event in events:
            if event.get('type') == 'assistant':
                for item in event.get('message', {}).get('content', []):
                    if item.get('type') == 'tool_use':
                        calls.append({'name': item.get('name'), 'input': item.get('input'), 'id': item.get('id')})
            if event.get('type') == 'user':
                for item in event.get('message', {}).get('content', []):
                    if item.get('type') == 'tool_result' and item.get('is_error'):
                        tool_errors.append(item)
        record.update(tool_calls=calls, malformed_stdout_lines=malformed,
                      tool_errors=tool_errors, final_result=results[-1] if results else None)
        if record['status'] == 'RUNNING':
            ok = process.returncode == 0 and bool(results) and not results[-1].get('is_error', False)
            record['status'] = ('RESPONSE_WITH_TOOL_ERRORS' if tool_errors else 'RESPONSE_COMPLETED') if ok else 'FAILED'
            exit_code = (2 if tool_errors else 0) if ok else (process.returncode or 1)
        if results:
            response = results[-1].get('result', '')
            (turn / 'response.txt').write_text(response + '\n')
            print(response, flush=True)
        else:
            print('No completed response. Inspect the retained stream and error log.', flush=True)
        if process.returncode:
            print((turn / 'stderr.log').read_text(errors='replace')[-3000:], flush=True)
    except Exception as exc:
        record['status'], record['error'], exit_code = 'ERROR', repr(exc), 1
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        print(str(exc), file=sys.stderr)
    finally:
        for name in ['stdout.stream.jsonl', 'stderr.log']:
            if (live / name).is_file():
                shutil.copyfile(live / name, turn / name)
        record.update(end_utc=now(), elapsed_seconds=round(time.monotonic() - started, 3),
                      exit_code=exit_code, after=inventory())
        record['changed_paths'] = sorted(k for k in set(record['before']) | set(record['after'])
                                         if record['before'].get(k) != record['after'].get(k))
        if debug.is_file():
            shutil.copyfile(debug, turn / 'debug.log')
        # Preserve a snapshot of this session's authentic native transcript, if available.
        transcripts = []
        for path in (ROOT / 'runtime/native-config').rglob(session_id + '.jsonl'):
            if path.is_file():
                target = turn / ('native-session-' + str(len(transcripts)) + '.jsonl')
                shutil.copyfile(path, target)
                transcripts.append({'source': str(path), 'copy': str(target), 'sha256': sha(target)})
        record['native_transcripts'] = transcripts
        save(turn / 'receipt.json', record)
        save(turn / 'HASHES.json', {p.name: sha(p) for p in turn.iterdir()
                                    if p.is_file() and p.name != 'HASHES.json'})
    print('Status: ' + record['status'] + '; changed paths: ' + ', '.join(record['changed_paths']), flush=True)
    return exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prompt-file', type=Path, help='Run one task from a text file.')
    parser.add_argument('--timeout', type=float, default=600)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 3600:
        parser.error('--timeout must be between 1 and 3600 seconds')
    session = str(uuid.uuid4())
    if args.prompt_file:
        return run_turn(args.prompt_file.read_text(), session, timeout=args.timeout)
    print('Local Qwen coding assistant. Editable project copy:\n' + str(WORK))
    print('Type a task and press Enter. /paste accepts multiple lines ending with /send.')
    print('/new starts a fresh conversation; /quit exits. All turns are recorded.')
    resume = False
    while True:
        try:
            prompt = input('\nYou: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nSession closed. Logs are preserved.')
            return 0
        if prompt == '/quit':
            return 0
        if prompt == '/new':
            session, resume = str(uuid.uuid4()), False
            print('Fresh conversation started.')
            continue
        if prompt == '/paste':
            print('Paste your task; put /send on its own line when done.')
            lines = []
            while True:
                line = input()
                if line == '/send':
                    break
                lines.append(line)
            prompt = '\n'.join(lines)
        if not prompt:
            continue
        code = run_turn(prompt, session, resume=resume, timeout=args.timeout)
        resume = code in (0, 2)
        if not resume:
            session = str(uuid.uuid4())
            print('The next task will start fresh; failed interaction logs remain saved.')


if __name__ == '__main__':
    sys.exit(main())
