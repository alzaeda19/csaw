# Actual-binary structural decode

The copied binary was unpacked directly with the pinned OSS CAD Suite iceunpack, then decoded with the existing pinned IceStorm source at revision 00da9c3e6ceff056248e3451dd6fd3210d6ceec9. No build was rerun. No original candidate, input or decoder source was changed. The generic decoder correctly recovered the regenerated clock input without a tool patch.

Use `regenerated_compatible.v` and `regenerated_protocol_dut.sv` with top `protocol_dut`. Compile with Icarus `-g2012 -DNO_ICE40_DEFAULT_ASSIGNMENTS` and the pinned suite `share/yosys/ice40/cells_sim.v`; this provides real RAM behavior. Clean compile passed. `regenerated_raw.v` is the unmodified decode. `compatibility.diff` contains only the output-reg declaration/initialization adjustment needed by Icarus; all functional statements are unchanged.

`io_mapping_evidence.json` verifies all nine functional port roles against this build's physical PACKAGE_PIN links, automatically placed BEL coordinates, decoded top directions, PAD/data-path coordinates and actual decoded PINTYPE bits. This is not board pin validation.

Use only `physical_decoded_correspondence_v3.json` for supplemental state mapping. It covers all 71 FFs and four RAMs, records physical aliases and decoded state names, and checks FF configuration/polarity and RAM modes/initialization against the actual binary decode. It does not prove next-state equations or route equivalence. The v2 file `physical_decoded_correspondence.json` is retained but superseded because its comment-block parser misidentified a header-declared clock net; v3 fixes ownership and asserts every FF clock against the decoded always statement. Raw RTL, compatible RTL and adapter were never affected.

A separate direct LUT_INIT comparison failed and remains an unresolved encoding-comparison attempt: 1315 of 1443 parameter strings differ when directly compared without accounting for LUT input permutation. This is not a design-mismatch finding. All results and failed attempts remain available; formal and simulation comparisons are handled by other agents.

`commands.jsonl` records exact decode/validation subprocess arguments, working directory, UTC timestamps, elapsed times, exit codes and stdout/stderr hashes. Tools and inputs have SHA-256 records. Initial read-only exploration exists in the agent tool transcript but lacks separately captured timestamps here. All supplied input hashes were checked unchanged at completion. No network access, board programming, build rerun, key work or implementation modification occurred.
