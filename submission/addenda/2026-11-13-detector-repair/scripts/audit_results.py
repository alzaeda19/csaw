"""Read-only audit of saved graphs, fixed inputs, components and model results."""
from pathlib import Path
import collections
import hashlib
import json
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]

def read(relative):
    return json.loads((ROOT / relative).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

freeze = read('records/INFERENCE_FREEZE.json')
for relative, digest in freeze['files'].items():
    assert sha(ROOT / relative) == digest, relative
initial = read('records/INPUT_HASHES.json')['files']
changed = [p for p, digest in initial.items() if sha(ROOT / p) != digest]
assert changed == ['package/hw2vec/hw2vec/hw2graph.py'], changed
results = read('analysis/inference/RESULTS.json')
assert results['checkpoint_candidate_classifications'] == 8
assert not results['detector_or_design_tuning'] and not results['model_training']
audits = []
for name in ['flat_clean', 'flat_modified']:
    folder = 'detectors/repaired_' + name
    raw = read(folder + '/graph_before_normalization.json')
    coverage = read(folder + '/SYMBOL_COVERAGE.json')
    graph = nx.DiGraph()
    graph.add_nodes_from((item['id'], item) for item in raw['nodes'])
    graph.add_edges_from(raw['edges'])
    roots = coverage['definition_roots']
    components = sorted(nx.weakly_connected_components(graph), key=lambda c: (-len(c), sorted(c)))
    detail = []
    for component in components:
        labels = collections.Counter(str(graph.nodes[n].get('label', '')) for n in component)
        detail.append({'nodes': len(component), 'edges': graph.subgraph(component).number_of_edges(),
                       'output_roots': [key for key in ['top.MISO', 'top.BUSY', 'top.ICE_LED'] if roots[key] in component],
                       'definitions': sorted(key for key, node in roots.items() if node in component),
                       'labels': dict(labels) if len(component) < 10 else {'omitted_large_component': len(component)}})
    vocabulary = read(folder + '/feature_vocabulary.json')
    other = 'flat_modified' if name == 'flat_clean' else 'flat_clean'
    assert vocabulary == read('detectors/repaired_' + other + '/feature_vocabulary.json')
    scores = next(run['scores'] for run in results['runs'] if run['candidate'] == name)
    audits.append({'candidate': name, 'component_count': len(components), 'components': detail,
                   'model_outcomes': {model: ('true_positive' if score['prediction'] else 'false_negative')
                                      if name == 'flat_modified' else ('false_positive' if score['prediction'] else 'true_negative')
                                      for model, score in scores.items()},
                   'vocabulary_sha256': sha(ROOT / folder / 'feature_vocabulary.json')})
out = {'all_pre_inference_freeze_hashes_unchanged': True, 'frozen_file_count': len(freeze['files']),
       'changed_initial_inputs': changed, 'same_vocabulary_both_candidates': True,
       'new_model_runs_performed_by_this_audit': 0, 'candidates': audits,
       'limits': 'One labeled pair, fixed checkpoints, dependency graph abstraction; no estimated general accuracy or calibrated security probabilities.'}
(ROOT / 'analysis/FINAL_AUDIT.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({'freeze_verified': True, 'changed_initial_inputs': changed, 'components': [
    {'candidate': item['candidate'], 'sizes': dict(collections.Counter(c['nodes'] for c in item['components'])),
     'small_components': item['components'][1:4], 'model_outcomes': item['model_outcomes']}
    for item in audits]}, indent=2))
