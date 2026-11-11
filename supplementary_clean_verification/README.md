# Additional clean-design verification

These are existing saved results reviewed by the Trojan orchestrator on November 11; no experiments were rerun for publication. The original November 11 package is baseline-focused and omits this separate readiness-repair work. The [source copy receipt](SOURCE_COPY_RECEIPT.json) identifies all 31 copied files and SHA-256 hashes.

The repaired RTL is a transparent normal-operation timing repair, distinct from the recovered baseline and the baseline-generated automatic-pin bitstream. It does not satisfy the required Trojan-modified RTL deliverable.

| Saved result | Scope |
|---|---|
| Strict readiness checks: repaired 1,122/1,122 pass; baseline 14 failures | Repair intentionally changes result-readiness behavior. Original baseline failures remain retained. |
| Disabled-ROM checks: 67,584 assertions pass | Eight synthetic omitted-enable controls rejected; earlier nondiscriminating check remains documented. |
| Synthesis and internal timing pass | Assumed UP5K/SG48, automatic pins, 1 MHz target; no verified board constraints or physical validation. |
| Repaired RTL/mapped netlist matched-state proof passes | Seven unavailable internal simulation monitors untested; unrestricted longer proof timed out. |
| Two consecutive transactions, mode pairs 00/01/10/11 pass | Prescribed timing and mode-change point; arbitrary schedules and unbounded independent-power-up equivalence unproved. |

The later baseline-to-actual-bitstream-decode equivalence report supersedes the old build chat's unresolved status. It preserves the baseline immediate-read failure; it does not prove that timing behavior correct.

This supplement includes selected reports, recorded methods, candidate sources and receipts; embedded experiment manifests describe larger local dependency sets. It is not a standalone complete experiment installation. The repository manifest describes included bytes.

The [orchestrator handoff](LATEST_STATUS.md) is preserved as a time-bounded review. Its statement that Opus 5.5 was unverified applies to that review's own actions. A subsequent actual Opus 5.5 review is included separately under `publication/claude-review/`.
