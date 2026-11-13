# Submission closeout — November 13, 2026

This update clarifies what the original assignment requires, preserves three real Qwen reviews and their corrections, explains stealth in plain English, and adds one authentic tool-output recovery. It does not change hardware, add concealment, run a new detector, or claim full challenge compliance.

Start with the [required-versus-optional submission checklist](../../SUBMISSION_CHECKLIST.md) and [plain-English stealth explanation](STEALTH_IN_PLAIN_ENGLISH.md). The four required artifact categories are present. The principal unresolved requirement-level concerns remain incomplete relevant AI records and unestablished stealth. Normal behavior has documented protocol/model boundaries. Numeric key recovery is a bonus; physical execution is not required in this simulation-only phase. Full generation automation and negligible overhead are higher-score targets, not missing file categories.

## What the records audit recovered

The Trojan chat performed a bounded recheck of exactly twelve unavailable reviewer inputs and two originally truncated tool outputs. One 28,140-character output is now fully assembled from two authentic captures: a 20,000-character API prefix and a 9,000-character native suffix overlap exactly by 860 characters. The assembly restores 10,140 formerly omitted characters. It is labeled derived assembly, not a newly discovered complete transcript.

The other 46,178-character output gains four characters from the available API prefix but retains a 6,178-character central gap. All twelve reviewer instruction bodies remain unavailable. No text was guessed, reconstructed from current file contents, decrypted or invented. The original captures and earlier sealed addenda remain unchanged. See the [bounded audit and exact source checks](trojan_review/REPORT.md).

## Qwen's role

Three text-only requests went to the existing local Qwen3 8B model through Ollama. Qwen received no tools or file-writing permissions. The first readiness reply invented several requirements and overlooked supplied evidence. The corrective prompt and replies are retained, and [QWEN_REVIEW_NOTES.md](QWEN_REVIEW_NOTES.md) explicitly rejects unsupported assertions. The third request reviewed the existing wrapper's observability and detector limitations; it did not implement or optimize stealth.

The saved evidence takes precedence over model opinions. No claim is made that Qwen certified stealth, instructor acceptance, a grade or complete log coverage. Each call directory in `ai_logs/` contains the actual request, stream, response, completion receipt and hashes. This task's visible records have an explicit cutoff and exclude hidden reasoning/platform data.

## What was checked in this update

The current public commit was matched to the local checkout before changes. The repository byte verifier passed all 1,615 pre-update entries and 751 source-copy checks. Original requirements were read from the preserved local file and the same commit-pinned GitHub file. Existing simulation, waveform, formal and synthesis evidence was reviewed without rerunning those experiments. Final archive and repository preservation checks are recorded in the publication receipts.

Current docs supersede older unknown-cipher/pre-upload wording; older originals remain intact. No published challenge solution, new Trojan generation, board access, professor message or collaborator invitation was used. The course destination remains GitHub according to the user. Instructor receipt is an administrative status, not a fabricated pre-submission requirement.
