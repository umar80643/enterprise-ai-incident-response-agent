# Agent responsibility matrix
| Agent | Responsibility | Inputs | Outputs | Permissions |
|---|---|---|---|---|
| Supervisor | routing/bounds | request/state | next node | none |
| Planner | investigation plan | incident | InvestigationPlan | read |
| Repository | structure | repo | files/components | read |
| Retrieval | evidence | query/index | Evidence[] | read |
| Debugger | competing explanations | evidence | Hypothesis[] | read |
| Root Cause | rank/ground | hypotheses | RootCauseAnalysis | read |
| Solution | minimal patch | root cause/evidence | PatchProposal | none |
| Testing | tests/validation | patch | TestPlan/TestResult | SAFE_EXECUTION |
| Reviewer | second pass | patch/tests | ReviewResult | read |
| GitHub | branch/PR | approved patch | PR proposal/result | CREATE_PR |
