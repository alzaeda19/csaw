"""Read-only coverage/accounting audit of saved graphs; no graph or design repairs."""
from pathlib import Path
import json,hashlib,collections,shutil
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text())
def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2)+'\n')
def reach(start,adj):
 seen=set();todo=list(adj.get(start,[]))
 while todo:
  x=todo.pop()
  if x not in seen:seen.add(x);todo.extend(adj.get(x,[]))
 return seen
coverage=[]
for name in ['flat_clean','flat_modified']:
 g=load(f'detectors/result_{name}/graph_before_normalization.json');nodes={x['id'] for x in g['nodes']};adj=collections.defaultdict(list)
 for a,b in g['edges']:adj[a].append(b)
 definitions={x.split('_graphrename')[0]:x for x in nodes if x.startswith('top.')}
 unjoined=[]
 for n in sorted(nodes):
  if n.startswith('top_'):
   # Exact top-scope prefix conversion only; original identifier underscores retained.
   key='top.'+n[len('top_'):]
   if key in definitions:
    unjoined.append({'reference_node':n,'definition_node':definitions[key],'reference_successors':adj.get(n,[]),'definition_reachable_from_reference':definitions[key] in reach(n,adj)})
 miso=next(x for x in nodes if x.startswith('top.MISO_graphrename'))
 reachable=reach(miso,adj)
 faults=[x for x in nodes if x.startswith('top.fault_active_graphrename')]
 record={'candidate':name,'unjoined_exact_top_scope_reference_pairs':len(unjoined),'unjoined_pairs':unjoined,'miso_definition':miso,'miso_dependency_graph_nodes':len(reachable),'miso_direct_dependencies':adj.get(miso,[]),'fault_definition_nodes':faults,'miso_reaches_fault_definition':any(x in reachable for x in faults),'root_cause_evidence':'Unchanged hw2graph.py lines 387-400 join references by replacing every underscore with a dot, conflating hierarchy separators with literal identifier underscores. Saved graph retains distinct reference/definition nodes; no graph repair attempted.','conclusion':'Exact backend completed, but graph is not a fully connected representation of the original design; output scores cannot establish whole-design stealth.'}
 coverage.append(record)
write('analysis/GRAPH_COVERAGE.json',coverage)
struct=[]
for name in ['clean','modified']:
 m=load(f'synthesis/{name}.json')['modules']['top'];counts=collections.Counter(c['type'] for c in m['cells'].values())
 struct.append({'candidate':name,'generic_cell_types':dict(counts),'generic_cells_excluding_scope_metadata':sum(v for k,v in counts.items() if k!='$scopeinfo'),'state_Q_bits_including_mapped_RAM_model':sum(len(c['connections'].get('Q',[])) for c in m['cells'].values() if 'dff' in c['type'].lower()),'no_unresolved_cells':all(c['type'].startswith('$') for c in m['cells'].values()),'mapped_memories_remaining':len(m.get('memories',{}))})
write('analysis/STRUCTURAL_COMPARISON.json',{'designs':struct,'added_state_bits':struct[1]['state_Q_bits_including_mapped_RAM_model']-struct[0]['state_Q_bits_including_mapped_RAM_model'],'added_generic_cells':struct[1]['generic_cells_excluding_scope_metadata']-struct[0]['generic_cells_excluding_scope_metadata'],'meaning':'Same-flow structural difference, not physical area/timing or a maliciousness classifier. Generic-cell and RAM-mapped-state counts differ from previously recorded FPGA primitives. Previous actual FPGA resource differences remain +36 LUT4, +48 registers, +13 carry, RAM unchanged.'})
matrix=[]
for name in ['raw_clean','raw_modified','flat_clean','flat_modified']:
 result=load(f'detectors/result_{name}/RESULTS.json');prep=load(f'detectors/result_{name}/preprocessing.json')
 matrix.append({'candidate':name,'route':result['preprocessing_route'],'models':{k:v['label'] for k,v in result['per_model'].items()},'trojan_scores':{k:v['prob_trojan'] for k,v in result['per_model'].items()},'nodes':prep['graph_nodes'],'edges':prep['graph_edges'],'whole_design_evidence_valid':False,'limitation':'Syntax failure invokes incomplete heuristic graph' if name.startswith('raw_') else 'Backend completes but unresolved reference/definition joins fragment graph'})
write('analysis/DETECTOR_COMPARISON.json',matrix)
print(json.dumps({'coverage':[{'candidate':x['candidate'],'unjoined_pairs':x['unjoined_exact_top_scope_reference_pairs'],'miso_dependency_nodes':x['miso_dependency_graph_nodes'],'miso_reaches_fault_definition':x['miso_reaches_fault_definition']} for x in coverage],'matrix':matrix},indent=2))
