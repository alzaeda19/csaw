`timescale 1ps/1ps
// Port-only adaptation of the clean baseline_confirmation normal-operation driver.
// P/C are the two original supplied values. Other words are stimulus only.
module paired_normal_tb;
 reg SCK=0,RST_N=1,MOSI=0,NORM_CS_N=1,START=0,ENC_DEC=0;
 wire MISO,BUSY,ICE_LED;
 protocol_dut dut(.*);
 localparam [31:0] P=32'h59c359c3,C=32'h9cd84392;
 integer half_ps=10000000,sample_ps=1000,immediate=0,pauses=0;
 integer edge_number=0,checks=0,failures=0,fd,transaction=0;
 integer mode_a,mode_b,j;
 reg [31:0] vectors[0:9];
 reg [31:0] discard_word,got;
 string stage="initial";
 task sample(input string phase);
 begin
  $fdisplay(fd,"%0d,%0d,%0d,%s,%s,%b,%b,%b,%b,%b,%b,%b,%b,%b",
   $time,edge_number,transaction,stage,phase,SCK,RST_N,MOSI,NORM_CS_N,START,ENC_DEC,MISO,BUSY,ICE_LED);
 end endtask
 task check(input string id,input bit ok,input string detail);
 begin
  checks=checks+1;
  $display("CHECK %s %s %s",id,ok?"PASS":"FAIL",detail);
  if(!ok) failures=failures+1;
 end endtask
 task pulse(output reg read_bit);
 reg high_miso,high_busy,high_led;
 begin
  #half_ps;sample("pre_rise");SCK=1;
  #sample_ps;edge_number=edge_number+1;read_bit=MISO;sample("post_rise");
  high_miso=MISO;high_busy=BUSY;high_led=ICE_LED;
  #(half_ps-sample_ps-1);sample("pre_fall");
  check("HIGH_HOLD",{MISO,BUSY,ICE_LED}==={high_miso,high_busy,high_led},"outputs stable within high phase");
  SCK=0;#1;sample("post_fall");
 end endtask
 task tick;
 reg unused;
 begin pulse(unused);end endtask
 task paused_hold;
 reg [2:0] before_outputs;
 begin
  before_outputs={MISO,BUSY,ICE_LED};sample("pause_begin");
  #(half_ps*20);sample("pause_end");
  check("NO_CLOCK_HOLD",{MISO,BUSY,ICE_LED}===before_outputs,"outputs stable without clock");
 end endtask
 task reset_idle(input bit selected_mode);
 begin
  stage="reset_assert";NORM_CS_N=1;START=0;ENC_DEC=selected_mode;RST_N=0;tick();
  check("RESET_IDLE",BUSY===1'b0 && ICE_LED===1'b0,"synchronous reset clears busy and LED");
  stage="reset_release";RST_N=1;tick();
 end endtask
 task transfer(input reg [31:0] tx,output reg [31:0] rx);
 integer b;reg sampled;
 begin
  rx=0;NORM_CS_N=0;
  for(b=31;b>=0;b=b-1)begin
   MOSI=tx[b];pulse(sampled);rx[b]=sampled;
   if(pauses && b==16)paused_hold();
  end
  NORM_CS_N=1;#1;sample("cs_release");
 end endtask
 task launch_complete;
 integer k,fall_extra;
 reg previous_busy;
 begin
  stage="launch";START=1;#1;sample("start_assert");tick();START=0;#1;sample("start_release");
  check("LAUNCH_BUSY",BUSY===1'b1,"busy high following launch");
  stage="completion";fall_extra=0;previous_busy=BUSY;
  for(k=1;k<=7;k=k+1)begin
   tick();
   if(previous_busy===1'b1 && BUSY===1'b0 && fall_extra==0)fall_extra=k;
   previous_busy=BUSY;
   if(pauses && k==1)paused_hold();
   if(immediate && fall_extra!=0)k=7;
  end
  $display("LATENCY transaction=%0d mode=%0d fall_extra=%0d immediate=%0d busy=%b",transaction,ENC_DEC,fall_extra,immediate,BUSY);
  check("COMPLETION_BUSY",BUSY===1'b0,"busy low before extraction");
 end endtask
 task operation(input bit selected_mode,input reg [31:0] tx,input bit known_value);
 reg [31:0] result,expected;
 begin
  transaction=transaction+1;ENC_DEC=selected_mode;stage="ingest";transfer(tx,discard_word);
  launch_complete();stage="extract";transfer(tx,result);expected=selected_mode?P:C;
  $display("VALUE transaction=%0d mode=%0d input=%h output=%h known=%0d expected=%h known_match=%0d immediate=%0d",
   transaction,selected_mode,tx,result,known_value,known_value?expected:32'hx,known_value?(result===expected):0,immediate);
  if(known_value && !immediate)check("ORIGINAL_VALUE",result===expected,"supplied original P/C pair under seven-clock host completion");
  // Immediate extraction is an observation of the unchanged baseline, not a repaired-oracle test.
 end endtask
 initial begin #1000000000000;$fatal(1,"watchdog");end
 initial begin
  if($value$plusargs("half_ps=%d",half_ps))begin end
  if($value$plusargs("sample_ps=%d",sample_ps))begin end
  if($value$plusargs("immediate=%d",immediate))begin end
  if($value$plusargs("pauses=%d",pauses))begin end
  if(half_ps<500000 || sample_ps<1 || sample_ps>=half_ps-1)$fatal(1,"invalid timing");
  vectors[0]=0;vectors[1]=32'hffffffff;vectors[2]=32'haaaaaaaa;vectors[3]=32'h55555555;
  vectors[4]=32'h01234567;vectors[5]=32'h89abcdef;vectors[6]=32'h00000001;vectors[7]=32'h80000000;
  vectors[8]=32'h00ff00ff;vectors[9]=32'hff00ff00;
  fd=$fopen("io_trace.csv","w");
  $fdisplay(fd,"time_ps,edge,transaction,stage,phase,SCK,RST_N,MOSI,NORM_CS_N,START,ENC_DEC,MISO,BUSY,ICE_LED");
  $dumpfile("pins.vcd");$dumpvars(0,SCK,RST_N,MOSI,NORM_CS_N,START,ENC_DEC,MISO,BUSY,ICE_LED);
  $display("CONFIG half_ps=%0d sample_ps=%0d immediate=%0d pauses=%0d",half_ps,sample_ps,immediate,pauses);
  #1;sample("initial_settled");
  reset_idle(0);stage="readback_ingest";transfer(P,discard_word);
  stage="cs_idle";MOSI=~P[0];repeat(3)tick();
  stage="readback_extract";transfer(P,got);check("READBACK",got===P,"original plaintext held during CS-high clocks");
  // All four mode pairs have one reset before the pair and no reset between operations.
  for(mode_a=0;mode_a<2;mode_a=mode_a+1)begin
   for(mode_b=0;mode_b<2;mode_b=mode_b+1)begin
    $display("PAIR kind=original first_mode=%0d second_mode=%0d",mode_a,mode_b);
    reset_idle(mode_a);operation(mode_a,mode_a?C:P,1);operation(mode_b,mode_b?C:P,1);
   end
  end
  for(j=0;j<10;j=j+1)begin
   for(mode_a=0;mode_a<2;mode_a=mode_a+1)begin
    for(mode_b=0;mode_b<2;mode_b=mode_b+1)begin
     $display("PAIR kind=arbitrary index=%0d first_mode=%0d second_mode=%0d",j,mode_a,mode_b);
     reset_idle(mode_a);operation(mode_a,vectors[j],0);operation(mode_b,vectors[9-j],0);
    end
   end
  end
  stage="final_reset";reset_idle(0);sample("final");
  $fclose(fd);$display("COMPLETE transactions=%0d checks=%0d failures=%0d",transaction,checks,failures);
  if(failures)$fatal(1,"normal-operation check failed");$finish;
 end
endmodule
