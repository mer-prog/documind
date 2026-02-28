<div align="center">

# DocuMind — AI Document Search Platform

**Upload documents. Ask questions. Get cited answers instantly.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-documind--pi.vercel.app-000?style=for-the-badge&logo=vercel)](https://documind-pi.vercel.app)

</div>

---

## 1. Skills Demonstrated

| Category | Implementation |
|---|---|
| **Hybrid Search** | Combines pgvector cosine similarity + pg_trgm trigram matching via Reciprocal Rank Fusion (k=60). Vector and keyword searches run concurrently with `asyncio.gather()` |
| **Dual-Mode Architecture** | SHA-256 hash-based pseudo-embeddings for a $0 demo mode; swap to OpenAI `text-embedding-3-small` + `gpt-4o-mini` with a single environment variable |
| **SSE Streaming** | Token-by-token real-time streaming via Server-Sent Events. Backend uses `sse-starlette`, frontend uses `@microsoft/fetch-event-source` |
| **Multi-Tenant Isolation** | Workspace-scoped data separation. All tables and queries enforce `workspace_id` scope. RBAC with admin/member roles |
| **Internationalization (i18n)** | Japanese/English switching with `next-intl`. Cookie-based locale, `localStorage` persistence, locale-aware date/number/currency formatting |
| **Semantic Chunking** | Heading-aware document splitting for Markdown, PDF, and DOCX. 500-token chunks with 50-token overlap. Token counting via `tiktoken` (cl100k_base) |
| **Conversation Memory** | Retains last 5 messages plus automatic summarization of older context (GPT-powered in live mode) |
| **Security** | Prompt injection detection (14 regex patterns), input sanitization (4000-char limit, whitespace normalization, null byte removal), bcrypt password hashing |
| **Analytics Dashboard** | Daily aggregation of token usage, query count, and latency. Visualized with `Recharts` line, area, and bar charts |
| **Async Architecture** | Fully async backend with FastAPI + SQLAlchemy 2.0 async + asyncpg. Connection pooling (pool_size=20, max_overflow=10) |
| **CI/CD** | GitHub Actions running pytest (77 backend tests) + ESLint + Next.js build on push/PR |

---

## 2. Tech Stack (with Versions)

### Backend

| Technology | Purpose |
|---|---|
| Python 3.12 | Core language |
| FastAPI | Async REST API framework |
| SQLAlchemy 2.0 (asyncio) | Type-safe async ORM |
| asyncpg | High-performance async PostgreSQL driver |
| Alembic | Database migration management |
| pgvector | Vector similarity search (cosine distance) |
| pg_trgm | Trigram-based keyword search |
| Pydantic >= 2.0 | Request/response schema validation |
| pydantic-settings | Environment variable-based configuration |
| python-jose (cryptography) | JWT token generation and verification |
| bcrypt | Password hashing |
| openai | OpenAI API client (live mode) |
| tiktoken | OpenAI-compatible token counting (cl100k_base) |
| PyMuPDF (fitz) | PDF document parsing |
| python-docx | DOCX document parsing |
| sse-starlette | Server-Sent Events response |
| httpx | Async HTTP client |
| python-dotenv | .env file loading |
| python-multipart | Multipart form data parsing |

### Frontend

| Technology | Purpose |
|---|---|
| Next.js 15 (App Router) | React framework |
| React 19 | UI library |
| TypeScript 5.7 | Type-safe development |
| NextAuth.js v5 (beta.25) | Authentication (Credentials Provider) |
| TanStack Query 5 | Server state management and caching (staleTime: 60s) |
| Tailwind CSS 3.4 | Utility-first CSS framework |
| shadcn/ui + Radix UI | Accessible component library |
| Recharts 2.15 | Analytics data visualization (line, area, bar charts) |
| next-intl 4.8 | Internationalization (i18n) — Japanese/English |
| Zod 3.24 | Runtime schema validation |
| lucide-react | Icon library |
| @microsoft/fetch-event-source | SSE client for chat streaming |
| class-variance-authority | Component variant styling |
| tailwind-merge / clsx | CSS class merging utilities |
| tailwindcss-animate | Animation plugin |

### Infrastructure

| Service | Purpose |
|---|---|
| Vercel | Frontend hosting (Edge Network) |
| Render | Backend hosting (Python runtime, free plan) |
| Neon | Serverless PostgreSQL 17 (pgvector-enabled) |

---

## 3. Architecture Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vercel)                       │
│              Next.js 15 · React 19 · TypeScript 5.7         │
│     NextAuth.js v5 · TanStack Query 5 · Tailwind CSS 3.4   │
│                 next-intl (JP/EN i18n)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API + SSE (Server-Sent Events)
┌──────────────────────────▼──────────────────────────────────┐
│                     Backend (Render)                         │
│               Python 3.12 · FastAPI · SQLAlchemy 2.0        │
│      Hybrid Search Engine · SSE Streaming · RAG Pipeline    │
│            Security (Injection Detection + bcrypt)           │
└──────────────────────────┬──────────────────────────────────┘
                           │ asyncpg + SSL
┌──────────────────────────▼──────────────────────────────────┐
│                   Database (Neon)                            │
│          PostgreSQL 17 · pgvector · pg_trgm                 │
│    vector(1536) Embeddings · GIN Index · HNSW / IVFFlat     │
└─────────────────────────────────────────────────────────────┘
```

### Search Pipeline

```
User Query: "What is the remote work policy?"
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  Semantic Search          Keyword Search
  pgvector cosine          pg_trgm trigram
  1 - (embedding <=> q)    similarity() > 0.05
  top 20 results           top 20 results
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

### Chat Pipeline (RAG)

```
User Message
     │
     ▼
Security Check (14-pattern injection detection)
     │
     ▼
Input Sanitization (4000-char limit, whitespace normalization, null byte removal)
     │
     ▼
Hybrid Search (vector + keyword + RRF)
     │
     ▼
Context Assembly (search results + last 5 messages + summary)
     │
     ├─── Live Mode: OpenAI GPT-4o-mini streaming
     │
     └─── Demo Mode: Template-based pseudo-SSE (35ms/word)
     │
     ▼
SSE token-by-token delivery → Save assistant message → Update analytics
```

---

## 4. Key Features

### 4.1 Hybrid Search Engine

- **Vector Search**: pgvector `<=>` operator for cosine distance. Filters by `embedding IS NOT NULL` and `workspace_id`
- **Keyword Search**: pg_trgm `similarity()` function with a 0.05 threshold. Accelerated by a GIN index (`gin_trgm_ops`)
- **RRF Fusion**: `score = Σ 1/(rank + 1 + k)` (k=60). Rank-based fusion that is robust to score distribution differences between retrieval methods
- **Concurrent Execution**: `asyncio.gather()` runs vector and keyword searches in parallel

### 4.2 Dual-Mode Architecture

| | Demo Mode | Live Mode |
|---|---|---|
| **Embeddings** | SHA-256 hash-based pseudo-vectors (free) | OpenAI `text-embedding-3-small` |
| **Chat** | Template response + 35ms pseudo-SSE | GPT-4o-mini streaming |
| **Search** | Real hybrid search (pgvector + pg_trgm) | Identical |
| **Cost** | $0 | OpenAI API pay-per-token |
| **Activation** | Default (no API key required) | Set `OPENAI_API_KEY` environment variable |

Pseudo-embedding generation algorithm (`embedding_service.py`):
1. Lowercase text and split into words
2. For each dimension: compute `SHA-256("{first 10 words}_{dimension index}")`
3. Normalize to [-1.0, 1.0] range via `(hash % 10000) / 5000 - 1.0`
4. L2-normalize the vector (unit norm)

### 4.3 SSE Streaming

- Backend: `sse-starlette` `EventSourceResponse` generates events
- Frontend: `@microsoft/fetch-event-source` receives events
- Event types: `conversation_id` → `sources` → `token` (repeated) → `done` / `error`
- Disconnect detection: `request.is_disconnected()` halts the stream on client disconnect

### 4.4 Semantic Chunking

- **Markdown parsing**: Split by headings (`#{1,3}`) → further split by paragraphs (`\n\s*\n`)
- **PDF parsing**: PyMuPDF page-by-page text extraction → paragraph splitting (20+ characters only)
- **DOCX parsing**: python-docx Heading style detection → text accumulation and splitting
- **Chunk splitting**: Chunks under 500 tokens are kept as-is; larger chunks split at sentence boundaries (`[.!?]\s+`)
- **Overlap**: Last 50 tokens of each chunk are prepended to the next chunk

### 4.5 Internationalization (i18n)

- **Library**: `next-intl` 4.8 (App Router compatible)
- **Locale switching**: Cookie-based (no URL path changes). Server-side locale resolution via `getRequestConfig`
- **Persistence**: Saved to `localStorage` → restored on revisit → synced to cookie
- **Translation files**: `ja.json` (132 lines) / `en.json` (132 lines). Namespaces: common, nav, auth, dashboard, documents, chat, analytics, settings, language
- **Toggle UI**: LanguageToggle component. 44x44px button, flag emojis (JP/US), 150ms fade transition, `router.refresh()` for reload-free switching
- **Locale-aware formatting**: `Intl.DateTimeFormat` (dates), `Intl.NumberFormat` (numbers, currency). ja-JP / en-US

### 4.6 Authentication System

- **Frontend**: NextAuth.js v5 (Credentials Provider) → JWT session strategy
- **Token generation**: `jose` `SignJWT` with HS256 signing. Payload includes `sub`, `email`, `name`, `workspace_id`. 24-hour expiration
- **Backend verification**: `python-jose` JWT decode → user lookup → `get_current_user` dependency injection
- **Passwords**: bcrypt hashing and verification with random salt generation
- **Route protection**: NextAuth middleware protects `/dashboard/*`. Unauthenticated users redirect to `/login`
- **Token caching**: Frontend caches tokens for 50 minutes (against a 1-hour token lifetime)

### 4.7 Analytics Dashboard

- **Daily aggregation table** (`daily_analytics`): Unique constraint on `workspace_id` + `date`
- **Metrics**: Query count, prompt tokens, completion tokens, average latency (ms), query text history (JSONB)
- **Visualization**: Token usage (stacked area chart), daily queries (bar chart), average latency (line chart), top queries (progress bars)

---

## 5. API Endpoints

| Method | Endpoint | Description | Auth | Request | Response |
|---|---|---|---|---|---|
| `POST` | `/api/auth/login` | Authenticate user | None | `{ email, password }` | `UserResponse` |
| `POST` | `/api/auth/register` | Register user (auto-creates workspace) | None | `{ name, email, password }` | `UserResponse` |
| `POST` | `/api/auth/verify` | Verify JWT token | Bearer | — | `UserResponse` |
| `GET` | `/api/documents` | List workspace documents | Bearer | `?skip=0&limit=50` | `DocumentListResponse` |
| `POST` | `/api/documents` | Upload document (multipart) | Bearer | `FormData (file)` | `DocumentResponse` |
| `DELETE` | `/api/documents/:id` | Delete document (cascades to chunks) | Bearer | — | 204 No Content |
| `POST` | `/api/documents/:id/ingest` | Process document (parse → chunk → embed) | Bearer | — | `IngestResponse` |
| `POST` | `/api/chat` | Send chat message (SSE stream) | Bearer | `{ message, conversation_id? }` | SSE EventStream |
| `GET` | `/api/conversations` | List conversations | Bearer | — | `ConversationSummary[]` |
| `GET` | `/api/conversations/:id` | Get conversation with messages | Bearer | — | `ConversationDetail` |
| `GET` | `/api/analytics/usage` | Get usage statistics | Bearer | `?days=30` (1-365) | `UsageResponse` |
| `GET` | `/api/analytics/top-queries` | Get top queries ranking | Bearer | `?days=30&limit=10` | `TopQueriesResponse` |
| `GET` | `/health` | Health check | None | — | `{ status: "healthy" }` |
| `GET` | `/api/mode` | Get operating mode | None | — | `{ mode, model }` |
| `POST` | `/api/seed` | Seed demo data (admin only) | Bearer (admin) | — | `{ status }` |

**Supported file types**: Markdown (.md), PDF (.pdf), DOCX (.docx)
**Maximum upload size**: 20 MB

---

## 6. Database Design

### ER Diagram

```
workspaces ──┬── users (role: admin | member)
             │     └── conversations ── messages (sources: JSONB)
             ├── documents ── chunks (embedding: vector(1536))
             ├── usage_logs (prompt_tokens, completion_tokens)
             └── daily_analytics (aggregated metrics, query_texts: JSONB)
```

### Table Specifications

#### workspaces
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| api_key_hash | VARCHAR(255) | NULLABLE |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### users
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE, INDEX |
| hashed_password | VARCHAR(255) | NOT NULL |
| name | VARCHAR(255) | NOT NULL |
| role | VARCHAR(50) | DEFAULT 'member' |
| workspace_id | UUID | FK → workspaces.id |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### documents
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| workspace_id | UUID | FK → workspaces.id |
| uploaded_by | UUID | FK → users.id |
| filename | VARCHAR(512) | NOT NULL |
| file_type | VARCHAR(20) | NOT NULL |
| file_size | INTEGER | DEFAULT 0 |
| file_content | BYTEA | NULLABLE, DEFERRED |
| status | VARCHAR(20) | DEFAULT 'pending' |
| page_count | INTEGER | NULLABLE |
| chunk_count | INTEGER | DEFAULT 0 |
| content_hash | VARCHAR(64) | NULLABLE (SHA-256) |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### chunks
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| document_id | UUID | FK → documents.id (CASCADE), INDEX |
| workspace_id | UUID | FK → workspaces.id |
| content | TEXT | NOT NULL |
| token_count | INTEGER | DEFAULT 0 |
| page_number | INTEGER | NULLABLE |
| heading | VARCHAR(512) | NULLABLE |
| chunk_index | INTEGER | DEFAULT 0 |
| embedding | vector(1536) | NULLABLE |

**Indexes**:
- `idx_chunk_content_trgm`: GIN index (`gin_trgm_ops`) — trigram keyword search
- `idx_chunk_embedding_ivfflat`: IVFFlat index (`vector_cosine_ops`, lists=100) — approximate nearest neighbor

#### conversations
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users.id, INDEX |
| workspace_id | UUID | FK → workspaces.id |
| title | VARCHAR(512) | DEFAULT 'New Conversation' |
| summary | TEXT | NULLABLE (older message summary) |
| message_count | INTEGER | DEFAULT 0 |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### messages
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| conversation_id | UUID | FK → conversations.id (CASCADE), INDEX |
| role | VARCHAR(20) | NOT NULL (user / assistant) |
| content | TEXT | NOT NULL |
| token_count | INTEGER | DEFAULT 0 |
| sources | JSONB | NULLABLE (citation metadata) |
| latency_ms | INTEGER | NULLABLE |
| created_at | TIMESTAMP | NOT NULL |

#### daily_analytics
| Column | Type | Constraints |
|---|---|---|
| id | SERIAL | PK |
| workspace_id | UUID | FK → workspaces.id |
| date | DATE | INDEX |
| total_queries | INTEGER | DEFAULT 0 |
| total_tokens_prompt | INTEGER | DEFAULT 0 |
| total_tokens_completion | INTEGER | DEFAULT 0 |
| average_latency_ms | FLOAT | DEFAULT 0 |
| query_texts | JSONB | NULLABLE |

**Unique constraint**: `(workspace_id, date)` — one record per workspace per day

### Migrations

- `001_initial_schema.py`: Creates all tables, enables pgvector/pg_trgm extensions, creates GIN index
- `002_add_workspace_id_to_chunks.py`: Adds `workspace_id` column to the chunks table

---

## 7. Design System

### Color Palette

| Name | Value | Usage |
|---|---|---|
| Primary | `#4F46E5` (Indigo 600) | Buttons, active states, chart lines |
| Primary 50-900 | Indigo scale | Hover, background, focus states |
| Success | `#10B981` (Emerald 500) | Completed status, success indicators |
| Background | `slate-50` | Page background |
| Foreground | `slate-900` | Body text |
| Muted | CSS variable (`--muted`) | Secondary text |
| Destructive | CSS variable (`--destructive`) | Delete actions |

### Typography

- **Inter** (Google Fonts) — `latin` subset
- Global classes: `bg-slate-50 text-slate-900`

### Component Library

shadcn/ui-based components:
- `Button` (4 variants: default, destructive, outline, ghost)
- `Card` (CardHeader, CardContent, CardTitle, CardDescription)
- `Input`, `Textarea`, `Label`
- `Tabs` (TabsList, TabsTrigger, TabsContent)
- `Badge` (5 variants: default, secondary, destructive, outline, success)
- `ScrollArea`, `Separator`, `Skeleton`

Custom components:
- `LanguageToggle` — 44x44px, 150ms fade transition, flag emoji display
- `StatCard` — Dashboard stat card with icon, title, value, and description
- `ChatInterface` — SSE streaming chat with auto-scroll
- `MessageBubble` — User/assistant message with source citations
- `SourceCitation` — Document citation card with document name, page number, and snippet
- `DocumentCard` — Document status display with status badge, chunk count, and file size

---

## 8. Project Structure (with Line Counts)

```
documind/
├── backend/                               # Python backend (3,179 lines)
│   ├── app/
│   │   ├── main.py                        # FastAPI app + CORS + seed endpoint (209 lines)
│   │   ├── config.py                      # Pydantic Settings configuration (32 lines)
│   │   ├── database.py                    # Async SQLAlchemy engine + session (28 lines)
│   │   ├── dependencies.py                # Auth dependency injection (30 lines)
│   │   ├── models/                        # SQLAlchemy ORM models
│   │   │   ├── base.py                    #   DeclarativeBase + TimestampMixin (24 lines)
│   │   │   ├── workspace.py               #   Workspace (22 lines)
│   │   │   ├── user.py                    #   User with role (25 lines)
│   │   │   ├── document.py                #   Document metadata + content hash (38 lines)
│   │   │   ├── chunk.py                   #   Text chunk + vector(1536) embedding (40 lines)
│   │   │   ├── conversation.py            #   Chat session + summary (29 lines)
│   │   │   ├── message.py                 #   Message + JSONB sources (28 lines)
│   │   │   ├── usage_log.py               #   Token consumption log (19 lines)
│   │   │   └── analytics.py               #   Daily aggregated metrics (27 lines)
│   │   ├── schemas/                       # Pydantic request/response schemas
│   │   │   ├── auth.py                    #   Login/register/token (33 lines)
│   │   │   ├── chat.py                    #   Chat request + SSE events (23 lines)
│   │   │   ├── document.py                #   Document list/response (29 lines)
│   │   │   ├── conversation.py            #   Conversation summary/detail (33 lines)
│   │   │   └── analytics.py               #   Usage stats/top queries (24 lines)
│   │   ├── routers/                       # API endpoint handlers
│   │   │   ├── auth.py                    #   Login / register / verify (34 lines)
│   │   │   ├── documents.py               #   Upload / list / delete / ingest (143 lines)
│   │   │   ├── chat.py                    #   SSE streaming chat (41 lines)
│   │   │   ├── conversations.py           #   Conversation management (61 lines)
│   │   │   └── analytics.py               #   Usage stats + top queries (95 lines)
│   │   └── services/                      # Business logic layer
│   │       ├── auth_service.py            #   User authentication + registration (71 lines)
│   │       ├── security_service.py        #   Injection detection + sanitization (39 lines)
│   │       ├── embedding_service.py       #   Dual-mode embedding generation (69 lines)
│   │       ├── ingest_service.py          #   Document parsing + semantic chunking (311 lines)
│   │       ├── search_service.py          #   Hybrid search (vector+keyword+RRF) (162 lines)
│   │       └── chat_service.py            #   RAG pipeline + SSE streaming (355 lines)
│   ├── alembic/                           # Database migrations
│   │   └── versions/
│   │       ├── 001_initial_schema.py      #   Initial schema (198 lines)
│   │       └── 002_add_workspace_id_to_chunks.py  # Workspace isolation (32 lines)
│   ├── seed/                              # Demo data seeder
│   │   ├── seed.py                        #   Seed script (297 lines)
│   │   └── data/                          #   Sample documents (Markdown)
│   │       ├── company-handbook.md
│   │       ├── product-roadmap.md
│   │       └── api-documentation.md
│   ├── tests/                             # pytest tests (77 tests)
│   │   ├── test_search_service.py         #   RRF fusion tests (104 lines)
│   │   ├── test_ingest_service.py         #   Parsing + chunking tests (134 lines)
│   │   ├── test_security_service.py       #   Injection detection tests (82 lines)
│   │   ├── test_embedding_service.py      #   Pseudo-embedding tests (58 lines)
│   │   ├── test_chat_service.py           #   Demo mode response tests (59 lines)
│   │   └── test_auth_service.py           #   bcrypt hashing tests (63 lines)
│   ├── requirements.txt                   # Production dependencies (18 packages)
│   ├── requirements-dev.txt               # Development dependencies (pytest)
│   └── render.yaml                        # Render.com deployment config
│
├── frontend/                              # TypeScript frontend (2,875 lines)
│   ├── src/
│   │   ├── app/                           # Next.js 15 App Router
│   │   │   ├── layout.tsx                 #   Root layout + NextIntlClientProvider (35 lines)
│   │   │   ├── page.tsx                   #   Root page (/ → /dashboard redirect) (5 lines)
│   │   │   ├── globals.css                #   Global styles + CSS variables
│   │   │   ├── (auth)/                    #   Auth page group
│   │   │   │   ├── layout.tsx             #     Auth layout + LanguageToggle (16 lines)
│   │   │   │   ├── login/page.tsx         #     Login page (5 lines)
│   │   │   │   └── register/page.tsx      #     Register page (5 lines)
│   │   │   ├── dashboard/                 #   Protected routes
│   │   │   │   ├── layout.tsx             #     Sidebar + Header layout (18 lines)
│   │   │   │   ├── page.tsx               #     Dashboard overview (57 lines)
│   │   │   │   ├── chat/page.tsx          #     Chat interface (32 lines)
│   │   │   │   ├── chat/[id]/page.tsx     #     Conversation detail (24 lines)
│   │   │   │   ├── documents/page.tsx     #     Document management (24 lines)
│   │   │   │   ├── analytics/page.tsx     #     Analytics dashboard (40 lines)
│   │   │   │   └── settings/page.tsx      #     Settings (105 lines)
│   │   │   └── api/auth/                  #   NextAuth API routes
│   │   │       ├── [...nextauth]/route.ts #     NextAuth handler (2 lines)
│   │   │       └── token/route.ts         #     Backend token endpoint (30 lines)
│   │   ├── components/
│   │   │   ├── language-toggle.tsx         #   Language switch button (60 lines)
│   │   │   ├── auth/
│   │   │   │   ├── login-form.tsx         #     Login form (102 lines)
│   │   │   │   └── register-form.tsx      #     Registration form (154 lines)
│   │   │   ├── chat/
│   │   │   │   ├── chat-interface.tsx      #     Main chat view (101 lines)
│   │   │   │   ├── chat-input.tsx         #     Message input (85 lines)
│   │   │   │   ├── conversation-list.tsx  #     Conversation list (68 lines)
│   │   │   │   ├── message-bubble.tsx     #     Message bubble (51 lines)
│   │   │   │   ├── source-citation.tsx    #     Citation card (46 lines)
│   │   │   │   ├── empty-state.tsx        #     Empty state + sample questions (46 lines)
│   │   │   │   └── thinking-indicator.tsx #     Thinking indicator (27 lines)
│   │   │   ├── documents/
│   │   │   │   ├── document-card.tsx      #     Document card (82 lines)
│   │   │   │   ├── document-list.tsx      #     Document list (46 lines)
│   │   │   │   └── upload-dialog.tsx      #     Upload dialog (63 lines)
│   │   │   ├── analytics/
│   │   │   │   ├── token-usage-chart.tsx  #     Token usage chart (81 lines)
│   │   │   │   ├── query-count-chart.tsx  #     Query count chart (66 lines)
│   │   │   │   ├── latency-chart.tsx      #     Latency chart (74 lines)
│   │   │   │   └── top-queries-list.tsx   #     Top queries list (48 lines)
│   │   │   ├── dashboard/
│   │   │   │   ├── sidebar.tsx            #     Sidebar navigation (100 lines)
│   │   │   │   ├── header.tsx             #     Header + LanguageToggle (29 lines)
│   │   │   │   └── stat-card.tsx          #     Stat card (32 lines)
│   │   │   └── ui/                        #   shadcn/ui primitives (10 components)
│   │   ├── hooks/
│   │   │   ├── use-chat.ts                #   Chat state management (78 lines)
│   │   │   ├── use-sse.ts                 #   SSE client (84 lines)
│   │   │   ├── use-documents.ts           #   Document CRUD (45 lines)
│   │   │   ├── use-conversations.ts       #   Conversation fetching (22 lines)
│   │   │   └── use-analytics.ts           #   Analytics data fetching (23 lines)
│   │   ├── i18n/
│   │   │   ├── config.ts                  #   Locale definitions (ja, en) (3 lines)
│   │   │   └── request.ts                 #   Server-side locale resolution (17 lines)
│   │   ├── messages/
│   │   │   ├── ja.json                    #   Japanese translations (132 lines)
│   │   │   └── en.json                    #   English translations (132 lines)
│   │   ├── lib/
│   │   │   ├── api-client.ts              #   Fetch wrapper + auth headers (119 lines)
│   │   │   ├── auth.ts                    #   NextAuth config + JWT callbacks (83 lines)
│   │   │   ├── auth.config.ts             #   Route protection config (19 lines)
│   │   │   └── utils.ts                   #   Utility functions (95 lines)
│   │   ├── providers/
│   │   │   ├── auth-provider.tsx           #   SessionProvider wrapper (7 lines)
│   │   │   └── query-provider.tsx          #   QueryClient wrapper (22 lines)
│   │   └── types/
│   │       ├── chat.ts                    #   Chat type definitions (24 lines)
│   │       ├── document.ts                #   Document type definitions (22 lines)
│   │       ├── conversation.ts            #   Conversation type definitions (22 lines)
│   │       ├── analytics.ts               #   Analytics type definitions (22 lines)
│   │       └── next-auth.d.ts             #   NextAuth type extensions (57 lines)
│   ├── middleware.ts                      #   NextAuth route protection middleware (8 lines)
│   ├── next.config.ts                     #   Next.js + next-intl plugin config (10 lines)
│   ├── tailwind.config.ts                 #   Tailwind CSS custom config (71 lines)
│   └── package.json                       #   Dependencies (49 lines)
│
├── .github/workflows/ci.yml              # GitHub Actions CI pipeline (60 lines)
├── README.md                              # Project overview (407 lines)
└── LICENSE                                # MIT License
```

**Total lines of code**: Python 3,179 + TypeScript 2,875 = 6,054 lines

---

## 9. Setup Instructions

### Prerequisites

- Python 3.12 or later
- Node.js 20 or later
- PostgreSQL 17 with `pgvector` and `pg_trgm` extensions

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env:
#   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/documind  (required)
#   NEXTAUTH_SECRET=your-secret                                          (required)
#   OPENAI_API_KEY=sk-...                                               (optional — omit for demo mode)

# Run database migrations
alembic upgrade head

# Seed demo data (no API key needed)
python -m seed.seed
# For real OpenAI embeddings: python -m seed.seed --use-openai

# Start server
uvicorn app.main:app --reload
# API available at http://localhost:8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.local.example .env.local
# Edit .env.local:
#   NEXTAUTH_SECRET=your-secret            (must match backend)
#   NEXTAUTH_URL=http://localhost:3000
#   NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
# App available at http://localhost:3000
```

### Demo Credentials

- Email: `admin@documind.dev`
- Password: `demo1234`

### Running Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
# 77 tests — 6 modules
```

### Environment Variables

| Variable | Required | Description | Default |
|---|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string (asyncpg) | `postgresql+asyncpg://user:password@localhost:5432/documind` |
| `NEXTAUTH_SECRET` | Yes | JWT signing secret | (auto-generated at startup; must be set in production) |
| `OPENAI_API_KEY` | No | OpenAI API key (omit for demo mode) | `None` |
| `CORS_ORIGINS` | No | Allowed origins (comma-separated) | `http://localhost:3000` |
| `EMBEDDING_MODEL` | No | Embedding model name | `text-embedding-3-small` |
| `EMBEDDING_DIMENSIONS` | No | Embedding vector dimensions | `1536` |
| `CHAT_MODEL` | No | Chat model name | `gpt-4o-mini` |
| `CHUNK_SIZE` | No | Chunk size in tokens | `500` |
| `CHUNK_OVERLAP` | No | Chunk overlap in tokens | `50` |
| `RRF_K` | No | RRF parameter | `60` |
| `CONVERSATION_MEMORY_LIMIT` | No | Messages kept in conversation context | `5` |
| `MAX_UPLOAD_SIZE_MB` | No | Maximum upload file size | `20` |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL | `http://localhost:8000` |
| `NEXTAUTH_URL` | Yes | Frontend URL | `http://localhost:3000` |

---

## 10. Design Decisions

| Decision | Rationale |
|---|---|
| **Monorepo structure** | Simplifies deployment, versioning, and cross-stack refactoring |
| **FastAPI + Next.js separation** | Demonstrates polyglot architecture: Python for ML/backend, TypeScript for frontend |
| **Hybrid search over vector-only** | Production RAG systems need keyword fallback for exact matches — vector search alone is insufficient |
| **RRF over linear combination** | Rank-based fusion is robust to score distribution differences. Only one tuning parameter (k) |
| **Dual-mode architecture** | Run a $0 portfolio demo while proving production-ready code paths |
| **SSE over WebSocket** | Sufficient for unidirectional streaming; simpler protocol with fewer failure modes |
| **Semantic chunking** | Heading-aware splitting preserves document structure better than fixed-size chunking |
| **500-token chunks with 50-token overlap** | Balanced granularity for retrieval precision without fragmenting context |
| **asyncio.gather for concurrent search** | Eliminates sequential bottleneck between vector and keyword search |
| **Workspace-scoped queries** | Multi-tenant isolation at the query level, not just the application level |
| **Cookie-based i18n (not path-based)** | Preserves existing URL structure. Path-based locale SEO benefits are negligible for authenticated SaaS apps |
| **IVFFlat index (lists=100)** | Created after data load. Faster to build than HNSW; appropriate for moderate-scale datasets |
| **50-minute token cache** | Eliminates redundant `/api/auth/token` calls against a 1-hour token lifetime |
| **TanStack Query (staleTime=60s)** | Server state caching with automatic invalidation. Removes the complexity of manual state management |

---

## 11. Running Costs

### Demo Mode ($0 Configuration)

| Service | Plan | Cost |
|---|---|---|
| Vercel | Hobby (free) | $0 |
| Render | Free | $0 |
| Neon | Free Tier (0.5 GiB storage) | $0 |
| OpenAI | Not used | $0 |
| **Total** | | **$0/month** |

### Live Mode (with OpenAI)

| Service | Estimated Cost |
|---|---|
| Vercel | $0 (Hobby) to $20/month (Pro) |
| Render | $0 (Free) to $7/month (Starter) |
| Neon | $0 (Free) to $19/month (Launch) |
| OpenAI `text-embedding-3-small` | ~$0.02 / 1M tokens |
| OpenAI `gpt-4o-mini` | ~$0.15 / 1M input tokens, $0.60 / 1M output tokens |
| **Total** | **$0 to ~$50/month** (usage dependent) |

---

## 12. Author

**[@mer-prog](https://github.com/mer-prog)**

---

## License

MIT
