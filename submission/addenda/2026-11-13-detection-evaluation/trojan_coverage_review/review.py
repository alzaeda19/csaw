"""Read-only interpretation review of saved detector/representation evidence."""
from pathlib import Path
from collections import defaultdict, Counter
import argparse
import hashlib
import json

OUT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=Path('/Users/al-zayedal-hassan/Documents/Codex/2026-11-10/referenced-chatgpt-conversation-this-is-an/outputs/CSAW_detection_evaluation_2026-11-13'))
SRC = parser.parse_args().source
manifest = {}
sha = lambda data: hashlib.sha256(data).hexdigest()

def read(name, copy=False):
    data = (SRC/name).read_bytes()
    manifest[name] = {'source':str(SRC/name),'bytes':len(data),'sha256':sha(data),'copied':copy}
    if copy:
        dest=OUT/'snapshots'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    return data.decode()

def js(name, copy=False): return json.loads(read(name,copy))
def save(name, data): (OUT/name).write_text(json.dumps(data,indent=2)+'\n')

read('TEST_PLAN.json',True)
js('analysis/REPRESENTATIONS.json',True)
js('analysis/representation_validation/RESULTS.json',True)
js('records/QWEN_LABEL_KEY.json',True)
code = read('package/hw2vec/hw2vec/hw2graph.py').splitlines()
excerpt=[{'line':n,'text':code[n-1]} for n in range(362,421)]
save('DFG_GENERATOR_EXCERPT.json',{'source':'package/hw2vec/hw2vec/hw2graph.py','lines':excerpt})
assert "label.replace('_', '.')" in '\n'.join(code[393:400])
assert 'walk=False' in code[383]
detectors=[]; coverage=[]; examples={}
for candidate in ['raw_clean','raw_modified','flat_clean','flat_modified']:
    root='detectors/result_'+candidate
    result=js(root+'/RESULTS.json',True)
    prep=js(root+'/preprocessing.json')
    log=read(root+'/extraction.stdout',True)
    source=read('detectors/'+candidate+'/topModule.v')
    assert sha(source.encode())==result['candidate_sha256']==prep['candidate_sha256']
    detectors.append({'candidate':candidate,'route':result['preprocessing_route'],'predictions':{k:v['label'] for k,v in result['per_model'].items()},'ensemble':result['ensemble'],'valid_whole_design_result':result['valid_whole_design_result'],'source_hash_matches':True,'extraction_error_lines':[l for l in log.splitlines() if any(x in l for x in ['DFG generation failed','Using heuristic DFG fallback'])]})
    if not candidate.startswith('flat_'): continue
    graph=js(root+'/graph_before_normalization.json')
    model=js(root+'/model_input.json')
    nodes={n['id']:n for n in graph['nodes']}; inc=defaultdict(list); out=defaultdict(list)
    for a,b in graph['edges']:out[a].append(b);inc[b].append(a)
    paired=[]
    for name in nodes:
        original=name.split('_graphrename')[0]
        if not original.startswith('top.') or '_' not in original[4:]:continue
        leaf='top_'+original[4:]
        if leaf not in nodes or leaf==name:continue
        paired.append({'definition':name,'reference':leaf,'definition_in_degree':len(inc[name]),'definition_out_degree':len(out[name]),'reference_in_degree':len(inc[leaf]),'reference_out_degree':len(out[leaf]),'underscore_to_dot_lookup':leaf.replace('_','.'),'actual_definition_label':original})
    separated=[x for x in paired if x['definition_in_degree']==0 and x['definition_out_degree']>0 and x['reference_in_degree']>0 and x['reference_out_degree']==0]
    selected=paired[:3]+[x for x in paired if any(s in x['definition'] for s in ['read_count','fault_active','ingress_count'])]
    for row in selected:
        row.update(definition_node=nodes[row['definition']],reference_node=nodes[row['reference']],definition_incoming=inc[row['definition']],definition_outgoing=out[row['definition']],reference_incoming=inc[row['reference']],reference_outgoing=out[row['reference']])
    examples[candidate]=selected
    index={n['id']:i for i,n in enumerate(graph['nodes'])}
    original_edges={(index[a],index[b]) for a,b in graph['edges']}
    model_edges=set(zip(*model['edge_index']))
    assert original_edges==model_edges
    assert model['num_nodes']==len(nodes)==len(model['x'])
    assert model['num_edges']==len(graph['edges'])
    coverage.append({'candidate':candidate,'nodes':len(nodes),'edges':len(graph['edges']),'weak_components_reported':prep['weakly_connected_components'],'paired_underscore_names':len(paired),'separate_definition_roots_reference_leaves':len(separated),'model_input_edges_exactly_equal_saved_graph':True,'neighborhood_evidence':'GRAPH_NEIGHBORHOODS.json','interpretation':'Current naming/normalization flow leaves references disconnected from their definitions. Successful exact-backend completion does not establish complete design semantics.'})
