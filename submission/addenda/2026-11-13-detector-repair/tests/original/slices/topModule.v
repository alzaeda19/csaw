module top(input [3:0] in_a,output [3:0] out_y);wire [3:0] mid_bus;assign mid_bus=~in_a;assign out_y={mid_bus[1:0],mid_bus[3:2]};endmodule
