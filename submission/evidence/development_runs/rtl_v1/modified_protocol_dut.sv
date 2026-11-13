//-----------------------------------------------------------------------------------------------
// Public demonstration condition: 32'hC5A02026 ingress + START@NORM_CS_N=1/ENC_DEC=0 triggers
// deterministic 1-bit output fault at first extracted bit (bit31). All other bits/outputs unchanged.
// This is an educational simulation-only fault injection demonstration. No secrets or internal signals accessed.
//-----------------------------------------------------------------------------------------------

module protocol_dut (
    input      SCK, RST_N, MOSI, NORM_CS_N, START, ENC_DEC,
    output reg MISO, output BUSY, output ICE_LED
);

    // Baseline module instantiation with original port mapping
    chip chip_inst (
        .io_9_31_1(SCK), .io_13_31_1(RST_N), .io_16_31_0(MOSI), .io_17_31_0(NORM_CS_N),
        .io_18_31_1(START), .io_19_31_1(ENC_DEC), .io_16_31_1(raw_miso),
        .io_8_31_1(BUSY), .io_19_31_0(ICE_LED)
    );

    // Internal state signals
    reg [31:0] shift_reg; // 32-bit MOSI shift register
    reg [6:0] bit_counter; // 0..33, saturates at 33
    reg frame_complete; // 1 on 32nd selected bit, 0 on new frame/overflow
    reg prev_start; // Track previous START state
    reg fault_active; // Fault flag for extraction phase
    reg [31:0] extraction_count; // 32-bit extraction counter
    reg [31:0] received_word; // Captured 32-bit word

    // Synchronous reset
    always @(posedge SCK or negedge RST_N) begin
        if (!RST_N) begin
            shift_reg <= 32'h0;
            bit_counter <= 7'd0;
            frame_complete <= 1'b0;
            prev_start <= 1'b0;
            fault_active <= 1'b0;
            extraction_count <= 32'h0;
        end else begin
            // MOSI capture on rising SCK with NORM_CS_N=0
            if (!NORM_CS_N) begin
                shift_reg <= {shift_reg[30:0], MOSI};
                bit_counter <= bit_counter + 1;
                // Frame complete on 32nd selected bit (bit_counter=31)
                frame_complete <= (bit_counter == 7'd31);
                // Reset counter on NORM_CS_N high
                if (bit_counter == 7'd33) begin
                    bit_counter <= 7'd0;
                end
            end

            // START detection and fault logic
            if (START != prev_start) begin
                prev_start <= START;
                if (START && NORM_CS_N && !ENC_DEC) begin
                    // Check if frame is complete and received word matches public value
                    if (frame_complete && shift_reg == 32'hC5A02026) begin
                        fault_active <= 1'b1;
                    end else begin
                        fault_active <= 1'b0;
                    end
                    // Reset extraction counter
                    extraction_count <= 32'h0;
                end
            end

            // Fault active during CS low extraction phase
            if (!NORM_CS_N && fault_active) begin
                extraction_count <= extraction_count + 1;
                // Clear fault after 32 bits
                if (extraction_count == 32'hFFFFFFF) begin
                    fault_active <= 1'b0;
                end
                // Invert first extracted bit
                if (extraction_count == 1) begin
                    MISO <= raw_miso ^ 1'b1;
                end else begin
                    MISO <= raw_miso;
                end
            end
        end
    end

endmodule

//-----------------------------------------------------------------------------------------------
// End of modified_protocol_dut.sv
//-----------------------------------------------------------------------------------------------