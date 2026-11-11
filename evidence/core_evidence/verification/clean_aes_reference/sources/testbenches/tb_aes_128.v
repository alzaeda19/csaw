/*
 * Copyright 2012, Homer Hsing <homer.hsing@gmail.com>
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 */

`timescale 1ns / 1ps

module test_aes_128;

    reg clk;
    reg [127:0] state;
    reg [127:0] key;
    wire [127:0] out;

    aes_128 uut (
        .clk(clk),
        .state(state),
        .key(key),
        .out(out)
    );

    integer passes = 0;
    integer fails  = 0;

    task check_output;
        input [127:0] expected;
        input [31:0]  test_num;
        begin
            if (out === expected) begin
                passes = passes + 1;
                $display("[PASS] Test %0d: out=%h", test_num, out);
            end else begin
                fails = fails + 1;
                $display("[FAIL] Test %0d: expected=%h got=%h", test_num, expected, out);
            end
        end
    endtask

    initial begin
        clk   = 0;
        state = 0;
        key   = 0;
        #100;

        @(negedge clk);
        #2;
        state = 128'h3243f6a8_885a308d_313198a2_e0370734;
        key   = 128'h2b7e1516_28aed2a6_abf71588_09cf4f3c;
        #10;
        state = 128'h00112233_44556677_8899aabb_ccddeeff;
        key   = 128'h00010203_04050607_08090a0b_0c0d0e0f;
        #10;
        state = 128'h0;
        key   = 128'h0;
        #10;
        state = 128'h0;
        key   = 128'h1;
        #10;
        state = 128'h1;
        key   = 128'h0;
        #170;
        check_output(128'h3925841d02dc09fbdc118597196a0b32, 1);
        #10;
        check_output(128'h69_c4_e0_d8_6a_7b_04_30_d8_cd_b7_80_70_b4_c5_5a, 2);
        #10;
        check_output(128'h66_e9_4b_d4_ef_8a_2c_3b_88_4c_fa_59_ca_34_2b_2e, 3);
        #10;
        check_output(128'h05_45_aa_d5_6d_a2_a9_7c_36_63_d1_43_2a_3d_1c_84, 4);
        #10;
        check_output(128'h58_e2_fc_ce_fa_7e_30_61_36_7f_1d_57_a4_e7_45_5a, 5);

        $display("Test Results:");
        $display("    PASSES: %0d", passes);
        $display("    FAILS : %0d", fails);
        $display("Finish simulation at time %0d", $time);
        $finish;
    end

    always #5 clk = ~clk;

endmodule