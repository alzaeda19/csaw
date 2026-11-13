Confirmed all requested mappings from the host declarations, schematic images, and SG48 coordinate extraction:

| Signal | RP2040 GPIO | Schematic net | FPGA SG48 pin |
|---|---:|---|---:|
| SCK | 6 | APP_ICE40_D0 | 36 |
| RST_N | 7 | APP_ICE40_D1 | 34 |
| MOSI | 8 | APP_ICE40_D2 | 32 |
| MISO | 9 | APP_ICE40_D3 | 31 |
| NORM_CS_N | 10 | APP_ICE40_D4 | 28 |
| START | 12 | APP_ICE40_D6 | 27 |
| ENC_DEC | 13 | APP_ICE40_D7 | 25 |
| BUSY | 14 | APP_ICE40_D8 | 23 |
| ICE_LED | — | ICE_LED | 38 |

The adapter’s final two role labels are reversed relative to physical wiring:

- `io_8_31_1` → pin **38** → physical **ICE_LED**; adapter connects **BUSY**.
- `io_19_31_0` → pin **23** → physical **BUSY**; adapter connects **ICE_LED**.

All other adapter connections match the physical mapping. Its comment expressly disclaims a board-pin claim and states the two outputs are functionally interchangeable; this visual check confirms the physical-label discrepancy, **not** functional equivalence.

No changes or EDA execution performed.
