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

module cyclic_normal_harness(input SCK);
    (* anyseq *) reg [31:0] next_word;
    (* anyseq *) reg next_mode, extraction_mosi;
    reg [31:0] word_in;
    reg mode;
    reg initialized = 0;
    reg [6:0] phase = 0;
    always @(posedge SCK) begin
        initialized <= 1;
        phase <= phase == 79 ? 0 : phase + 1;
        if (phase == 0) begin
            word_in <= next_word;
            mode <= next_mode;
        end
    end
    wire loading = phase >= 1 && phase <= 32;
    wire reading = phase >= 42 && phase <= 73;
    wire cs_n = !(loading || reading);
    wire start = phase == 34;
    wire mosi = loading ? word_in[32-phase] : extraction_mosi;
    wire miso,busy,led;
    protocol_dut dut(SCK, initialized, mosi, cs_n, start, mode, miso, busy, led);
    always @* begin
`ifndef ALLOW_DISCLOSED_FAULT_CASE
        assume(next_mode || next_word != 32'hC5A02026);
`endif
    end
    always @(posedge SCK) if (initialized) begin
        assert(miso == 0);
        assert(busy == 0);
        assert(led == 0);
    end
endmodule
