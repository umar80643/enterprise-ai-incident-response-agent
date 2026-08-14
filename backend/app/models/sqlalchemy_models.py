from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Float, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass

class RepositoryModel(Base):
    __tablename__="repositories"
    id: Mapped[str]=mapped_column(String, primary_key=True)
    name: Mapped[str]=mapped_column(String, index=True)
    path: Mapped[str]=mapped_column(Text)
    branch: Mapped[str]=mapped_column(String)
    created_at: Mapped[datetime]=mapped_column(DateTime)

class InvestigationModel(Base):
    __tablename__="investigations"
    id: Mapped[str]=mapped_column(String, primary_key=True)
    repository_id: Mapped[str]=mapped_column(ForeignKey("repositories.id"), index=True)
    title: Mapped[str]=mapped_column(String)
    description: Mapped[str]=mapped_column(Text)
    status: Mapped[str]=mapped_column(String, index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime)

class AgentRunModel(Base):
    __tablename__="agent_runs"
    id: Mapped[str]=mapped_column(String, primary_key=True)
    investigation_id: Mapped[str]=mapped_column(String, index=True)
    agent: Mapped[str]=mapped_column(String)
    latency_ms: Mapped[int]=mapped_column(Integer, default=0)

class EvidenceModel(Base):
    __tablename__="evidence"
    id: Mapped[str]=mapped_column(String, primary_key=True)
    investigation_id: Mapped[str]=mapped_column(String, index=True)
    file_path: Mapped[str]=mapped_column(Text)
    line_start: Mapped[int]=mapped_column(Integer)
    line_end: Mapped[int]=mapped_column(Integer)
    score: Mapped[float]=mapped_column(Float)

# Production schema also includes workflow_events, hypotheses, patch_proposals, test_runs,
# approvals, pull_requests, llm_usage, audit_logs. Alembic migration documents all tables.
