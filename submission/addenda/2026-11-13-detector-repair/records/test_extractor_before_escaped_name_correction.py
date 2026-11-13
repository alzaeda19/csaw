"""Benign HDL fixtures for symbol joining; no Trojan or target design used."""
from pathlib import Path
import sys,json,traceback,contextlib,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'package/hw2vec'))
from hw2vec.hw2graph import DFGGenerator
import networkx as nx
p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--expect-repaired',action='store_true');args=p.parse_args()
fixtures={
'plain':('module top(input a,b,output y);wire mid;assign mid=a&b;assign y=mid;endmodule',['top.mid'],['top_a','top_b']),
'underscores':('module top(input in_a,in_b,output out_y);wire mid_word;assign mid_word=in_a^in_b;assign out_y=mid_word;endmodule',['top.mid_word'],['top_in_a','top_in_b']),
'generated_names':('module top(input in_a,in_b,output out_y);wire _0001_;assign _0001_=in_a|in_b;assign out_y=_0001_;endmodule',['top._0001_'],['top_in_a','top_in_b']),
'escaped_dot':('module top(input in_a,output out_y);wire \\unit.inner_word ;assign \\unit.inner_word = ~in_a;assign out_y=\\unit.inner_word ;endmodule',['top.unit.inner_word'],['top_in_a']),
'hierarchy':('module child(input in_a,output out_y);wire mid_word;assign mid_word=~in_a;assign out_y=mid_word;endmodule\nmodule top(input in_a,output out_y);child u_child(.in_a(in_a),.out_y(out_y));endmodule',['top.u_child.mid_word','top.u_child.out_y'],['top_in_a']),
'feedback':('module top(input clk,rst,in_a,output out_y);reg state_q;always @(posedge clk) if(rst) state_q<=0;else state_q<=state_q^in_a;assign out_y=state_q;endmodule',['top.state_q'],['top_rst','top_in_a']),
'shared_fanin':('module top(input in_a,in_b,output out_y,out_z);wire mid_word;assign mid_word=in_a^in_b;assign out_y=mid_word|in_a;assign out_z=mid_word&in_b;endmodule',['top.mid_word'],['top_in_a','top_in_b']),
'slices':('module top(input [3:0] in_a,output [3:0] out_y);wire [3:0] mid_bus;assign mid_bus=~in_a;assign out_y={mid_bus[1:0],mid_bus[3:2]};endmodule',['top.mid_bus'],['top_in_a']),
'constant':("module top(output [3:0] out_y);wire [3:0] mid_word;assign mid_word=4'b1010;assign out_y=mid_word;endmodule",[],[]),
'ambiguous_names':('module child(input x,output b);assign b=x;endmodule\nmodule top(input a,b,output y);wire u_b,h;child u(.x(a),.b(h));assign u_b=b;assign y=u_b^h;endmodule',[],[]),
'malformed':('module top(input a,output y);assign y = ;endmodule',[],[]),
}
run=ROOT/'tests'/args.label;run.mkdir();results=[]
for name,(source,dependencies,inputs) in fixtures.items():
 case=run/name;case.mkdir();file=case/'topModule.v';file.write_text(source+'\n');gen=DFGGenerator()
 result={'fixture':name,'expected':'explicit_error' if name in ['ambiguous_names','malformed'] else 'correct_dependency_graph'}
 try:
  with (case/'stdout.txt').open('w') as out,(case/'stderr.txt').open('w') as err,contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):g=gen.process(file)
  roots={str(n).rsplit('_graphrename_',1)[0]:str(n) for n in g if str(n).startswith('top.') and '_graphrename_' in str(n)}
  output=roots.get('top.out_y',roots.get('top.y'));assert output,roots
  reach=nx.descendants(g,output);missing=[x for x in dependencies if roots.get(x) not in reach]+[x for x in inputs if x not in reach]
  if name=='feedback':
   root=roots.get('top.state_q');cycle=bool(root and any(root in nx.descendants(g,n) or n==root for n in g.successors(root)))
   if not cycle:missing.append('state_feedback_cycle')
  if name=='shared_fanin':
   if roots['top.mid_word'] not in nx.descendants(g,roots['top.out_z']):missing.append('shared_out_z_dependency')
  result.update(status='graph_returned',nodes=len(g),edges=g.number_of_edges(),missing=missing,pass_check=not missing and name not in ['ambiguous_names','malformed'])
  (case/'graph.json').write_text(json.dumps({'nodes':[{'id':str(n),**d} for n,d in g.nodes(data=True)],'edges':list(g.edges())},indent=2)+'\n')
  if hasattr(gen,'last_report'):(case/'coverage.json').write_text(json.dumps(gen.last_report,indent=2)+'\n')
 except Exception as exc:
  (case/'error.txt').write_text(traceback.format_exc());result.update(status='error',error_type=type(exc).__name__,error=str(exc),pass_check=name=='malformed' or (name=='ambiguous_names' and 'ambiguous' in str(exc).lower()))
 results.append(result)
(run/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
if args.expect_repaired:assert all(x['pass_check'] for x in results),'fixture failure'
else:assert not next(x for x in results if x['fixture']=='underscores')['pass_check'],'original bug not reproduced'
