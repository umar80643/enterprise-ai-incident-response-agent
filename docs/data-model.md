# Data model
Core durable entities: users, repositories, repository_indexes, investigations, agent_runs, workflow_events, evidence, hypotheses, patch_proposals, test_runs, approvals, pull_requests, llm_usage, audit_logs. Foreign keys center on repository/investigation IDs; event and usage tables are indexed by investigation and time.
