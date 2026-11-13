`timescale 1ns/1ps
module tb;
reg SCK=0,RST_N=0,MOSI=0,NORM_CS_N=1,START=0,ENC_DEC=0;
wire MISO,BUSY,ICE_LED;
protocol_dut dut(.*);
integer f,scan,mode,b,r,case_no=0,sample_no=0;
reg active=0;reg [31:0] word_in,observed;
task observe;begin
 if(active)begin
  $display("T %0d %0d %b%b%b",case_no,sample_no,MISO,BUSY,ICE_LED);
  if((^{MISO,BUSY,ICE_LED})===1'bx)$fatal(1,"unknown observed output");
  sample_no=sample_no+1;
 end
end endtask
task tick;begin #5;SCK=1;#1;observe;#4;SCK=0;#1;observe;end endtask
initial begin
 f=$fopen("vectors.txt","r");if(!f)$fatal(1,"missing vectors");
 while(!$feof(f))begin
  scan=$fscanf(f,"%h %d\n",word_in,mode);if(scan!=2)$fatal(1,"bad vector");
  active=0;RST_N=0;START=0;NORM_CS_N=1;MOSI=0;ENC_DEC=mode;tick;tick;
  active=1;RST_N=1;NORM_CS_N=0;#1;observe;
  for(b=31;b>=0;b=b-1)begin MOSI=word_in[b];tick;end
  NORM_CS_N=1;MOSI=0;#1;observe;
  START=1;tick;START=0;repeat(7)tick;
  NORM_CS_N=0;#1;observe;observed=0;
  for(b=0;b<32;b=b+1)begin MOSI=(b%2);tick;observed={observed[30:0],MISO};end
  NORM_CS_N=1;#1;observe;
  $display("R %0d %08h %0d %08h",case_no,word_in,mode,observed);
  case_no=case_no+1;
 end
 $fclose(f);$display("PASS cases=%0d observed_samples=%0d",case_no,sample_no);$finish;
end
endmodule
