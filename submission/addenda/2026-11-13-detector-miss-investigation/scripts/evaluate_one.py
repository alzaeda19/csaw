"""Fixed-model reliability check; HDL is parsed, never simulated or executed."""
from pathlib import Path
import collections
import contextlib
import hashlib
import json
import os
import re
import resource
import signal
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
IDENT = sys.argv[1]
assert re.fullmatch(r'design_\d{3}|flat_clean|flat_modified', IDENT)
OUT = ROOT / 'runs' / IDENT

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

def main():
    OUT.mkdir()
    os.chdir(OUT)
    for kind, value in [(resource.RLIMIT_CPU, 75), (resource.RLIMIT_FSIZE, 134217728), (resource.RLIMIT_CORE, 0)]:
        hard = resource.getrlimit(kind)[1]
        limit = value if hard == resource.RLIM_INFINITY else min(value, hard)
        resource.setrlimit(kind, (limit, limit))
    expected = json.loads((ROOT / 'records/INPUT_MANIFEST.json').read_text())['files']
    for relative, digest in expected.items():
        if relative.startswith('package/'):
            assert sha(ROOT / relative) == digest, relative
    sys.path.insert(0, str(ROOT / 'package/hw2vec'))
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import networkx as nx
    import numpy
    import torch_geometric
    import pyverilog
    from torch_geometric.data import Data
    from torch_geometric.loader import DataLoader
    from hw2vec.config import Config
    from hw2vec.hw2graph import DFGGenerator, DataProcessor
    from hw2vec.graph2vec.models import GRAPH2VEC, GRAPH_CONV, GRAPH_POOL, GRAPH_READOUT

    torch.manual_seed(0)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    cfg = Config(['--yaml_path', str(ROOT / 'package/hw2vec/examples/example_gnn4tj.yaml'),
                  '--data_pkl_path', str(ROOT / 'runtime/UNUSED.pkl'), '--graph_type', 'DFG',
                  '--model_path', '', '--device', 'cpu'])
    cfg.num_feature_dim = 37
    processor = DataProcessor(cfg)
    vocabulary = json.loads((ROOT / 'records/expected_feature_vocabulary.json').read_text())
    assert processor.global_type2idx_DFG == vocabulary
    save('VERSIONS.json', {'python': sys.version, 'torch': torch.__version__, 'numpy': numpy.__version__,
                          'torch_geometric': torch_geometric.__version__, 'networkx': nx.__version__,
                          'pyverilog': pyverilog.__version__})
    if IDENT.startswith('design_'):
        entries = json.loads((ROOT / 'records/inference_inputs.json').read_text())['inputs']
        row = next(item for item in entries if item['design_id'] == IDENT)
        assert set(row) == {'design_id', 'source_path', 'sha256'}
        source = ROOT / row['source_path']
        assert sha(source) == row['sha256'] == expected[row['source_path']]
        generator = DFGGenerator()
        def deadline(*_):
            raise TimeoutError('45-second exact extraction deadline; no fallback')
        old = signal.signal(signal.SIGALRM, deadline)
        signal.setitimer(signal.ITIMER_REAL, 45)
        started = time.monotonic()
        try:
            with (OUT / 'extraction.stdout').open('w') as stdout, (OUT / 'extraction.stderr').open('w') as stderr, contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                graph = generator.process(source)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)
        coverage = generator.last_report
        save('SYMBOL_COVERAGE.json', coverage)
        assert not coverage['ambiguous_labels'], 'ambiguous symbols'
        assert not coverage['unresolved_bound_references'], 'unresolved bound references'
        assert not coverage['unbound_noninput_references'], 'unexpected unbound non-input references'
        assert 1 < len(graph) < 100000 and graph.number_of_edges() > 0, 'invalid graph size'
        roots = coverage['definition_roots']
        assert all(node in graph for node in roots.values())
        for joined in coverage['joined_references']:
            assert joined['reference_node'] not in graph
            assert all(graph.has_edge(parent, joined['definition_node']) for parent in joined['parents'])
        outputs = {}
        for name, symbol in coverage['symbols'].items():
            if 'Output' in symbol['term_types'] and name in roots:
                outputs[name] = len(nx.descendants(graph, roots[name]))
        assert outputs and all(count > 0 for count in outputs.values()), 'empty bound output dependency'
        raw = {'nodes': [{'id': str(node), **attrs} for node, attrs in graph.nodes(data=True)],
               'edges': [[str(a), str(b)] for a, b in graph.edges()]}
        save('graph_before_normalization.json', raw)
        graph.name = IDENT
        graph.type = 'DFG'
        graph.graph['hw_type'] = 'Test'
        graph.graph['label'] = 0  # Placeholder only; never passed into model inference.
        processor.process(graph)
        data = processor.get_graphs()[0]
        tensor = {'x': data.x.tolist(), 'edge_index': data.edge_index.tolist(),
                  'num_nodes': int(data.num_nodes), 'num_edges': int(data.edge_index.shape[1])}
        save('model_input.json', tensor)
        indices = {node: i for i, node in enumerate(graph.nodes)}
        edges = {(indices[a], indices[b]) for a, b in graph.edges()}
        assert edges == set(zip(*tensor['edge_index']))
        assert len(graph) == tensor['num_nodes'] and len(edges) == tensor['num_edges']
        assert sha(source) == row['sha256']
        gate = {'status': 'PASS', 'route': 'repaired_exact_DFG_no_fallback', 'source_sha256': sha(source),
                'nodes': len(graph), 'edges': graph.number_of_edges(),
                'weak_components': nx.number_weakly_connected_components(graph),
                'joined_references': len(coverage['joined_references']), 'output_dependency_counts': outputs,
                'unresolved_bound_references': 0, 'unbound_noninput_references': 0,
                'graph_edges_preserved_in_model_input': True, 'seconds': time.monotonic() - started}
    else:
        source = ROOT / 'inputs' / IDENT / 'model_input.json'
        assert sha(source) == expected[str(source.relative_to(ROOT))]
        tensor = json.loads(source.read_text())
        save('model_input.json', tensor)
        gate = {'status': 'PASS', 'route': 'exact_saved_csaw_tensor', 'source_sha256': sha(source),
                'nodes': tensor['num_nodes'], 'edges': tensor['num_edges'],
                'previous_coverage_gates_reused_for_identical_bytes': True}
    assert min(tensor['x']) >= 0 and max(tensor['x']) < 37
    save('COVERAGE_GATE.json', gate)
    data = Data(x=torch.tensor(tensor['x'], dtype=torch.long),
                edge_index=torch.tensor(tensor['edge_index'], dtype=torch.long), num_nodes=tensor['num_nodes'])
    assert data.x.tolist() == tensor['x'] and data.edge_index.tolist() == tensor['edge_index']
    loader = DataLoader([data], batch_size=1, shuffle=False)
    models, identities = {}, []
    for number in range(1, 5):
        name = 'HT' + str(number)
        folder = ROOT / 'package' / ('model_' + name)
        configuration = json.loads((folder / 'model.cfg').read_text())
        assert configuration['convs'][0][1] == 37 and configuration['fc'][1] == 2
        model = GRAPH2VEC(cfg)
        model.set_graph_conv([GRAPH_CONV(*layer) for layer in configuration['convs']])
        model.set_graph_pool(GRAPH_POOL(*configuration['pool']))
        model.set_graph_readout(GRAPH_READOUT(configuration['readout']))
        model.set_output_layer(nn.Linear(*configuration['fc']))
        state = torch.load(str(folder / 'model.pth'), map_location='cpu', weights_only=True)
        assert isinstance(state, dict) and all(isinstance(v, torch.Tensor) and torch.isfinite(v).all() for v in state.values())
        loaded = model.load_state_dict(state, strict=True)
        assert not loaded.missing_keys and not loaded.unexpected_keys
        models[name] = model.to('cpu').eval()
        identities.append({'model': name, 'checkpoint_sha256': sha(folder / 'model.pth'),
                           'config_sha256': sha(folder / 'model.cfg'), 'strict_load': True,
                           'weights_only': True, 'all_parameters_finite': True,
                           'parameter_count': sum(p.numel() for p in model.parameters()),
                           'device': 'cpu', 'training': model.training})
    save('MODEL_IDENTITIES.json', identities)

    def stats(value):
        value = value.detach().cpu().contiguous()
        assert torch.isfinite(value).all()
        return {'shape': list(value.shape), 'dtype': str(value.dtype),
                'sha256': hashlib.sha256(value.numpy().tobytes()).hexdigest(),
                'nonzero': int(torch.count_nonzero(value)), 'elements': value.numel(),
                'min': float(value.min()), 'max': float(value.max()),
                'mean': float(value.float().mean()), 'l2_norm': float(value.float().norm())}

    scores = {}
    for name, model in models.items():
        stages, handles = {}, []
        def hook(stage, tuple_output=False):
            def capture(module, inputs, output):
                stages[stage] = stats(output[0] if tuple_output else output)
                # Returning None leaves the original forward result unchanged.
            return capture
        for i, layer in enumerate(model.layers):
            handles.append(layer.register_forward_hook(hook('conv_' + str(i + 1) + '_before_relu')))
        handles.append(model.pool1.register_forward_hook(hook('after_pool', True)))
        handles.append(model.graph_readout.register_forward_hook(hook('readout')))
        handles.append(model.fc.register_forward_hook(hook('logits')))
        try:
            with torch.no_grad():
                item = next(iter(loader)).to('cpu')
                embedded, _ = model.embed_graph(item.x, item.edge_index, item.batch)
                logits = model.mlp(embedded)
                log_probs = F.log_softmax(logits, dim=1)
                probs = log_probs.exp()[0]
                prediction = int(log_probs.max(1)[1].item())
                bias_only = torch.equal(logits[0], model.fc.bias)
        finally:
            for handle in handles:
                handle.remove()
        scores[name] = {'prediction': prediction, 'label': 'TROJAN' if prediction else 'CLEAN',
                        'prob_trojan': float(probs[1]), 'prob_clean': float(probs[0]),
                        'logits': logits.tolist()[0], 'log_probabilities': log_probs.tolist()[0],
                        'stages': stages, 'logits_equal_output_bias': bias_only}
    if not IDENT.startswith('design_'):
        previous = json.loads((ROOT / 'records/previous_csaw_scores.json').read_text())
        original = next(run for run in previous['runs'] if run['candidate'] == IDENT)
        for name in scores:
            assert scores[name]['logits'] == original['scores'][name]['logits'], ('diagnostic replay differs', IDENT, name)
    votes = [name for name, value in scores.items() if value['prediction'] == 1]
    save('RESULTS.json', {'design_id': IDENT, 'status': 'scored', 'input_sha256': sha(OUT / 'model_input.json'),
                         'source_or_saved_tensor_sha256': gate['source_sha256'], 'gate': gate,
                         'scores': scores, 'ensemble': {'prediction': int(bool(votes)), 'triggered_models': votes},
                         'truth_label_read_by_worker': False, 'model_training': False,
                         'prior_logits_exactly_reproduced': True if not IDENT.startswith('design_') else None})
    print(json.dumps({'design_id': IDENT, 'status': 'scored', 'predictions': {name: value['prediction'] for name, value in scores.items()}}))

if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        OUT.mkdir(exist_ok=True)
        (OUT / 'failure.txt').write_text(traceback.format_exc())
        save('FAILURE.json', {'design_id': IDENT, 'status': 'unscored', 'error_type': type(error).__name__, 'error': str(error)})
        traceback.print_exc()
        sys.exit(2)
