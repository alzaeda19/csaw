"""Static Boolean cofactors of original recovered RTL; no INIT interpretation."""
from pathlib import Path
import re, json, hashlib, functools, collections, datetime, os
OUT=Path(__file__).resolve().parent
SOURCE=Path(os.environ.get('CSAW_BASELINE_SOURCE','/Users/al-zayedal-hassan/Documents/Codex/2026-11-10/referenced-chatgpt-conversation-this-is-an/work/csaw-github/fresh-clone/submission/rtl/baseline.v')).resolve()
INVENTORY=Path(os.environ.get('CSAW_STATIC_INVENTORY',str(SOURCE.parents[1]/'addenda/2026-11-12/explanation/STATIC_BASELINE_ANALYSIS.json'))).resolve()
raw=SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765'
inventory=json.loads(INVENTORY.read_text())
assert inventory['source']['sha256']==hashlib.sha256(raw).hexdigest()
parsed_state={}
for line,text in enumerate(raw.decode().splitlines(),1):
    m=re.search(r'always @\(posedge (\w+)\) if \((.*?)\) (\w+) <= (.*?) \? (.*?) : (.*?);',text)
    if m:parsed_state[m[3]]=dict(line=line,clock=m[1],enable=m[2],reset=m[4],reset_value=m[5],data=m[6])
assert set(parsed_state)==set(inventory['state'])
for q,actual in parsed_state.items():
    assert all(inventory['state'][q][k]==v for k,v in actual.items())
assigns={}
for line,text in enumerate(raw.decode().splitlines(),1):
    if re.search(r'\.INIT_[0-9A-F]+\(',text):continue
    m=re.search(r'\bassign\s+(\w+)\s*=\s*(.*?);',text)
    if m:assigns[m[1]]={'line':line,'expression':re.sub(r'/\*.*?\*/','',m[2]).strip()}
class Parser:
    def __init__(self,s):
        self.tokens=re.findall(r"1'b[01]|[A-Za-z_][A-Za-z_0-9]*|[!?:()]",s)
        assert ''.join(self.tokens)==re.sub(r'\s+','',s)
        self.i=0
    def take(self):
        a=self.tokens[self.i];self.i+=1;return a
    def atom(self):
        a=self.take()
        if a=='!':return ('not',self.atom())
        if a=='(':
            v=self.expr();assert self.take()==')';return v
        if a in ["1'b0","1'b1"]:return int(a[-1])
        return a
    def expr(self):
        a=self.atom()
        if self.i<len(self.tokens) and self.tokens[self.i]=='?':
            self.take();b=self.expr();assert self.take()==':';c=self.expr();return ('if',a,b,c)
        return a
trees={}
for n,v in assigns.items():
    p=Parser(v['expression']);trees[n]=p.expr();assert p.i==len(p.tokens)
state=inventory['state']
serial=inventory['serial_path_MOSI_to_last_register']
work=inventory['working_registers']
memories=[]
for m in inventory['memories']:
    addr=list(reversed(m['connections']['RADDR']['value'].strip('{}').split(', ')))
    data=list(reversed(m['connections']['RDATA']['value'].strip('{}').split(', ')))
    memories.append({'source_line':m['line'],'address_lsb_first':[addr[i] for i in [0,1,2,3,4,5,6,8]],'data_lsb_first':[data[i] for i in range(0,16,2)]})
def neg(a):
    if isinstance(a,int):return 1-a
    if isinstance(a,tuple) and a[0]=='not':return a[1]
    return ('not',a)
def ite(c,a,b):
    if isinstance(c,int):return a if c else b
    if a==b:return a
    if a==1 and b==0:return c
    if a==0 and b==1:return neg(c)
    if isinstance(c,tuple) and c[0]=='not':return ite(c[1],b,a)
    return ('if',c,a,b)
def expand_for(env):
    @functools.cache
    def ex(x):
        if isinstance(x,int):return x
        if isinstance(x,str):
            if x in env:return env[x]
            if x in trees:return ex(trees[x])
            return x
        if x[0]=='not':return neg(ex(x[1]))
        c=ex(x[1])
        if isinstance(c,int):return ex(x[2] if c else x[3])
        return ite(c,ex(x[2]),ex(x[3]))
    return ex
@functools.cache
def leaves(x):
    if isinstance(x,int):return frozenset()
    if isinstance(x,str):return frozenset([x])
    return frozenset().union(*(leaves(y) for y in x[1:]))
def evaluate(x,env):
    if isinstance(x,int):return x
    if isinstance(x,str):return env[x]
    if x[0]=='not':return 1-evaluate(x[1],env)
    return evaluate(x[2] if evaluate(x[1],env) else x[3],env)
def characterize(x):
    ls=sorted(leaves(x))
    if len(ls)==0:return {'kind':'constant','value':x}
    if len(ls)==1:
        vals=[evaluate(x,{ls[0]:i}) for i in [0,1]]
        if vals==[0,1]:return {'kind':'wire','net':ls[0]}
        if vals==[1,0]:return {'kind':'inverted_wire','net':ls[0]}
        return {'kind':'constant_after_truth_check','value':vals[0]}
    return {'kind':'multi_input_boolean','leaves':ls,'leaf_count':len(ls)}
common={'io_13_31_1':1,'io_17_31_0':1,'n588':1}
shift_check=expand_for({'io_17_31_0':0})
assert len(serial)==32 and len(set(serial))==32
for i,q in enumerate(serial):
    assert state[q]['enable']=='n1'
    assert characterize(shift_check(state[q]['data']))=={'kind':'wire','net':serial[i-1] if i else 'io_16_31_0'}
assert set(work)=={q for q,s in parsed_state.items() if s['enable']=='n3' and q not in {'n844','n846'}}
cofactors={}
for name,extra in [('initial',{'n485':0,'n383':0}),('feedback',{'n485':1,'n383':1})]:
    ex=expand_for(common|extra)
    cofactors[name]={'memory_addresses':[[characterize(ex(x)) for x in m['address_lsb_first']] for m in memories], 'working_D':{q:characterize(ex(state[q]['data'])) for q in work}}
outmap={}
for mode in [0,1]:
    ex=expand_for(common|{'io_19_31_1':mode})
    outmap[str(mode)]=[{'serial_word_bit':i,'serial_register':q,'D_line':assigns[state[q]['data']]['line'],'function':characterize(ex(state[q]['data']))} for i,q in enumerate(serial)]
# Group working-register cones by their independent input leaves. Values of any
# fixed transformation constants are deliberately not reported as secret keys.
groups={}
for phase,co in cofactors.items():
    gs=collections.defaultdict(list)
    for q,d in co['working_D'].items():gs[tuple(d.get('leaves',[d.get('net')]))].append(q)
    groups[phase]=[{'input_nets':list(k),'output_registers':v,'input_count':len(k),'output_count':len(v)} for k,v in gs.items()]
result={'method':'Static source AST substitution and small Boolean truth checking; INIT excluded; no clocked target execution','source':{'path':str(SOURCE),'sha256':hashlib.sha256(raw).hexdigest()},'source_lines':{n:x['line'] for n,x in assigns.items()},'memories':memories,'serial_lsb_first':serial,'cofactors':cofactors,'parallel_load_by_mode':outmap,'working_cone_groups':groups}
(OUT/'DATAPATH_COFACTORS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'memory_addresses':{k:v['memory_addresses'] for k,v in cofactors.items()},'working_groups':groups,'output_mapping_kinds':{k:dict(collections.Counter(v['function']['kind'] for v in vals)) for k,vals in outmap.items()}},indent=2))
