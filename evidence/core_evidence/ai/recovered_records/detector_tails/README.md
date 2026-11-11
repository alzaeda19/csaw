# Recovered detector transcript tails

Recovered **42 new visible records**, including **2 root final answers**, in three bounded segments. Old experiment folders remain unchanged.

- `baseline_root_completion`: source lines 1298–1336, 14 retained records. Native assistant final_answer at line 1336; subsequent records excluded.
- `clean_aes_before_followup`: source lines 1528–1543, 3 retained records. Ends immediately before incoming same-task coordinator delegation at line 1544.
- `clean_aes_completion_followup`: source lines 1544–1605, 25 retained records. Begins at incoming same-task coordinator delegation and ends with native assistant final_answer at line 1605.

Each segment provides exact retained native fields, source thread/turn IDs where present, complete original source-line hashes, canonical field hashes, readable visible messages, and exclusions. Prior snapshot prefixes match original hashes; no old exported source lines are duplicated.

The three included children have no post-snapshot records; their already exported finals are references in `CHILD_CUTOFF_STATUS.json`, not new records. The coordinator follow-up at line 1544 begins an explicit separate segment. Final answers retain historical snapshot-limited record counts verbatim.

`RECOVERY_MANIFEST.json` and `RECOVERY_INDEX.json` record counts, boundaries and limitations. `preservation/old_files_unchanged.json` records content-hash comparisons. `HASH_MANIFEST.json` covers this folder except itself and the index; the index records its hash.

Remaining gaps:

- Encrypted/nontext collaboration bodies remain unavailable; none decrypted or reconstructed.
- No additional detector_environment, detector_input_audit, or clean_aes_detector_review child records exist beyond prior cutoffs; existing child finals are carried-forward references, not newly recovered records.
- Clean-AES source line 1577 output element 1 excluded in full because it contains mixed coordinator history; its native truncation indicator is documented and no missing text reconstructed. Separate native local command record at line 1575 retained.
- Exporter-worker sessions and their root message bodies remain outside the previously included detector/review child scope.
- Earlier root history, hidden reasoning, system/developer/platform context, compaction/replacement history, tool-discovery documentation, and records after each boundary excluded.
- Source-user coordinator history handled separately by parent recovery task; already exported single source-user request not duplicated.
- This is a local consistency-preserving recovery of available visible records, not independent authentication of historical claims, serving weights, missing logs, or complete task history.
