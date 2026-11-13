Verified both exact executables exist and match the previously recorded SHA-256 values. No EDA binaries or project scripts were executed; no files changed.

| Tool | Exact verified path | Current metadata |
|---|---|---|
| Yosys | `/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/synthesis_fit_timing_2026-11-06/tooling/oss-cad-suite/libexec/yosys` | Regular executable, `-rwxr-xr-x`, 25,957,712 bytes, Mach-O 64-bit ARM64 |
| nextpnr | `/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/synthesis_fit_timing_2026-11-06/tooling/oss-cad-suite/libexec/nextpnr-ice40` | Regular executable, `-rwxr-xr-x`, 236,688,880 bytes, Mach-O 64-bit ARM64 |

Current executable SHA-256 values:

- Yosys: `2f9ccb27f821a8da68d45b6ac6b6093338404c205d75d9cb2cee0a049326761e`
- nextpnr: `670b5e8844c8aba66f2da4d81818b4c514e9922c10a9bfe07ace9bdb7b5bc6f0`

These match both `records/used_tool_identities.json` and the baseline `BUILD_SUMMARY.json`. Baseline `commands.json` records these exact `libexec` paths returning code 0 on 2026-11-07 at 17:15 UTC. This is historical compatibility evidence; current runtime/library compatibility was not tested.

**HISTORICAL versions**, from saved version-call outputs dated 2026-11-07:

- Yosys `0.70+344`, git SHA1 `2f2307ad6` (Release; Clang 21.1.8, aarch64 Apple Darwin build).
- nextpnr `0.11.1-88-g937c770c`.

The corresponding `bin/yosys` and `bin/nextpnr-ice40` files also currently exist. They are regular executable Bash launchers, **not symlinks**:

| Launcher | Bytes | Current SHA-256 |
|---|---:|---|
| `bin/yosys` | 370 | `8a6175ee88d6412c3d792c47d0750b8707a8e12cc2222c1322546d47cd85edb9` |
| `bin/nextpnr-ice40` | 900 | `15ec669b1657e6fae2a453053108265905e083903486dc5c519b7a610e882767` |

The saved initial nextpnr launcher version call returned 0 but printed a home-directory permission warning. The later isolated version record returned 0 with only the version text. No claim that the launcher is appropriate for read-only execution.

Source SHA-256 values, verified now (paths relative to restart root):

```text
AGENTS.md
ba5a4d27e3d62266a4078cb513f0b6046207a2a3a067104a7b5ca66cf177847b

baseline_bitstream_build_20261107T171511Z/BUILD_SUMMARY.json
9b60bd3d01afc6fdd6aa7491bef5dd947a18eff9b6f9eb218bc3b0edb5a83ecf
baseline_bitstream_build_20261107T171511Z/commands.json
de31433054e9393e89541271dc6373e82158328892352c6e2f9462157fb625b4
baseline_bitstream_build_20261107T171511Z/README.txt
b94d1477c0bfa55a20676a00f52267c6e9372999b406c9092c211d57b69369b8

synthesis_fit_timing_2026-11-06/REPORT.md
c84304d1c34a8e545d3a9a88e718699912e78671d052e14431abc55eb0de5603
synthesis_fit_timing_2026-11-06/records/used_tool_identities.json
93b9d410ae2f99a84773669451bd060d925cc2498d9b22af8418f68742292b10
synthesis_fit_timing_2026-11-06/records/tool_bundle_identity.json
b613a08dddeca7e72fa59ceee19de4ce207af2dbc1634adb975f31f84ab1f5a3

handoff_and_records_index_2026-11-07/MAC_SIMULATION_INSTRUCTIONS.md
07b8728d29335ba4283feb9eb72f2fb59f9d4eeaf0e7abb0e1bd5010515b7ae2
```

Version evidence under `synthesis_fit_timing_2026-11-06/records/commands/`:

```text
20261107T010432399220Z_yosys_version/command.json
904e2b0c1321271e603ae13a549a1f5e46c51df5a31742884e7a90978f7f7ab0
20261107T010432399220Z_yosys_version/stdout
6a8f43eec7c8c62478ccc91570484997418c476877c8afce2d37d19010d4a2fc

20261107T010434356643Z_nextpnr_version/command.json
2db43e84a0d46852e526a7a1b52f964c09732975d32c2ee92e60dec1fb27b9ad
20261107T010434356643Z_nextpnr_version/stderr
07bbd76bd91e5840673f25fe41b3b464eed769bf6151fcb355877a6f0c2c42f9

20261107T010501420834Z_isolated_nextpnr_version/command.json
6c65fb8c713da0fb616cf5b0f365cccd3244ced524f09469e6af8e59532c4f05
20261107T010501420834Z_isolated_nextpnr_version/stderr
41f95c4b94a00f665042b049d2b5fd8daaad597970590913097eb3ec580acdfe
```

Read-boundary note: keyword filtering of authorized `REPORT.md` displayed some historical synthesis result paragraphs. Parent confirmed these were authorized original-derived historical evidence. No RTL, solution, or netlist was read.
