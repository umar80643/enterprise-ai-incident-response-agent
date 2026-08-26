"use client";

import { useMemo, useState } from "react";

const API_BASE = "http://localhost:8000";
const API_KEY = "dev-key";

const steps = [
  "Request",
  "Planning",
  "Retrieval",
  "Analysis",
  "Root Cause",
  "Solution",
  "Tests",
  "Review",
  "Approval",
];

type Evidence = {
  id: string;
  repository: string;
  branch: string;
  file_path: string;
  line_start: number;
  line_end: number;
  symbol?: string | null;
  chunk_type: string;
  excerpt: string;
  score: number;
};

type PatchProposal = {
  summary: string;
  changed_files: string[];
  unified_diff: string;
  expected_behavior: string;
  side_effects: string[];
};

type RootCause = {
  status: string;
  root_cause: string;
  confidence: number;
  evidence_ids: string[];
  inference?: string;
};

type Review = {
  approved: boolean;
  findings: string[];
  risk_level: string;
};

type PullRequest = {
  mode: string;
  branch: string;
  status: string;
  message: string;
};

type TestResult = {
  passed: boolean;
  command: string[];
  output: string;
  duration_ms: number;
};

type Investigation = {
  id: string;
  repository_id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
  result?: {
    retrieved_context?: Evidence[];
    proposed_solution?: PatchProposal;
    root_cause?: RootCause;
    review_findings?: Review;
    approval_status?: string;
    test_results?: TestResult[];
  };
  pull_request?: PullRequest;
};

async function api<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...(options.headers || {}),
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.error?.message || `Request failed (${response.status})`
    );
  }

  return data;
}

function statusLabel(status?: string) {
  if (!status) return "UNKNOWN";

  switch (status) {
    case "WAITING_APPROVAL":
      return "Awaiting approval";
    case "SUCCESS":
      return "Resolved";
    case "RUNNING":
      return "Investigating";
    case "REJECTED":
      return "Rejected";
    default:
      return status.replaceAll("_", " ");
  }
}

function statusClass(status?: string) {
  switch (status) {
    case "SUCCESS":
      return "status-success";
    case "WAITING_APPROVAL":
      return "status-warning";
    case "RUNNING":
      return "status-info";
    case "REJECTED":
      return "status-danger";
    default:
      return "status-neutral";
  }
}

