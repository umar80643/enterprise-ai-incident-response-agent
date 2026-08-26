from typing import TypedDict

from app.schemas.domain import *


class WorkflowState(TypedDict, total=False):
    request_id: str
    session_id: str
    investigation_id: str
    repository: str
    repository_path: str
    branch: str
    issue: str
    incident_description: str
    execution_plan: InvestigationPlan
    _chunks: list
    retrieved_context: list[Evidence]
    relevant_files: list[str]
    suspected_components: list[str]
    hypotheses: list[Hypothesis]
    root_cause: RootCauseAnalysis
    proposed_solution: PatchProposal
    tests: TestPlan
    test_results: list[TestResult]
    review_findings: ReviewResult
    risk_level: str
    approval_status: str
    execution_errors: list[str]
    usage: list[UsageRecord]
    timestamps: dict[str, str]
    step_count: int
    solution_retries: int
