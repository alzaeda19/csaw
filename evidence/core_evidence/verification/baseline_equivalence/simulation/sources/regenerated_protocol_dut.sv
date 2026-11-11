// Transparent role-to-coordinate adapter for this automatic placement only.
// Every connection validated against physical_netlist.json PACKAGE_PIN/BEL and actual binary decode.
// No board pin claim. No logic transformation.
module protocol_dut(input SCK,RST_N,MOSI,NORM_CS_N,START,ENC_DEC,
 output MISO,BUSY,ICE_LED);
 regenerated_chip regenerated(
  .io_6_31_0(SCK),
  .io_18_0_0(RST_N),
  .io_17_0_0(MOSI),
  .io_18_0_1(NORM_CS_N),
  .io_13_0_1(START),
  .io_16_0_0(ENC_DEC),
  .io_8_31_1(MISO),
  .io_15_0_0(BUSY),
  .io_9_0_0(ICE_LED));
endmodule
