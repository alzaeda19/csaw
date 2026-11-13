// Functional role mapping inferred from original-derived connectivity.
// BUSY/LED duplicate outputs are functionally interchangeable; no board pin claim.
module protocol_dut(input SCK,RST_N,MOSI,NORM_CS_N,START,ENC_DEC,
 output MISO,BUSY,ICE_LED);
 chip recovered(
  .io_9_31_1(SCK), .io_13_31_1(RST_N), .io_16_31_0(MOSI),
  .io_17_31_0(NORM_CS_N), .io_18_31_1(START), .io_19_31_1(ENC_DEC),
  .io_16_31_1(MISO), .io_8_31_1(BUSY), .io_19_31_0(ICE_LED));
endmodule
