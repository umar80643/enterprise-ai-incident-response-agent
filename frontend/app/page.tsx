const steps=["Request","Planning","Retrieval","Analysis","Root Cause","Solution","Tests","Review","Approval"];
export default function Home(){
 const metrics=[["Investigations","—"],["Success rate","—"],["Open approvals","—"],["Estimated cost","—"]];
 return <main className="shell"><div className="nav"><div className="brand">AI Incident Resolution</div><span className="pill">Development-safe</span></div>
 <p className="muted">Enterprise software engineering agent platform</p><h1>Investigate incidents with evidence, not guesses.</h1>
 <p className="muted">LangGraph orchestration · Hybrid RAG · MCP tools · Human approval · GitHub PR control</p>
 <div className="section grid">{metrics.map(([a,b])=><div className="card" key={a}><div className="muted">{a}</div><div className="metric">{b}</div><small className="muted">Populated from persisted API data</small></div>)}</div>
 <div className="section card"><b>Investigation workflow</b><div className="flow">{steps.map((s,i)=><div className={"step "+(i<7?"accent":"")} key={s}>{s}</div>)}</div></div>
 <div className="section grid"><div className="card"><h3>Evidence Viewer</h3><p className="muted">Citations include repository, branch, file, symbol and line range. Retrieved text remains untrusted.</p></div>
 <div className="card"><h3>Patch Review</h3><div className="code">--- a/checkout/service.py{"\n"}+++ b/checkout/service.py{"\n"}+ if timeout_seconds is None:{"\n"}+     timeout_seconds = 5</div></div>
 <div className="card"><h3>Approval Center</h3><p className="muted">Repository writes and PR creation remain blocked until explicit approval.</p><button className="btn">Approve</button></div></div>
 </main>}
