"""Copy fixed inputs into a new directory; do not overwrite archived results."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('destination', type=Path)
args = parser.parse_args()
destination = args.destination.expanduser().resolve()
if destination.exists() or destination.is_relative_to(ROOT):
    parser.error('Choose a nonexistent directory outside this evidence bundle')
destination.mkdir(parents=True)
for name in ['package', 'inputs', 'scripts']:
    shutil.copytree(ROOT / name, destination / name)
for name in ['records', 'runs', 'runtime', 'analysis', 'ai_logs']:
    (destination / name).mkdir()
for name in ['INPUT_MANIFEST.json', 'inference_inputs.json', 'DATASET_MANIFEST.json',
             'previous_csaw_scores.json', 'expected_feature_vocabulary.json']:
    shutil.copy2(ROOT / 'records' / name, destination / 'records' / name)
shutil.copytree(ROOT / 'records/prior_toy_run', destination / 'records/prior_toy_run')
shutil.copy2(ROOT / 'TEST_PLAN.md', destination / 'TEST_PLAN.md')
expected = json.loads((destination / 'records/INPUT_MANIFEST.json').read_text())['files']
for relative, digest in expected.items():
    assert hashlib.sha256((destination / relative).read_bytes()).hexdigest() == digest, relative
receipt = {'source': str(ROOT), 'destination': str(destination), 'input_files_verified': len(expected),
           'models_or_hdl_executed': False,
           'next_commands_in_destination': ['python3 scripts/run_investigation.py', 'python3 scripts/analyze_results.py'],
           'environment': 'Set CSAW_DETECTOR_PYTHON and CSAW_TOOL_SUITE to compatible local tools'}
(destination / 'records/REPLAY_PREPARATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
