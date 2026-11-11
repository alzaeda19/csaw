# Current technical summary

This summary combines the preserved core evidence with the later defensive appendix. It reports completed work and its limits, not completion of the original assignment.

## Recovery and ordinary verification

The core package contains the recovered baseline and a regenerated bitstream. Their recorded equivalence is conditional on the stated digital primitive models and state relation; it is not independent proof of the recovered cipher algorithm or physical-board behavior.

The retained original-host checks passed 24 of 24 known-answer cases per model. Immediate reads at the first BUSY-low failed eight of eight known-answer cases per model. The two models agreeing does not remove that failure or establish universal normal-operation correctness.

The separate professor-supplied clean AES reference passed all five supplied ordinary tests. This is a different reference design; these tests do not establish equivalence to the recovered CSAW baseline.

Earlier four-detector runs classified both the clean AES reference and recovered baseline CLEAN. The AES run used a large-table heuristic graph; the baseline run used fallback after exact extraction failed on missing RAM definitions. These classifications are not proof of Trojan absence.

Details and source identities: [preserved technical brief](core_evidence/TECHNICAL_BRIEF.txt).

## Defensive appendix: existing supplied designs

All 23 designs were scored by all four fixed detectors: 92 individual predictions, no unscored designs and no inference reruns. The source labels identify 14 infected and nine clean designs. All 23 used the parser-based extraction route; that route does not certify complete hardware semantics.

| Detector | Infected detected / 14 | Infected missed / 14 | Clean falsely flagged / 9 | Clean correctly unflagged / 9 |
|---|---:|---:|---:|---:|
| HT1 | 9 | 5 | 5 | 4 |
| HT2 | 6 | 8 | 6 | 3 |
| HT3 | 0 | 14 | 1 | 8 |
| HT4 | 4 | 10 | 2 | 7 |
| Any-positive-vote combination | 9 | 5 | 7 | 2 |

The combined rule detected 64.3% of the supplied infected examples and falsely flagged 77.8% of the clean controls. These results demonstrate missed detections and frequent false alarms on this set.

Labels come from the package directories; behavior was not activated to independently prove infection. Related design families dominate the small dataset. Item-level training overlap is unknown, so the study is not established as held-out evaluation. Prior AES and CSAW cases are outside the 23-design denominator. Model scores are not calibrated probabilities of compromise.

The full report, per-design values, fixed method, independent arithmetic checks and raw command evidence are in [defensive_appendix](defensive_appendix/REPORT.txt).

## Unfinished and qualified requirements

No completed Trojan-modified RTL or demonstration testbench is included. Ordinary benches and detector inference do not satisfy those original requirements. The alternative defensive scope remains unapproved.

Available AI exports are authentic within their stated boundaries, with encrypted, truncated, unmapped and post-cutoff gaps. Comprehensive project-wide coverage remains unproven. The technical brief documents available work but is not a completed version of every original brief requirement.

Independent key recovery is not established; it is a bonus in the preserved qualifier instructions. Physical-board testing is not required by that original simulation-only phase, though later course instructions could differ.

The retained Claude review covered an earlier evidence packet. It did not review the subsequently produced clean-AES detector result or this toy benchmark. Current packaging checks establish file/record consistency, not a new Claude approval or a security certification.

