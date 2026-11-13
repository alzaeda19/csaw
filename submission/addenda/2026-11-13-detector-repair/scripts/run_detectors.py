"""Fixed-checkpoint, fixed-design evaluation. No training or design changes."""
import os,sys,json,hashlib,signal,traceback,contextlib,time,collections,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PKG=ROOT/'package'
NAME=sys.argv[1]; RUN=ROOT/'detectors'/('result_'+NAME)
SOURCE=ROOT/'detectors'/NAME/'topModule.v'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(RUN/n).write_text(json.dumps(d,indent=2)+'\n')
def main():
 RUN.mkdir();os.chdir(RUN);before=sha(SOURCE)
 sys.path.insert(0,str(PKG/'hw2vec'))
 import torch,numpy,networkx,torch_geometric,pyverilog
 import torch.nn as nn
 import torch.nn.functional as F
 from torch_geometric.loader import DataLoader
 from hw2vec.config import Config
 from hw2vec.hw2graph import HW2GRAPH,DataProcessor
 from hw2vec.graph2vec.models import GRAPH2VEC,GRAPH_CONV,GRAPH_POOL,GRAPH_READOUT
 torch.manual_seed(0);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
 save('versions.json',{'python':platform.python_version(),'torch':torch.__version__,'torch_geometric':torch_geometric.__version__,'numpy':numpy.__version__,'networkx':networkx.__version__,'pyverilog':pyverilog.__version__})
 cfg=Config(['--yaml_path',str(PKG/'hw2vec/examples/example_gnn4tj.yaml'),'--data_pkl_path',str(ROOT/'runtime/UNUSED.pkl'),'--graph_type','DFG','--model_path','','--device','cpu'])
 proc=DataProcessor(cfg);cfg.num_feature_dim=len(proc.global_type2idx_DFG);assert cfg.num_feature_dim==37
 save('feature_vocabulary.json',proc.global_type2idx_DFG)
 models={};identities=[]
 for i in range(1,5):
  name='HT'+str(i);folder=PKG/('model_'+name);cp=folder/'model.cfg';wp=folder/'model.pth'
  mc=json.loads(cp.read_text());assert mc['convs'][0][1]==37 and mc['fc'][1]==2
  model=GRAPH2VEC(cfg);model.set_graph_conv([GRAPH_CONV(*c) for c in mc['convs']]);model.set_graph_pool(GRAPH_POOL(*mc['pool']));model.set_graph_readout(GRAPH_READOUT(mc['readout']));model.set_output_layer(nn.Linear(*mc['fc']))
  sd=torch.load(str(wp),map_location='cpu',weights_only=True)
  assert isinstance(sd,dict) and all(isinstance(v,torch.Tensor) for v in sd.values())
  loaded=model.load_state_dict(sd,strict=True);assert not loaded.missing_keys and not loaded.unexpected_keys
  models[name]=model.to('cpu').eval()
  identities.append({'model':name,'checkpoint_sha256':sha(wp),'config_sha256':sha(cp),'strict_load':True,'weights_only':True,'training':model.training,'device':'cpu'})
 save('model_loads.json',identities)
 def alarm(*_):raise TimeoutError('Exact DFG exceeded preregistered 120 seconds')
 old=signal.signal(signal.SIGALRM,alarm);start=time.monotonic();signal.setitimer(signal.ITIMER_REAL,120)
 try:
  with (RUN/'extraction.stdout').open('w') as out,(RUN/'extraction.stderr').open('w') as err,contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
   graph=HW2GRAPH(cfg).code2graph(SOURCE.parent)
 finally:
  signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)
 log=(RUN/'extraction.stdout').read_text();route='heuristic_fallback' if 'Using heuristic DFG fallback' in log else 'exact_DFG'
 assert graph is not None and graph.number_of_nodes()>1 and graph.number_of_edges()>0 and 'sig_dummy' not in graph.nodes
 graph.graph['hw_type']='Test';graph.graph['label']=0 # Unused notebook placeholder, not ground truth.
 rawlabels=collections.Counter(str(d.get('label')) for _,d in graph.nodes(data=True))
 save('graph_before_normalization.json',{'nodes':[{'id':str(n),**d} for n,d in graph.nodes(data=True)],'edges':[[str(a),str(b)] for a,b in graph.edges()]})
 proc.process(graph);assert len(proc.graph_data)==1
 data=proc.get_graphs()[-1];assert data.x.ndim==1 and int(data.x.min())>=0 and int(data.x.max())<37
 save('model_input.json',{'x':data.x.tolist(),'edge_index':data.edge_index.tolist(),'num_nodes':int(data.num_nodes),'num_edges':int(data.edge_index.shape[1])})
 prep={'candidate_sha256':before,'candidate_bytes':SOURCE.stat().st_size,'canonical_top':'top','global_underscore_removal_bypassed':True,'route':route,'exact_timeout_seconds':120,'elapsed_seconds':time.monotonic()-start,'graph_nodes':graph.number_of_nodes(),'graph_edges':graph.number_of_edges(),'weakly_connected_components':networkx.number_weakly_connected_components(graph),'raw_label_counts':dict(rawlabels),'feature_counts':{str(k):v for k,v in collections.Counter(data.x.tolist()).items()},'dataset_cache_loaded':False,'full_design_validity':'INVALID: heuristic graph does not preserve complete HDL semantics' if route=='heuristic_fallback' else 'Exact backend completed; coverage and transformation checks still required; no complete-semantics certificate'}
 save('preprocessing.json',prep)
 loader=DataLoader([data],shuffle=False,batch_size=1);results={}
 for name,model in models.items():
  with torch.no_grad():
   item=next(iter(loader));item.to('cpu');emb,_=model.embed_graph(item.x,item.edge_index,item.batch);logits=model.mlp(emb);outputs=F.log_softmax(logits,dim=1).cpu();pred=outputs.max(1)[1].item();probs=torch.exp(outputs).numpy()[0]
  assert numpy.isfinite(probs).all() and abs(float(probs.sum())-1)<1e-5
  results[name]={'prediction':int(pred),'label':'TROJAN' if pred else 'CLEAN','prob_clean':float(probs[0]),'prob_trojan':float(probs[1]),'log_probabilities':outputs.tolist()[0],'logits':logits.cpu().tolist()[0]}
 votes=[k for k,v in results.items() if v['prediction']==1]
 result={'candidate':NAME,'candidate_sha256':before,'per_model':results,'ensemble':{'trojan_votes':len(votes),'triggered_models':votes,'verdict':'TROJAN' if votes else 'CLEAN','rule':'any model votes 1'},'preprocessing_route':route,'source_unchanged':sha(SOURCE)==before,'valid_whole_design_result':False,'qualification':'Fallback diagnostic only' if route=='heuristic_fallback' else 'Exact graph classification only; coverage/applicability reviewed separately','limits':['Scores are not calibrated compromise probabilities.','Same four checkpoints are not four independent security certificates.','One frozen clean/modified pair does not estimate general detection accuracy.','No model tuning, generation, design feedback, or training.']}
 assert result['source_unchanged'];save('RESULTS.json',result);print(json.dumps({'candidate':NAME,'route':route,'nodes':graph.number_of_nodes(),'edges':graph.number_of_edges(),'votes':votes}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  RUN.mkdir(parents=True,exist_ok=True);(RUN/'failure.txt').write_text(traceback.format_exc());raise
