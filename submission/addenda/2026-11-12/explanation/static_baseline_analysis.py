#!/usr/bin/env python3
"""Static text/connectivity analysis only. No HDL execution or INIT decoding.

The only design input is the fixed original recovered baseline. RAM INIT lines
are discarded before parsing and neither interpreted nor copied to outputs.
"""
import collections
import hashlib
import itertools
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
SOURCE = Path('/Users/al-zayedal-hassan/Documents/CSAW_Qwen_Submission_20261113T001822Z_9sj2k3k6/package/submission/rtl/baseline.v')
EXPECTED = '180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765'
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == EXPECTED
original_lines = raw.decode().splitlines()
lines = [(i, s) for i, s in enumerate(original_lines, 1) if not re.search(r'\.INIT_[0-9A-F]+\(', s)]

assigns, state, memories = {}, {}, []
for i, line in lines:
    m = re.search(r'\bassign\s+(\w+)\s*=\s*(.*?);', line)
    if m:
        assigns[m[1]] = {'line': i, 'expr': re.sub(r'/\*.*?\*/', '', m[2]).strip(), 'lut': '/* LUT' in line}
    m = re.search(r'always @\(posedge (\w+)\) if \((.*?)\) (\w+) <= (.*?) \? (.*?) : (.*?);', line)
    if m:
        state[m[3]] = dict(line=i, clock=m[1], enable=m[2], reset=m[4], reset_value=m[5], data=m[6])
    if line.startswith('SB_RAM40_4K'):
        memories.append({'line': i, 'connections': {}})
    m = re.match(r'\s*\.(READ_MODE|WRITE_MODE|WADDR|RADDR|MASK|WDATA|RDATA|WE|WCLKE|WCLK|RE|RCLKE|RCLK)\((.*)\)', line)
    if m:
        memories[-1]['connections'][m[1]] = {'line': i, 'value': m[2]}

def refs(expr):
    return sorted(set(re.findall(r'\b(?:n\d+|io_\d+_\d+_\d+)\b', expr)))

def leaves(net, seen=None):
    if net in state or net not in assigns:
        return {net}
    seen = set() if seen is None else seen
    if net in seen:
        raise ValueError('Unexpected combinational cycle: ' + net)
    return set().union(*(leaves(r, seen | {net}) for r in refs(assigns[net]['expr'])))

def alias(net):
    chain=[]
    while net in assigns:
        item=assigns[net]
        chain.append({'net':net, **item})
        if not re.fullmatch(r'n\d+', item['expr']):
            break
        net=item['expr']
    return chain

# Small syntax parser for conditional Boolean expressions used in the recovered
# LUT assignments. Used only to substitute CS=0 in each serial register D input.
# It does not step state, evaluate memory, or execute Verilog.
class Expr:
    def __init__(self, s):
        self.tokens=re.findall(r"1'b[01]|[A-Za-z_][A-Za-z_0-9]*|[!?:()]",s); self.pos=0
    def take(self):
        x=self.tokens[self.pos]; self.pos+=1; return x
    def parse(self):
        x=self.take()
        if x=='!': a=('not',self.atom())
        elif x=='(': a=self.parse(); assert self.take()==')'
        else: a=x
        if self.pos<len(self.tokens) and self.tokens[self.pos]=='?':
            self.take(); b=self.parse(); assert self.take()==':'; c=self.parse(); a=('if',a,b,c)
        return a
    def atom(self):
        x=self.take()
        if x=='!': return ('not',self.atom())
        if x=='(':
            a=self.parse(); assert self.take()==')'; return a
        return x

def substitute(node, env):
    if isinstance(node,str): return env.get(node,node)
    parts=[substitute(p,env) for p in node[1:]]
    if node[0]=='not':
        return {'1\'b0':'1\'b1','1\'b1':'1\'b0'}.get(parts[0],('not',parts[0])) if isinstance(parts[0],str) else ('not',parts[0])
    c,a,b=parts
    if c=="1'b0": return b
    if c=="1'b1": return a
    if a==b: return a
    if a=="1'b1" and b=="1'b0": return c
    if a=="1'b0" and b=="1'b1": return ('not',c)
    return ('if',c,a,b)

