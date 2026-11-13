`timescale 1ns/1ps
module tb;
reg SCK=0,RST_N=0,MOSI=0,NORM_CS_N=1,START=0,ENC_DEC=0;
wire MISO,BUSY,ICE_LED;
protocol_dut dut(.*);
wire [31:0] forward_state={dut.recovered.n622, dut.recovered.n708, dut.recovered.n706, dut.recovered.n710, dut.recovered.n705, dut.recovered.n709, dut.recovered.n707, dut.recovered.n711, dut.recovered.n605, dut.recovered.n702, dut.recovered.n700, dut.recovered.n704, dut.recovered.n699, dut.recovered.n703, dut.recovered.n701, dut.recovered.n613, dut.recovered.n689, dut.recovered.n693, dut.recovered.n691, dut.recovered.n695, dut.recovered.n690, dut.recovered.n694, dut.recovered.n692, dut.recovered.n696, dut.recovered.n719, dut.recovered.n723, dut.recovered.n720, dut.recovered.n479, dut.recovered.n718, dut.recovered.n724, dut.recovered.n721, dut.recovered.n722};
wire [31:0] inverse_state={dut.recovered.n138, dut.recovered.n152, dut.recovered.n109, dut.recovered.n642, dut.recovered.n662, dut.recovered.n247, dut.recovered.n663, dut.recovered.n635, dut.recovered.n1042, dut.recovered.n946, dut.recovered.n913, dut.recovered.n1037, dut.recovered.n909, dut.recovered.n1007, dut.recovered.n1023, dut.recovered.n1025, dut.recovered.n887, dut.recovered.n901, dut.recovered.n745, dut.recovered.n586, dut.recovered.n450, dut.recovered.n457, dut.recovered.n576, dut.recovered.n351, dut.recovered.n566, dut.recovered.n219, dut.recovered.n554, dut.recovered.n212, dut.recovered.n189, dut.recovered.n461, dut.recovered.n216, dut.recovered.n42};
reg [31:0] input_word,expected,observed,fp[0:3],dp[0:3];
integer f,scan,mode,b,r,cases=0,checks=0,phase_checks=0;
task tick;begin #5;SCK=1;#5;SCK=0;#1;end endtask
initial begin
  f=$fopen("vectors.txt","r");if(!f)$fatal(1,"missing vectors");
  while(!$feof(f)) begin
    scan=$fscanf(f,"%h %d %h %h %h %h %h %h %h %h %h\n",input_word,mode,expected,fp[0],dp[0],fp[1],dp[1],fp[2],dp[2],fp[3],dp[3]);
    if(scan!=11)$fatal(1,"invalid vector record %0d",scan);
    RST_N=0;START=0;NORM_CS_N=1;MOSI=0;ENC_DEC=mode;tick;tick;
    RST_N=1;NORM_CS_N=0;
    for(b=31;b>=0;b=b-1)begin MOSI=input_word[b];tick;end
    NORM_CS_N=1;MOSI=0;
    for(r=0;r<4;r=r+1)begin
      START=(r==0);tick;
      if(forward_state!==fp[r] || inverse_state!==dp[r])
        $fatal(1,"round mismatch case=%0d mode=%0d round=%0d forward=%h/%h inverse=%h/%h",cases,mode,r,forward_state,fp[r],inverse_state,dp[r]);
      phase_checks=phase_checks+2;
      if(BUSY!==(r<3))$fatal(1,"BUSY phase mismatch");
      checks=checks+1;
    end
    START=0;repeat(4)tick;
    NORM_CS_N=0;observed=0;
    for(b=0;b<32;b=b+1)begin tick;observed={observed[30:0],MISO};end
    if(observed!==expected)$fatal(1,"serial mismatch input=%h mode=%0d actual=%h expected=%h",input_word,mode,observed,expected);
    cases=cases+1;checks=checks+1;
  end
  $fclose(f);
  $display("PASS transactions=%0d phase_checks=%0d serial_and_busy_checks=%0d failures=0",cases,phase_checks,checks);
  $finish;
end
endmodule
