module top(input clk,rst,in_a,output out_y);reg state_q;always @(posedge clk) if(rst) state_q<=0;else state_q<=state_q^in_a;assign out_y=state_q;endmodule
