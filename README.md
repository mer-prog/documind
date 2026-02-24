<div align="center">

# DocuMind

**AI-Powered Document Intelligence Platform**

Upload documents. Ask questions. Get cited answers instantly.

[![Live Demo](https://img.shields.io/badge/Live_Demo-documind--pi.vercel.app-000?style=for-the-badge&logo=vercel)](https://documind-pi.vercel.app)

[![Next.js](https://img.shields.io/badge/Next.js-15-000?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=000)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=fff)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL_17-pgvector-4169E1?logo=postgresql&logoColor=fff)](https://www.postgresql.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=fff)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=fff)](https://www.python.org/)

</div>

---

DocuMind is a full-stack AI document intelligence platform that transforms organizational knowledge bases into a conversational interface. Upload Markdown, PDF, or DOCX files — the system automatically performs semantic chunking, vector embedding, and indexing, enabling instant natural-language search with source-cited answers.

> **Demo credentials:** `admin@documind.dev` / `demo1234`

---

## Why This Project Stands Out

Most portfolio RAG apps rely on a single retrieval method and wrap an OpenAI call. DocuMind goes further:

| | What DocuMind Does | Why It Matters |
|---|---|---|
| **Hybrid Search** | Combines pgvector cosine similarity + pg_trgm trigram matching via Reciprocal Rank Fusion (k=60) | Handles both semantic queries *and* exact keyword matches — the way production RAG systems actually work |
| **Dual-Mode Architecture** | Runs a real search engine with hash-based deterministic embeddings at $0 cost; swap in OpenAI with one env var | Proves production-grade code without burning API credits for portfolio demos |
| **Async Concurrent Search** | Vector and keyword searches execute in parallel via `asyncio.gather()` | Demonstrates real performance engineering, not just "it works" |
| **Multi-Tenant Isolation** | Workspace-scoped data with RBAC (admin/member) across all tables | Shows enterprise architecture patterns, not toy single-user apps |
| **SSE Streaming** | Token-by-token Server-Sent Events for ChatGPT-like UX | Real-time streaming protocol, not polling or batch responses |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                     │
│           Next.js 15 · React 19 · TypeScript            │
│        NextAuth.js · TanStack Query · Tailwind CSS      │
└──────────────────────────┬──────────────────────────────┘
                           │ REST + SSE
┌──────────────────────────▼──────────────────────────────┐
│                   Backend (Render)                       │
│             Python · FastAPI · SQLAlchemy                │
│       Hybrid Search Engine · SSE Streaming · RAG        │
└──────────────────────────┬──────────────────────────────┘
                           │ asyncpg + SSL
┌──────────────────────────▼──────────────────────────────┐
│                   Database (Neon)                        │
│        PostgreSQL 17 · pgvector · pg_trgm               │
│      Vector Embeddings · Full-Text Search · HNSW        │
└─────────────────────────────────────────────────────────┘
```

---

## Features

### Hybrid Search Engine (pgvector + pg_trgm + RRF)

DocuMind doesn't rely on vector search alone. It fuses **semantic search** (pgvector cosine similarity) with **keyword search** (pg_trgm trigram matching) using **Reciprocal Rank Fusion (k=60)**.

```
User Query: "What is the remote work policy?"
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  Semantic Search          Keyword Search
  pgvector cosine          pg_trgm trigram
  similarity               similarity > 0.05
  (top 20)                 (top 20)
        │                       │
        └───────────┬───────────┘
                    ▼
         Reciprocal Rank Fusion
           score = Σ 1/(k + rank_i)
                  k = 60
                    │
                    ▼
            Top-N fused results
         with source metadata
```

This approach ensures:
- **Semantic queries** ("tell me about vacation philosophy") leverage embedding similarity
- **Exact-match queries** ("PTO policy section 4.2") leverage trigram keyword matching
- **Mixed queries** get the best of both via rank-based fusion

### Conversational RAG with Source Citations

Every response includes inline source citations pointing to the original document chunks. The system maintains conversation memory (last 5 messages + automatic summarization of older context) for coherent follow-up questions.

### Real-Time SSE Streaming

Chat responses stream token-by-token via Server-Sent Events, delivering a ChatGPT-like responsive experience. Both live mode (OpenAI GPT-4o-mini) and demo mode (template-based) use the identical SSE protocol.

### Analytics Dashboard

Built-in observability dashboard tracking token consumption, query latency, search quality metrics, and usage patterns — demonstrating production-level operational design.

### Multi-Tenant Workspace Architecture

Complete data isolation by workspace with role-based access control (admin/member), ensuring organizational data separation across all tables and queries.

### Dual-Mode Architecture

| | Demo Mode | Live Mode |
|---|---|---|
| **Embeddings** | SHA-256 hash-based deterministic vectors (free) | OpenAI `text-embedding-3-small` |
| **Chat** | Template responses from search results + 35ms pseudo-SSE | GPT-4o-mini streaming |
| **Search** | Real hybrid search (pgvector + pg_trgm) | Identical |
| **Cost** | $0 | Pay-per-token (OpenAI API) |
| **Activate** | Default (no API key required) | Set `OPENAI_API_KEY` env var |

> Demo mode is not a mock — the hybrid search engine performs real cosine similarity and trigram matching against pre-computed embeddings.

---

## Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| **Python 3.12** | Core language |
| **FastAPI** | Async REST API framework |
| **SQLAlchemy 2.0** | Type-safe async ORM |
| **Alembic** | Database migration management |
| **pgvector** | Vector similarity search (cosine distance) |
| **pg_trgm** | Trigram-based keyword search |
| **asyncpg** | High-performance async PostgreSQL driver |
| **PyMuPDF** | PDF document parsing |
| **python-docx** | DOCX document parsing |
| **tiktoken** | OpenAI-compatible token counting |
| **bcrypt** | Password hashing |
| **python-jose** | JWT token management |

### Frontend

| Technology | Purpose |
|---|---|
| **Next.js 15** | React framework with App Router |
| **React 19** | UI library |
| **TypeScript 5.7** | Type-safe development |
| **NextAuth.js v5** | Authentication (Credentials Provider) |
| **TanStack Query 5** | Server state management & caching |
| **Tailwind CSS** | Utility-first styling |
| **shadcn/ui + Radix UI** | Accessible component library |
| **Recharts** | Analytics data visualization |
| **Zod** | Runtime schema validation |

### Infrastructure

| Service | Purpose |
|---|---|
| **Vercel** | Frontend hosting (Edge Network) |
| **Render** | Backend hosting (Python runtime) |
| **Neon** | Serverless PostgreSQL (pgvector-enabled) |

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL with `pgvector` and `pg_trgm` extensions

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
cp .env.example .env
# Set DATABASE_URL (required)
# Set OPENAI_API_KEY (optional — omit for demo mode)
```

```bash
# Seed demo workspace, users, and documents (no API key needed)
python -m seed.seed
```

```bash
uvicorn main:app --reload
# API available at http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
```

```bash
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
npm run dev
# App available at http://localhost:3000
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authenticate user |
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/verify` | Verify JWT token |
| `GET` | `/api/documents` | List workspace documents |
| `POST` | `/api/documents` | Upload document |
| `DELETE` | `/api/documents/:id` | Delete document |
| `POST` | `/api/documents/:id/ingest` | Process document (chunk + embed) |
| `POST` | `/api/chat` | Send chat message (SSE stream) |
| `GET` | `/api/conversations` | List conversations |
| `GET` | `/api/conversations/:id` | Get conversation with messages |
| `GET` | `/api/analytics/usage` | Usage statistics (configurable range) |
| `GET` | `/api/analytics/top-queries` | Top queries ranking |

---

## Database Schema

```
workspaces ──┬── users (role: admin | member)
             ├── documents ── chunks (embedding: vector(1536))
             ├── conversations ── messages (sources: jsonb)
             └── usage_logs (tokens, latency_ms)
                 daily_analytics (aggregated metrics)
```

Key design choices:

- **`vector(1536)`** — OpenAI-compatible embedding vectors stored directly in the chunks table
- **GIN index (pg_trgm)** — Enables fast trigram keyword search on chunk content
- **HNSW index (pgvector)** — Approximate nearest neighbor search for vector similarity
- **JSONB sources** — Flexible citation metadata in messages (chunk ID, document name, page number, relevance score)
- **SHA-256 content hash** — Deduplication at document level

---

## Design Decisions

| Decision | Rationale |
|---|---|
| **Monorepo** | Single repository simplifies deployment, versioning, and cross-stack refactoring |
| **FastAPI + Next.js separation** | Demonstrates polyglot architecture (Python ML/backend + TypeScript frontend) |
| **Hybrid search over vector-only** | Production RAG systems need keyword fallback for exact matches — this is table stakes |
| **RRF over linear combination** | Rank-based fusion is robust to score distribution differences between retrieval methods |
| **Dual-mode architecture** | Run a $0 portfolio demo while proving production-ready code paths |
| **SSE over WebSocket** | Sufficient for unidirectional streaming; simpler protocol, fewer failure modes |
| **Semantic chunking** | Heading-aware splitting preserves document structure better than fixed-size chunking |
| **500-token chunks with 50-token overlap** | Balanced granularity for retrieval precision without fragmenting context |
| **asyncio.gather for search** | Concurrent vector + keyword search eliminates sequential bottleneck |
| **Workspace-scoped queries** | Multi-tenant isolation at the query level, not just the application level |

---

## Project Structure

```
documind/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app + CORS + seed endpoint
│   │   ├── config.py                  # Pydantic settings (chunk size, RRF k, etc.)
│   │   ├── database.py                # Async SQLAlchemy engine + session factory
│   │   ├── dependencies.py            # Auth dependency injection
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── user.py                #   User with workspace FK + role
│   │   │   ├── workspace.py           #   Multi-tenant root entity
│   │   │   ├── document.py            #   Document metadata + content hash
│   │   │   ├── chunk.py               #   Text chunks + vector(1536) embedding
│   │   │   ├── conversation.py        #   Chat session with summary
│   │   │   ├── message.py             #   Messages with JSONB sources
│   │   │   ├── usage_log.py           #   Token count + latency tracking
│   │   │   └── analytics.py           #   Daily aggregated metrics
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── routers/                   # API endpoint handlers
│   │   │   ├── auth.py                #   Login / register / verify
│   │   │   ├── documents.py           #   Upload / list / delete / ingest
│   │   │   ├── chat.py                #   SSE streaming chat
│   │   │   ├── conversations.py       #   Conversation management
│   │   │   └── analytics.py           #   Usage stats + top queries
│   │   └── services/                  # Business logic layer
│   │       ├── auth_service.py        #   User authentication
│   │       ├── security_service.py    #   JWT + password hashing
│   │       ├── embedding_service.py   #   Dual-mode embeddings (OpenAI / hash)
│   │       ├── ingest_service.py      #   Document parsing + semantic chunking
│   │       ├── search_service.py      #   Hybrid search (vector + keyword + RRF)
│   │       └── chat_service.py        #   RAG pipeline + SSE streaming
│   ├── alembic/                       # Database migrations
│   ├── seed/                          # Demo data seeder
│   │   └── data/                      #   Sample documents (Markdown)
│   ├── requirements.txt
│   └── render.yaml                    # Render.com deployment config
│
├── frontend/
│   ├── src/
│   │   ├── app/                       # Next.js 15 App Router
│   │   │   ├── (auth)/                #   Auth pages (login, register)
│   │   │   ├── dashboard/             #   Protected routes
│   │   │   │   ├── chat/              #     Chat interface + conversation detail
│   │   │   │   ├── documents/         #     Document management
│   │   │   │   ├── analytics/         #     Usage dashboard
│   │   │   │   └── settings/          #     Workspace settings
│   │   │   └── api/auth/              #   NextAuth API route
│   │   ├── components/
│   │   │   ├── chat/                  #   Chat UI (message bubbles, citations, input)
│   │   │   ├── documents/             #   Document list + upload
│   │   │   ├── analytics/             #   Charts (tokens, latency, queries)
│   │   │   ├── dashboard/             #   Layout (sidebar, header, stat cards)
│   │   │   └── ui/                    #   shadcn/ui primitives
│   │   ├── lib/
│   │   │   ├── api-client.ts          #   Fetch wrapper with auth headers
│   │   │   └── auth.config.ts         #   NextAuth configuration
│   │   └── types/                     #   TypeScript type definitions
│   ├── middleware.ts                  # NextAuth route protection
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── README.md
└── .gitignore
```

---

## Language Breakdown

- **Python** — 51.1%
- **TypeScript** — 47.7%
- **Other** (CSS, SQL) — 1.2%

---

## License

MIT

## Author

**[@mer-prog](https://github.com/mer-prog)**
