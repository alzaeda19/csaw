Clean AES reference setup — verified November 10, 2026

RESULT: compilation succeeded; simulation succeeded; 5 passes, 0 failures.
The four unmodified sources match the professor ZIP and the orchestrator's earlier inputs.
Retained orchestrator log hashes were also verified, without changing that work.

Run again from this directory:
    python3 verify_clean_aes.py
Each invocation creates a new timestamped runs/ directory and preserves its logs.
Requires Python 3 and existing /opt/homebrew/bin/iverilog and /opt/homebrew/bin/vvp.
No Python packages, API key, notebook, PyTorch, detector assets, or network access are needed.
The runner checks input hashes before compiling and verifies both exit codes and all five PASS messages.

Included: the professor's three clean AES RTL files and functional testbench,
source-manifest.json, standalone runner, and actual command/tool/result logs.
The complete professor package was separately extracted, without executing it, to:
/Users/al-zayedal-hassan/Documents/Codex/2026-11-10/referenced-chatgpt-conversation-this-is-an/work/professor-package/TrojanGYM_AES_Course_Package

Only the standalone clean AES subset is configured for execution. The notebook,
generation/evasion workflow, detector checkpoints and pickle cache were not executed or loaded.
No dependencies for those workflows were installed. No AI gateway was contacted.
No CSAW or project repository file was modified or used in this standalone run.
No published solutions or solution-derived vectors were consulted. Expected outputs
come solely from the professor-supplied AES testbench.

Limits: these five tests demonstrate the supplied reference behavior for those inputs;
they do not establish exhaustive correctness, absence of Trojans, recovered-baseline
equivalence, key recovery, or course completion.

Coordination: user-authorized communication with the existing chat titled 'trojan'
(thread 01a1b0ad-f593-7f90-a689-b621984f7cb4). Its original runner used a toolchain
inside CSAW and a fixed output directory; this standalone runner removes those dependencies.
