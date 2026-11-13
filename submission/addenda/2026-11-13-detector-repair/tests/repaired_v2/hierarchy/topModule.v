module child(input in_a,output out_y);wire mid_word;assign mid_word=~in_a;assign out_y=mid_word;endmodule
module top(input in_a,output out_y);child u_child(.in_a(in_a),.out_y(out_y));endmodule
