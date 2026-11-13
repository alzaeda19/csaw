"""One fixed-model evaluation of the two already validated, frozen graph inputs."""
from pathlib import Path
import sys,json,hashlib,time,platform
ROOT=Path(__file__).resolve().parents[1];PKG=ROOT/'package'
sys.path.insert(0,str(PKG/'hw2vec'))
import torch,numpy,networkx,torch_geometric,pyverilog
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from hw2vec.config import Config
from hw2vec.graph2vec.models import GRAPH2VEC,GRAPH_CONV,GRAPH_POOL,GRAPH_READOUT
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
OUT=ROOT/'analysis/inference';OUT.mkdir()
gate=json.loads((ROOT/'analysis/PRE_INFERENCE_GATES.json').read_text());assert gate['status']=='PASS'
initial=json.loads((ROOT/'records/INPUT_HASHES.json').read_text())['files']
for p,digest in initial.items():
 if p.startswith(('sources/','detectors/','package/model_')):assert sha(ROOT/p)==digest,p
extractor=ROOT/'package/hw2vec/hw2vec/hw2graph.py'
for item in gate['targets']:
 directory=ROOT/'detectors'/('repaired_'+item['candidate'])
 assert sha(directory/'model_input.json')==item['model_input_sha256']
 assert sha(directory/'graph_before_normalization.json')==item['graph_sha256']
 assert sha(extractor)==item['extractor_sha256']
torch.manual_seed(0);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
cfg=Config(['--yaml_path',str(PKG/'hw2vec/examples/example_gnn4tj.yaml'),'--data_pkl_path',str(ROOT/'runtime/UNUSED.pkl'),'--graph_type','DFG','--model_path','','--device','cpu']);cfg.num_feature_dim=37
versions={'python':platform.python_version(),'torch':torch.__version__,'torch_geometric':torch_geometric.__version__,'numpy':numpy.__version__,'networkx':networkx.__version__,'pyverilog':pyverilog.__version__};save(OUT/'VERSIONS.json',versions)
models={};identities=[]
for i in range(1,5):
 name='HT'+str(i);cp=PKG/('model_'+name)/'model.cfg';wp=cp.parent/'model.pth';mc=json.loads(cp.read_text())
 assert mc['convs'][0][1]==37 and mc['fc'][1]==2
 model=GRAPH2VEC(cfg);model.set_graph_conv([GRAPH_CONV(*c) for c in mc['convs']]);model.set_graph_pool(GRAPH_POOL(*mc['pool']));model.set_graph_readout(GRAPH_READOUT(mc['readout']));model.set_output_layer(nn.Linear(*mc['fc']))
 state=torch.load(str(wp),map_location='cpu',weights_only=True);assert isinstance(state,dict) and all(isinstance(v,torch.Tensor) for v in state.values())
 load=model.load_state_dict(state,strict=True);assert not load.missing_keys and not load.unexpected_keys
 models[name]=model.to('cpu').eval();identities.append({'model':name,'checkpoint_sha256':sha(wp),'config_sha256':sha(cp),'strict_load':True,'weights_only':True,'device':'cpu','training':model.training})
save(OUT/'MODEL_IDENTITIES.json',identities)
results=[]
for candidate in ['flat_clean','flat_modified']:
 directory=ROOT/'detectors'/('repaired_'+candidate);source=directory/'model_input.json';raw=json.loads(source.read_text())
 data=Data(x=torch.tensor(raw['x'],dtype=torch.long),edge_index=torch.tensor(raw['edge_index'],dtype=torch.long),num_nodes=raw['num_nodes'])
 assert data.x.tolist()==raw['x'] and data.edge_index.tolist()==raw['edge_index']
 loader=DataLoader([data],shuffle=False,batch_size=1);scores={}
 for name,model in models.items():
  with torch.no_grad():
   item=next(iter(loader));item.to('cpu');embedded,_=model.embed_graph(item.x,item.edge_index,item.batch);logits=model.mlp(embedded);outputs=F.log_softmax(logits,dim=1).cpu();probs=torch.exp(outputs).numpy()[0];prediction=outputs.max(1)[1].item()
  assert numpy.isfinite(probs).all() and abs(float(probs.sum())-1)<1e-5
  scores[name]={'prediction':int(prediction),'label':'TROJAN' if prediction else 'CLEAN','prob_clean':float(probs[0]),'prob_trojan':float(probs[1]),'log_probabilities':outputs.tolist()[0],'logits':logits.cpu().tolist()[0]}
 votes=[n for n,s in scores.items() if s['prediction']==1]
 result={'candidate':candidate,'input_sha256':sha(source),'graph_input_loaded_without_changes':True,'scores':scores,'ensemble':{'verdict':'TROJAN' if votes else 'CLEAN','triggered_models':votes,'rule':'Any model votes 1'},'scope':'Classification of the repaired validated dataflow representation; no full temporal/physical proof, calibration or universal stealth claim.'}
 results.append(result);save(OUT/(candidate+'.json'),result);print(json.dumps({'candidate':candidate,'ensemble':result['ensemble'],'trojan_scores':{k:v['prob_trojan'] for k,v in scores.items()}}),flush=True)
save(OUT/'RESULTS.json',{'runs':results,'checkpoint_candidate_classifications':8,'detector_or_design_tuning':False,'model_training':False,'graph_gates_passed_before_inference':True})
