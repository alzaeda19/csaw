"""Inspect original fixed storage and count mapped resources; never extract a key."""
from pathlib import Path
import hashlib
import itertools
import json
import re

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT/'sources/baseline.v').read_text()
blocks = re.findall(r'SB_RAM40_4K\s*#\((.*?)\)\s*(ram40_\w+)\s*\((.*?)\);', source, re.S)
assert len(blocks) == 4
tables, details = {}, []
for params, name, ports in blocks:
    init = {int(k,16): int(v,16) for k,v in re.findall(r'\.INIT_([0-9A-F])\(256\'h([0-9a-fA-F]+)\)', params)}
    assert len(init) == 16
    assert re.search(r'\.READ_MODE\(1\)', params)
    addr = re.search(r'\.RADDR\(\{([^}]+)\}\)', ports).group(1).split(', ')
    assert len(addr) == 11 and addr[:2] == ["1'b0", "1'b0"] and addr[3] == "1'b0"
    assert len([a for a in addr if a != "1'b0"]) == 8
    rows = [(init[row//16] >> (16*(row%16))) & 65535 for row in range(256)]
    # Derived from the supplied SB_RAM40_4K READ_MODE=1 model:
    # RADDR[7:0] selects a row; RADDR[8] selects one interleaved byte.
    table = [sum(((rows[x & 127] >> (2*j+(x>>7))) & 1) << j for j in range(8)) for x in range(256)]
    tables[name] = table
    linear_basis = [table[1<<i] ^ table[0] for i in range(8)]
    affine = all(table[x] == table[0] ^ __import__('functools').reduce(int.__xor__, (linear_basis[i] for i in range(8) if x & (1<<i)), 0) for x in range(256))
    details.append({'instance': name, 'read_mode': 1, 'effective_address_bits': 8, 'effective_entries': 256, 'connected_output_bits': 8, 'distinct_outputs': len(set(table)), 'is_bijection': len(set(table)) == 256, 'is_affine_over_bits': affine, 'effective_table_sha256': hashlib.sha256(bytes(table)).hexdigest(), 'write_clock_net': 'n5', 'write_clock_enable_net': 'n5', 'write_enable_net': 'n466'})
pairs = [{'a':a,'b':b,'identical_in_effective_bit_order':tables[a]==tables[b],'inverse_in_effective_bit_order':all(tables[a][tables[b][i]]==i for i in range(256))} for a,b in itertools.combinations(tables,2)]
memory = {'method':'Decoded effective table properties from original INIT payloads using the supplied primitive model; raw values are not emitted. Effective address order is not claimed to equal algorithm byte order.', 'memories':details, 'pairs':pairs, 'key_recovered':False, 'named_cipher_identified':False, 'scope_limit':'Fixed initialized storage is observed; this does not identify a key, cipher, key schedule, or secret-bearing meaning.'}
(ROOT/'analysis/MEMORY_PROPERTIES.json').write_text(json.dumps(memory,indent=2)+'\n')
counts={}
for kind in ['baseline','modified']:
    d=json.loads((ROOT/'synthesis'/kind/'stats.json').read_text())['design']['num_cells_by_type']
    counts[kind]={'lut4':d.get('SB_LUT4',0),'flip_flops':sum(v for k,v in d.items() if k.startswith('SB_DFF')),'ram4k':d.get('SB_RAM40_4K',0),'carry':d.get('SB_CARRY',0),'total_cells_excluding_scopeinfo':sum(v for k,v in d.items() if k!='$scopeinfo')}
delta={k:{'baseline':counts['baseline'][k],'modified':counts['modified'][k],'added':counts['modified'][k]-counts['baseline'][k],'percent':round(100*(counts['modified'][k]-counts['baseline'][k])/counts['baseline'][k],4) if counts['baseline'][k] else None} for k in counts['baseline']}
result={'method':'Same installed Yosys synth_ice40 defaults, same frozen baseline and respective frozen wrappers; mapped primitive counts, no placement/routing/timing or power result.', 'resources':delta,'negligible_overhead_established':False}
(ROOT/'analysis/OVERHEAD.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'memory_properties':details,'table_pair_relations':pairs,'resources':delta},indent=2))
