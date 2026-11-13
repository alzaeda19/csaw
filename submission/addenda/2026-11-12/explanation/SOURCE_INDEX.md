# Source index for the proposed explanation

Line numbers are 1-based and inclusive. Original source paths below are relative to the submission root. The link layout assumes this folder is installed at `submission/addenda/2026-11-12/explanation/`; the exact original absolute paths and SHA-256 hashes remain in [EVIDENCE_MAP.json](EVIDENCE_MAP.json).

## Sources

| ID | Source |
|---|---|
| B | [rtl/baseline.v](../../../rtl/baseline.v), unchanged recovered baseline; SHA-256 `180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765` |
| A | [reference/baseline_protocol_dut.sv](../../../reference/baseline_protocol_dut.sv) |
| T | [reference/paired_normal_tb.sv](../../../reference/paired_normal_tb.sv), read as existing driver source only |
| S | [evidence/original_materials/qualifier/ice40_cryptographic_IP.md](../../../evidence/original_materials/qualifier/ice40_cryptographic_IP.md) |
| H | [evidence/original_materials/qualifier/spi_ice40_crypto_ip_test.py](../../../evidence/original_materials/qualifier/spi_ice40_crypto_ip_test.py), read only |
| R | [evidence/historical_recovery/REPORT.md](../../../evidence/historical_recovery/REPORT.md) |
| P | [evidence/historical_recovery/PRIOR_TECHNICAL_BRIEF.txt](../../../evidence/historical_recovery/PRIOR_TECHNICAL_BRIEF.txt) |
| Q | [Bundled historical baseline-equivalence report](source_records/BASELINE_BITSTREAM_EQUIVALENCE_REPORT.md), exact copy of the authorized November 7 report |
| J | [Bundled historical simulation summary](source_records/BASELINE_SIMULATION_SUMMARY.json), exact copy of that report's authorized summary |

Q and J are copied byte-for-byte and hash-verified. Their internal absolute links remain original historical text; linked proof logs and models are **not** bundled by this addendum and were not opened or rerun. The cited report and summary themselves are available above. A separately read original recovery report is indexed as `R_ORIGINAL` in the machine-readable map; it has the same content hash as packaged R.

## Claims and principal line references

| Claim | Supporting lines and scope |
|---|---|
| E01 — origin and architectural proposal | R:7–14; B:42766–42898 contains memory instances; B:42901–45708 contains equations and registers. The proposal synthesizes the narrower observations below. |
| E02 — specified interface and host sequence | S:4–24, 29–55; H:14–21, 25–34, 41–48, 59–87, 96–137. |
| E03 — functional signal roles | A:1–9; B:30051 duplicates status; R:20–33 explains the inferred mapping and unresolved physical pins. |
| E04 — serial bank and registered output | B:43628/45031 place MOSI into n628; B:44269/45673 place n800 into registered MISO. Every one of the 32 shift steps has exact D-assignment and register lines in the static inventory's `serial_path_evidence`. |
| E05 — structural counts and state grouping | B:42901–44304, 44305–45708; four memory instance starts at B:42766, 42800, 42834, 42868. Q:26–28 separately records modeled internal state. Inventory `counts`, `state` and `working_registers` give individual members/lines. |
| E06 — fixed lookup storage | B:42766–42768, 42786–42796; repeat blocks at 42800–42830, 42834–42864, 42868–42898 **excluding INIT payload lines**. B:42901/45177 resolve n5=0; B:43384/44787 resolve n466=1. R:13 describes original-derived initialization provenance. |
| E07 — direction and table-assisted datapath | B:43238 gives representative mode selection; all 32 direct mode consumers appear with lines in inventory `mode_direct_lut_consumers`. B:42920 and inventory `qualification_bit_direct_lut_consumers` show table-output qualification. T:81–89, 108–119 holds the chosen mode through each operation. |
| E08 — completion/load boundary | B:43089/44492 serial enable; 42938/44341 inverse BUSY; 43123/44526 BUSY; 43764/45167 delayed BUSY; 43410/44813 and 43923/45327 counter activity; 44093/45497 memory/read control. The receipt records 768 combinational identity checks. |
| E09 — historical timing observations | R:39–49, 57–67; H:72–78, 118–124; Q:16–20; J:65–86. Failures and sampling qualifications are retained. |
| E10 — value oracle and finite coverage | H:33–34; R:59–60, 74; T:8, 81–89, 96–99, 108–119; Q:16–20, 32. |
| E11 — historical equivalence scope | Q:3–5, 12–20, 26–34, 65–71; P:7–9. Historical report evidence only, with no new proof or simulation. |
| E12 — proposal and unknowns | R:11–14, 73–74; P:3–9. Unknown cipher/key semantics remain explicitly unknown. |

## Fresh analysis artifacts

- [Static analysis script](static_baseline_analysis.py): reads only the original baseline, verifies its expected hash, removes INIT lines before parsing, and performs structural/Boolean analysis.
- [Static inventory](STATIC_BASELINE_ANALYSIS.json) and [compact output](STATIC_ANALYSIS_STDOUT.json): exact state members, connections, source lines and checks.
- [Evidence-map builder](build_evidence_map.py) and [map validation output](EVIDENCE_MAP_STDOUT.json).
- [Run and integrity receipt](STATIC_ANALYSIS_RUN_RECEIPT.json): scope, source comparisons, final artifact hashes, actual development failures and independent-review correction. Intermediate failures are summaries, not invented native transcripts.

No HDL, attack implementation, key extraction, hardware operation or Git operation was performed for this addendum.
