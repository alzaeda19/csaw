#!/usr/bin/env python3
"""Static Boolean proof of selected baseline control equations only.

No HDL execution, RTL mutation, ROM content decoding, synthesis or hardware access.
The parser discards INIT-bearing lines before extracting assignments.
"""
from pathlib import Path
import hashlib
import itertools
import json
import re

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/Users/al-zayedal-hassan/Documents/Codex/2026-11-10/referenced-chatgpt-conversation-this-is-an/work/csaw-github/fresh-clone/submission/rtl/baseline.v')
EXPECTED = '180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765'
data = SOURCE.read_bytes()
assert hashlib.sha256(data).hexdigest() == EXPECTED
lines = data.decode().splitlines()
assigns, ffs, inits = {}, {}, {}
for num, raw in enumerate(lines, 1):
    if re.search(r'\.INIT_', raw):
        continue
    line = re.sub(r'/\*.*?\*/', '', raw).strip()
    m = re.fullmatch(r'assign (\w+) = (.*);', line)
    if m:
        assigns[m[1]] = {'line': num, 'expr': m[2], 'source': raw}
    m = re.fullmatch(r'always @\(posedge (\w+)\) if \(([^)]+)\) (\w+) <= (\w+) \? (1\x27b[01]) : (\w+);', line)
    if m:
        ffs[m[3]] = dict(zip(['clock', 'enable', 'reg', 'reset', 'reset_value', 'data'], m.groups())) | {'line': num, 'source': raw}
    m = re.fullmatch(r'reg (\w+) = ([01]);', line)
    if m:
        inits[m[1]] = {'value': int(m[2]), 'line': num, 'source': raw}

class Expr:
    def __init__(self, text):
        self.tokens = re.findall(r"1'b[01]|[A-Za-z_]\w*|[!?:()]", text)
        self.i = 0
        self.tree = self.expr()
        assert self.i == len(self.tokens), (text, self.tokens[self.i:])

    def take(self):
        value = self.tokens[self.i]
        self.i += 1
        return value

    def expr(self):
        condition = self.unary()
        if self.i < len(self.tokens) and self.tokens[self.i] == '?':
            self.take()
            yes = self.expr()
            assert self.take() == ':'
            no = self.expr()
            return ('if', condition, yes, no)
        return condition

    def unary(self):
        token = self.take()
        if token == '!':
            return ('not', self.unary())
        if token == '(':
            value = self.expr()
            assert self.take() == ')'
            return value
        return ('leaf', token)

parsed = {}
def resolve(net, env):
    if net in env:
        return env[net]
    if net in ("1'b0", "1'b1"):
        return int(net[-1])
    assert net in assigns, ('Unexpected leaf outside the control cone', net)
    if net not in parsed:
        parsed[net] = Expr(assigns[net]['expr']).tree
    def tree_eval(tree):
        op, *args = tree
        if op == 'leaf':
            return resolve(args[0], env)
        if op == 'not':
            return 1 - tree_eval(args[0])
        return tree_eval(args[1] if tree_eval(args[0]) else args[2])
    result = tree_eval(parsed[net])
    env[net] = result
    return result

def next_reg(net, env):
    ff = ffs[net]
    if not resolve(ff['enable'], env):
        return env[net]
    return resolve(ff['reset_value'] if resolve(ff['reset'], env) else ff['data'], env)

names = ['n842', 'n840', 'n844', 'n846', 'n588', 'n972', 'io_13_31_1', 'io_18_31_1', 'io_17_31_0']
registers = ['n840', 'n842', 'n846', 'n844', 'n588', 'n972']
roots = ['n1', 'n2', 'n3', 'n681', 'n680', 'n845', 'n383', 'n485', 'n970', 'n749', 'io_8_31_1', 'io_19_31_0']
all_rows = []
check_count = 0
for bits in itertools.product((0, 1), repeat=len(names)):
    env = dict(zip(names, bits))
    ah, al, bh, bl, q, d, r, s, cs = bits
    a, b = ah | al, bh | bl
    busy = r & (s | a | b)
    expected_outputs = {
        'n1': (1-cs) | (1-r) | (d & (1-busy)),
        'n2': 1-r,
        'n3': (1-r) | s | b,
        'n681': (1-r) | s | a,
        'n680': (1-r) | (s & (1-a)),
        'n845': (1-r) | (s & (1-b)),
        'n383': r & b,
        'n485': r & a,
        'n970': 1-busy,
        'n749': r & (s | a),
        'io_8_31_1': busy,
        'io_19_31_0': busy,
    }
    expected_next = {
        'n840': r & (1-al) & (s | ah),
        'n842': r & (ah ^ al),
        'n846': r & (1-bl) & (s | bh),
        'n844': r & (bh ^ bl),
        'n588': r & (q | s | a),
        'n972': busy,
    }
    actual_outputs = {n: resolve(n, env) for n in roots}
    actual_next = {n: next_reg(n, env) for n in registers}
    assert actual_outputs == expected_outputs, (bits, actual_outputs, expected_outputs)
    assert actual_next == expected_next, (bits, actual_next, expected_next)
    check_count += len(expected_outputs) + len(expected_next)
    all_rows.append({'inputs': dict(zip(names, bits)), 'outputs': actual_outputs, 'next': actual_next})

# The qualifier appears only as an AND input to 32 directly assigned output gates.
# Enumerate those local two-input truth tables without inspecting their ROM drivers.
qualification = []
for net, info in assigns.items():
    if not re.search(r'\bn588\b', info['expr']):
        continue
    leaves = set(re.findall(r'\b(?:n\d+|io_\d+_\d+_\d+)\b', info['expr']))
    assert len(leaves) == 2 and 'n588' in leaves
    other = (leaves - {'n588'}).pop()
    for q, x in itertools.product((0, 1), repeat=2):
        assert resolve(net, {'n588': q, other: x}) == q & x
        check_count += 1
    qualification.append({'net': net, 'other_input': other, **info})
