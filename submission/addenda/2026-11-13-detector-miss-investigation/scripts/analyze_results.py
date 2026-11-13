"""Summarize frozen results without rerunning or changing a model."""
from pathlib import Path
import collections
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]

def load(relative):
    return json.loads((ROOT / relative).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

inputs = load('records/INPUT_MANIFEST.json')
for relative, digest in inputs['files'].items():
    assert sha(ROOT / relative) == digest, relative
for relative, digest in load('records/EXPERIMENT_FREEZE.json')['files'].items():
    assert sha(ROOT / relative) == digest, relative
result = load('analysis/RESULTS.json')
dataset = result['dataset']
assert len(dataset) == 23 and collections.Counter(row['supplied_truth'] for row in dataset) == {0: 9, 1: 14}
pair = {row['design_id']: row for row in result['csaw_diagnostic_replays']}
assert set(pair) == {'flat_clean', 'flat_modified'}
assert all(row['status'] == 'scored' and row['prior_logits_exactly_reproduced'] for row in pair.values())
assert pair['flat_clean']['input_sha256'] != pair['flat_modified']['input_sha256']
diagnostic = {}
for name in ['HT1', 'HT2', 'HT3', 'HT4']:
    clean = pair['flat_clean']['scores'][name]
    modified = pair['flat_modified']['scores'][name]
    diagnostic[name] = {
        'clean_prediction': clean['prediction'], 'modified_prediction': modified['prediction'],
        'clean_class1_score': clean['prob_trojan'], 'modified_class1_score': modified['prob_trojan'],
        'logits_identical': clean['logits'] == modified['logits'],
        'stage_comparison': {stage: {
            'shape_equal': clean['stages'][stage]['shape'] == modified['stages'][stage]['shape'],
            'bytes_equal': clean['stages'][stage]['sha256'] == modified['stages'][stage]['sha256'],
            'clean_nonzero': clean['stages'][stage]['nonzero'],
            'modified_nonzero': modified['stages'][stage]['nonzero'],
        } for stage in clean['stages']},
        'clean_logits_equal_output_bias': clean['logits_equal_output_bias'],
        'modified_logits_equal_output_bias': modified['logits_equal_output_bias'],
    }
prior = load('records/prior_toy_run/RESULTS.json')['designs']
prior = {row['design_id']: row for row in prior}
comparisons, details = {}, {}
scored = [row for row in dataset if row['status'] == 'scored']
for model in ['HT1', 'HT2', 'HT3', 'HT4']:
    old_counts = collections.Counter(TP=0, FN=0, FP=0, TN=0)
    changes = []
    for row in scored:
        old = prior[row['design_id']]['per_model'][model]['prediction']
        actual = row['supplied_truth']
        old_counts['TP' if actual and old else 'FN' if actual else 'FP' if old else 'TN'] += 1
        new = row['scores'][model]['prediction']
        if old != new:
            changes.append({'design_id': row['design_id'], 'design': row['source_design_name'], 'old': old, 'new': new})
    comparisons[model] = {'prior_counts_on_same_scored_subset': dict(old_counts),
                           'current_counts': result['metrics'][model], 'prediction_changes': changes}
    details[model] = {
        'missed_infected_designs': [row['source_design_name'] for row in scored if row['supplied_truth'] == 1 and row['scores'][model]['prediction'] == 0],
        'falsely_flagged_clean_designs': [row['source_design_name'] for row in scored if row['supplied_truth'] == 0 and row['scores'][model]['prediction'] == 1],
        'distinct_logit_vectors_on_scored_examples': len({tuple(row['scores'][model]['logits']) for row in scored}),
        'readout_all_zero_count': sum(row['scores'][model]['stages']['readout']['nonzero'] == 0 for row in scored),
    }
failures = []
for row in dataset:
    if row['status'] == 'scored':
        continue
    file = ROOT / 'runs' / row['design_id'] / 'SYMBOL_COVERAGE.json'
    coverage = json.loads(file.read_text()) if file.exists() else {}
    failures.append({'design_id': row['design_id'], 'design': row['source_design_name'],
                     'supplied_truth': row['supplied_truth'], 'error': row.get('error'),
                     'unbound_noninput_references': coverage.get('unbound_noninput_references', [])})
identities = [load('runs/' + row['design_id'] + '/MODEL_IDENTITIES.json') for row in scored + list(pair.values())]
assert all(identity == identities[0] for identity in identities)
for row in scored + list(pair.values()):
    assert row['truth_label_read_by_worker'] is False and row['model_training'] is False
    assert load('runs/' + row['design_id'] + '/COVERAGE_GATE.json')['status'] == 'PASS'
report = {'frozen_inputs_and_scripts_unchanged': True, 'model_identities_identical_all_scored_runs': True,
          'csaw_pair_input_hashes_different': True, 'all_8_csaw_logits_exactly_reproduced': True,
          'csaw_diagnostics': diagnostic, 'dataset_total': 23, 'dataset_scored': len(scored),
          'scored_positive': sum(row['supplied_truth'] == 1 for row in scored),
          'scored_negative': sum(row['supplied_truth'] == 0 for row in scored),
          'current_metrics': result['metrics'], 'per_model_details': details,
          'prior_comparison_same_subset': comparisons, 'unscored': failures,
          'successful_model_classifications': 4 * (len(scored) + len(pair)),
          'new_inference_performed_by_analysis': False,
          'limits': result['limits']}
(ROOT / 'analysis/FINDINGS.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: report[key] for key in ['dataset_total', 'dataset_scored', 'scored_positive', 'scored_negative', 'current_metrics', 'csaw_diagnostics', 'unscored']}, indent=2))
