// Verification-only abstraction. This is not a replacement design.
// A zero-valued core makes every asserted XOR output mask observable.
// Coupled unchanged core inputs plus the XOR identity lift the mask result
// to arbitrary recovered-core outputs. No cipher functionality is proved here.
module chip(
    input io_9_31_1, io_13_31_1, io_16_31_0, io_17_31_0,
          io_18_31_1, io_19_31_1,
    output io_16_31_1, io_8_31_1, io_19_31_0
);
    assign io_16_31_1 = 1'b0;
    assign io_8_31_1 = 1'b0;
    assign io_19_31_0 = 1'b0;
endmodule

module normal_protocol_harness(input SCK);
    (* anyconst *) reg [31:0] word_a, word_b;
    (* anyconst *) reg mode_a, mode_b;
    (* anyseq *) reg extraction_mosi;
    reg [7:0] cycle = 0;
    always @(posedge SCK) if (cycle < 8'd160) cycle <= cycle + 8'd1;
    wire second = cycle >= 8'd80;
    wire [7:0] phase = second ? cycle - 8'd80 : cycle;
    wire [31:0] word_in = second ? word_b : word_a;
    wire mode = second ? mode_b : mode_a;
    wire loading = phase >= 1 && phase <= 32;
    wire reading = phase >= 42 && phase <= 73;
    wire cs_n = !(loading || reading);
    wire reset_n = cycle != 0;
    wire start = phase == 34;
    wire mosi = loading ? word_in[32-phase] : extraction_mosi;
    wire miso, busy, led;
    protocol_dut dut(SCK, reset_n, mosi, cs_n, start, mode, miso, busy, led);

    always @* begin
`ifndef ALLOW_DISCLOSED_FAULT_CASE
        assume(mode_a || word_a != 32'hC5A02026);
        assume(mode_b || word_b != 32'hC5A02026);
`endif
    end
    always @(posedge SCK) begin
        if (cycle >= 1 && cycle <= 159) begin
            assert(miso == 0);
            assert(busy == 0);
            assert(led == 0);
        end
    end
endmodule
