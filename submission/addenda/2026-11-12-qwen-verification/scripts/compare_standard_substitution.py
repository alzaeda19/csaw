"""Compare original lookup properties with the public AES standard, not a challenge solution."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
def multiply(a,b):
    result=0
    for _ in range(8):
        if b&1: result ^= a
        a = ((a<<1) ^ (0x11b if a&0x80 else 0)) & 255
        b >>= 1
    return result
def power(a,n):
    result=1
    while n:
        if n&1:result=multiply(result,a)
        a=multiply(a,a);n>>=1
    return result
def rotate(a,n):return ((a<<n)|(a>>(8-n)))&255
def standard_sbox(a):
    inverse=power(a,254) if a else 0
    return inverse ^ rotate(inverse,1) ^ rotate(inverse,2) ^ rotate(inverse,3) ^ rotate(inverse,4) ^ 0x63
sbox=[standard_sbox(i) for i in range(256)]
assert sbox[0]==0x63 and sbox[0x53]==0xed and len(set(sbox))==256
inverse=[sbox.index(i) for i in range(256)]
source=(ROOT/'sources/baseline.v').read_text()
blocks=re.findall(r'SB_RAM40_4K\s*#\((.*?)\)\s*(ram40_\w+)\s*\((.*?)\);',source,re.S)
comparisons=[]
for params,name,ports in blocks:
    init={int(k,16):int(v,16) for k,v in re.findall(r'\.INIT_([0-9A-F])\(256\'h([0-9a-fA-F]+)\)',params)}
    rows=[(init[i//16]>>(16*(i%16)))&65535 for i in range(256)]
    table=[sum(((rows[x&127]>>(2*j+(x>>7)))&1)<<j for j in range(8)) for x in range(256)]
    comparisons.append({'instance':name,'entries_compared':256,'matches_AES_SBOX_exact_effective_order':table==sbox,'matches_AES_inverse_SBOX_exact_effective_order':table==inverse})
result={'reference':'https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf','reference_scope':'Sections 4 and 5.1.1, equation 5.3 and Table 4; independently implemented finite-field/affine definition. Public standard, no challenge solution.', 'standard_sbox_sha256':hashlib.sha256(bytes(sbox)).hexdigest(),'comparisons':comparisons,'whole_cipher_identified':False,'key_extraction_performed':False,'limitation':'A matching component does not identify the surrounding 32-bit cipher or its key schedule. A mismatch in this effective order does not rule out an algorithm with different bit wiring.'}
(ROOT/'analysis/STANDARD_SUBSTITUTION_COMPARISON.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
