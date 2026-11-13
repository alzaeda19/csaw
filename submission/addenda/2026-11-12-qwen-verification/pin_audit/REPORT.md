# Original-materials pin-map audit

November 12, 2026 (America/New_York). Read-only documentation and static-file checks; no design execution.

The nine functional connections can now be mapped to physical FPGA package pins **for the published February 2026 Rev A Hackster schematic**. The original host declarations, the board designer's schematic, the original-bitstream-derived pad coordinates and Lattice's package pin table agree. This closes the previously missing reference-board mapping. It does not identify or test a particular physical board, validate the automatically allocated regenerated image, or authorize programming.

## Sources and boundary

- All six original challenge files match their pinned release receipt by size, SHA-256 and Git blob ID. The release commit is `9913ac31aa47a46de9cfb8f928be21ae4e249ad4`. See `ORIGINALS_VERIFICATION.json` and the copied original receipt.
- The original host program, lines 5-14, assigns RP2040 GPIO numbers. The original interface description, lines 14-24, supplies directions and meanings. Neither original release file is an FPGA package-constraint file; none of the six originals is a PCF or board schematic.
- The original README's board-documentation link identifies the primary board designer repository. Only its hardware PDF was downloaded; no example designs, shared implementations, challenge solutions or later challenge branch was consulted.
- Board schematic: [pinned primary hardware PDF](https://raw.githubusercontent.com/kiwih/hackster-programmer/e664a4335e14bdef1e95b8a1a7e2f3c340777f98/hardware/unsw-cse-hackster-cc-by-sa-4.0/cse-hackster-feb-2026.pdf). Git blob `d8cba03cc2fcca80236da4f35ec06189aebb808b`; 734,879 bytes; SHA-256 `d22dab37a784d9ae325a02ac13b2177a6d5f26e2b779b802fa4dbacfe7c47a04`. Page 1, U13 application processor, U4 FPGA and indicator-LED sections were visually inspected at 400 DPI. This is an explicitly identified primary-document supplement, not one of the six original release files.
- Hardware attribution: **Hammond Pearce, UNSW Sydney - CC BY-SA 4.0**.
- The preserved IceStorm source at commit `00da9c3e6ceff056248e3451dd6fd3210d6ceec9` supplies coordinate-to-package mapping. Its `pinloc_db["5k-sg48"]` literal was parsed with Python AST without importing or executing the tool. Relevant entries are at `icebox.py:5048-5059`. Exact source hash and extraction are retained.
- [Lattice iCE40UP5K Pinout](https://www.latticesemi.com/view_document?document_id=51971), revision 1.1, independently matches all nine SG48 package-pin names and identifies Bank 0. Downloaded XLSX SHA-256 `cee14ad47beaf22298246228e913e539c87e33bf078e04d65988d1a24237d938`. Its cells were read as ZIP/XML, without macros or spreadsheet execution.

## Physical mapping for that schematic

Directions are relative to the FPGA. The recovered `io_x_y_z` name denotes a die tile and I/O-cell index, not a board or package-pin number.

| Signal | FPGA direction | RP2040 GPIO | Board net | FPGA SG48 pin | Vendor pin name | Original recovered port |
|---|---|---:|---|---:|---|---|
| SCK | Input | 6 | APP_ICE40_D0 | 36 | IOT_48b | io_9_31_1 |
| RST_N | Input | 7 | APP_ICE40_D1 | 34 | IOT_44b | io_13_31_1 |
| MOSI | Input | 8 | APP_ICE40_D2 | 32 | IOT_43a | io_16_31_0 |
| MISO | Output | 9 | APP_ICE40_D3 | 31 | IOT_42b | io_16_31_1 |
| NORM_CS_N | Input | 10 | APP_ICE40_D4 | 28 | IOT_41a | io_17_31_0 |
| START | Input | 12 | APP_ICE40_D6 | 27 | IOT_38b | io_18_31_1 |
| ENC_DEC | Input | 13 | APP_ICE40_D7 | 25 | IOT_36b | io_19_31_1 |
| BUSY | Output | 14 | APP_ICE40_D8 | 23 | IOT_37a | io_19_31_0 |
| ICE_LED | Output | Not an application GPIO | ICE_LED | 38 | IOT_50b | io_8_31_1 |

The application-processor GPIO numbering is distinct from its own package-pad numbering as well. For example, GPIO6 is U13 pad 8, while its net reaches FPGA U4 package pin 36. Those three numbers must not be substituted for one another.

## Concrete correction: BUSY versus LED labels

The unchanged simulation adapter connects `io_8_31_1` to its logical BUSY output and `io_19_31_0` to its logical ICE_LED output. The board schematic resolves those physical identities in the opposite order: **pin 38 is LED, pin 23 is BUSY to GPIO14**.

The original recovered source contains `assign io_19_31_0 = io_8_31_1;` at line 30051. The adapter explicitly documented that these outputs were interchangeable in its digital model and made no board-pin claim. This explains why their logical interchange did not distinguish the saved simulations. It does not independently prove physical equivalence or validate any new design. No adapter or RTL was changed. A future board-specific constraint document must use the physical identities in the table.

## Device, electrical and clock interpretation

- The original unpacked ASC identifies `.device 5k`. The schematic labels U4 `ICE40UP5K-SG48ITR` and its title block identifies February 2026 Rev A. Lattice's [family data sheet](https://www.latticesemi.com/view_document?document_id=51968), FPGA-DS-02008-2.4, page 43, defines SG48 as 48-pin QFN and I as industrial grade; it does not make that I a numeric speed grade. A particular board's marking/BOM/revision was not inspected.
- All nine mapped pins are Bank 0. The schematic supplies its VCCIO0 and application-processor IOVDD from +3V3. Series resistors are shown on application data connections. This establishes the documented supply arrangement, not measured voltages, actual I/O-standard settings, drive strength, rise/fall time or setup/hold compliance.
- ICE_LED drives Q5, a 2N7002 low-side switch for D6, with R47 pulling the gate low. The depicted circuit makes a high ICE_LED signal illuminate that indicator. This polarity is a schematic inference, not a board measurement.
- The challenge's SCK is **pin 36**, not board net ICE_CLK at pin 37 or APP_ICE_CLK at pin 35. The vendor pin table classifies pin 36 as ordinary DPIO, while pins 35/37 carry dedicated global-input labels. Do not move SCK to a different pin merely because another pin is labelled clock. This audit does not establish its actual routed clock path or timing. The family data sheet, page 13, describes logic clocks from global buffers or general-purpose fabric; a non-GBIN label alone is not evidence of a defect.
- RST_N on pin 34 is the user design's synchronous active-low reset. It is distinct from FPGA configuration CRESET at pin 8. Likewise, GPIO3's `ice_done` is a configuration-status connection, not BUSY; the schematic interposes Q6 on that connection.
- The original interface limits SCK to 1 MHz. The supplied host requests 50 kbit/s SoftSPI, but its manually issued clock pulses have no explicit delay. Neither statement supplies measured waveforms, board delays or complete external timing constraints.

## What remains unverified

1. The model/revision and fitted FPGA marking of the particular physical board intended for use.
2. Continuity, assembly options, actual voltage levels, I/O configuration and analog timing on that board.
3. A board-constrained rebuild and external timing analysis. The previously regenerated image used automatic I/O allocation; discovering this table does not retroactively make that image match these pins.
4. Hardware behavior or readiness to program. No hardware was accessed and no PCF, RTL or bitstream was modified or generated by this audit.

This work provides board requirements and source-backed pin identity. It supplies no key, cipher proof, new simulation, synthesis result, stealth result or detector claim.

## Tools, preservation and AI records

`TOOL_PATHS_PEER.md` records exact existing ARM64 Yosys and nextpnr paths, sizes and hashes, with saved historical versions clearly separated from present execution. The binaries were not run by this audit. The independent peer's native final response confirms the complete mapping in `PIN_MAP_PEER_REVIEW.md`.

The Git checkout was observed clean at `61346ebfc534a75c46b098341563d1ef213417fc`; this audit performed no repository writes. Six-original integrity checks passed. New material exists only in this audit folder. Native visible task records, errors, refinements and export omissions are indexed under `ai_records/`. The initial Python HTTPS download failed certificate verification; system curl subsequently downloaded the pinned PDF with TLS verification retained and its Git blob hash confirmed. Empty PDF text extraction was preserved, followed by visual rendering. A browser PDF/XLSX fetch limitation and an overbroad metadata-print truncation are recorded rather than erased. The record export is bounded by its explicit cutoff and does not include future packaging or final-response events.
