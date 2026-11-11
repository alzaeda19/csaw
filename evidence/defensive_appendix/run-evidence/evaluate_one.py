#!/usr/bin/env python3
"""One frozen graph classification; no HDL execution or truth-label input."""
import os,sys,json,hashlib,signal,traceback,contextlib,time,collections,re,resource,errno
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PKG=ROOT/'package';DESIGN=sys.argv[1]
assert re.fullmatch(r'design_\d{3}',DESIGN)
RUN=ROOT/'runs'/DESIGN
class ExtractionDeadline(BaseException):pass
class ResourceFailure(BaseException):pass
class InvalidGraph(BaseException):pass
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(RUN/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 RUN.mkdir(exist_ok=False);os.chdir(RUN);limits={}
 for name,kind,value in [('cpu_seconds',resource.RLIMIT_CPU,60),('file_bytes',resource.RLIMIT_FSIZE,134217728),('open_files',resource.RLIMIT_NOFILE,512),('core_bytes',resource.RLIMIT_CORE,0)]:
  old=resource.getrlimit(kind);hard=old[1];v=value if hard==resource.RLIM_INFINITY else min(value,hard)
  resource.setrlimit(kind,(v,v));limits[name]=list(resource.getrlimit(kind))
 save('worker_limits.json',limits)
 rows=json.loads((ROOT/'records/inference_inputs.json').read_text())['inputs'];row=next(x for x in rows if x['design_id']==DESIGN)
 assert not any(k in row for k in ['truth','truth_label','label','family','archive_member'])
 assert row['eligible'],row.get('rejection_reasons')
 source=ROOT/row['source_path'];assert sha(source)==row['sha256']
 sys.path.insert(0,str(PKG/'hw2vec'))
 import torch,numpy,networkx
 import torch.nn as nn
 import torch.nn.functional as F
 from torch_geometric.loader import DataLoader
 from hw2vec.config import Config
 from hw2vec.hw2graph import HW2GRAPH,DataProcessor,DFGGenerator,heuristic_dfg_from_code
 from hw2vec.graph2vec.models import GRAPH2VEC,GRAPH_CONV,GRAPH_POOL,GRAPH_READOUT
 torch.manual_seed(0);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
 cfg=Config(['--yaml_path',str(PKG/'hw2vec/examples/example_gnn4tj.yaml'),'--data_pkl_path',str(PKG/'dfg_tj_rtl.pkl'),'--graph_type','DFG','--model_path','','--device','cpu'])
 proc=DataProcessor(cfg);cfg.num_feature_dim=len(proc.global_type2idx_DFG)
 assert cfg.num_feature_dim==37 and cfg.device=='cpu'
 assert proc.global_type2idx_DFG==json.loads((ROOT/'records/expected_feature_vocabulary.json').read_text())
 save('feature_vocabulary.json',proc.global_type2idx_DFG);models={};identities=[]
 for i in range(1,5):
  name='HT'+str(i);folder=PKG/('model_'+name);cp=folder/'model.cfg';wp=folder/'model.pth';mc=json.loads(cp.read_text())
  assert mc['convs'][0][1]==37 and mc['fc'][1]==2
  model=GRAPH2VEC(cfg);model.set_graph_conv([GRAPH_CONV(*c) for c in mc['convs']]);model.set_graph_pool(GRAPH_POOL(*mc['pool']));model.set_graph_readout(GRAPH_READOUT(mc['readout']));model.set_output_layer(nn.Linear(*mc['fc']))
  sd=torch.load(str(wp),map_location='cpu',weights_only=True)
  assert isinstance(sd,dict) and all(isinstance(v,torch.Tensor) for v in sd.values())
  loaded=model.load_state_dict(sd,strict=True);assert not loaded.missing_keys and not loaded.unexpected_keys
  models[name]=model.to('cpu').eval()
  identities.append({'model':name,'checkpoint_sha256':sha(wp),'config_sha256':sha(cp),'tensors':len(sd),'parameters':sum(p.numel() for p in model.parameters()),'strict_load':True,'weights_only':True,'training':model.training,'device':'cpu'})
 assert identities==json.loads((ROOT/'records/expected_model_loads.json').read_text());save('model_loads.json',identities)
 gd=RUN/'graph_input';gd.mkdir();target=gd/'topModule.v';target.write_bytes(source.read_bytes());exact={'status':'not_attempted'};original=DFGGenerator.process
 def observed(generator,path):
  exact['status']='running'
  try:g=original(generator,path)
  except (MemoryError,RecursionError) as e:
   exact.update(status='resource_failure',exception_type=type(e).__name__,error=str(e));save('exact_extraction.json',exact);raise ResourceFailure(type(e).__name__) from e
  except OSError as e:
   exact.update(status='failed',exception_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());save('exact_extraction.json',exact)
   if e.errno in [errno.ENOMEM,errno.EFBIG,errno.EMFILE,errno.ENFILE]:raise ResourceFailure(str(e)) from e
   raise
  except Exception as e:
   exact.update(status='failed',exception_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());save('exact_extraction.json',exact);raise
  exact.update(status='success' if g is not None and g.number_of_nodes()>0 else 'empty',nodes=g.number_of_nodes() if g is not None else 0,edges=g.number_of_edges() if g is not None else 0);save('exact_extraction.json',exact)
  if exact['status']=='empty':raise InvalidGraph('Exact extraction returned empty graph; unscored')
  return g
 DFGGenerator.process=observed
 entries=len(re.findall(r"(?im)^\s*8'h[0-9a-f]{2}\s*:",target.read_text()));start=time.monotonic();extractor=HW2GRAPH(cfg)
 def alarm(*_):
  exact.update(status='timeout',error='30-second graph extraction deadline');save('exact_extraction.json',exact);raise ExtractionDeadline('30-second graph extraction deadline')
 old=signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,30)
 try:
  with (RUN/'extraction.stdout').open('w') as output,contextlib.redirect_stdout(output):
   if entries>=128:
    path=extractor.preprocess(gd);print('[HW2GRAPH] Large lookup table detected; using original direct heuristic rule.',flush=True);graph=heuristic_dfg_from_code(path.read_text(),name='snippet',hw_type='DFG');route='heuristic_large_lookup_direct'
   else:graph=extractor.code2graph(gd);route='heuristic_fallback' if exact['status']=='failed' else 'exact_DFG'
 finally:
  signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old);save('exact_extraction.json',exact)
 messages=(RUN/'extraction.stdout').read_text()
 if graph is None or graph.number_of_nodes()<=1 or graph.number_of_edges()==0 or 'sig_dummy' in graph.nodes:raise InvalidGraph('Empty, dummy, or edgeless final graph; unscored')
 if route=='heuristic_fallback':assert 'Using heuristic DFG fallback' in messages
 assert sha(target)==row['sha256'],'Provided topModule.v must bypass optional flatten/rename preprocessing'
 graph.graph['hw_type']='Test';graph.graph['label']=0
 save('graph_before_normalization.json',{'nodes':[{'id':str(n),**d} for n,d in graph.nodes(data=True)],'edges':[[str(a),str(b)] for a,b in graph.edges()]});rawlabels=dict(collections.Counter(str(d.get('label')) for _,d in graph.nodes(data=True)))
 proc.process(graph);assert len(proc.graph_data)==1;data=proc.get_graphs()[-1]
 assert data.x.ndim==1 and int(data.x.min())>=0 and int(data.x.max())<37
 save('model_input.json',{'x':data.x.tolist(),'edge_index':data.edge_index.tolist(),'num_nodes':int(data.num_nodes),'num_edges':int(data.edge_index.shape[1])})
 prep={'source_sha256':row['sha256'],'source_bytes':source.stat().st_size,'source_lines':len(source.read_text().splitlines()),'route':route,'exact_extraction':exact,'large_lookup_entries':entries,'graph_extraction_seconds':time.monotonic()-start,'graph_nodes':graph.number_of_nodes(),'graph_edges':graph.number_of_edges(),'weakly_connected_components':networkx.number_weakly_connected_components(graph),'raw_label_counts':rawlabels,'feature_counts':dict(collections.Counter(str(x) for x in data.x.tolist())),'preprocessed_sha256':sha(target),'preprocessing':'Existing topModule.v passthrough; no flattening/renaming/underscore removal.','dataset_pickle_loaded':False,'truth_label_accessed':False,'placeholder_label':0,'messages':messages.splitlines()};save('preprocessing.json',prep)
 loader=DataLoader([data],shuffle=False,batch_size=1);results={}
 for name,model in models.items():
  with torch.no_grad():
   outs=[]
   for item in loader:
    item.to('cpu');emb,_=model.embed_graph(item.x,item.edge_index,item.batch);logits=model.mlp(emb);outs.append(F.log_softmax(logits,dim=1).cpu())
   outputs=torch.cat(outs).reshape(-1,2).detach();pred=outputs.max(1)[1].item();probs=torch.exp(outputs).numpy()[0]
  assert torch.isfinite(logits).all() and torch.isfinite(outputs).all() and numpy.isfinite(probs).all() and abs(float(probs.sum())-1)<1e-5
  results[name]={'prediction':int(pred),'label':'TROJAN' if pred else 'CLEAN','prob_clean':float(probs[0]),'prob_trojan':float(probs[1]),'log_probabilities':outputs.tolist()[0],'logits':logits.detach().cpu().tolist()[0]};print('DETECTOR_RESULT',name,json.dumps(results[name]),flush=True)
 assert len(results)==4 and sha(source)==row['sha256'];votes=[k for k,v in results.items() if v['prediction']==1]
 save('RESULTS.json',{'design_id':DESIGN,'status':'scored','source_sha256':row['sha256'],'per_model':results,'ensemble':{'prediction':int(bool(votes)),'label':'TROJAN' if votes else 'CLEAN','trojan_votes':len(votes),'triggered_models':votes,'rule':'any model argmax=1'},'preprocessing':prep,'source_unchanged':True});print('ALL_FOUR_COMPLETE',DESIGN,flush=True)
if __name__=='__main__':
 try:main()
 except BaseException as e:
  RUN.mkdir(parents=True,exist_ok=True);(RUN/'failure.txt').write_text(traceback.format_exc());save('FAILURE.json',{'design_id':DESIGN,'status':'unscored','error_type':type(e).__name__,'error':str(e),'prediction':None});traceback.print_exc();sys.exit(2)
