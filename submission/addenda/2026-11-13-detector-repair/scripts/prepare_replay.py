"""Prepare a fresh detector-only replay directory without changing saved evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('destination', type=Path, help='New directory outside the evidence bundle; must not exist')
args = parser.parse_args()
destination = args.destination.expanduser().resolve()
if destination.exists() or destination.is_relative_to(ROOT):
    parser.error('Choose a nonexistent directory outside this evidence bundle')
destination.mkdir(parents=True)
for directory in ['package', 'sources', 'scripts']:
    shutil.copytree(ROOT / directory, destination / directory)
for relative in ['records/INPUT_HASHES.json', 'records/hw2graph_original.py',
                 'tests/original/plain/graph.json', 'detectors/flat_clean/topModule.v',
                 'detectors/flat_modified/topModule.v']:
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / relative, target)
(destination / 'runtime').mkdir()
(destination / 'analysis').mkdir()
initial = json.loads((destination / 'records/INPUT_HASHES.json').read_text())['files']
changed = [relative for relative, expected in initial.items()
           if hashlib.sha256((destination / relative).read_bytes()).hexdigest() != expected]
assert changed == ['package/hw2vec/hw2vec/hw2graph.py'], changed
steps = [
    ['python3', 'scripts/run_python.py', 'final_fixtures', 'scripts/test_extractor.py', '--label', 'final', '--expect-repaired'],
    ['python3', 'scripts/run_python.py', 'target_extraction', 'scripts/extract_targets.py'],
    ['python3', 'scripts/run_python.py', 'repaired_inference', 'scripts/infer_repaired.py'],
]
receipt = {'source': str(ROOT), 'destination': str(destination), 'frozen_inputs_verified': True,
           'known_extractor_change_only': changed, 'models_or_extraction_run': False,
           'baseline_control': 'Preserved original plain-name graph, not rerun by preparation',
           'run_in_destination_in_order': steps}
(destination / 'records/REPLAY_PREPARATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
