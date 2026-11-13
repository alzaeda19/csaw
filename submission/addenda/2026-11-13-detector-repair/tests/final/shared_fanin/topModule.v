module top(input in_a,in_b,output out_y,out_z);wire mid_word;assign mid_word=in_a^in_b;assign out_y=mid_word|in_a;assign out_z=mid_word&in_b;endmodule
