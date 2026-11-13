"""Bounded evaluation controller; truth labels are joined after worker inference."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import collections
import csv
import hashlib
import json
import os
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
PYTHON = os.environ.get('CSAW_DETECTOR_PYTHON', '/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runtime/venv/bin/python')
SUITE = os.environ.get('CSAW_TOOL_SUITE', '/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/synthesis_fit_timing_2026-11-06/tooling/oss-cad-suite/bin')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def run_one(ident):
    record = ROOT / 'records' / ident
    record.mkdir()
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg', PYTHONPATH=str(ROOT / 'package/hw2vec'), PATH=SUITE + ':' + env.get('PATH', ''))
    for key, sub in [('TMPDIR', 'tmp'), ('MPLCONFIGDIR', 'mpl'), ('XDG_CACHE_HOME', 'cache')]:
        folder = ROOT / 'runtime' / ident / sub
        folder.mkdir(parents=True)
        env[key] = str(folder)
    command = [PYTHON, str(ROOT / 'scripts/evaluate_one.py'), ident]
    start = time.monotonic()
    reason, peak = None, 0
    with (record / 'stdout.txt').open('w') as stdout, (record / 'stderr.txt').open('w') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            while process.poll() is None:
                snapshot = subprocess.run(['/bin/ps', '-axo', 'pgid=,rss='], capture_output=True, text=True, timeout=3, check=True)
                rss = sum(int(parts[1]) for line in snapshot.stdout.splitlines()
                          if len(parts := line.split()) == 2 and int(parts[0]) == process.pid)
                peak = max(peak, rss)
                if rss > 2097152:
                    reason = 'sampled_process_group_memory_above_2GiB'
                    break
                if time.monotonic() - start > 90:
                    reason = 'worker_wall_limit_90_seconds'
                    break
                time.sleep(0.2)
        except BaseException as error:
            reason = 'monitor_failure: ' + repr(error)
        finally:
            if reason:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            code = process.wait()
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    receipt = {'command': command, 'cwd': str(ROOT), 'exit_code': code, 'parent_failure': reason,
               'seconds': time.monotonic() - start, 'peak_sampled_rss_kib': peak,
               'rss_limit_is_sampled_not_kernel_enforced': True}
    save(record / 'COMMAND.json', receipt)
    result = ROOT / 'runs' / ident / 'RESULTS.json'
    if code == 0 and reason is None and result.exists():
        outcome = json.loads(result.read_text())
    else:
        failure = ROOT / 'runs' / ident / 'FAILURE.json'
        outcome = json.loads(failure.read_text()) if failure.exists() else {'design_id': ident, 'status': 'unscored', 'error': reason or 'missing successful result'}
        outcome['status'] = 'unscored'
    save(record / 'OUTCOME.json', outcome)
    print(json.dumps({'design_id': ident, 'status': outcome['status'], 'seconds': round(receipt['seconds'], 2), 'error': outcome.get('error')}), flush=True)
    return outcome

if __name__ == '__main__':
    manifest = json.loads((ROOT / 'records/INPUT_MANIFEST.json').read_text())
    for relative, digest in manifest['files'].items():
        assert sha(ROOT / relative) == digest, relative
    frozen = {'frozen_utc': datetime.now(timezone.utc).isoformat(),
              'files': {str(path.relative_to(ROOT)): sha(path) for path in [ROOT / 'TEST_PLAN.md', ROOT / 'scripts/evaluate_one.py', Path(__file__), ROOT / 'records/INPUT_MANIFEST.json']},
              'input_manifest_sha256': sha(ROOT / 'records/INPUT_MANIFEST.json'), 'inference_has_not_run': True}
    with (ROOT / 'records/EXPERIMENT_FREEZE.json').open('x') as output:
        json.dump(frozen, output, indent=2)
    identities = [row['design_id'] for row in json.loads((ROOT / 'records/inference_inputs.json').read_text())['inputs']]
    assert len(identities) == len(set(identities)) == 23
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(run_one, identities + ['flat_clean', 'flat_modified']))
    truth = {row['design_id']: row for row in json.loads((ROOT / 'records/DATASET_MANIFEST.json').read_text())['designs']}
    dataset = [row for row in outcomes if row['design_id'] in truth]
    for row in dataset:
        row['supplied_truth'] = truth[row['design_id']]['truth']
        row['source_design_name'] = truth[row['design_id']]['design']
    metrics = {}
    for model in ['HT1', 'HT2', 'HT3', 'HT4', 'ensemble']:
        counts = collections.Counter(TP=0, FN=0, FP=0, TN=0, unscored_positive=0, unscored_negative=0)
        for row in dataset:
            actual = row['supplied_truth']
            if row['status'] != 'scored':
                counts['unscored_positive' if actual else 'unscored_negative'] += 1
                continue
            prediction = row['ensemble']['prediction'] if model == 'ensemble' else row['scores'][model]['prediction']
            counts['TP' if actual and prediction else 'FN' if actual else 'FP' if prediction else 'TN'] += 1
        metrics[model] = dict(counts)
    result = {'completed_utc': datetime.now(timezone.utc).isoformat(), 'dataset_total': 23,
              'dataset_scored': sum(row['status'] == 'scored' for row in dataset),
              'dataset_unscored': sum(row['status'] != 'scored' for row in dataset),
              'metrics': metrics, 'dataset': dataset,
              'csaw_diagnostic_replays': [row for row in outcomes if row['design_id'] not in truth],
              'limits': ['Supplied directory labels, not independently simulated behavior', 'Unknown checkpoint training overlap; not held-out accuracy', 'Repeated circuit families', 'Dependency abstraction only; no full temporal/physical proof', 'No hardware/model/threshold changes or training']}
    save(ROOT / 'analysis/RESULTS.json', result)
    rows = []
    for row in dataset:
        for model in ['HT1', 'HT2', 'HT3', 'HT4']:
            score = row.get('scores', {}).get(model, {})
            rows.append({'design_id': row['design_id'], 'design': row['source_design_name'], 'supplied_truth': row['supplied_truth'],
                         'status': row['status'], 'model': model, 'prediction': score.get('prediction'),
                         'prob_trojan': score.get('prob_trojan'), 'error': row.get('error', '')})
    with (ROOT / 'analysis/PER_DESIGN.csv').open('w', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({'dataset_scored': result['dataset_scored'], 'dataset_unscored': result['dataset_unscored'], 'metrics': metrics}, indent=2), flush=True)
