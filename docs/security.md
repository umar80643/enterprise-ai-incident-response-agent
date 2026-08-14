# Security
- API key foundation; JWT can be layered for users/organizations.
- HMAC GitHub webhook verification.
- Path traversal prevention via resolved-root containment.
- Tool permission guard.
- Fixed subprocess allowlist; no shell.
- Retrieved repository content is wrapped/treated as untrusted evidence.
- Secrets are redacted from structured logs.
- GitHub writes disabled by default and require approval plus CREATE_PR.
- Default branch is never directly mutated.
