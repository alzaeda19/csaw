# Recovered records — publication supplement

This supplement adds the separately collected Claude, Qwen and Trojan-chat records to the submission. The [101-file collection](records/README.md) is preserved byte-for-byte, with its [original manifest](records/MANIFEST.json) and [copy receipt](COPY_RECEIPT.json). Its statements that the collection was local or not yet uploaded describe the collection stage; this supplement is included in the current GitHub package and downloadable ZIP.

## What these records contribute

| Source | Added evidence | Coverage limits |
|---|---|---|
| Qwen setup and terminal | Prompts, available responses, receipts and errors for 15 setup attempts; a 100-line native prompt-history snapshot. | Setup sessions overlap. The history contains no replies or reliable timestamps. Live terminal scrollback was inaccessible. |
| Claude Desktop and Code | Saved review outputs and scoped UI observations from relevant own chats. | The review files already matched the repository. UI coverage is partial, and the older repository audit describes an earlier package. |
| Trojan/CSAW conversations | Three additional clean-history status messages, 14 bitstream-history messages and four exact, narrowly selected caveat excerpts. | Exact-string comparisons are bounded to the enumerated prior exports and published ZIP. These are not 21 new technical findings or a complete export of every conversation. |
| Current generation-file comparison | All 51 compared source files and the three received Qwen streams matched published copies. | This confirms preservation, not recovery of nonexistent or unreadable responses. |

The original source-copy inventory contains 63 files, of which 45 had no identical file anywhere in the repository at the collection cutoff. The separate sealed chat inventory contains 27 files. The collection's remaining files are indexes, checks and new annotations. Counts refer to files or messages as labeled, not independent experiments.

## How to interpret failed drafts

The two [early Qwen drafts](records/unverified_qwen_drafts/README.md) are retained as erroneous model-output evidence. Their run had a tool error; the claimed archive is absent. Their AES-128 and completion claims are not adopted. Completion labels in other setup receipts likewise do not prove a correct design or passing tests.

An older Claude plan explicitly relied on published architecture. Its code, archive and cipher details were excluded. The retained source-origin note explains that exclusion and supplies no solution. No shared third-party Claude implementation was imported.

## What this does not resolve

The twelve unreadable reviewer instructions, two originally truncated tool outputs, and some older missing dialogue remain unresolved. No new verified cipher identity, table meaning or key interpretation was found. Historical chats sometimes omit work completed elsewhere; their stale status statements do not override the current package or later evidence.

The [current encryption explanation](../../ENCRYPTION_EXPLANATION.md) and [submission guide](../../CURRENT_GUIDE.md) state the present assessment. Source/test files and the original sealed package remain unchanged. This is a documentation and provenance update, with no new design execution or simulation result.
