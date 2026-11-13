"""Extract and validate both frozen flat inputs before any classifier inference."""
from pathlib import Path
import json,hashlib,sys,time,signal,contextlib,platform,collections
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'package/hw2vec'))
from hw2vec.hw2graph import DFGGenerator,DataProcessor
from hw2vec.config import Config
import networkx as nx
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
fixtures=json.loads((ROOT/'tests/final/RESULTS.json').read_text());assert all(x['pass_check'] for x in fixtures)
# Previously supported plain names must retain the original graph semantics.
old=json.loads((ROOT/'tests/original/plain/graph.json').read_text());new=json.loads((ROOT/'tests/final/plain/graph.json').read_text())
assert old['nodes']==new['nodes'] and set(map(tuple,old['edges']))==set(map(tuple,new['edges']))
initial=json.loads((ROOT/'records/INPUT_HASHES.json').read_text())['files']
allowed={'package/hw2vec/hw2vec/hw2graph.py','scripts/run_detectors.py','scripts/run_matrix.py'}
for rel,digest in initial.items():
 if rel not in allowed:assert sha(ROOT/rel)==digest,rel
cfg=Config(['--yaml_path',str(ROOT/'package/hw2vec/examples/example_gnn4tj.yaml'),'--data_pkl_path',str(ROOT/'runtime/UNUSED.pkl'),'--graph_type','DFG','--model_path','','--device','cpu'])
all_checks=[]
for candidate in ['flat_clean','flat_modified']:
 out=ROOT/'detectors'/('repaired_'+candidate);out.mkdir();source=ROOT/'detectors'/candidate/'topModule.v';gen=DFGGenerator();start=time.monotonic()
 def timeout(*_):raise TimeoutError('Exact extraction exceeded 120 seconds; no fallback allowed')
 previous=signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,120)
 try:
  with (out/'extraction.stdout').open('w') as so,(out/'extraction.stderr').open('w') as se,contextlib.redirect_stdout(so),contextlib.redirect_stderr(se):g=gen.process(source)
 finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
 coverage=gen.last_report;save(out/'SYMBOL_COVERAGE.json',coverage)
 assert not coverage['ambiguous_labels'] and not coverage['unresolved_bound_references'] and not coverage['unbound_noninput_references']
 roots=coverage['definition_roots'];assert all(root in g for root in roots.values())
 for item in coverage['joined_references']:
  assert item['reference_node'] not in g
  assert all(g.has_edge(parent,item['definition_node']) for parent in item['parents'])
 raw={'nodes':[{'id':str(n),**d} for n,d in g.nodes(data=True)],'edges':[[str(a),str(b)] for a,b in g.edges()]};save(out/'graph_before_normalization.json',raw)
 outputs={}
 for name in ['MISO','BUSY','ICE_LED']:
  root=roots['top.'+name];desc=nx.descendants(g,root)
  outputs[name]={'root':root,'dependency_nodes':len(desc),'reachable_primary_inputs':sorted(x['symbol'] for x in coverage['unbound_references'] if x['reference_node'] in desc),'reachable_definitions':sum(v in desc for v in roots.values())}
  assert desc
 miso_dependencies=nx.descendants(g,roots['top.MISO'])
 assert 'top_MOSI' in miso_dependencies
 assert 'top_START' in nx.descendants(g,roots['top.BUSY'])
 expected_modified=['top.fault_active','top.read_count','top.ingress_word','top.ingress_count']
 if candidate=='flat_modified':assert all(roots[name] in miso_dependencies for name in expected_modified)
 else:assert not any(name in roots for name in expected_modified)
 g.name=candidate;g.type='DFG';g.graph['hw_type']='Test';g.graph['label']=0
 proc=DataProcessor(cfg);proc.process(g);data=proc.get_graphs()[0]
 assert len(proc.global_type2idx_DFG)==37 and data.x.ndim==1 and data.x.min()>=0 and data.x.max()<37
 tensor={'x':data.x.tolist(),'edge_index':data.edge_index.tolist(),'num_nodes':int(data.num_nodes),'num_edges':int(data.edge_index.shape[1])};save(out/'model_input.json',tensor)
 ids={n:i for i,n in enumerate(g.nodes)};graph_edges={(ids[a],ids[b]) for a,b in g.edges()};model_edges=set(zip(*tensor['edge_index']))
 assert graph_edges==model_edges and len(g)==tensor['num_nodes'] and len(graph_edges)==tensor['num_edges']
 save(out/'feature_vocabulary.json',proc.global_type2idx_DFG)
 check={'candidate':candidate,'source_sha256':sha(source),'extractor_sha256':sha(ROOT/'package/hw2vec/hw2vec/hw2graph.py'),'graph_sha256':sha(out/'graph_before_normalization.json'),'model_input_sha256':sha(out/'model_input.json'),'nodes':len(g),'edges':g.number_of_edges(),'weak_components':nx.number_weakly_connected_components(g),'bound_definitions':len(roots),'joined_reference_nodes':len(coverage['joined_references']),'unresolved_bound_references':0,'ambiguous_symbols':0,'unbound_noninput_references':0,'outputs':outputs,'model_edge_set_matches_graph':True,'feature_vocabulary_count':37,'seconds':time.monotonic()-start,'coverage_gate':'PASS for audited dataflow abstraction; not full temporal/physical semantics'}
 save(out/'COVERAGE_GATE.json',check);all_checks.append(check)
save(ROOT/'analysis/PRE_INFERENCE_GATES.json',{'status':'PASS','fixtures':len(fixtures),'plain_graph_unchanged':True,'frozen_inputs_verified':True,'targets':all_checks,'inference_not_yet_run':True})
print(json.dumps(all_checks,indent=2))
