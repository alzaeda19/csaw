# Reproduce the frozen-design evaluation

Use a new disposable directory outside the existing project. Copy only this addendum's `scripts/`, `sources/` and `package/` into it. Create empty `records`, `analysis`, `synthesis`, `detectors`, `runtime` and `ai_logs` directories. Do not copy saved result directories into the new run: scripts refuse to overwrite completed runs. Existing projects and the sealed evidence need not be edited.

Supply an installed compatible OSS CAD Suite and the Python interpreter containing the detector dependencies. The actual tested paths and commands are preserved in `records/`. `CSAW_TOOL_SUITE` and `CSAW_DETECTOR_PYTHON` are optional portable overrides; their defaults are the recorded local environment. These override hooks were added after the successful runs and do not change the tested flow or default commands.

From the new analysis directory, with those two environment variables set to your installed tool locations:

```sh
python3 scripts/prepare_inputs.py --suite "$CSAW_TOOL_SUITE"
python3 scripts/validate_representations.py
python3 scripts/run_matrix.py
python3 scripts/audit_results.py
```

The first step elaborates both frozen sources and creates the two predeclared representations. The second compares six full-core simulations using the same fixed vectors. The third runs all four supplied checkpoints on all four candidate representations. The last audits the saved graphs without repairing them. Expect the original parser/fallback and flat-graph joining limitations described in the report; a successful process exit is not a full-design validity certificate.

Tested versions include Yosys 0.70+344 (git 2f2307ad6), Icarus/VVP 14 development build, Python 3.12.1, PyTorch 2.10.0, torch-geometric 2.3.1, PyVerilog 1.3.0 and NetworkX 3.2.1. Exact dependency versions are in each `detectors/result_*/versions.json`. The interpreter is the existing native detector environment, with system/user packages as originally configured. Do not force `PYTHONNOUSERSITE`; an earlier environment check found that it selects an incompatible Torch installation. No training dataset pickle is loaded. Checkpoints load with `weights_only=True`, strict matching, CPU, one thread and fixed seed zero. Runtime cache directories are isolated.

The independent formal report retains its exact command, unchanged harness, tool version and output. Its source paths can be relocated to another disposable directory. Its zero-core abstraction and schedule limits remain part of the result.

Qwen reviews are optional advisory evidence. Their exact prompt files and HTTP requests are retained. Repeating `scripts/ask_qwen.py` requires the already configured local Ollama model with the recorded digest; use a new call name/output directory. No model download, installation, remote API or new design generation is part of these commands. Fresh model responses may differ and must be reviewed, not substituted for the recorded originals.

The graph defects are intentionally reported, not silently repaired after seeing scores. A future independent detector-tool validation would be a separate study with its own protocol and controls; this report claims only the present frozen evaluation.
