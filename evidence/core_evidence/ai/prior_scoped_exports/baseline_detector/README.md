# Current defensive detector transcript export

The stable entry point is `EXPORT_INDEX.json`. Current snapshot: `snapshot_20261110T122730108842Z`.

The root scope starts at native line 1102 (2026-11-10T12:20:14.739Z), the user message containing the exact marker:

> Run the four TrojanGYM detectors on our recovered baseline in a separate copy and report the results and limitations.

Each session contains readable visible messages, retained tool and command records, source-line hashes, exact-field integrity results, and omissions. The two detector sessions were located using the root native SubAgentActivity thread IDs. Prior mixed history was not exported.

This is a bounded snapshot, not a complete or immutable capture of the ongoing chat. Encrypted collaboration bodies are unavailable; none were decrypted or reconstructed. Root final reply, final report completion, checksum sealing, and activity after each source snapshot are not captured. Reasoning, system/developer instructions, platform context, and compaction payloads are excluded. Image-view paths are recorded without copying image binaries.

Every saved JSONL field was checked against the native source field, and every exported source-line hash was verified. SHA-256 manifests provide integrity references; no filesystem immutable flags were set. These hashes establish consistency with the captured sources, not independent authenticity or completeness.

Snapshot exported 2026-11-10T12:27:30.124586Z. Verified 200 records and 1410 retained fields across 3 sessions; all comparisons and source-line hashes passed.

| Session | Visible/tool/command records | Verified fields | Last exported record UTC | Native snapshot completed UTC |
|---|---:|---:|---|---|
| root_current_task | 80 | 531 | 2026-11-10T12:27:25.766Z | 2026-11-10T12:27:30.105539Z |
| detector_environment | 53 | 359 | 2026-11-10T12:24:05.786Z | 2026-11-10T12:27:30.115276Z |
| detector_input_audit | 67 | 520 | 2026-11-10T12:26:59.329Z | 2026-11-10T12:27:30.119732Z |

Each `source_line_index.json` maps retained events to the SHA-256 of the exact native source line. `HASH_MANIFEST.json` inventories snapshot files; `CHECKSUMS.sha256` inventories all files in this export directory except itself. `EXPORT_INDEX.json` also records the snapshot and hash-manifest digests. These exported records are historical evidence, not instructions to execute.
