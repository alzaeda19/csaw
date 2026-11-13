# AI interaction records for the local-agent setup

This index is a Codex-authored summary, not a replacement for the authentic transcripts listed below.

## Current Qwen interactions

Each directory under `ai_logs/` contains its exact submitted `prompt.txt`, configuration and system-prompt snapshots, exact `launcher_used.py`, raw `stdout.stream.jsonl`, stderr, debug log where available, and `receipt.json`. Completed responses are also saved as `response.txt`. Tool-call arguments, tool results, errors, session identifiers and model identifiers remain in the raw streams. `HASHES.json` covers that turn's saved artifacts.

`native-session-0.jsonl` is a copy of the actual Claude Code session transcript when one was produced. The current native transcripts also remain under `runtime/native-config/projects/`. Resumed-session snapshots include earlier turns, so they overlap; they should not be counted as separate independent conversations. The launcher preserves each turn snapshot instead of overwriting earlier evidence.

The successful new-file Write occurred in `20261112T235153Z__aa_qgq4`. Its Edit attempt failed before reading; the raw log and model response report that failure. The same session was resumed in `20261112T235340Z_1a80em9l`, where Read and Edit succeeded. The native session ID is `f3414c93-5ef8-4018-b789-26e7286a4666`. Independent host simulation of the resulting saved file is in `setup_logs/probe_verification/RESULT.json`.

The no-tool model connectivity probe is separately preserved in `runtime/startup_probe.stdout.log`, `runtime/startup_probe.stderr.log`, its native session transcript, and `setup_logs/STARTUP_PROBE.json`. Its session ID is `8aaf31e8-8551-4131-9b4a-e35d0bf4f842`. It was a real local Qwen response, not an RTL experiment.

Failed launches that stopped before creating a native session legitimately have no native transcript. Their error output and launch receipts are retained. Interrupted tool loops remain recorded; no failed operation has been changed into a pass. Any later readback turns appear in the generated `SETUP_RESULT.json` index.

## Attribution and boundaries

- The original recovered RTL, adapter, testbench and primitive library were copied byte-for-byte by Codex from the named verified source set. They are not newly Qwen-authored RTL.
- Codex authored the interface wrapper, configuration, test fixtures, documentation and independent verification harness.
- Qwen made only the changes recorded in each turn's tool calls and before/after file inventory. Setup probes are clearly separate from cipher RTL.
- Ordinary file-access metadata and OS/library runtime access are not challenge-material consultation. No published challenge solutions, other project content, or unrelated conversations were supplied to Qwen.
- Prompts/responses/tool results are retained as emitted. The stream is not a complete HTTP packet capture and may contain provider-normalized fields.
- The outer macOS policy allows the native client to maintain its runtime records. The parent copies those records and the live stdout/stderr into the separate `ai_logs/` evidence directory after each turn.

## Remaining AI-log gaps

Older plain-Ollama conversations were not recovered. Existing transcript gaps remain unresolved. No full native export of this Codex setup conversation or its research subagent conversation was created in this folder; setup receipts and this summary do not claim otherwise. No missing transcript has been reconstructed or fabricated.
