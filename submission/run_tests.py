#!/usr/bin/env python3
"""Reproduce the frozen simulation package. Every run retains its own evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def command(argv, cwd, name, timeout):
    r = {'argv': [str(a) for a in argv], 'cwd': str(cwd),
         'start_utc': datetime.now(timezone.utc).isoformat(), 'timeout_seconds': timeout,
         'stdout': str(cwd / (name + '.stdout.log')), 'stderr': str(cwd / (name + '.stderr.log'))}
    started = time.monotonic()
    with open(r['stdout'], 'xb') as out, open(r['stderr'], 'xb') as err:
        p = subprocess.Popen(r['argv'], cwd=cwd, stdout=out, stderr=err, start_new_session=True)
        try:
            r['returncode'] = p.wait(timeout=timeout)
            r['timed_out'] = False
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            os.killpg(p.pid, signal.SIGKILL)
            r.update(returncode=p.wait(), timed_out=isinstance(exc, subprocess.TimeoutExpired),
                     interrupted=isinstance(exc, KeyboardInterrupt))
    r['elapsed_seconds'] = round(time.monotonic() - started, 6)
    save(cwd / (name + '.command.json'), r)
    return r


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-bin', type=Path, help='Directory containing the tested iverilog and vvp.')
    parser.add_argument('--output-root', type=Path, default=ROOT / 'runs')
    args = parser.parse_args()
    output = args.output_root.expanduser().resolve()
    if any((p / '.git').exists() for p in [output, *output.parents]):
        parser.error('Select an output directory outside a Git repository.')
    output.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ_'), dir=output))
    result = {'status': 'RUNNING', 'run_dir': str(run), 'cases': [], 'versions': [], 'source_checks': {}}
    print('Evidence folder: ' + str(run), flush=True)
    save(run / 'result.json', result)
    try:
        pins = json.loads((ROOT / 'SOURCE_HASHES.json').read_text())
        for name, expected in pins.items():
            actual = sha(ROOT / name)
            result['source_checks'][name] = {'expected': expected, 'actual': actual, 'matches': actual == expected}
            if actual != expected:
                raise RuntimeError('Source hash mismatch: ' + name)
        executables = {}
        for name in ['iverilog', 'vvp']:
            candidate = str(args.tool_bin / name) if args.tool_bin else shutil.which(name)
            if not candidate or not Path(candidate).is_file():
                raise RuntimeError('Missing tool: ' + name)
            executables[name] = str(Path(candidate).resolve())
            r = command([executables[name], '-V'], run, name + '_version', 20)
            result['versions'].append(r)
            if r['returncode'] != 0 or r['timed_out']:
                raise RuntimeError('Tool version query failed: ' + name)
        normal_args = ['+half_ps=500000', '+sample_ps=1000', '+immediate=0', '+pauses=0']
        cases = [
            ('baseline_normal', 'paired_normal_tb', 'reference/paired_normal_tb.sv', 'reference/baseline_protocol_dut.sv', None, normal_args),
            ('modified_normal', 'paired_normal_tb', 'reference/paired_normal_tb.sv', 'rtl/modified_protocol_dut.sv', None, normal_args),
            ('demonstration', 'demo_tb', 'tb/demo_tb.sv', 'rtl/modified_protocol_dut.sv', None, []),
            ('negative_no_fault', 'demo_tb', 'tb/demo_tb.sv', 'rtl/modified_protocol_dut.sv', 'no_fault', []),
            ('negative_always_fault', 'demo_tb', 'tb/demo_tb.sv', 'rtl/modified_protocol_dut.sv', 'always_fault', []),
        ]
        for label, top, tb_name, rtl_name, mutation, plusargs in cases:
            folder = run / label
            folder.mkdir()
            src = folder / 'sources'
            src.mkdir()
            for rel in ['rtl/baseline.v', 'rtl/cells_sim.v', rtl_name, tb_name]:
                shutil.copyfile(ROOT / rel, src / Path(rel).name)
            wrapper = src / Path(rtl_name).name
            if mutation:
                source = wrapper.read_text()
                replacement = 'assign MISO = raw_miso;' if mutation == 'no_fault' else 'assign MISO = ~raw_miso;'
                source, count = re.subn(r'assign MISO = raw_miso \^ \(fault_active && !NORM_CS_N && read_count == 6\x27d1\);', replacement, source)
                if count != 1:
                    raise RuntimeError('Negative-control mutation anchor must match exactly once.')
                wrapper.write_text(source)
            compile_argv = [executables['iverilog'], '-g2012', '-DNO_ICE40_DEFAULT_ASSIGNMENTS', '-Wall',
                            '-s', top, '-o', str(folder / 'sim.vvp'), str(src / Path(tb_name).name),
                            str(src / 'baseline.v'), str(wrapper), str(src / 'cells_sim.v')]
            compiled = command(compile_argv, folder, 'compile', 60)
            case = {'name': label, 'negative_control': bool(mutation), 'compile': compiled,
                    'source_hashes': {p.name: sha(p) for p in src.iterdir()}, 'meets_expectation': False}
            if compiled['returncode'] == 0 and not compiled['timed_out']:
                simulated = command([executables['vvp'], '-n', str(folder / 'sim.vvp'), *plusargs], folder, 'simulate', 60)
                case['simulate'] = simulated
                text = Path(simulated['stdout']).read_text(errors='replace')
                summaries = re.findall(r'^COMPLETE (.+)$', text, re.M)
                case['summary_lines'] = summaries
                values = dict((k, int(v)) for k, v in re.findall(r'(\w+)=(\d+)', summaries[0])) if len(summaries) == 1 else {}
                case['counts'] = values
                if mutation:
                    case['meets_expectation'] = (not simulated['timed_out'] and simulated['returncode'] != 0
                                                 and values.get('failures', 0) > 0)
                elif top == 'paired_normal_tb':
                    case['meets_expectation'] = (simulated['returncode'] == 0 and not simulated['timed_out']
                        and values == {'transactions': 88, 'checks': 6726, 'failures': 0})
                else:
                    case['meets_expectation'] = (simulated['returncode'] == 0 and not simulated['timed_out']
                        and values == {'checks': 39718, 'failures': 0, 'reads': 120, 'normal_reads': 114,
                                       'fault_reads': 6, 'known_operations': 10, 'expected_flips': 7, 'observed_flips': 7}
                        and all((folder / n).is_file() and (folder / n).stat().st_size > 0 for n in ['demo_trace.csv', 'demo_pins.vcd']))
            save(folder / 'RESULT.json', case)
            result['cases'].append(case)
            save(run / 'result.json', result)
            print(label + ': ' + ('EXPECTED OUTCOME VERIFIED' if case['meets_expectation'] else 'FAIL'), flush=True)
        result['sources_preserved'] = all(sha(ROOT / name) == value for name, value in pins.items())
        result['status'] = 'PASS' if result['sources_preserved'] and all(c['meets_expectation'] for c in result['cases']) else 'FAIL'
    except Exception as exc:
        result['status'], result['error'] = 'ERROR', repr(exc)
    result['finished_utc'] = datetime.now(timezone.utc).isoformat()
    save(run / 'result.json', result)
    print('Overall: ' + result['status'])
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
