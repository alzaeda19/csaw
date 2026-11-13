# Bounded own-chat evidence inventory

Prepared November 12, 2026 (Eastern). This read-only search covers relevant own Codex/ChatGPT conversations and previously retained clean records. It does not change the design, run experiments, edit a repository, or publish anything. The coordinating chat separately handles Claude Desktop, Claude Code and Qwen records.

## Findings

**No original visible copy of the 12 missing reviewer instruction bodies was found. No new verified cipher identification was found.** The relevant earlier clean discussions describe interface behavior, serial-buffer readiness and verification limits. They explicitly distinguish structural RTL recovery and known-answer checks from identifying the cipher or recovering a key.

| Source, using its actual title | Search boundary | Result |
| --- | --- | --- |
| **CSAW original-materials protocol review** | Four API pages, all 18 visible turns; native records compared with the existing clean export | 118 retained visible records: 115 exact prior overlaps and three additional November 11 status records. All 100 assistant texts match the paginated API. No November 12 reviewer instruction bodies or complete cipher explanation. |
| **Verify regenerated CSAW bitstream** | One API page, all four visible turns | 14 retained messages/excerpts: three user requests and 11 assistant responses. None exactly matches the five prior indexed visible-message files used for comparison. Engineering facts overlap existing evidence; this is not a claim of 14 new technical discoveries. |
| **Troubleshoot dot issues** | Human-named ChatGPT reference, two pages, all five API-visible turns | Four narrowly selected, exact project caveat excerpts retained. They distinguish the supplied AES kit from recovered FPGA RTL and explain why structural recovery or one test pair does not identify a cipher. Attachments and solution links were not opened. Support correspondence, unrelated business content and potential solution-derived details are not exported. |
| Original protocol/report reviewer chats | All five protocol and four report turns available through the thread API | No user-message/delegation prompt bodies returned. Existing reviewer finals are already covered by the published addendum. The same 12 encrypted sender/recipient exchanges remain unavailable. |
| **Inspect TrojanGYM course package (2)** | Latest four turn requests/status metadata, following one older-page cursor | Latest code-generation request has failed status and no assistant response. Older requests/pasted audit narratives are not implementation evidence. Older fork history was not exhaustively reviewed or exported. |

See [clean-thread report](records/clean_protocol_history/REPORT.md), [three additional status records](records/clean_protocol_history/ADDITIONAL_NOV11_STATUS_RECORDS.jsonl), [bitstream-history report](records/bitstream_history/REPORT.md), and [named ChatGPT excerpts](records/TROUBLESHOOT_DOT_SAFE_EXCERPTS.json).

## Claims versus verified evidence

The clean chat's readout explanation is consistent with the original-source analysis already published in the current addendum: a separate serial-load boundary follows BUSY falling. This inventory did not rerun or extend that analysis. No earlier algorithm/key claim is promoted into the encryption explanation.

The bitstream chat's November 11 recap still describes equivalence as unresolved in that chat. That must not replace the broader project's later completed digital-model-equivalence evidence: the retained baseline-equivalence report and root-tail final already report conditional passes. A later-dated recap can still omit work completed in another chat. The bitstream report flags this limitation explicitly.

The named ChatGPT conversation contains historical status and quoted third-party narratives. These are conversation claims, not authentic original Claude transcripts or new execution receipts. Only the four safe caveats are retained, with message IDs and exact character offsets. Its discussion acknowledging excluded solution-assisted history was not used to infer a key or cipher.

## Overlap and novelty limits

The 115 clean-history overlaps are exact comparisons with the November 10 native clean export. Three later status records were outside that old cutoff. The separate bitstream comparison uses five enumerated prior message files; no-match does not establish absence from every possible archive.

An additional check compared the 14 bitstream records, three added clean-status records and four ChatGPT excerpts against 220 text entries/parsed visible JSON strings in the **published 311-file ZIP at commit c5021a4e04205b45d778d216177669164aee68e2**. None of the 21 complete retained strings matched that ZIP. This does not exhaust the additional files elsewhere in the 1,185-file repository. The published ZIP's verified local hash is `4e158096547a915fc35a913f9d7481da20149dfd5a02428a8793af163df469ef`. See [comparison receipt](verification/PUBLISHED_ZIP_TEXT_OVERLAP.json). The initial seven-record comparison is retained separately; the corrected comparison accounts for all 21 records/excerpts.

## Discovery and exclusions

Codex active/archived history metadata produced eight relevant candidates. ChatGPT metadata search scanned six pages / 300 active summaries and the archived list, using CSAW/Trojan/Qwen keywords. It found no keyword match. The explicitly named **Troubleshoot dot issues** chat was then retrieved directly; its nondescript title illustrates why keyword discovery alone is incomplete. No broader account search was continued after the coordinating chat requested this bounded inventory be finished.

Unrelated titles/body content were not retained. Presentation chats, the coordinating chat's own work, pre-clean/solution-comparison portions of the main **trojan** chat, and the unreviewed **trojan (2)** fork remain outside this content review. Shared/Jordan Claude sources, published solutions, solution diagrams, hidden reasoning, encrypted values and unrelated private content were excluded. No attempt was made to decrypt missing prompts or invent dialogue.

## Remaining gaps

API-complete here means every visible turn returned by the selected chat API was paginated to its end. It does **not** mean an unabridged native export: reasoning, platform instructions, encrypted bodies, unavailable tool content and deliberate privacy exclusions are not included.

- The same 12 encrypted reviewer instruction bodies remain inaccessible; this search adds no replacement text.
- The two previously documented report-review tool outputs remain truncated (1,546 and 2,535 omitted tokens). The incomplete Qwen timeout is not repaired by unrelated older messages; no completed response existed for that timeout.
- The collected architecture/timing discussions do not establish named cipher identity, table/key semantics or cryptographic strength.
- Only enumerated histories and comparison sets were checked. Unreviewed older forks, nondescript account chats, attachments and inaccessible original sources are not claimed complete.
- Historical claims and saved record hashes establish provenance/consistency, not new test passes or instructor acceptance.

The original sealed package and the already-published addendum were preserved. A staging manifest and verification receipts identify every output. This inventory is local and has not been pushed or submitted by this chat.
