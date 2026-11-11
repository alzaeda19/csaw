# Revision note — AUDIT_FINDINGS.md correction (2026-11-11)

## Attribution
- **This revision:** a new, tool-disabled Claude Code document correction (session model `claude-opus-5-5`). It is based only on the original audit text, the original session record and the supplied verified source facts.
- **Original audit:** its attribution (configured model Claude Opus 4.8; serving model may differ) is retained as historical.
- **Original session record:** `AUDIT_SESSION_RECORD.md` is preserved unchanged as the authentic record of the original session. It is not rewritten, and this note does not alter it.

## Supplied verified facts used
- **Netlist:** `supplementary_clean_verification/synthesis_fit_timing_2026-11-06/runs/synthesize_repaired_02/mapped_clean.json`
  - 3,963,320 bytes.
  - sha256 `b9274fdac6870c7b04b67d73ae0206dab97d7f1d9da22793071aef823658e2d7`.
  - Listed in the existing manifest.
  - Top-level keys `creator` and `modules`; contains the protocol DUT module.
- **`readiness-review-stdout.json`:** `modelUsage` keys `claude-haiku-4-5-20251001` and `claude-opus-4-8`; `is_error` false.
- **`opus55-readiness-review-stdout.json`:** `modelUsage` key `claude-opus-5-5`; `is_error` false.
- **Two-transaction records:** `trace_audit.json`, `completion_review.json`, `result_matrix.json`, `final_seal_checks.json`.

## Corrections made
1. **Mapped netlist:** replaced 'NOT packaged / absent' with the verified path, size, full hash and manifest status.
   - It is described as a Yosys netlist JSON.
   - No Verilog-format mapped netlist is claimed.
   - The formal-proof JSONs are identified as separate records.
   - Recommendation 2, the results line and the limitations were updated to match.
2. **Model provenance:**
   - `readiness-review-stdout.json` now lists both `claude-opus-4-8` and `claude-haiku-4-5-20251001`, not Haiku-only.
   - The opus55 review lists `claude-opus-5-5`.
   - The older archived review is kept as a separate record.
   - Recommendation 3 was updated.
3. **Two-transaction supplement:** replaced 'one result file' with the four listed records. It is still characterized as a selected record subset, not full proof dependencies or raw solver logs.
4. **Integrity scope:** the 20/20 sample and the coverage check are now scoped as the earlier reviewer-reported result for the original 842-entry manifest and 843-file inventory.
   - The audit files were added afterward.
   - The current expanded tree is not claimed to be fully manifested.
   - No check was rerun.
5. **Synthesis bundle description:** corrected so it no longer implies the bundle holds only the three record files. The finding that raw synthesis run logs are absent is retained.

## Preserved unchanged
- The raw readiness/ROM/synthesis run-log absence finding.
- That historical reports are not fresh independent reruns.
- That a hash match proves integrity only.
- All retained failures, timeouts and untested items.
- The original assignment gaps:
  - Trojan-modified RTL and the demonstration testbench are absent.
  - The technical brief's proposed-cipher-explanation section is absent.
  - GenAI transcripts are partial.
  - Key recovery remains a bonus.
- Pending professor approval, and the unconfirmed deadline and destination.
- The original closeout's file and check record, kept as historical.

## Not done in this revision
- No tools were used: no file reads, hashing, script execution, simulation, synthesis, formal solving, detector inference or reruns.
- No cipher or design-logic analysis, RTL repair, hardware modification, Trojan generation or attack content.
- No commits, pushes, course approval or submission.
- No missing evidence was inferred.