save('GRAPH_NEIGHBORHOODS.json',examples)

logs={}; sim=[]
for name in ['original_clean','original_modified','raw_clean','raw_modified','flat_clean','flat_modified']:
    lines=read('analysis/representation_validation/'+name+'_simulate.stdout').splitlines()
    logs[name]={'T':[x for x in lines if x.startswith('T ')],'R':[x for x in lines if x.startswith('R ')]}
    assert len(logs[name]['T'])==39960 and len(logs[name]['R'])==270
    assert all(set(x.split()[-1])<={'0','1'} for x in logs[name]['T'])
    assert 'PASS cases=270 observed_samples=39960' in lines
    sim.append({'candidate':name,'sample_triples':39960,'transactions':270,'pass_line_present':True})
comparisons=[]
for kind in ['raw','flat']:
    for design in ['clean','modified']:
        a=kind+'_'+design;b='original_'+design
        assert logs[a]==logs[b]
        comparisons.append({'candidate':a,'reference':b,'exact_T_and_R_lines_equal':True})
transaction_diffs=[{'row':i,'clean':a,'modified':b} for i,(a,b) in enumerate(zip(logs['original_clean']['R'],logs['original_modified']['R'])) if a!=b]
sample_diffs=[{'row':i,'clean':a,'modified':b} for i,(a,b) in enumerate(zip(logs['original_clean']['T'],logs['original_modified']['T'])) if a!=b]
assert len(transaction_diffs)==1 and transaction_diffs[0]['row']==8
assert all(x['clean'].split()[1]=='8' and x['modified'].split()[1]=='8' for x in sample_diffs)

qwen=[]
for name in ['candidate_R','candidate_S']:
    read('ai_logs/'+name+'/request.json',True)
    reply=js('ai_logs/'+name+'/response.txt',True)
    qwen.append({'candidate':name,'finding':reply['finding'],'recorded_limitations':reply['limitations']})
read('sources/modified_protocol_dut.sv',True)
read('sources/baseline_protocol_dut.sv',True)
result={'scope':'Independent read-only review of existing outputs; no detector/model/synthesis/simulation rerun or source changes.','detectors':detectors,'graph_coverage':coverage,'simulation_review':{'runs':sim,'representation_comparisons':comparisons,'transaction_differences':transaction_diffs,'sample_differences':sample_diffs,'scope':'Finite digital trace consistency does not validate graph semantic coverage or stealth.'},'qwen_review':{'responses':qwen,'assessment':'Classifications match the wrapper sources. R limitations incorrectly place visible fault_active-setting logic inside chip; it is present in the provided wrapper. Label-masked is not double-blind or an independent certification.'},'overall':'Agree with the bounded interpretation: raw fallback predictions are diagnostics; flat CLEAN labels are valid outputs for incomplete graphs and do not establish full-design stealth. No inference that the naming gap caused the model verdict or that a complete graph would change it.'}
save('REVIEW_RESULTS.json',result)
for name,receipt in manifest.items():
    assert sha((SRC/name).read_bytes())==receipt['sha256']
save('SOURCE_MANIFEST.json',{'sources':manifest,'all_read_sources_unchanged_at_completion':True,'large_inputs':'Full graphs/model tensors/simulation logs are identified by source hashes, not recopied. Selected graph neighborhoods and exact small source snapshots are preserved. Reproduction needs the original evaluation bundle.'})
print(json.dumps({'coverage':coverage,'simulation_runs_reviewed':len(sim),'transaction_differences':len(transaction_diffs),'sample_differences':len(sample_diffs),'sources_checked':len(manifest),'outcome':result['overall']},indent=2))
