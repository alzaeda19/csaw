"""Exhaustive one-byte source-function checks; never emit a key/mask value.

Uses the unchanged baseline's four fixed lookup tables and combinational D
equations. No HDL execution and no modified-design input.
"""
from pathlib import Path
import contextlib, io, json, re, hashlib, functools, datetime
OUT=Path(__file__).resolve().parent
captured=io.StringIO()
with contextlib.redirect_stdout(captured):
    import trace_datapath as dp
(OUT/'DATAPATH_RECHECK_STDOUT.json').write_text(captured.getvalue())
blocks=re.findall(r'SB_RAM40_4K\s*#\((.*?)\)\s*(ram40_\w+)\s*\((.*?)\);',dp.raw.decode(),re.S)
assert len(blocks)==4
tables=[]
for params,name,ports in blocks:
    init={int(k,16):int(v,16) for k,v in re.findall(r"\.INIT_([0-9A-F])\(256'h([0-9a-fA-F]+)\)",params)}
    assert len(init)==16 and re.search(r'\.READ_MODE\(1\)',params)
    rows=[(init[r//16]>>(16*(r%16)))&65535 for r in range(256)]
    table=[sum(((rows[x&127]>>(2*j+(x>>7)))&1)<<j for j in range(8)) for x in range(256)]
    assert hashlib.sha256(bytes(table)).hexdigest()=='ab40298c12186501c43297c3d81ee4fb8aabbe95246c8cd48bf5c231b07f173f'
    tables.append(table)
assert all(t==tables[0] for t in tables)
ALL=(1<<256)-1
patterns=[sum(((x>>bit)&1)<<x for x in range(256)) for bit in range(8)]
def byte_function(expressions,input_nets):
    env=dict(zip(input_nets,patterns))
    @functools.cache
    def v(x):
        if isinstance(x,int):return ALL if x else 0
        if isinstance(x,str):return env[x]
        if x[0]=='not':return ALL^v(x[1])
        c=v(x[1]);return (c&v(x[2]))|((ALL^c)&v(x[3]))
    outputs=[v(x) for x in expressions]
    return [sum(((bits>>x)&1)<<bit for bit,bits in enumerate(outputs)) for x in range(256)]
mode0=[x['function']['net'] for x in dp.outmap['0']]
mode1=[x['function']['net'] for x in dp.outmap['1']]
output_permutation=[0,4,2,6,1,5,3,7]
def reorder(value):return sum(((value>>s)&1)<<i for i,s in enumerate(output_permutation))
normal=[reorder(tables[0][(x>>1)|((x&1)<<7)]) for x in range(256)]
normal_hash=hashlib.sha256(bytes(normal)).hexdigest()
forward={};inverse={}
for phase,controls in [('initial',{'n485':0,'n383':0}),('feedback',{'n485':1,'n383':1})]:
    ex=dp.expand_for(dp.common|controls)
    forward[phase]=[];inverse[phase]=[]
    for source_byte in range(4):
        inputs=dp.serial[8*source_byte:8*source_byte+8] if phase=='initial' else mode0[8*source_byte:8*source_byte+8]
        addresses=byte_function([ex(n) for n in dp.memories[source_byte]['address_lsb_first']],inputs)
        forward[phase].append([reorder(tables[source_byte][addr]) for addr in addresses])
    for output_byte in range(4):
        input_byte=(output_byte+1)%4
        inputs=dp.serial[8*input_byte:8*input_byte+8] if phase=='initial' else mode1[8*input_byte:8*input_byte+8]
        expressions=[ex(dp.state[q]['data']) for q in mode1[8*output_byte:8*output_byte+8]]
        inverse[phase].append(byte_function(expressions,inputs))
checks=[];identities=0
for j in range(4):
    f=forward['initial'][j];g=inverse['initial'][j]
    checks.append({'byte_slot':j,'forward_output_slot':(j+1)%4,'inverse_input_slot':(j+1)%4,'forward_is_bijection':len(set(f))==256,'inverse_is_bijection':len(set(g))==256,'forward_initial_equals_feedback':f==forward['feedback'][j],'inverse_initial_equals_feedback':g==inverse['feedback'][j],'inverse_after_forward_all_256':all(g[f[x]]==x for x in range(256)),'forward_after_inverse_all_256':all(f[g[x]]==x for x in range(256))})
    assert all(value for key,value in checks[-1].items() if isinstance(value,bool))
    identities+=4*256
source_cones={}
for phase,co in dp.cofactors.items():
    source_cones[phase]={'forward_each_address_bit_is_one_literal':all(d['kind'] in {'wire','inverted_wire'} for byte in co['memory_addresses'] for d in byte),'inverse_groups':dp.groups[phase]}
result={'scope':'Exact single-byte combinational identities using original Boolean cones and fixed primitive lookup semantics; not a clocked HDL/silicon proof','source_sha256':hashlib.sha256(dp.raw).hexdigest(),'effective_table_sha256':hashlib.sha256(bytes(tables[0])).hexdigest(),'normalized_substitution_sha256':normal_hash,'standard_name_identified_by_this_script':False,'normalized_substitution_relation':'S(x) = output-bit permutation [0,4,2,6,1,5,3,7] of T(ROR8(x,1))','byte_checks':checks,'exact_identities_checked':identities,'all_pass':True,'round_equations':{'forward':'out[(j+1) mod 4] = S(in[j] XOR K[j]), j=0..3, bytes numbered least-significant first','inverse':'out[j] = inverse_S(in[(j+1) mod 4]) XOR K[j]','K':'Symbolic fixed byte masks represented by original per-wire inversions. Numeric mask/key values are not computed or emitted as an artifact. No runtime key input or update state is inferred.'},'source_cones':source_cones,'decoder_assumption':'Same READ_MODE=1 interpretation as the saved official primitive model analysis; this does not independently validate silicon RAM semantics.'}
(OUT/'BYTE_INVERSE_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'all_pass':True,'exact_identities_checked':identities,'byte_checks':checks,'normalized_substitution_sha256':normal_hash},indent=2))
