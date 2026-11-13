Completed static control analysis. Baseline hash remained unchanged; all **9,344 identities passed** across 512 control combinations. No HDL execution or ROM-content interpretation.

Let `R=io_13_31_1`, `S=io_18_31_1`, `A=(n842,n840)`, `B=(n844,n846)`:

```text
n840' = R & ~n840 & (S | n842)
n842' = R & (n842 XOR n840)
n846' = R & ~n846 & (S | n844)
n844' = R & (n844 XOR n846)
```

Both pairs initialize/reset to `00` and remain synchronized. Normal progression is `00 → 01 → 10 → 11 → 00`; START launches only from idle and does not restart an active sequence. Sources: D equations 43960, 43773, 43490, 43883; registers 45364, 45176, 44893, 45287.

```text
RAM RCLKE n749 = R & (S | n840 | n842)
BUSY = R & (S | n840 | n842 | n844 | n846)
n588' = R & (n588 | S | n840 | n842)
n972' = BUSY
n1 = ~CS_N | ~R | (n972 & ~BUSY)
```

`n588` is a sticky memory-output qualifier, distinct from actual RAM clock enable `n749`. Its 32 direct consumers are AND gates. It sets on the first launch and clears only on reset.

Completion edge 4 takes both counters `11→00`, dropping BUSY while `n972` remains one. **The following CS-high edge 5 loads the serial result bank** and clears `n972`. Sources: qualifier FF 44679; delayed BUSY FF 45167; serial enable 43089/44492; BUSY 43123/44526; RAM enable 44093/45497.

Artifacts:

- [Complete findings and source references](/Users/al-zayedal-hassan/Documents/ChatGPT/trojan/CSAW_baseline_phase_analysis_20261113T023306Z_unl_u4cw/control_peer/CONTROL_FINDINGS.md)
- [Machine-readable findings](/Users/al-zayedal-hassan/Documents/ChatGPT/trojan/CSAW_baseline_phase_analysis_20261113T023306Z_unl_u4cw/control_peer/CONTROL_FINDINGS.json)
- [Exhaustive truth table](/Users/al-zayedal-hassan/Documents/ChatGPT/trojan/CSAW_baseline_phase_analysis_20261113T023306Z_unl_u4cw/control_peer/CONTROL_TRUTH_TABLE.json)
- [Static-analysis script](/Users/al-zayedal-hassan/Documents/ChatGPT/trojan/CSAW_baseline_phase_analysis_20261113T023306Z_unl_u4cw/control_peer/analyze_control.py)
- [Commands](/Users/al-zayedal-hassan/Documents/ChatGPT/trojan/CSAW_baseline_phase_analysis_20261113T023306Z_unl_u4cw/control_peer/COMMANDS.md), [execution records](/Users/al-zayedal-hassan/Documents/ChatGPT/trojan/CSAW_baseline_phase_analysis_20261113T023306Z_unl_u4cw/control_peer/EXECUTION_LOG.json), [hash manifest](/Users/al-zayedal-hassan/Documents/ChatGPT/trojan/CSAW_baseline_phase_analysis_20261113T023306Z_unl_u4cw/control_peer/HASHES.sha256).
