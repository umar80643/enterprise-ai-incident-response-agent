-- Reference PostgreSQL migration (Alembic-ready schema)
CREATE TABLE IF NOT EXISTS users (id UUID PRIMARY KEY, email TEXT UNIQUE NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS repositories (id TEXT PRIMARY KEY, name TEXT NOT NULL, path TEXT NOT NULL, branch TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS repository_indexes (id UUID PRIMARY KEY, repository_id TEXT REFERENCES repositories(id), commit_sha TEXT, status TEXT, chunk_count INT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS investigations (id UUID PRIMARY KEY, repository_id TEXT REFERENCES repositories(id), title TEXT, description TEXT, status TEXT, created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS agent_runs (id UUID PRIMARY KEY, investigation_id UUID REFERENCES investigations(id), agent TEXT, model TEXT, latency_ms INT, status TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS workflow_events (id BIGSERIAL PRIMARY KEY, investigation_id UUID REFERENCES investigations(id), event_type TEXT, payload JSONB, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS evidence (id UUID PRIMARY KEY, investigation_id UUID REFERENCES investigations(id), file_path TEXT, line_start INT, line_end INT, score DOUBLE PRECISION, metadata JSONB);
CREATE TABLE IF NOT EXISTS hypotheses (id UUID PRIMARY KEY, investigation_id UUID REFERENCES investigations(id), hypothesis TEXT, confidence DOUBLE PRECISION, payload JSONB);
CREATE TABLE IF NOT EXISTS patch_proposals (id UUID PRIMARY KEY, investigation_id UUID REFERENCES investigations(id), diff TEXT, risk TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS test_runs (id UUID PRIMARY KEY, investigation_id UUID REFERENCES investigations(id), passed BOOLEAN, output TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS approvals (id UUID PRIMARY KEY, investigation_id UUID REFERENCES investigations(id), decision TEXT, comment TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS pull_requests (id UUID PRIMARY KEY, investigation_id UUID REFERENCES investigations(id), url TEXT, status TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS llm_usage (id BIGSERIAL PRIMARY KEY, investigation_id UUID REFERENCES investigations(id), agent TEXT, model TEXT, input_tokens INT, output_tokens INT, estimated_cost DOUBLE PRECISION);
CREATE TABLE IF NOT EXISTS audit_logs (id BIGSERIAL PRIMARY KEY, investigation_id UUID, actor TEXT, action TEXT, payload JSONB, created_at TIMESTAMPTZ DEFAULT now());
CREATE INDEX IF NOT EXISTS ix_events_investigation ON workflow_events(investigation_id, created_at);
CREATE INDEX IF NOT EXISTS ix_usage_investigation ON llm_usage(investigation_id);
