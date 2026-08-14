from datetime import datetime, timezone
from enum import StrEnum
from pydantic import BaseModel, Field

def now():
    return datetime.now(timezone.utc)

class Status(StrEnum):
    PENDING="PENDING"; RUNNING="RUNNING"; SUCCESS="SUCCESS"; FAILED="FAILED"; WAITING_APPROVAL="WAITING_APPROVAL"; REJECTED="REJECTED"

class ApprovalDecision(StrEnum):
    APPROVE="APPROVE"; REJECT="REJECT"; REQUEST_CHANGES="REQUEST_CHANGES"

class Permission(StrEnum):
    READ_ONLY="READ_ONLY"; SAFE_EXECUTION="SAFE_EXECUTION"; WRITE_REPOSITORY="WRITE_REPOSITORY"; CREATE_PR="CREATE_PR"

class InvestigationPlan(BaseModel):
    objective: str
    subtasks: list[str]
    required_tools: list[str]
    dependencies: list[str] = []
    expected_evidence: list[str]

class Evidence(BaseModel):
    id: str
    repository: str
    branch: str
    file_path: str
    line_start: int
    line_end: int
    symbol: str | None = None
    chunk_type: str = "code"
    excerpt: str
    score: float = 0
    source: str = "retrieved"

class Hypothesis(BaseModel):
    hypothesis: str
    evidence_ids: list[str]
    confidence: float = Field(ge=0, le=1)
    relevant_files: list[str]
    relevant_symbols: list[str] = []
    counter_evidence: list[str] = []
    assumptions: list[str] = []

class RootCauseAnalysis(BaseModel):
    status: str = "SUPPORTED"
    root_cause: str
    confidence: float = Field(ge=0, le=1)
    evidence_ids: list[str]
    inference: str
    assumptions: list[str] = []

class PatchProposal(BaseModel):
    summary: str
    changed_files: list[str]
    unified_diff: str
    expected_behavior: str
    side_effects: list[str] = []

class TestPlan(BaseModel):
    unit_tests: list[str] = []
    integration_tests: list[str] = []
    regression_tests: list[str] = []

class TestResult(BaseModel):
    passed: bool
    command: list[str]
    output: str
    duration_ms: int = 0

class ReviewResult(BaseModel):
    approved: bool
    findings: list[str]
    risk_level: str
    missing_tests: list[str] = []
    unsupported_assumptions: list[str] = []

class UsageRecord(BaseModel):
    agent: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0

class RepositoryIndexRequest(BaseModel):
    name: str
    path: str
    branch: str = "main"

class InvestigationCreate(BaseModel):
    repository_id: str
    title: str
    description: str
    branch: str = "main"

class ApprovalInput(BaseModel):
    comment: str | None = None

class RequestChangesInput(BaseModel):
    comment: str
