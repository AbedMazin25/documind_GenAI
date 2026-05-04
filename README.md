# DocuMind

[![CI](https://github.com/abedmandour/documind/actions/workflows/ci.yml/badge.svg)](https://github.com/abedmandour/documind/actions)
[![Coverage](https://codecov.io/gh/abedmandour/documind/branch/main/graph/badge.svg)](https://codecov.io/gh/abedmandour/documind)

**Financial Document Intelligence Platform** — enterprise-grade RAG pipeline for SEC filings,
earnings transcripts, and balance sheets with multi-hop GraphRAG, hybrid retrieval (BM25 + dense
+ ColBERT reranking), and a LangGraph agent that routes queries to the right sub-system.

## Architecture

- **Backend**: FastAPI + PostgreSQL + ChromaDB + Celery
- **LLM**: OpenAI GPT-4o with structured output
- **Retrieval**: BM25 + dense embeddings + RRF fusion + ColBERT cross-encoder
- **Graph**: NetworkX entity graph with multi-hop augmentation
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Infra**: Kubernetes (AKS) + Helm + Terraform + Prometheus/Grafana

## Quick start

```bash
make dev       # start all services with docker-compose
make test      # run test suite with coverage
make migrate   # run alembic migrations
```

## Key features

- Multi-tenant with org isolation enforced at query layer
- Async document ingestion pipeline (Celery + S3)
- Streaming WebSocket responses
- RAFT synthetic fine-tuning data generator
- SharePoint Online connector
- Financial metric extractor (DCF, ratios, tables)
