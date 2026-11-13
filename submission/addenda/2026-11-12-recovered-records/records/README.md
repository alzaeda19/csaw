# CSAW: fetched records and what they establish

Collected November 12, 2026, Eastern time (November 13 UTC). This is a separate local evidence collection. It has not been added to GitHub. The existing CSAW repository and tested design were not changed or executed during this collection.

## Main finding

The submitted design's saved Qwen generation records and Claude Code review files were already present in the repository. Additional authentic setup records were recovered, but they do not establish the cipher's identity or fill the twelve unreadable reviewer instructions. Some older AI statements are unsupported or rely on published material and must not be used as technical evidence.

## What was fetched

| Source | Coverage and useful result | Limitation |
|---|---|---|
| Qwen terminal history | An exact snapshot of the saved prompt history: 100 lines, 9,105 bytes. Useful for documenting earlier requests. | Contains prompts, not replies or reliable turn timestamps. Live Terminal access was blocked by the computer-use tool; no bypass was attempted. |
| Qwen agent setup | Prompts, available replies, receipts and errors from 15 saved setup attempts. There are 10 response files. Useful for documenting connection tests, tool errors and refinements. | Several records are overlapping resumed sessions. They are not 15 independent design-generation conversations, and completion labels do not prove correctness. |
| Final Qwen submission records | Compared 51 source files across the three generation attempts and separate Codex/reviewer records with their published copies. All matched; the three saved live streams also matched. | This confirms preservation of the saved files, not the existence of replies that were never produced. |
| Claude Code reviews | Copied three saved review/model-probe output files. All already match the repository copies. | The visible cloud session list contained no own CSAW session. This does not prove no other local or account history exists. |
| Claude Desktop | Inspected selected visible messages from three relevant own chats and saved a scoped excerpt of the historical repository audit with provenance. | This is partial UI coverage, not three complete native conversation exports. The older audit describes an earlier package, so its missing-file statements are stale. |
| Trojan/CSAW chats | The Trojan orchestrator reviewed relevant visible histories and searched for original copies of missing instructions and prior cipher explanations. Its separate inventory records precise coverage. | Visible API messages are not equivalent to complete native transcripts. No unreadable message was reconstructed or decrypted. |

The local source-copy receipt covers **63 byte-identical file copies**. Of these, **45 have no byte-identical match in the current repository**. Those are file counts, not 45 new conversations or missing generation prompts. Most are setup records and the old prompt-history snapshot.

The orchestrator's sealed 27-file inventory is also copied into `trojan_chat_inventory/`. It includes three additional November 11 status records, fourteen bitstream-history messages, and four narrowly selected caveat excerpts from the named ChatGPT conversation. None of those 21 complete strings exactly matched the published submission ZIP in the recorded comparison; this does not establish absence from every other repository file. The clean protocol history also preserves 115 records that overlap a prior export. See [its detailed coverage report](trojan_chat_inventory/README.md).

## Material that must not become submission claims

- **Old Claude qualifier plan:** it explicitly says its baseline came from published architecture. Its code, cipher details and archive were excluded under the no-published-solutions rule. Only a short source-origin observation was retained to explain the exclusion.
- **Early Qwen draft:** it claims AES-128 and an archive ready for submission. Its recorded run had a tool error and exit code 2; the claimed archive is absent. The two draft documents are retained under `unverified_qwen_drafts` solely as evidence of an erroneous model output. They do not identify the recovered cipher or prove a build, test or submission.
- **Professor's AES package and detector experiments:** those are separate from identifying the recovered FPGA cipher or proving the current modified design's behavior.
- **Shared Claude Code session:** another person's shared session was excluded. It is not evidence of this user's independent work.

## What still remains unresolved

1. **Encryption explanation:** the current repository contains a source-supported architectural proposal. Exact algorithm identity, lookup-table meanings, round equations and key handling are still unestablished. This search found no independent earlier explanation that closes those gaps. The qualifier asks for a proposed explanation; uncertainty about these details should remain visible rather than be replaced with an unsupported AES claim.
2. **AI-record completeness:** twelve reviewer instruction bodies remain unreadable (nine requests and three steering messages). Two original tool outputs remain truncated, with 1,546 and 2,535 tokens omitted. Older interactive Qwen replies and some complete historical conversations were not recovered. Missing replies must not be recreated as if they were originals.
3. **Limits of the saved tests:** the repository contains modified RTL, a demonstration testbench and saved passing ordinary/demonstration results. Those finite tests do not establish universal normal-operation preservation, stealth, negligible hardware cost or fully automated generation. This collection did not rerun tests or strengthen those technical claims.
4. **Delivery and acceptance:** the public GitHub package exists, and collaborator invitations remain skipped as requested. Instructor receipt, acceptance and grade are not verified. This newly fetched local bundle is not yet part of that published package.

Board programming and key recovery are not newly missing mandatory tasks: the original qualifier is simulation-only, and key recovery is a bonus. The defensive alternative was not approved. Paper 5 is a separate assignment.

## How to use these records

Use the authentic setup prompts, errors and refinements as supplementary process evidence. Keep the existing final generation logs as the main source for code authorship. Use Claude's historical audit only for the version it reviewed. Keep unsupported model outputs clearly labeled, and keep solution-derived technical material excluded. Any later publication should carry the coverage limitations and source receipts with the records; it should not claim that all AI history was recovered.

## Files in this collection

- `SOURCE_COPY_RECEIPTS.json`: original paths, byte counts, SHA-256 hashes and existing-repository matches for the 63 copied files.
- `QWEN_SETUP_INVENTORY.json`: the 15 saved setup attempts and their actual statuses.
- `CURRENT_QWEN_COMPARISON.json`: preservation checks for the final submission records.
- `FETCH_VERIFICATION.json`: verification of copied sources and the recorded access limitation.
- `ui_observations/PROVENANCE.json`: exactly which Claude UI portions were observed, with native tool-record provenance.
- `COLLECTION_NOTES.md`: collection decisions, errors and refinements.
- `CONVERSATION_INVENTORY_RECEIPT.json`: verified receipt for the orchestrator's sealed chat inventory; all 27 copied files match the originals.
- `MANIFEST.json`: hashes of all final files in this local bundle, excluding the manifest itself.

Repository assessed: https://github.com/alzaeda19/csaw, commit `c5021a4e04205b45d778d216177669164aee68e2`. Existing published limitations: https://github.com/alzaeda19/csaw/blob/main/SUBMISSION_GAPS.md.
