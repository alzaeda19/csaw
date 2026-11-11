# Current existing-design detector transcript export

The stable entry point is `EXPORT_INDEX.json`. Current snapshot: `snapshot_20261110T181844101994Z`.

Root scope begins at native line 1987 (2026-11-10T18:08:46.496Z), the unique original delegation from coordinator chat `01a1c563-aa79-7e12-ae2f-72d867d1e3da` whose input begins `New direct user request in coordinating chat:` and contains `existing Trojan-infected and clean designs`. No broad earlier root history or fallback boundary is included. Exactly one original human request, coordinator native line 791, is included.

Current `/root/existing_design_intake` and `/root/existing_detector_method_review` sessions are located from native SubAgentActivity records within the current root scope and checked against each child's native session IDs, parent ID and agent path. The exporter worker and unrelated sessions are excluded.

Each session has readable visible messages; exact retained tool/command fields; field locations and hashes; original native line hashes; source thread/turn IDs with native references; omission notes; and saved-file integrity verification. Selected metadata retains only identifiers and model configuration labels. Those labels do not authenticate serving weights or actual inference parameters.

Each source was captured once after RESULTS_READY. These are bounded, non-atomic snapshots with explicit byte/line/time cutoffs. Events after each cutoff, including the root's later final reply and final packaging if not yet captured, are outside the export. Encrypted bodies are excluded without decryption or reconstruction. Hidden reasoning, instructions, platform context, mixed history from read_thread, compaction and internal metadata are excluded. No earlier source conversation is exported. See SNAPSHOT_MANIFEST.json and per-session omissions_and_gaps.json for exact limits.

All retained fields and provenance references were compared to the original native sources after re-reading the saved JSONL. SHA-256 manifests support consistency checks; no immutable flags were used. Hashes do not independently prove authenticity or completeness.