assert len(qualification) == 32

# This is a tabulation of the proven transition relation, not an HDL run.
# Phase rows specify the pre-edge control state and all sampled controls.
phase_specs = [
    ('reset edge', 0, 0, 1, 0, 0, 0, 0),
    ('idle / shift edge', 1, 0, 0, 0, 0, 0, 0),
    ('launch edge 1', 1, 1, 1, 0, 0, 0, 0),
    ('run edge 2', 1, 0, 1, 1, 1, 1, 1),
    ('run edge 3', 1, 0, 1, 2, 2, 1, 1),
    ('completion edge 4', 1, 0, 1, 3, 3, 1, 1),
    ('parallel-result load edge 5', 1, 0, 1, 0, 0, 1, 1),
    ('settled idle edge 6', 1, 0, 1, 0, 0, 1, 0),
]
phases = []
for label, r, s, cs, a, b, q, d in phase_specs:
    env = dict(zip(names, [a >> 1, a & 1, b >> 1, b & 1, q, d, r, s, cs]))
    pre = {n: resolve(n, env) for n in roots}
    nxt = {n: next_reg(n, env) for n in registers}
    post = {'A': 2*nxt['n842']+nxt['n840'], 'B': 2*nxt['n844']+nxt['n846'], 'Q': nxt['n588'], 'D': nxt['n972']}
    # START is lowered after the launch edge; other listed controls remain fixed.
    post_env = {'io_13_31_1': r, 'io_18_31_1': 0, 'io_17_31_0': cs, **nxt}
    post['BUSY_after_START_low'] = resolve('io_8_31_1', post_env)
    post['serial_enable_after_START_low'] = resolve('n1', post_env)
    phases.append({'label': label, 'pre': {'R': r, 'S': s, 'CS_N': cs, 'A': a, 'B': b, 'Q': q, 'D': d}, 'sampled_controls': pre, 'post': post})

selected_nets = set()
def walk(net):
    if net in selected_nets or net not in assigns:
        return
    selected_nets.add(net)
    for child in re.findall(r'\b(?:n\d+|io_\d+_\d+_\d+)\b', assigns[net]['expr']):
        walk(child)
for net in roots:
    walk(net)
for net in registers:
    for key in ['enable', 'reset', 'data']:
        walk(ffs[net][key])
source_refs = [{'kind': 'assignment', 'net': net, **assigns[net]} for net in selected_nets]
source_refs += [{'kind': 'register', 'net': net, **ffs[net]} for net in registers]
source_refs += [{'kind': 'initializer', 'net': net, **inits[net]} for net in registers]
source_refs += [{'kind': 'memory_read_pin', 'line': i, 'source': line} for i, line in enumerate(lines, 1) if '.RCLKE(' in line or '.RCLK(' in line]
source_refs.sort(key=lambda v: v['line'])

report = {
    'method': 'Static source-text parse; exhaustive evaluation of control-cone Boolean expressions and one-edge transition identities. No HDL execution; INIT lines excluded from parsing; no ROM values or key data extracted or interpreted.',
    'source': {'path': str(SOURCE), 'sha256': EXPECTED, 'lines': len(lines)},
    'variables': {'R': 'io_13_31_1 (active-low reset released)', 'S': 'io_18_31_1 (START)', 'CS_N': 'io_17_31_0', 'A': '(n842,n840), high then low', 'B': '(n844,n846), high then low', 'Q': 'n588', 'D': 'n972'},
    'equations': {
        'n840_next': 'R & ~n840 & (S | n842)', 'n842_next': 'R & (n842 XOR n840)',
        'n846_next': 'R & ~n846 & (S | n844)', 'n844_next': 'R & (n844 XOR n846)',
        'n588_next': 'R & (n588 | S | n840 | n842)', 'n972_next': 'BUSY',
        'n681': '~R | S | n840 | n842', 'n3': '~R | S | n844 | n846',
        'n680': '~R | (S & ~(n840 | n842))', 'n845': '~R | (S & ~(n844 | n846))',
        'n749_RAM_RCLKE': 'R & (S | n840 | n842)',
        'BUSY': 'R & (S | n840 | n842 | n844 | n846)',
        'n970': '~BUSY', 'n1': '~CS_N | ~R | (n972 & ~BUSY)',
    },
    'exhaustive_combinations': len(all_rows), 'checked_identities': check_count, 'passed': True,
    'qualification_gates': qualification, 'phase_table': phases, 'source_references': source_refs,
    'limits': ['The phase schedule assumes one sampled START=1 edge, then START=0, reset released, CS_N high through the post-completion result-load edge.', 'These proofs do not establish datapath arithmetic or ROM identity.', 'Both counter groups initialize to 00 and have identical update functions, so equality is an inductive invariant for every sampled R/S sequence.'],
}
(ROOT / 'CONTROL_FINDINGS.json').write_text(json.dumps(report, indent=2)+'\n')
(ROOT / 'CONTROL_TRUTH_TABLE.json').write_text(json.dumps(all_rows, indent=2)+'\n')
(ROOT / 'CONTROL_SOURCE_EXCERPTS.txt').write_text('\n'.join(f"{v['line']}: {v['source']}" for v in source_refs)+'\n')
print(json.dumps({'passed': True, 'input_combinations': len(all_rows), 'identities': check_count, 'qualifier_gates': len(qualification), 'source_sha256': EXPECTED}, indent=2))
