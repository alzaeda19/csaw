# Original-derived baseline candidate

Read REPORT.md for results, source-linked functional mapping and limitations. This folder contains only fresh recovery work; prior intake/harness records and original materials are preserved.

- raw/: untouched IceStorm ASC/Verilog and original harness source snapshots.
- adapters/: declaration-only compiler compatibility version and wiring-only functional adapter.
- tooling/: pinned official IceStorm source/local build and Yosys primitive-model source; no target solution material.
- harness/: relocated existing runner with unchanged testbench; its actual-candidate data checks FAIL.
- harness_postedge/: separately documented sampling experiment; supplied-vector/status checks PASS, with explicit timing-policy differences.
- experiments/: standalone compile, diagnostic-only tool copy and fresh offline reproduction artifacts.
- records/: request/accessible AI record, exact commands, actual versions, hashes, failures, diffs and preservation audits.

Reproduce from the restart root:

```sh
python3 baseline_recovery_2026-11-06/reproduce.py
python3 baseline_recovery_2026-11-06/records/audit_preservation.py
```

The first command succeeds only if the documented mixture of passes and failures repeats; it does not report all requirements satisfied. It creates a fresh experiment and appends fresh simulation runs. The second confirms preserved inputs/prior artifacts and refreshes this new folder's output manifest. No boards, original Python program or harness fixture are invoked.

Principal candidate files: adapters/recovered_iverilog.v, adapters/protocol_dut.sv, tooling/yosys/techlibs/ice40/cells_sim.v. Original tool output: raw/recovered_default.v. Complete target correctness, physical wiring and exact real-board SPI sampling remain unestablished. Original unchanged-harness conformance is failed; cite the post-edge adaptation explicitly when reporting the passing supplied-vector result.
