"""Strict Boolean/ROM interpreter of the original recovered baseline.

Only whitelisted one-bit Verilog expressions are parsed; no source commands,
system tasks, arbitrary Python, or external files are executed from the RTL.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
EXPECTED='180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765'

class Parser:
    def __init__(self,text):
        self.tokens=re.findall(r"1'b[01]|[A-Za-z_]\w*|[()!?:]",text)
        assert ''.join(self.tokens)==re.sub(r'\s+','',text),text
        self.i=0
    def take(self,expected=None):
        t=self.tokens[self.i];self.i+=1
        if expected is not None:assert t==expected,(expected,t)
        return t
    def unary(self):
        t=self.take()
        if t=='!':return ('not',self.unary())
        if t=='(':
            a=self.expression();self.take(')');return a
        if t in ("1'b0","1'b1"):return ('const',int(t[-1]))
        assert re.fullmatch(r'n\d+|io_\d+_\d+_\d+|open_\d+',t),t
        return ('var',t)
    def expression(self):
        a=self.unary()
        if self.i<len(self.tokens) and self.tokens[self.i]=='?':
            self.take('?');b=self.expression();self.take(':');c=self.expression();return ('ite',a,b,c)
        return a
    def parse(self):
        a=self.expression();assert self.i==len(self.tokens);return a

def refs(a):
    if a[0]=='var':return {a[1]}
    if a[0]=='const':return set()
    return set().union(*(refs(x) for x in a[1:]))
def render(a):
    if a[0] in ('var','const'):return str(a[1])
    if a[0]=='not':return '(1 ^ '+render(a[1])+')'
    if a[0]=='ite':return '('+render(a[2])+' if '+render(a[1])+' else '+render(a[3])+')'
    raise ValueError(a)

class Model:
    functional_ports={'SCK':'io_9_31_1','RST_N':'io_13_31_1','MOSI':'io_16_31_0','NORM_CS_N':'io_17_31_0','START':'io_18_31_1','ENC_DEC':'io_19_31_1'}
    def __init__(self):
        path=ROOT/'sources/baseline.v';raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
        text=re.sub(r'/\*.*?\*/','',raw.decode(),flags=re.S)
        text=re.sub(r'//[^\n]*','',text)
        pairs=re.findall(r'assign\s+(\w+)\s*=\s*(.*?);',text)
        self.assigns={name:Parser(expr).parse() for name,expr in pairs};assert len(self.assigns)==len(pairs)==2738
        self.registers={}
        for clock,enable,name,expr in re.findall(r'always\s*@\(posedge\s+(\w+)\)\s*if\s*\(([^)]+)\)\s*(\w+)\s*<=\s*(.*?);',text):
            assert clock=='io_9_31_1';self.registers[name]=(Parser(enable).parse(),Parser(expr).parse())
        assert len(self.registers)==71
        self.memories={}
        for params,name,ports in re.findall(r'SB_RAM40_4K\s*#\((.*?)\)\s*(ram40_\w+)\s*\((.*?)\);',text,re.S):
            init={int(k,16):int(v,16) for k,v in re.findall(r"\.INIT_([0-9A-F])\(256'h([0-9a-fA-F]+)\)",params)}
            assert len(init)==16 and re.search(r'\.READ_MODE\(1\)',params)
            rows=[(init[i//16]>>(16*(i%16)))&65535 for i in range(256)]
            p={k:v for k,v in re.findall(r'\.(\w+)\(([^()]*)\)',ports)}
            address=[Parser(v.strip()).parse() for v in p['RADDR'].strip('{}').split(',')][::-1]
            outputs=[v.strip() for v in p['RDATA'].strip('{}').split(',')][::-1]
            assert p['RCLK']=='io_9_31_1' and p['WCLK']==p['WCLKE']=='n5'
            self.memories[name]={'rows':rows,'address':address,'outputs':outputs,'enable':Parser(p['RCLKE']).parse(),'re':Parser(p['RE']).parse()}
        assert len(self.memories)==4
        roots=set(self.registers)|set(self.functional_ports.values())|{n for m in self.memories.values() for n in m['outputs']}
        ordered=[];done=set(roots);pending=dict(self.assigns)
        while pending:
            batch=[n for n,a in pending.items() if refs(a)<=done]
            assert batch,{'unresolved':{n:sorted(refs(a)-done) for n,a in list(pending.items())[:8]}}
            for n in batch:ordered.append(n);done.add(n);del pending[n]
        lines=['def comb(state, ports, memory):']
        for n in sorted(self.registers):lines.append(f'    {n} = state[{n!r}]')
        for n in sorted(self.functional_ports.values()):lines.append(f'    {n} = ports[{n!r}]')
        for name,m in self.memories.items():
            for i,n in enumerate(m['outputs']):lines.append(f'    {n} = '+(f'((memory[{name!r}] >> {i//2}) & 1)' if i%2==0 else '0'))
        for n in ordered:lines.append(f'    {n} = {render(self.assigns[n])}')
        lines.append('    return locals()')
        env={};exec(compile('\n'.join(lines),'<validated-original-boolean-model>','exec'),{'__builtins__':{'locals':locals}},env);self._comb=env['comb']
        self.reg_functions={n:(compile(render(e),'<enable>','eval'),compile(render(d),'<data>','eval')) for n,(e,d) in self.registers.items()}
        self.mem_functions={name:([compile(render(a),'<address>','eval') for a in m['address']],compile(render(m['enable']),'<enable>','eval'),compile(render(m['re']),'<read-enable>','eval')) for name,m in self.memories.items()}
        inv=json.loads((ROOT/'sources/static_inventory.json').read_text());self.serial=inv['serial_path_MOSI_to_last_register'];self.work=inv['working_registers']
        self.reset_state()
    def reset_state(self):
        self.state={n:0 for n in self.registers};self.memory={n:0 for n in self.memories}
    def ports(self,**kwargs):
        values={'SCK':0,'RST_N':1,'MOSI':0,'NORM_CS_N':1,'START':0,'ENC_DEC':0};values.update(kwargs)
        return {self.functional_ports[k]:int(v) for k,v in values.items()}
    def comb(self,**kwargs):return self._comb(self.state,self.ports(**kwargs),self.memory)
    def tick(self,**kwargs):
        v=self.comb(**kwargs);new=dict(self.state);mem=dict(self.memory)
        for n,(enable,data) in self.reg_functions.items():
            if eval(enable,{'__builtins__':{}},v):new[n]=eval(data,{'__builtins__':{}},v)
        for name,(address,enable,re_) in self.mem_functions.items():
            if eval(enable,{'__builtins__':{}},v) and eval(re_,{'__builtins__':{}},v):
                addr=sum(eval(a,{'__builtins__':{}},v)<<i for i,a in enumerate(address));row=self.memories[name]['rows'][addr&255]
                mem[name]=sum(((row>>(2*j+((addr>>8)&1)))&1)<<j for j in range(8))
        self.state=new;self.memory=mem
        return self.comb(**kwargs)
    def word(self,names):return sum(self.state[n]<<i for i,n in enumerate(names))
    def snapshot(self,**kwargs):
        v=self.comb(**kwargs)
        addr={name:sum(eval(a,{'__builtins__':{}},v)<<i for i,a in enumerate(fs[0])) for name,fs in self.mem_functions.items()}
        return {'serial_word':f'{self.word(self.serial):08x}','working_word_packed':f'{self.word(self.work):08x}','control':{n:v[n] for n in ['n840','n842','n844','n846','n588','n972','n1','n3','n681','n749','io_8_31_1']},'RAM_addresses':addr,'RAM_output_bytes':dict(self.memory)}
    def transaction(self,word,mode,trace=False):
        self.reset_state();self.tick(RST_N=0);self.tick(RST_N=0)
        for bit in range(31,-1,-1):self.tick(NORM_CS_N=0,MOSI=(word>>bit)&1,ENC_DEC=mode)
        rows=[{'phase':'loaded',**self.snapshot(ENC_DEC=mode)}]
        self.tick(START=1,ENC_DEC=mode);rows.append({'phase':'launch',**self.snapshot(START=1,ENC_DEC=mode)})
        for i in range(7):
            self.tick(ENC_DEC=mode);rows.append({'phase':f'process_{i+1}',**self.snapshot(ENC_DEC=mode)})
        result=0
        for _ in range(32):
            v=self.tick(NORM_CS_N=0,ENC_DEC=mode);result=(result<<1)|v['io_16_31_1']
        return (result,rows) if trace else result

if __name__=='__main__':
    model=Model();cases=[]
    for word,mode,expected in [(0x59C359C3,0,0x9CD84392),(0x9CD84392,1,0x59C359C3)]:
        result,rows=model.transaction(word,mode,True);cases.append({'input':f'{word:08x}','mode':mode,'output':f'{result:08x}','expected':f'{expected:08x}','matches':result==expected,'trace':rows})
    (ROOT/'analysis/INITIAL_MODEL_TRACE.json').write_text(json.dumps({'cases':cases,'model_counts':{'assignments':len(model.assigns),'registers':len(model.registers),'memories':len(model.memories)}},indent=2)+'\n')
    print(json.dumps([{k:v for k,v in c.items() if k!='trace'} for c in cases],indent=2));assert all(c['matches'] for c in cases)
