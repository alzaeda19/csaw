# AI records and authorship

This is an index of retained evidence, not a reconstructed conversation. Records cover this separate simulation package. They do not certify a complete history of the entire earlier project.

## Actual tools and authors

- Qwen3:8b ran locally through Ollama using model alias `qwen3-csaw-agent:20261112234518`. Claude Code was the file-tool interface; this is not a claim of Claude-model authorship.
- Qwen produced the initial RTL draft. Codex supplied substantial corrected RTL and authored/saved the final testbench and runner. The final result must not be described as solely Qwen-authored.
- Qwen had Read/Edit/Write/Glob/Grep tools in the separate work folder. Codex ran simulations independently. Model-written claims were not treated as test results.
- Exact configuration snapshots, launcher, prompts, raw streamed responses, native Qwen sessions, stderr/debug logs, tool errors, before/after file inventories, exits and hashes are preserved for each Qwen attempt.
- Codex model family is self-identified as GPT-6 in project context. Exact serving-model revision and sampling parameters are not independently established here.

## New Qwen interactions

| Folder under `qwen/` | Observed outcome |
| --- | --- |
| `20261113T002025Z_f8pf3qt7` | Initial RTL draft; model response completed, launcher exit 0. Subsequent simulation failed 9 ordinary checks. |
| `20261113T002330Z_nqwhdxe4` | Applied a Codex correction template with tool/order and copy errors. Launcher exit 2. Saved RTL contained Markdown fences/missing end; compiler exit 2. |
| `20261113T003819Z_540gdr_f` | Attempted final testbench save; timed out after 360 seconds, launcher exit 124. No completed response and no saved testbench; partial stream and native session retained. |

The timeout receipt's changed-path inventory includes `report/TECHNICAL_BRIEF.md`, which the Codex report subagent wrote concurrently. This is not evidence that Qwen wrote the report. Each receipt's before/after inventory reports observed changes, not causal attribution.

Codex then saved its validated final testbench template. See `evidence/setup_records/FINAL_FILE_PROVENANCE.json` and `CODEX_CORRECTIONS.json`. `controller_templates/` holds the exact prompts and successive correction/bench templates; those are supporting artifacts, not substitutes for authentic transcript records.

## Codex records

`codex_current_task/` contains a bounded, filtered native export of only the current generation/correction task, with an index, native line numbers and hashes. Read its export manifest for exact cutoff, filters and inaccessible fields. `reviewer_exports/` contains visible app exports for the two independent reviewers; app exports can truncate outputs and do not expose every delegation prompt. They are labeled accordingly.

The coding-interface launcher/configuration is preserved under `launcher_reference/`. These records retain original local paths. They document the actual interface; they are not a portable installer. The portable simulation entry point is `../run_tests.py`. Logs likewise retain their original absolute paths; packaged source files are self-contained relative to that runner.

## Earlier recovery records and limitations

Selected historical records are copied under `evidence/historical_recovery/`, including the recovery AI_RECORD, original delegated request, derivation script and tool-source metadata. All pre-existing project records remain in their original locations. They are not all duplicated in this focused archive.

Known gaps are explicit:

- Historical full conversations are not all available. The retained recovery AI_RECORD is a visible summary/command record, not a full native conversation.
- Encrypted native fields cannot be read or recreated. Some delegation prompt bodies are inaccessible; the bounded export records these omissions.
- Hidden reasoning, platform instructions, inherited/compacted earlier history, and unrelated conversation/sidebar metadata are intentionally excluded.
- Current native export ends at its stated snapshot. Subsequent archive sealing, verification and final user-facing reply fall after that cutoff; fresh run/packaging receipts provide execution evidence rather than invented dialogue.
- A timed-out Qwen response is incomplete by definition, even when every received byte is retained. No missing continuation has been fabricated.

The qualifier requires comprehensive generation prompts/responses. This package includes available authentic evidence and explicitly disclosed gaps; it does not claim that summaries or newly written logs eliminate missing historical records or guarantee rubric acceptance.

## Technical failures retained

`evidence/development_runs/` keeps initial normal-operation failures, the invalid copied RTL, the intermediate frame-delimiter failure (3 checks), and the corrected template preflight. `evidence/final_runs/` holds passing final saved-file runs and two deliberately broken controls that correctly fail. The latter are expected negative-control outcomes, not unresolved faults in the final tested design.