export default function Home() {
  const repositoryId = "checkout-demo";

  const [title, setTitle] = useState("Checkout 500");

  const [description, setDescription] = useState(
    "Checkout requests started returning HTTP 500 after the latest deployment."
  );

  const [investigation, setInvestigation] =
    useState<Investigation | null>(null);

  const [loading, setLoading] = useState(false);
  const [approving, setApproving] = useState(false);

  const [error, setError] = useState("");

  const [showChangeForm, setShowChangeForm] = useState(false);
  const [changeComment, setChangeComment] = useState("");
  const [actionMessage, setActionMessage] = useState("");

  const evidence =
    investigation?.result?.retrieved_context ?? [];

  const patch =
    investigation?.result?.proposed_solution;

  const rootCause =
    investigation?.result?.root_cause;

  const review =
    investigation?.result?.review_findings;

  const testResults =
    investigation?.result?.test_results ?? [];

  const completedSteps = useMemo(() => {
    if (!investigation) {
      return 0;
    }

    switch (investigation.status) {
      case "SUCCESS":
        return steps.length;

      case "WAITING_APPROVAL":
        return 8;

      case "RUNNING":
        return 7;

      case "REJECTED":
        return 8;

      default:
        return 0;
    }
  }, [investigation]);

  async function runInvestigation() {
    try {
      setLoading(true);
      setError("");
      setActionMessage("");
      setShowChangeForm(false);

      const result = await api<Investigation>(
        "/api/v1/investigations",
        {
          method: "POST",
          body: JSON.stringify({
            repository_id: repositoryId,
            title,
            description,
          }),
        }
      );

      setInvestigation(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Investigation failed"
      );
    } finally {
      setLoading(false);
    }
  }

  async function approveInvestigation() {
    if (!investigation) {
      return;
    }

    try {
      setApproving(true);
      setError("");
      setActionMessage("");
      setShowChangeForm(false);

      const result = await api<Investigation>(
        `/api/v1/investigations/${investigation.id}/approve`,
        {
          method: "POST",
          body: JSON.stringify({
            comment: "Approved from frontend",
          }),
        }
      );

      setInvestigation(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Approval failed"
      );
    } finally {
      setApproving(false);
    }
  }

  async function rejectInvestigation() {
    if (!investigation) {
      return;
    }

    try {
      setApproving(true);
      setError("");
      setActionMessage("");
      setShowChangeForm(false);

      const result = await api<Investigation>(
        `/api/v1/investigations/${investigation.id}/reject`,
        {
          method: "POST",
          body: JSON.stringify({
            comment: "Rejected from frontend",
          }),
        }
      );

      setInvestigation(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Rejection failed"
      );
    } finally {
      setApproving(false);
    }
  }

  async function requestChanges() {
    if (!investigation) {
      return;
    }

    if (!showChangeForm) {
      setError("");
      setActionMessage("");
      setShowChangeForm(true);
      return;
    }

    if (!changeComment.trim()) {
      setError(
        "Please describe the changes you want."
      );
      return;
    }

    try {
      setApproving(true);
      setError("");
      setActionMessage("");

      const result = await api<Investigation>(
        `/api/v1/investigations/${investigation.id}/request-changes`,
        {
          method: "POST",
          body: JSON.stringify({
            comment: changeComment.trim(),
          }),
        }
      );

      setInvestigation(result);
      setShowChangeForm(false);
      setChangeComment("");

      setActionMessage(
        "Changes requested successfully. The investigation remains open for review."
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Request changes failed"
      );
    } finally {
      setApproving(false);
    }
  }

  return (
    <main className="app-shell">
      <div className="background-glow glow-one" />
      <div className="background-glow glow-two" />

      {/* HEADER */}
      <header className="topbar">
        <div className="brand-wrap">
          <div className="brand-mark">AI</div>

          <div>
            <div className="brand-title">
              Incident Resolution
            </div>

            <div className="brand-subtitle">
              Enterprise Engineering Agent
            </div>
          </div>
        </div>

        <div className="topbar-right">
          <div className="environment-pill">
            <span className="pulse-dot" />
            Development-safe
          </div>

          <div className="api-pill">
            <span className="api-dot" />
            API Online
          </div>
        </div>
      </header>

      {/* HERO */}
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">
            AI-POWERED INCIDENT RESPONSE
          </div>

          <h1>
            Investigate incidents with
            <span> evidence, not guesses.</span>
          </h1>

          <p>
            Trace production failures, retrieve repository evidence,
            identify root causes, generate minimal fixes, and keep
            every code change behind human approval.
          </p>

          <div className="hero-tags">
            <span>LangGraph</span>
            <span>Hybrid RAG</span>
            <span>MCP Tools</span>
            <span>Human Approval</span>
            <span>GitHub Control</span>
          </div>
        </div>

        <div className="hero-status-card">
          <div className="mini-label">
            SYSTEM STATUS
          </div>

          <div className="system-status">
            <span className="large-pulse" />

            <div>
              <strong>
                All systems operational
              </strong>

              <span>
                Backend · RAG · Agent workflow
              </span>
            </div>
          </div>

          <div className="system-divider" />

          <div className="system-row">
            <span>Repository</span>
            <strong>{repositoryId}</strong>
          </div>

          <div className="system-row">
            <span>LLM mode</span>
            <strong>Deterministic</strong>
          </div>

          <div className="system-row">
            <span>Write access</span>
            <strong className="safe-text">
              Blocked
            </strong>
          </div>
        </div>
      </section>

      {/* METRICS */}
      <section className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">◉</div>

          <div>
            <div className="metric-label">
              Investigation
            </div>

            <div className="metric-value">
              {investigation ? "Active" : "Ready"}
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⌁</div>

          <div>
            <div className="metric-label">
              Status
            </div>

            <div className="metric-value">
              {investigation
                ? statusLabel(investigation.status)
                : "Idle"}
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">◇</div>

          <div>
            <div className="metric-label">
              Evidence
            </div>

            <div className="metric-value">
              {evidence.length}
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">✓</div>

          <div>
            <div className="metric-label">
              Risk level
            </div>

            <div className="metric-value">
              {review?.risk_level ?? "—"}
            </div>
          </div>
        </div>
      </section>

      {/* INCIDENT + WORKFLOW */}
      <section className="workspace-grid">
        <div className="panel incident-panel">
          <div className="panel-header">
            <div>
              <div className="section-kicker">
                01 · INCIDENT
              </div>

              <h2>
                Start an investigation
              </h2>
            </div>

            <span className="repo-badge">
              {repositoryId}
            </span>
          </div>

          <div className="form-group">
            <label>Incident title</label>

            <input
              value={title}
              onChange={(event) =>
                setTitle(event.target.value)
              }
              placeholder="Example: Checkout 500"
            />
          </div>

          <div className="form-group">
            <label>
              Incident description
            </label>

            <textarea
              value={description}
              onChange={(event) =>
                setDescription(event.target.value)
              }
              rows={5}
              placeholder="Describe the production issue..."
            />
          </div>

          <button
            className="primary-button"
            onClick={runInvestigation}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="button-spinner" />
                Investigating...
              </>
            ) : (
              <>
                Run investigation
                <span>→</span>
              </>
            )}
          </button>

          {error && (
            <div className="error-box">
              {error}
            </div>
          )}
        </div>

        <div className="panel workflow-panel">
          <div className="panel-header">
            <div>
              <div className="section-kicker">
                02 · WORKFLOW
              </div>

              <h2>Agent execution</h2>
            </div>

            {investigation && (
              <span
                className={`status-badge ${statusClass(
                  investigation.status
                )}`}
              >
                <span className="status-dot" />

                {statusLabel(
                  investigation.status
                )}
              </span>
            )}
          </div>

          <div className="workflow-progress">
            <div
              className="workflow-progress-bar"
              style={{
                width: `${
                  (completedSteps / steps.length) * 100
                }%`,
              }}
            />
          </div>

          <div className="workflow-list">
            {steps.map((step, index) => {
              const complete =
                index < completedSteps;

              const active =
                !complete &&
                index === completedSteps;

              return (
                <div
                  key={step}
                  className={`workflow-step ${
                    complete ? "complete" : ""
                  } ${
                    active ? "active" : ""
                  }`}
                >
                  <div className="workflow-number">
                    {complete
                      ? "✓"
                      : String(index + 1).padStart(
                          2,
                          "0"
                        )}
                  </div>

                  <div>
                    <strong>{step}</strong>

                    <span>
                      {complete
                        ? "Completed"
                        : active
                          ? "In progress"
                          : "Waiting"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ROOT CAUSE */}
      <section className="full-panel">
        <div className="panel-header">
          <div>
            <div className="section-kicker">
              03 · ROOT CAUSE
            </div>

            <h2>
              What the agent discovered
            </h2>
          </div>

          {rootCause && (
            <div className="confidence-chip">
              Confidence{" "}
              {(rootCause.confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>

        {rootCause ? (
          <div className="root-cause-content">
            <div className="root-cause-icon">
              !
            </div>

            <div>
              <div className="root-cause-title">
                {rootCause.root_cause}
              </div>

              <p>
                {rootCause.inference}
              </p>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            Run an investigation to generate the
            root-cause analysis.
          </div>
        )}
      </section>

      {/* EVIDENCE + PATCH */}
      <section className="content-grid">
        <div className="panel evidence-panel">
          <div className="panel-header">
            <div>
              <div className="section-kicker">
                04 · EVIDENCE
              </div>

              <h2>
                Retrieved evidence
              </h2>
            </div>

            <span className="count-badge">
              {evidence.length}
            </span>
          </div>

          {evidence.length === 0 ? (
            <div className="empty-state">
              No evidence retrieved yet.
            </div>
          ) : (
            <div className="evidence-list">
              {evidence.map((item) => (
                <div
                  className="evidence-item"
                  key={item.id}
                >
                  <div className="evidence-top">
                    <span className="file-type">
                      {item.file_path
                        .split(".")
                        .pop()
                        ?.toUpperCase()}
                    </span>

                    <div className="evidence-file">
                      <strong>
                        {item.file_path}
                      </strong>

                      <span>
                        Lines {item.line_start}–
                        {item.line_end}
                      </span>
                    </div>

                    <span className="evidence-score">
                      {(item.score * 100).toFixed(1)}
                    </span>
                  </div>

                  <div className="evidence-code">
                    {item.excerpt}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="panel patch-panel">
          <div className="panel-header">
            <div>
              <div className="section-kicker">
                05 · SOLUTION
              </div>

              <h2>
                Proposed patch
              </h2>
            </div>

            {patch && (
              <span className="review-approved">
                Evidence grounded
              </span>
            )}
          </div>

          {patch ? (
            <>
              <div className="patch-summary">
                <strong>
                  {patch.summary}
                </strong>

                <span>
                  {patch.expected_behavior}
                </span>
              </div>

              <div className="diff-header">
                <span>
                  {patch.changed_files[0] ??
                    "checkout/service.py"}
                </span>

                <span>
                  Unified diff
                </span>
              </div>

              <pre className="diff-view">
                {patch.unified_diff}
              </pre>

              <div className="side-effects">
                <div className="mini-label">
                  SIDE EFFECTS
                </div>

                {patch.side_effects.map(
                  (effect) => (
                    <div
                      key={effect}
                      className="side-effect"
                    >
                      <span>•</span>
                      {effect}
                    </div>
                  )
                )}
              </div>
            </>
          ) : (
            <div className="empty-state">
              No proposed patch yet.
            </div>
          )}
        </div>
      </section>

      {/* TESTS + APPROVAL */}
      <section className="content-grid bottom-grid">
        <div className="panel tests-panel">
          <div className="panel-header">
            <div>
              <div className="section-kicker">
                06 · VALIDATION
              </div>

              <h2>
                Test validation
              </h2>
            </div>

            <span className="count-badge">
              {testResults.length}
            </span>
          </div>

          {testResults.length === 0 ? (
            <div className="empty-state">
              Validation results will appear here.
            </div>
          ) : (
            <div className="test-list">
              {testResults.map(
                (test, index) => (
                  <div
                    className="test-item"
                    key={`${test.command.join(
                      " "
                    )}-${index}`}
                  >
                    <div
                      className={`test-icon ${
                        test.passed
                          ? "passed"
                          : "failed"
                      }`}
                    >
                      {test.passed
                        ? "✓"
                        : "×"}
                    </div>

                    <div className="test-main">
                      <strong>
                        {test.command.join(" ")}
                      </strong>

                      <span>
                        {test.output}
                      </span>
                    </div>

                    <div className="test-time">
                      {test.duration_ms}ms
                    </div>
                  </div>
                )
              )}
            </div>
          )}
        </div>

        <div className="panel approval-panel">
          <div className="panel-header">
            <div>
              <div className="section-kicker">
                07 · GOVERNANCE
              </div>

              <h2>
                Approval center
              </h2>
            </div>

            <span className="security-badge">
              Human gate
            </span>
          </div>

          {!investigation && (
            <div className="empty-state">
              Start an investigation to unlock
              approval controls.
            </div>
          )}

          {investigation?.status ===
            "WAITING_APPROVAL" && (
            <>
              <div className="approval-alert">
                <div className="approval-alert-icon">
                  !
                </div>

                <div>
                  <strong>
                    Review required
                  </strong>

                  <span>
                    Repository writes and PR
                    creation are blocked until
                    explicit approval.
                  </span>
                </div>
              </div>

              <div className="approval-actions">
                <button
                  className="secondary-button"
                  onClick={rejectInvestigation}
                  disabled={approving}
                >
                  Reject
                </button>

                <button
                  className="ghost-button"
                  onClick={requestChanges}
                  disabled={approving}
                >
                  {showChangeForm
                    ? "Submit changes"
                    : "Request changes"}
                </button>

                <button
                  className="approve-button"
                  onClick={approveInvestigation}
                  disabled={approving}
                >
                  {approving
                    ? "Processing..."
                    : "Approve patch"}
                </button>
              </div>

              {showChangeForm && (
                <div className="change-request-box">
                  <label>
                    What should be changed?
                  </label>

                  <textarea
                    value={changeComment}
                    onChange={(event) =>
                      setChangeComment(
                        event.target.value
                      )
                    }
                    rows={3}
                    placeholder="Example: Use a configurable fallback instead of hard-coding 5 seconds."
                    autoFocus
                  />

                  <div className="change-request-hint">
                    Your comment will be recorded
                    with this investigation.
                  </div>
                </div>
              )}

              {actionMessage && (
                <div className="action-success">
                  <span>✓</span>

                  <div>
                    <strong>
                      Changes requested
                    </strong>

                    <p>
                      {actionMessage}
                    </p>
                  </div>
                </div>
              )}
            </>
          )}

          {investigation?.status ===
            "SUCCESS" && (
            <>
              <div className="success-card">
                <div className="success-icon">
                  ✓
                </div>

                <div>
                  <strong>
                    Investigation approved
                  </strong>

                  <span>
                    The change was accepted and
                    the GitHub action completed.
                  </span>
                </div>
              </div>

              {investigation.pull_request && (
                <div className="pr-card">
                  <div className="pr-row">
                    <span>Mode</span>

                    <strong>
                      {
                        investigation
                          .pull_request.mode
                      }
                    </strong>
                  </div>

                  <div className="pr-row">
                    <span>Branch</span>

                    <strong>
                      {
                        investigation
                          .pull_request.branch
                      }
                    </strong>
                  </div>

                  <div className="pr-row">
                    <span>Status</span>

                    <strong className="safe-text">
                      {
                        investigation
                          .pull_request.status
                      }
                    </strong>
                  </div>

                  <p>
                    {
                      investigation
                        .pull_request.message
                    }
                  </p>
                </div>
              )}
            </>
          )}

          {investigation?.status ===
            "REJECTED" && (
            <div className="rejected-card">
              <strong>
                Investigation rejected
              </strong>

              <span>
                No repository mutation was
                performed.
              </span>
            </div>
          )}
        </div>
      </section>

      <footer className="footer">
        <span>
          Enterprise AI Incident Resolution Agent
        </span>

        <span>
          Development environment · GitHub
          writes disabled
        </span>
      </footer>
    </main>
  );
}