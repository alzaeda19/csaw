# Bounded reviewer-record recovery

One of the two historical tool-output gaps is now fully covered by authentic captured text. The other remains incomplete. **None of the twelve missing reviewer instruction bodies was recovered.** This does not complete the generation/review transcript.

This audit compares the two saved normal chat-API projections with exactly the twelve entries in `inputs/PROMPT_GAPS.json` and the two retained entries in `inputs/SOURCE_TRUNCATIONS.json`. All fourteen selected native source-line hashes and byte lengths match the published gap records. No historical command, project test, model generation or solution lookup was performed. The repository and original evidence are unchanged.

| Record | Newly recovered | What remains |
|---|---:|---|
| Twelve reviewer instructions: nine requests and three steering messages | None | All twelve ordinary instruction bodies remain unavailable. Native records retain a routing wrapper plus an opaque body. API snapshots cover all nine reviewer turns but expose no user message or instruction text. |
| Report reviewer native line 100; API item `exec-84b0552d-5f11-464f-b396-05908175e4f9` | Four characters beyond the previously retained head | 6,178 characters remain missing in the middle of the reported 46,178-character stdout. |
| Report reviewer native line 107; API item `exec-6d9dc924-b32b-4b14-920f-bcc70d5fad38` | 10,140 formerly missing characters | No stdout character gap remains in the derived 28,140-character assembly. This is an assembly of authentic fragments, not a newly retrieved full raw transcript. |

For line 107, parsing its ordinary JSON tool-result wrapper yields a 9,000-character head and a 9,000-character tail around the original truncation marker. The API contains the first 20,000 characters. Its final 860 characters exactly match the first 860 characters of the native tail, uniquely within that API prefix, at original offset 19,140. Joining the API prefix with the remainder of the native tail produces 28,140 characters, matching the API's original-length metadata and both retained native fragments. No missing text is guessed.

For line 100, the native head is 19,996 characters, while the API prefix is 20,000. The native tail begins at original offset 26,178 and contains 20,000 characters. The unresolved original range is therefore `[20000, 26178)`. The four additional authentic characters are saved separately; no placeholder is inserted into a purported complete output.

All ranges are zero-based Unicode character offsets, not byte positions or token counts. Original token-truncation markers and API truncation flags are retained unchanged. The former 2,535-token marker belongs to the now-covered output; the other output originally reported 1,546 omitted tokens, but no revised token count is inferred from character counts.

## Source identity and reproducibility

- Protocol reviewer: `01a1d245-26de-7730-8903-654a1eb4004d` (`api_protocol.json`, five turns).
- Report reviewer: `01a1d245-3808-71b3-a696-a4f14fca0a76` (`api_report.json`, four turns).
- Target output turn: `01a1d25f-d0b3-78e2-8959-429ec689173c`.
- Output native lines: 100 and 107 of the report-review session; exact source paths, line hashes, timestamps and call IDs are in `inputs/NATIVE_SOURCE_RECEIPT.json`.
- `RECEIPT.json` records every comparison, source hash, retained range and assembly segment. `recovered/report_line_107_stdout_assembled.txt` is the complete derived stdout. The original captures remain separate.
- The two API files are pre-existing filtered snapshots, not full raw API responses. Their projection notes explicitly exclude reasoning/internal content and preserve exact target command outputs. No new chat read or higher-limit retry was needed during the resumed overlap comparison.
- To repeat the bounded comparison, copy this entire folder to a new location and run `python3 audit.py` there. Once its saved inputs and source receipt exist, the script requires no original Mac paths, native sessions, repository or network. Do not rerun it inside the sealed evidence folder.

## Execution and record limits

The audit script completed with exit code zero; stdout, stderr, interpreter version, command and time are in `EXECUTION.json` and `audit_execution.*`. This checks record integrity and overlap only, not hardware correctness.

Earlier exploratory tool display exceeded the available context and was truncated. Both saved API files survived intact; the resumed check worked directly on those files and verified their exact target lengths. A later status-only command searching this audit folder for Markdown/result files returned exit code 1 because none yet existed; this was not a failed recovery or a missing API capture. These events are preserved in the bounded current-chat export where available. The coordinator separately reported a rejected above-limit API request; that was not executed here and supplies no recovered text. No such request was repeated.

`ai_records/` preserves a bounded exact-field projection of this audit's own visible native records, with a cutoff, per-source-line hashes, field pointers and omission reasons. It excludes hidden reasoning, platform instructions, opaque payloads and duplicate app events. It includes the intervening plain-English status handoff and the resumed recovery instructions because they occurred inside this audit interval. This audit record is separate from the twelve historical missing messages and does not repair them. Final sealing and handoff messages after its snapshot are not claimed to be included.

The audit snapshot retains 46 visible records and verifies 309 scalar field values against native lines 2051–2227, ending at 2026-11-13 05:49:01.562 UTC. It lists 131 excluded internal/context/event records. No selected visible record required an opaque-field omission in this snapshot. The exporter exited zero. Both saved API files and all historical selected output strings remain unchanged; source-line identity checks do not claim to decrypt unavailable instruction bodies.

Recommended handoff wording: **Twelve reviewer instruction bodies remain unavailable. Of two historical truncated tool outputs, one is now fully covered by a documented assembly of authentic captures; the other still lacks 6,178 characters. The AI trail remains incomplete.**
