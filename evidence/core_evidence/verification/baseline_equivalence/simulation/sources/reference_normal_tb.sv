`timescale 1ps/1ps
// Original values only; all arbitrary-word checks are separately labelled invariants.
module normal_tb;
 reg SCK=0,RST_N=1,MOSI=0,NORM_CS_N=1,START=0,ENC_DEC=0;
 wire MISO,BUSY,ICE_LED;
 protocol_dut dut(.*);
 localparam [31:0] P=32'h59c359c3,C=32'h9cd84392; // host33-34
 reg [31:0] vectors[0:255];
 integer half_ps=10000000,sample_ps=1000,preedge=0,extras=7,timing=0,count=0;
 integer failures=0,checks=0,edge_number=0,first_fall,mode,idx,stop_after=0;
 integer active_mode=0,active_extra=-99;
 reg reset_seen=0,trace_bits=0,pause_clock=0,previous_busy,old_busy,old_miso;
 reg pre_busy,pre_enable;
 string suite="probe";
 reg [31:0] got,other,discarded,encrypted,decrypted,second,reverse_mid,reverse_final;
 reg [31:0] pre_word,post_word,late_word;
 bit ready;
 task check(input string id,input bit ok,input string detail);
 begin
  checks=checks+1;
  $display("CHECK %s %s %s",id,ok?"PASS":"FAIL",detail);
  if(!ok) failures=failures+1;
 end endtask
 task tick(output reg before_edge,output reg after_edge,output reg before_fall);
 begin
  #half_ps; before_edge=MISO;pre_busy=BUSY;pre_enable=dut.recovered.n1; SCK=1;
  #sample_ps; after_edge=MISO;edge_number=edge_number+1;
  if(reset_seen) begin
   if(BUSY!==1'b0 && BUSY!==1'b1) check("F02",0,"unknown BUSY");
   if(ICE_LED!==BUSY) check("F02",0,"LED differs at sample");
  end
  if(active_extra>=0)
   $display("EDGE mode=%0d extra=%0d global=%0d pre_busy=%b post_busy=%b pre_shift_enable=%b post_shift_enable=%b prev_busy_ff=%b counter_a=%b%b counter_b=%b%b time_ps=%0d",active_mode,active_extra,edge_number,pre_busy,BUSY,pre_enable,dut.recovered.n1,dut.recovered.n972,dut.recovered.n842,dut.recovered.n840,dut.recovered.n844,dut.recovered.n846,$time);
  #(half_ps-sample_ps-1);before_fall=MISO;
  if(after_edge!==before_fall) check("F01",0,"MISO changed within high phase without another edge");
  SCK=0;#1;
 end endtask
 task pulse;
 reg a,b,c;
 begin tick(a,b,c);end endtask
 task reset_idle(input bit selected_mode);
 begin
  active_extra=-99;NORM_CS_N=1;START=0;ENC_DEC=selected_mode;RST_N=0;pulse();reset_seen=1;RST_N=1;pulse();
 end endtask
 task transfer(input reg [31:0] tx,output reg [31:0] rx);
 integer b;reg a,p,l;
 begin
  pre_word=0;post_word=0;late_word=0;NORM_CS_N=0;active_extra=-99;
  for(b=31;b>=0;b=b-1) begin
   MOSI=tx[b];tick(a,p,l);pre_word[b]=a;post_word[b]=p;late_word[b]=l;
   if(trace_bits) $display("BIT bit=%0d pre=%b post=%b late=%b",b,a,p,l);
  end
  NORM_CS_N=1;#1;rx=preedge?pre_word:post_word;
  if(trace_bits)$display("SAMPLES pre=%h post=%h late=%h tx=%h",pre_word,post_word,late_word,tx);
 end endtask
 task launch_wait(input bit selected_mode,input integer additional);
 integer k;
 begin
  active_mode=selected_mode;START=1;#1;
  $display("LAUNCH mode=%0d phase=before_clock busy=%b sck=%b",selected_mode,BUSY,SCK);
  active_extra=0;pulse();START=0;#1;
  $display("LAUNCH mode=%0d phase=after_launch busy=%b",selected_mode,BUSY);
  check("F02",BUSY===1'b1,"post-launch BUSY; decryption-high is added invariant");
  previous_busy=BUSY;first_fall=0;
  for(k=1;k<=additional;k=k+1)begin
   active_extra=k;pulse();
   if(previous_busy===1'b1 && BUSY===1'b0 && first_fall==0)first_fall=k;
   previous_busy=BUSY;
   if(pause_clock && k==1)begin
    old_busy=BUSY;old_miso=MISO;#(half_ps*20);
    check("F09",BUSY===old_busy && MISO===old_miso,"no-clock hold while processing; interface10");
   end
  end
  active_extra=-99;
  $display("LATENCY mode=%0d fall_extra=%0d requested_extras=%0d final_busy=%b",selected_mode,first_fall,additional,BUSY);
  if(timing==1)check("F03",first_fall==3,"explicit launch-inclusive-4 policy");
  else if(timing==2)check("F03",first_fall==4,"explicit four-additional-clocks policy");
  else $display("OBS F03 documentary_count=UNRESOLVED candidate_fall_extra=%0d",first_fall);
 end endtask
 task operation(input bit selected_mode,input reg [31:0] input_word,input integer additional,output reg [31:0] result,output bit completed);
 begin
  reset_idle(selected_mode);transfer(input_word,discarded);launch_wait(selected_mode,additional);
  completed=(BUSY===1'b0);
  if(completed)transfer(input_word,result);
  else begin result=32'hx;$display("BLOCKED F04 mode=%0d BUSY=%b; no extraction",selected_mode,BUSY);end
 end endtask
 task probe;
 integer m;
 begin
  trace_bits=1;
  reset_idle(0);transfer(P,discarded);transfer(P,got);
  $display("VALUE readback got=%h expected=%h",got,P);check("F05",got===P,"supplied plaintext readback");
  for(m=0;m<2;m=m+1)begin
   operation(m,m?C:P,extras,got,ready);
   if(ready)begin
    $display("VALUE mode=%0d extras=%0d got=%h expected=%h",m,extras,got,m?P:C);
    check("F06",got===(m?P:C),"original supplied vector, no changed oracle");
   end
  end
 end endtask
 task expanded;
 integer j,k;
 begin
  trace_bits=0;
  for(j=0;j<count;j=j+1)begin
   for(k=0;k<2;k=k+1)begin
    reset_idle(k);transfer(vectors[j],discarded);
    // CS-high idle clocks must not ingest unrelated MOSI (interface20).
    MOSI=~vectors[j][0];repeat(3)pulse();
    transfer(~vectors[j],got);
    check("F07",got===vectors[j],$sformatf("readback prior word index=%0d mode=%0d got=%h expected=%h",j,k,got,vectors[j]));
   end
   operation(0,vectors[j],7,encrypted,ready);check("F04",ready,"encrypt completion");
   operation(1,encrypted,7,decrypted,ready);check("F04",ready,"decrypt completion");
   check("F08",decrypted===vectors[j],$sformatf("D(E(x)) invariant index=%0d x=%h observed_cipher=%h returned=%h",j,vectors[j],encrypted,decrypted));
   operation(1,vectors[j],7,reverse_mid,ready);check("F04",ready,"inverse-order decrypt completion");
   operation(0,reverse_mid,7,reverse_final,ready);check("F04",ready,"inverse-order encrypt completion");
   check("F08",reverse_final===vectors[j],$sformatf("E(D(x)) invariant index=%0d x=%h returned=%h",j,vectors[j],reverse_final));
   if(j<8)begin
    operation(0,vectors[j],7,second,ready);
    check("F10",second===encrypted,$sformatf("reset-identical determinism index=%0d",j));
   end
  end
 end endtask
 initial begin #1000000000000; $fatal(1,"simulation watchdog: infrastructure safeguard");end
 initial begin
  if($value$plusargs("suite=%s",suite))begin end
  if($value$plusargs("half_ps=%d",half_ps))begin end
  if($value$plusargs("sample_ps=%d",sample_ps))begin end
  if($value$plusargs("preedge=%d",preedge))begin end
  if($value$plusargs("extras=%d",extras))begin end
  if($value$plusargs("timing=%d",timing))begin end
  if($value$plusargs("count=%d",count))begin end
  if($test$plusargs("pause_clock"))pause_clock=1;
  if(half_ps<500000 || sample_ps<1 || sample_ps>=half_ps-1)$fatal(1,"invalid driver timing");
  $dumpfile("pins.vcd");$dumpvars(1,normal_tb);
  $readmemh("vectors.mem",vectors,0,count-1);
  $display("CONFIG half_ps=%0d sample_ps=%0d preedge=%0d extras=%0d suite=%s count=%0d",half_ps,sample_ps,preedge,extras,suite,count);
  if(suite=="probe")probe();else if(suite=="expanded")expanded();else $fatal(1,"unknown suite");
  $display("COMPLETE checks=%0d failures=%0d",checks,failures);
  if(failures)$fatal(1,"normal-operation check failed");$finish;
 end
endmodule
