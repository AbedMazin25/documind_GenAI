# Changelog

## [2.0.0] - 2026-06-16

### Added
- GraphRAG multi-hop entity-relationship augmentation
- ColBERT cross-encoder reranker
- RAFT synthetic fine-tuning dataset generator
- SharePoint Online connector with OAuth2
- WebSocket streaming chat endpoint
- Prometheus / Grafana observability stack
- Terraform AKS infrastructure
- SAML 2.0 SSO support

### Changed
- Retriever upgraded to hybrid BM25 + dense + RRF
- LangGraph agent with conditional routing (rag / analytical / direct)
- Frontend rebuilt with streaming WebSocket chat

### Fixed
- CORS missing OPTIONS method for preflight requests
- Logout not invalidating refresh token in database
- GraphRAG JSON parse crash on LLM refusal
- Celery task retries not backing off correctly

## [1.0.0] - 2025-06-11

### Added
- Multi-tenant FastAPI backend with JWT + refresh token auth
- Alembic migrations with audit log table
- Async document ingestion pipeline (Celery + S3)
- ChromaDB vector store with dense retrieval
- LangGraph ReAct agent with router / retriever / analyzer / responder nodes
- React 18 frontend with Tailwind CSS
- Docker Compose and GitHub Actions CI

### Fixed
- Document list endpoint leaking cross-org data
- Paragraph chunker splitting on single newline instead of blank line
- Agent graph missing conditional edges — router decision was ignored
- Retriever node ignoring document_ids filter
