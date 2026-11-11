# Bounded native record recovery

| Task | Prior exported records | Newly recovered records | Final response |
|---|---:|---:|---|
| Bitstream root tail | 191 | 18 | Recovered from native line855 |
| Baseline bitstream simulation child | 122 | 0 | Already retained |
| Baseline mapped formal child | 165 | 0 | Already retained |
| Decode regenerated baseline child | 119 | 0 | Already retained |
| Mac infrastructure root task | No prior root-native export | 89 | Recovered from native line292 |

The bitstream root is limited to native lines805–858 after its old snapshot. The Mac root is the first recovery of its bounded task at lines50–295, beginning at its exact user request and ending at task completion. Earlier and later mixed root tasks are excluded.

- [Bitstream final](bitstream_root_tail/assistant_final.txt), [visible messages](bitstream_root_tail/VISIBLE_MESSAGES.md), [all retained records](bitstream_root_tail/visible_events.jsonl), [omissions](bitstream_root_tail/omissions_and_gaps.json).
- [Mac final](mac_root_task/assistant_final.txt), [user request and visible messages](mac_root_task/VISIBLE_MESSAGES.md), [all retained records](mac_root_task/visible_events.jsonl), [omissions](mac_root_task/omissions_and_gaps.json).
- [Combined manifest](MANIFEST.json), [prior-file integrity](prior_files_integrity.json).

Each retained field and source-line hash was verified against the native record. All 682 inspected prior evidence files are unchanged. Original truncation remains; encrypted and hidden bodies are not recovered. Historical commands appear only as records and were not executed. The new files do not claim provider attestation or restore unavailable content.

## Portable prior bitstream export

The original snapshot had **597 records**. This folder carries **587 existing records** in [prior_bitstream_export](prior_bitstream_export/MANIFEST.json), separate from the 107 new records. Ten instruction-output records are omitted; 46 encrypted argument fields are omitted. Original manifests, gaps, model labels and visible messages are copied exactly under clearly named original files; projection manifests record the differences. No raw native session history is copied.
