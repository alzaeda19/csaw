# Errors and refinements

- Initial read attempted `outputs/toy-dataset-detector-evaluation/README.md`, which does not exist. The exact command returned exit 1 after displaying the existing inventory CSV; dataset evidence was located under `run-evidence/`. No data was changed.
- Some exploratory tool displays were truncated. Saved source files and later bounded reads, rather than truncated displays, are used for conclusions.

- The frozen one-pass experiment completed with exit 0. Five workers intentionally returned exit 2 after the coverage assertion rejected unresolved `top.c_in` Reg references. Their exact tracebacks, symbols and receipts are preserved. They remain unscored; no fallback or retry was used.
- Both Qwen calls completed, but both contained factual/interpretive errors. The original requests, responses and received streams remain unchanged; QWEN_REVIEW_NOTES.md records accepted points and corrections.
- The user-supplied model response was preserved locally in full, with its final-answer portion included in the publication bundle. It did not inspect files and contains unsupported causal guesses; USER_RESPONSE_REVIEW.md records corrections.
- The diagnostic hooks reproduced all eight prior CSAW logits exactly. No source, checkpoint, configuration, feature mapping, graph-extractor repair or decision-rule refinement was made after the new experiment was frozen.
