# Architecture
LangGraph owns deterministic state transitions and approval boundaries. FastAPI only validates/transports requests. Services coordinate workflows. Agents produce typed domain objects. Retrieval and tools are separate adapters. PostgreSQL is the intended durable store; the development store preserves the same service boundary for zero-setup local execution.

## Scaling
Move workflow execution to Redis-backed workers, use Postgres/LangGraph checkpoint persistence, shard Qdrant collections by organization/repository, and enforce tenant IDs in every query/filter. Stateless API replicas can scale independently.