def boolean(net, env):
    if net in env: return env[net]
    if net=="1'b0": return False
    if net=="1'b1": return True
    if isinstance(net, tuple):
        if net[0]=='not': return not boolean(net[1],env)
        return boolean(net[2],env) if boolean(net[1],env) else boolean(net[3],env)
    p=Expr(assigns[net]['expr']); a=p.parse(); assert p.pos==len(p.tokens)
    return boolean(a,env)

# Exhaustive combinational identity check, not a clocked execution.
variables=['n972','io_17_31_0','io_13_31_1','io_18_31_1','n840','n842','n844','n846']
checks=0
for bits in itertools.product([False,True], repeat=len(variables)):
    e=dict(zip(variables,bits))
    busy=e['io_13_31_1'] and (e['io_18_31_1'] or e['n840'] or e['n842'] or e['n844'] or e['n846'])
    en1=not e['io_17_31_0'] or not e['io_13_31_1'] or (e['n972'] and not busy)
    en3=not e['io_13_31_1'] or e['io_18_31_1'] or e['n844'] or e['n846']
    assert boolean('io_8_31_1',e)==busy
    assert boolean('n1',e)==en1
    assert boolean('n3',e)==en3
    checks+=3

serial={}
for q,s in state.items():
    if s['enable']=='n1':
        chain=alias(s['data']); expr=chain[-1]['expr']; p=Expr(expr); ast=p.parse(); assert p.pos==len(p.tokens)
        serial[q]={'ff_line':s['line'],'data_line':chain[-1]['line'],'selected_data_CS_low':substitute(ast,{'io_17_31_0':"1'b0"})}
successors={s['selected_data_CS_low']:q for q,s in serial.items() if isinstance(s['selected_data_CS_low'],str)}
if len(successors)!=len(serial):
    print(json.dumps({'serial_diagnostic': serial}, indent=2))
assert len(successors)==len(serial)
serial_order=[]; prev='io_16_31_0'
while prev in successors:
    prev=successors[prev]; assert prev not in serial_order; serial_order.append(prev)
assert len(serial_order)==len(serial)

for q,s in state.items():
    s['data_combinational_leaves']=sorted(leaves(s['data']))
    s['data_assignment_chain']=alias(s['data'])

control_names=['n1','n2','n3','n5','n466','n749','n681','n680','n845','n383','n485','n970','io_8_31_1','io_19_31_0','n972','n588','n840','n842','n844','n846']
out={
 'method':'Static source-text parsing, register grouping, combinational leaf traversal, and CS-low Boolean substitution. No HDL or attack execution; no INIT interpretation.',
 'source':{'path':str(SOURCE),'sha256':EXPECTED,'bytes':len(raw),'lines':len(original_lines)},
 'counts':{'ram_primitives':len(memories),'lut_assignments':sum(a['lut'] for a in assigns.values()),'continuous_assignments':len(assigns),'posedge_registers':len(state),'registers_by_enable':dict(collections.Counter(s['enable'] for s in state.values())),'registers_by_clock':dict(collections.Counter(s['clock'] for s in state.values())),'init_lines_excluded':len(original_lines)-len(lines)},
 'memories':memories,
 'serial_path_MOSI_to_last_register':serial_order,
 'serial_path_evidence':serial,
 'working_registers':[q for q,s in state.items() if s['enable']=='n3' and q not in ('n844','n846')],
 'state':state,
 'control_alias_chains':{n:alias(n) for n in control_names},
 'control_boolean_identity_checks':{'assignments':2**len(variables),'checks':checks,'passed':True,'definitions':{'BUSY':'RST_N && (START || n840 || n842 || n844 || n846)','n1':'!NORM_CS_N || !RST_N || (n972 && !BUSY)','n3':'!RST_N || START || n844 || n846','n972':'previous-rising-edge BUSY when not reset'}},
 'mode_direct_lut_consumers':[{'net':n,**a} for n,a in assigns.items() if 'io_19_31_1' in refs(a['expr'])],
 'qualification_bit_direct_lut_consumers':[{'net':n,**a} for n,a in assigns.items() if 'n588' in refs(a['expr'])],
 'notes':['Register count excludes RAM-internal read pipeline state.','LUT and FF comments describe recovered logic-cell positions, not independently instantiated LUT/FF primitive counts.','No algorithm or key interpretation is performed.']
}
(OUT/'STATIC_BASELINE_ANALYSIS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'source':out['source'],'counts':out['counts'],'serial_path':serial_order,'mode_direct_lut_consumers':len(out['mode_direct_lut_consumers'])},indent=2))
