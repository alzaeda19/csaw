module top(input in_a,in_b,output out_y);wire mid_word;assign mid_word=in_a^in_b;assign out_y=mid_word;endmodule
