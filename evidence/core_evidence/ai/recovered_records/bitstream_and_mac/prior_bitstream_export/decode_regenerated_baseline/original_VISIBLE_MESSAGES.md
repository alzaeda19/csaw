# Authentic visible records: decode_regenerated_baseline

Native retained fields, copied without reconstruction. JSONL contains the tool records and command outputs. Encrypted collaboration bodies are explicitly unavailable in this readable export.


## agent_message_readable_envelope — 2026-11-07T17:20:48.915Z
Native source line 13.

Message Type: NEW_TASK
Task name: /root/decode_regenerated_baseline
Sender: /root
Payload:


[Message body is encrypted in the retained source; unavailable in this export.]

## agent_message_readable_envelope — 2026-11-07T17:21:11.975Z
Native source line 43.

Message Type: MESSAGE
Task name: /root/decode_regenerated_baseline
Sender: /root
Payload:


[Message body is encrypted in the retained source; unavailable in this export.]

## agent_message_readable_envelope — 2026-11-07T17:21:17.707Z
Native source line 51.

Message Type: MESSAGE
Task name: /root/decode_regenerated_baseline
Sender: /root/baseline_bitstream_simulation
Payload:


[Message body is encrypted in the retained source; unavailable in this export.]

## agent_message_readable_envelope — 2026-11-07T17:22:55.555Z
Native source line 137.

Message Type: MESSAGE
Task name: /root/decode_regenerated_baseline
Sender: /root/baseline_mapped_formal
Payload:


[Message body is encrypted in the retained source; unavailable in this export.]

## agent_message_readable_envelope — 2026-11-07T17:23:02.240Z
Native source line 149.

Message Type: MESSAGE
Task name: /root/decode_regenerated_baseline
Sender: /root
Payload:


[Message body is encrypted in the retained source; unavailable in this export.]

## agent_message_readable_envelope — 2026-11-07T17:23:58.150Z
Native source line 185.

Message Type: MESSAGE
Task name: /root/decode_regenerated_baseline
Sender: /root
Payload:


[Message body is encrypted in the retained source; unavailable in this export.]

## agent_message_readable_envelope — 2026-11-07T17:24:49.014Z
Native source line 231.

Message Type: MESSAGE
Task name: /root/decode_regenerated_baseline
Sender: /root/baseline_bitstream_simulation
Payload:


[Message body is encrypted in the retained source; unavailable in this export.]

## assistant_final_answer — 2026-11-07T17:25:50.350Z
Native source line 266.

Completed independent decode and adapter validation.

- Use `decode/regenerated_compatible.v` + `decode/regenerated_protocol_dut.sv`, top `protocol_dut`.
- Raw decode: `decode/regenerated_raw.v`.
- All nine IO roles verified against physical placement and decoded configuration.
- Compile passed with real RAM models.
- State correspondence: **`decode/physical_decoded_correspondence_v3.json` only**; covers 71 FFs and four RAMs.
- Summary and records: `decode/DECODE_SUMMARY.json`, `commands.jsonl`, `SHA256SUMS_v2.json`.

Only declaration compatibility edits were made. Inputs remain unchanged. The direct LUT encoding comparison remains unresolved; failures and superseded mapping attempts are preserved.
