# Read-only parent-script review

No concrete correctness correction is required within the stated normal-operation scope.

- Byte indexing checked against saved cofactor metadata: both output modes contain 32 distinct uninverted wires; all eight initial/feedback address-source permutations match byte-local ROR8(input,1), without extracting inversion signs; all four forward destination mappings match `(j+1)%4` with output-bit permutation `[0,4,2,6,1,5,3,7]`.
- **4,096 identities** is the correct count: four byte slots × 256 input values × four map equalities. Those are initial/feedback equality in each direction and the two inverse compositions. They are not 4,096 whole-word or clocked tests.
- The inverse formula `out[j] = S^-1(in[(j+1)%4]) XOR K[j]` and the inverse loop use the correct slot and mask index.
- The separate control proof enables four updates on launch-inclusive edges 1–4; edge 5, with CS high, loads the held result into the serial bank. The four-iteration composition matches this normal schedule. The pure composition script alone does not establish arbitrary clocked equivalence, as its limits already state.
- The runtime-key wording stays within normal-operation reconstruction. The fixed literal transformations, full register-role accounting, and disabled RAM writes support it. They do not establish the authored mask's provenance or redefine malformed/interrupted schedules as a supported interface.
- Identification of the normalized byte substitution as the AES S-box does **not** justify naming this 32-bit, four-update construction the standard AES block cipher.

No numeric K was calculated or emitted. No parent script was imported, run, or changed. The final source additions for environment overrides, fresh register-inventory checking, and serial-chain checking were inspected. The parent-reported separate Icarus results were not independently reviewed in this pass.

Exact reviewed input paths and SHA256 values are in `PARENT_SCRIPT_REVIEW.json`.
