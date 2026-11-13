"""Check normal-interface state roles without emitting fixed mask/key values."""
from pathlib import Path
import contextlib,io,json,hashlib,re,os
OUT=Path(__file__).resolve().parent
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    import check_byte_inverse as b
dp=b.dp
(OUT/'BYTE_RECHECK_STDOUT.json').write_text(buf.getvalue())
old=dp.expand_for({'io_13_31_1':1,'io_17_31_0':1,'n485':0,'n383':0,'n588':0})
new=dp.expand_for({'io_13_31_1':1,'io_17_31_0':1,'n485':0,'n383':0,'n588':1})
qual_checks=[]
for mi,m in enumerate(dp.memories):
    for bit,n in enumerate(m['address_lsb_first']):
        assert dp.characterize(old(n))==dp.characterize(new(n))
        qual_checks.append({'memory':mi,'effective_address_bit':bit,'first_step_independent_of_old_ROM_qualifier':True})
initial_serial=set(dp.serial)
assert all(set(g['input_nets'])<=initial_serial for g in dp.groups['initial'])
constant=dp.expand_for({})
memory_write=[]
for m in dp.inventory['memories']:
    c=m['connections']
    actual={k:constant(c[k]['value']) for k in ['WCLK','WCLKE','WE']}
    assert actual=={'WCLK':0,'WCLKE':0,'WE':1}
    memory_write.append({'source_line':m['line'],'WCLK_constant_zero':True,'WCLKE_constant_zero':True,'WE_constant_one':True})
def enc(word):
    state=[(word>>(8*j))&255 for j in range(4)]
    for _ in range(4):
        out=[0]*4
        for j in range(4):out[(j+1)%4]=b.forward['initial'][j][state[j]]
        state=out
    return sum(x<<(8*j) for j,x in enumerate(state))
def dec(word):
    state=[(word>>(8*j))&255 for j in range(4)]
    for _ in range(4):state=[b.inverse['initial'][j][state[(j+1)%4]] for j in range(4)]
    return sum(x<<(8*j) for j,x in enumerate(state))
host=Path(os.environ.get('CSAW_ORIGINAL_HOST_SOURCE',str(dp.SOURCE.parents[1]/'evidence/original_materials/qualifier/spi_ice40_crypto_ip_test.py'))).resolve()
h=host.read_bytes()
def given_word(name):
    body=re.search(name+r'\s*=\s*bytearray\(\[([^]]+)\]\)',h.decode()).group(1)
    octets=bytes(int(x.strip(),16) for x in body.split(','));assert len(octets)==4
    return int.from_bytes(octets,'big')
pt=given_word('plaintext');ct=given_word('ciphertext')
assert enc(pt)==ct and dec(ct)==pt
report={'source_sha256':hashlib.sha256(dp.raw).hexdigest(),'scope':'Normal prescribed launch from idle; independent combinational phase model, not an HDL or silicon run','known_pair':{'original_host_path':str(host),'original_host_sha256':hashlib.sha256(h).hexdigest(),'plaintext':f'{pt:08X}','ciphertext':f'{ct:08X}','four_round_encryption_matches':True,'four_round_decryption_matches':True,'independent_vector_pairs':1},'first_step_qualifier_checks':qual_checks,'initial_inverse_cones_use_only_current_serial_payload':True,'memory_write_controls':memory_write,'state_accounting':{'native_registers':len(dp.state),'serial_payload_result_bank':len(dp.serial),'inverse_datapath_bank':len(dp.work),'two_two_bit_phase_counters':4,'ROM_output_qualifier':1,'previous_BUSY':1,'registered_serial_output':1,'RAM_storage':'Four fixed initialized lookup memories; registered read pipeline is transient data, not a runtime writable key store'},'fixed_handling':'The same per-byte literal inversions occur in initial and feedback address wiring, with corresponding inverse operations in the Boolean path. K is a symbolic fixed 32-bit XOR mask, repeated each of four rounds; no numeric key/mask is emitted. No independent runtime key register, key-input transaction or round-key schedule is present in this normal-operation reconstruction.','limits':['No claim about original authored source variable names or the provenance/intent of the fixed mask.','Does not treat malformed or deliberately interrupted protocol sequences as a specified key-loading interface.','No hardware, arbitrary-protocol, primitive-model or full-clocked-equivalence proof from this script.'],'byte_dependence_inference':'Each round rotates whole bytes and applies independent byte bijections. Four rotations restore byte positions, so each final byte depends only on the corresponding input byte and fixed masks. This is a structural inference from the verified component maps, not a cryptographic-strength claim.'}
(OUT/'KEY_HANDLING_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'known_pair':report['known_pair'],'first_step_qualifier_checks':len(qual_checks),'fixed_storage_controls_pass':True,'state_accounting':report['state_accounting']},indent=2))
