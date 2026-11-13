"""Original-source reconstruction; no challenge solution or modified RTL used.

The original-derived constant mask is used internally for verification. This
script reports its handling, not a numeric bonus-key recovery claim.
"""
from pathlib import Path
import hashlib
import json
import random
from baseline_model import Model, ROOT

def gf_mul(a,b):
    result=0
    while b:
        if b&1: result^=a
        a=((a<<1)^(0x11b if a&128 else 0))&255
        b>>=1
    return result

def gf_pow(a,n):
    result=1
    while n:
        if n&1: result=gf_mul(result,a)
        a=gf_mul(a,a);n>>=1
    return result

def rol8(x,n): return ((x<<n)|(x>>(8-n)))&255
def rol32(x,n): return ((x<<n)|(x>>(32-n)))&0xffffffff

SBOX=[]
for x in range(256):
    q=gf_pow(x,254) if x else 0
    SBOX.append(q^rol8(q,1)^rol8(q,2)^rol8(q,3)^rol8(q,4)^0x63)
INV_SBOX=[SBOX.index(x) for x in range(256)]

def sub(word,table): return sum(table[(word>>(8*i))&255]<<(8*i) for i in range(4))

class Reconstructed:
    def __init__(self,model):
        self.model=model
        # Derive final output packing independently by walking basis states.
        self.working=[None]*32
        for net in model.work:
            model.reset_state();model.state[net]=1
            value=self.parallel_output(1)
            assert value and value&(value-1)==0,(net,value)
            bit=value.bit_length()-1;assert self.working[bit] is None
            self.working[bit]=net
        assert None not in self.working
        self.rom_to_word={}
        for name in model.memories:
            for bit in range(8):
                model.reset_state();model.memory[name]=1<<bit
                value=self.parallel_output(0)
                assert value and value&(value-1)==0,(name,bit,value)
                self.rom_to_word[name,bit]=value.bit_length()-1
        assert len(set(self.rom_to_word.values()))==32
        # Source byte j enters RAM j; its output moves to byte j+1 mod 4.
        self.rom_order=sorted(model.memories,key=lambda name:self.rom_to_word[name,0])
        self.source_byte={name:((min(self.rom_to_word[name,b] for b in range(8))//8)-1)%4 for name in model.memories}
        model.reset_state();v=model.comb()
        mask=0
        for name,functions in model.mem_functions.items():
            address=sum(eval(a,{'__builtins__':{}},v)<<i for i,a in enumerate(functions[0]))
            effective=(address&127)|((address>>1)&128)
            mask|=rol8(effective,1)<<(8*self.source_byte[name])
        self._fixed_mask=mask

    def parallel_output(self,mode):
        m=self.model;saved=dict(m.state)
        m.state.update(n840=0,n842=0,n844=0,n846=0,n588=1,n972=1)
        v=m.comb(ENC_DEC=mode)
        assert v['n1']==1
        word=sum(eval(m.reg_functions[n][1],{'__builtins__':{}},v)<<i for i,n in enumerate(m.serial))
        m.state=saved
        return word

    def forward(self,word): return rol32(sub(word^self._fixed_mask,SBOX),8)
    def inverse(self,word): return sub(rol32(word,24),INV_SBOX)^self._fixed_mask
    def cipher(self,word,mode):
        for _ in range(4):word=(self.inverse if mode else self.forward)(word)
        return word

    def normalization(self):
        m=self.model;tables=[]
        for name,ram in m.memories.items():
            table=[]
            for x in range(256):
                effective=rol8(x,7)
                address=(effective&127)|((effective&128)<<1)
                row=ram['rows'][address&255]
                raw=sum(((row>>(2*j+((address>>8)&1)))&1)<<j for j in range(8))
                logical=sum(((raw>>b)&1)<<(self.rom_to_word[name,b]%8) for b in range(8))
                table.append(logical)
            tables.append({'memory':name,'matches_AES_sbox':table==SBOX,'entries_checked':256,'sha256':hashlib.sha256(bytes(table)).hexdigest()})
        assert all(t['matches_AES_sbox'] for t in tables)
        return tables

def cases():
    values=[0,0xffffffff,0xaaaaaaaa,0x55555555,0x59c359c3,0x9cd84392]
    values += [1<<b for b in range(32)]
    # Every byte value in each position, plus mixed deterministic random words.
    values += [v<<(8*b) for b in range(4) for v in range(256)]
    rng=random.Random(20261112);values += [rng.getrandbits(32) for _ in range(256)]
    return sorted(set(values))

def main():
    m=Model();r=Reconstructed(m);normalization=r.normalization()
    vectors=cases();rows=[];phase_checks=0
    for word in vectors:
        for mode in [0,1]:
            m.reset_state();m.tick(RST_N=0);m.tick(RST_N=0)
            for b in range(31,-1,-1):m.tick(NORM_CS_N=0,MOSI=(word>>b)&1,ENC_DEC=mode)
            forward=inverse=word
            for phase in range(4):
                m.tick(START=int(phase==0),ENC_DEC=mode)
                forward=r.forward(forward);inverse=r.inverse(inverse)
                actual_f=r.parallel_output(0);actual_d=r.parallel_output(1)
                assert (forward,inverse)==(actual_f,actual_d),(hex(word),mode,phase,'round mismatch')
                phase_checks+=2
            for _ in range(4):m.tick(ENC_DEC=mode)
            observed=0
            for _ in range(32):
                v=m.tick(NORM_CS_N=0,ENC_DEC=mode);observed=(observed<<1)|v['io_16_31_1']
            expected=r.cipher(word,mode)
            assert observed==expected,(hex(word),mode,'serial mismatch')
            assert r.cipher(expected,1-mode)==word
            rows.append({'input':f'{word:08x}','mode':mode,'expected':f'{expected:08x}'})
    report={'original_sha256':hashlib.sha256((ROOT/'sources/baseline.v').read_bytes()).hexdigest(),'normalization':normalization,'unique_input_words':len(vectors),'transactions':len(rows),'per_path_round_state_checks':phase_checks,'serial_matches':len(rows),'roundtrip_checks':len(rows),'mismatches':0,'algorithm':{'word_bits':32,'rounds':4,'forward_round':'ROL32(SubBytes_AES(state XOR K),8)','inverse_round':'InvSubBytes_AES(ROR32(state,8)) XOR K','K_handling':'One fixed 32-bit source-derived inversion mask, reused unchanged each round. Not a runtime input or an evolving key schedule. Numeric bonus-key claim outside this report.','mode':'0 selects forward state; 1 selects inverse state; both paths compute concurrently.'},'working_registers_lsb_first':r.working,'rom_output_to_word_bit':{f'{name}:{bit}':dest for (name,bit),dest in r.rom_to_word.items()},'limits':['Python model initializes unobservable RAM read outputs to zero; Icarus cross-check uses original primitive unknown initial state.','Finite vector/phase comparisons; separate structural cofactor checks support byte separation and fixed routing.','No physical board or timing validation.']}
    (ROOT/'analysis/RECONSTRUCTION_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'verification/VECTORS.json').write_text(json.dumps(rows,indent=2)+'\n')
    (ROOT/'verification/vectors.txt').write_text(''.join(f"{v['input']} {v['mode']} {v['expected']}\n" for v in rows))
    print(json.dumps({k:report[k] for k in ['unique_input_words','transactions','per_path_round_state_checks','serial_matches','roundtrip_checks','mismatches']}))

if __name__=='__main__':main()
