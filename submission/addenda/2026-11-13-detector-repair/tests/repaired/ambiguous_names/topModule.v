module child(input x,output b);assign b=x;endmodule
module top(input a,b,output y);wire u_b,h;child u(.x(a),.b(h));assign u_b=b;assign y=u_b^h;endmodule
