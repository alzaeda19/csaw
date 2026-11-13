# Review of the user-supplied response

The response did not inspect the actual files. Its proposed mechanisms are hypotheses, not measured explanations.

- All four checkpoints receive the same graph tensor for each candidate and share the same configured architecture. Claims that HT1/HT3 use source syntax while HT2 uses a separate resource/netlist pipeline and HT4 mixes inputs are unsupported.
- HT2's positive vote alone does not establish resource-based detection or reliability on register-heavy modifications.
- HT4's false alarm does not establish erroneous training labels, overfitting or an outdated threshold. The current rule is fixed two-class argmax.
- Identical HT3 scores do not establish that extraction omitted the added logic. The prior repaired-graph checks already establish specified added-definition reachability; the model's aggregation can still map different graphs to identical outputs. That mechanism must be checked, not assumed.
- Checkpoint training sets and training overlap remain unknown. The supplied labels are annotations, not a new behavioral proof.
- Neither missed detection nor source visibility alone settles the whole stealth objective. The current justified statement remains: stealth is not established.

Further measured findings will be added in the investigation report. No hardware, threshold or model change is authorized by these speculative suggestions.
