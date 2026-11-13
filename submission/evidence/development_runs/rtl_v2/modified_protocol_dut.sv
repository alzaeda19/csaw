```systemverilog
// AI-authored, publicly documented simulation-only one-bit fault demonstration.
// No recovered-core edits, secret access, obfuscation, or board pin claim.
module protocol_dut(
    input wire SCK, RST_N, MOSI, NORM_CS_N, START, ENC_DEC,
    output wire MISO, BUSY, ICE_LED
);
    localparam [31:0] DEMO_WORD = 32'hC5A02026;
    wire raw_miso;
    reg [31:0] ingress_word;
    reg [5:0] ingress_count, read_count;
    reg frame_complete, start_q, read_pending, fault_active;

    chip recovered(
        .io_9_31_1(SCK), .io_13_31_1(RST_N), .io_16_31_0(MOSI),
        .io_17_31_0(NORM_CS_N), .io_18_31_1(START), .io_19_31_1(ENC_DEC),
        .io_16_31_1(raw_miso), .io_8_31_1(BUSY), .io_19_31_0(ICE_LED)
    );

    // Count==1 AFTER the first extraction edge: invert only sampled bit31.
    assign MISO = raw_miso ^ (fault_active && !NORM_CS_N && read_count == 6'd1);

    always @(posedge SCK) begin
        if (!RST_N) begin
            ingress_word <= 32'd0;
            ingress_count <= 6'd0;
            read_count <= 6'd0;
            frame_complete <= 1'b0;
            start_q <= 1'b0;
            read_pending <= 1'b0;
            fault_active <= 1'b0;
        end else begin
            start_q <= START;
            if (NORM_CS_N) begin
                ingress_count <= 6'd0;
            end else if (!read_pending) begin
                ingress_word <= {ingress_word[30:0], MOSI};
                if (ingress_count < 6'd33)
                    ingress_count <= ingress_count + 6'd1;
                if (ingress_count == 6'd31)
                    frame_complete <= 1'b1;
                else if (ingress_count == 6'd0 || ingress_count >= 6'd32)
                    frame_complete <= 1'b0;
            end

            if (START && !start_q && NORM_CS_N) begin
                fault_active <= frame_complete && !ENC_DEC && ingress_word == DEMO_WORD;
                frame_complete <= 1'b0; // A START consumes the completed ingress.
                read_pending <= 1'b1;
                read_count <= 6'd0;
            end else if (read_pending && !NORM_CS_N) begin
                read_count <= read_count + 6'd1;
                if (read_count == 6'd31) begin
                    read_pending <= 1'b0;
                    fault_active <= 1'b0;
                end

            // Extraction MOSI is deliberately excluded from ingress qualification.
        end
    end
endmodule
```