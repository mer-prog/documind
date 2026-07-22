<div align="center">

# DocuMind

**AI ドキュメントインテリジェンス・プラットフォーム / AI-Powered Document Intelligence Platform**

文書をアップロードし、自然言語で質問すると、出典付きの回答が返る RAG アプリケーション。

Upload documents. Ask questions. Get cited answers instantly.

[![Live Demo](https://img.shields.io/badge/Live_Demo-documind--pi.vercel.app-000?style=for-the-badge&logo=vercel)](https://documind-pi.vercel.app)

[![CI](https://github.com/mer-prog/documind/actions/workflows/ci.yml/badge.svg)](https://github.com/mer-prog/documind/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Next.js](https://img.shields.io/badge/Next.js-15-000?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=000)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=fff)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL_17-pgvector-4169E1?logo=postgresql&logoColor=fff)](https://www.postgresql.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=fff)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=fff)](https://www.python.org/)

</div>

> **デモ用アカウント / Demo credentials:** `admin@documind.dev` / `demo1234`

---

## 概要 / Overview

DocuMind は、Markdown / PDF / DOCX をアップロードすると自動でチャンク分割・ベクトル埋め込み・索引化を行い、出典付きの対話型検索を提供するフルスタック RAG アプリケーションです。ポートフォリオ RAG アプリの多くが「単一の検索手法 + OpenAI 呼び出しのラッパー」に留まる中、本プロジェクトは検索・ストリーミング・セキュリティの各層を実装レベルで作り込んでいます。

**技術的な見どころ 3 点:**

| | 実装内容 | コード上の根拠 |
|---|---|---|
| **ハイブリッド検索 (RRF)** | pgvector コサイン類似度（セマンティック）+ pg_trgm トライグラム（キーワード）の 2 系統を **Reciprocal Rank Fusion (k=60)** で統合。2 クエリは**独立した DB セッション**上で `asyncio.gather()` により並行実行 | `backend/app/services/search_service.py` |
| **実 LLM ストリーミング** | Live モードは OpenAI `gpt-4o-mini` への `stream=True` 呼び出しによる**本物のトークン単位 SSE**。`stream_options={"include_usage": True}` でトークン使用量を取得し分析に記録。API 例外は SSE error イベントとしてクライアントへ通知 | `backend/app/services/chat_service.py` |
| **プロンプトインジェクション対策** | 正規表現ベースの攻撃パターン検知（"ignore previous instructions" 系ほか）+ 入力サニタイズ（長さ制限 4000 字・空白正規化・null バイト除去）をチャット入口で適用し、検知時はブロック | `backend/app/services/security_service.py` |

そのほか、ワークスペース単位のマルチテナント分離（RBAC: admin/member、会話はユーザー所有者検証つき）、会話メモリ（直近 5 件 + 旧文脈の自動要約）、トークン消費・レイテンシの分析ダッシュボード、next-intl による日英 i18n を備えます。

**デュアルモード構成:** API キーなし（$0）でも検索エンジンと SSE パイプラインは本物のまま動作します。

| | Demo モード | Live モード |
|---|---|---|
| **埋め込み** | SHA-256 ベースの決定的疑似ベクトル（L2 正規化済み・無料） | OpenAI `text-embedding-3-small` |
| **チャット** | 検索結果からのテンプレート応答 + 35ms 間隔の擬似 SSE | `gpt-4o-mini` の実ストリーミング |
| **検索** | 実ハイブリッド検索（pgvector + pg_trgm + RRF） | 同一 |
| **コスト** | $0 | OpenAI API 従量課金 |
| **切替** | 既定（API キー不要） | 環境変数 `OPENAI_API_KEY` を設定 |

> 注: Demo モードの疑似埋め込みは決定的ハッシュであり意味的類似性は持ちません（検索品質は主にキーワード側 pg_trgm が担います）。検索エンジン・RRF・SSE のコードパス自体は Live と同一です。

> **EN:** DocuMind is a full-stack RAG application: hybrid retrieval (pgvector cosine + pg_trgm trigram fused via Reciprocal Rank Fusion, k=60, the two queries running concurrently on **separate DB sessions**), genuine token-by-token SSE streaming from OpenAI `gpt-4o-mini` with usage tracking, and prompt-injection detection/sanitization at the chat entry point. It ships with workspace-based multi-tenancy (conversations verified against the requesting user), conversation memory with summarization, an analytics dashboard, ja/en i18n, and a dual-mode architecture that runs the real search engine at $0 without an API key.

---

## アーキテクチャ / Architecture

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
│     vector(1536) 埋め込み · GIN トライグラム索引          │
└─────────────────────────────────────────────────────────┘
```

### 検索パイプライン / Search Pipeline

```
User Query: "What is the remote work policy?"
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  Semantic Search          Keyword Search
  pgvector cosine          pg_trgm trigram
  similarity               similarity > 0.05
  (top 20)                 (top 20)
   独立セッションで asyncio.gather() 並行実行
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

- 意味的な質問（「休暇の考え方を教えて」）は埋め込み類似度が拾い、完全一致系の質問（「PTO 規程 4.2 節」）はトライグラムが拾う。RRF はスコア分布の異なる 2 系統をランクベースで頑健に融合する。

### 技術スタック / Tech Stack

| レイヤ | 技術 |
|---|---|
| **Backend** | Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) · asyncpg · Alembic · PyMuPDF / python-docx（文書パース） · tiktoken · bcrypt · python-jose (JWT) · sse-starlette |
| **Frontend** | Next.js 15 (App Router) · React 19 · TypeScript 5.7 · NextAuth.js v5 · TanStack Query 5 · Tailwind CSS · shadcn/ui + Radix UI · Recharts · next-intl (ja/en) · Zod |
| **Database** | PostgreSQL 17 · pgvector（コサイン距離） · pg_trgm（GIN 索引） |
| **Infra** | Vercel（Frontend） · Render（Backend） · Neon（Serverless PostgreSQL） |

### データベーススキーマ / Database Schema

```
workspaces ──┬── users (role: admin | member)
             ├── documents ── chunks (embedding: vector(1536))
             ├── conversations ── messages (sources: jsonb)
             └── usage_logs (tokens, latency_ms)
                 daily_analytics (aggregated metrics)
```

- **`vector(1536)`** — OpenAI 互換次元の埋め込みを chunks テーブルに直接格納
- **GIN 索引 (pg_trgm)** — チャンク本文への高速トライグラム検索
- **JSONB sources** — メッセージごとの引用メタデータ（チャンク ID・文書名・ページ・スコア）
- **SHA-256 コンテンツハッシュ** — 文書レベルの重複排除
- ベクトル検索の ANN 索引（HNSW 等）は現状未導入（[既知の制限](#既知の制限--known-limitations)参照）

### API リファレンス / API Reference

| Method | Endpoint | 説明 |
|---|---|---|
| `POST` | `/api/auth/login` | ログイン |
| `POST` | `/api/auth/register` | ユーザー登録 |
| `POST` | `/api/auth/verify` | JWT 検証 |
| `GET` | `/api/documents` | ワークスペースの文書一覧 |
| `POST` | `/api/documents` | 文書アップロード |
| `DELETE` | `/api/documents/:id` | 文書削除 |
| `POST` | `/api/documents/:id/ingest` | 文書処理（チャンク化 + 埋め込み） |
| `POST` | `/api/chat` | チャット送信（SSE ストリーム） |
| `GET` | `/api/conversations` | 会話一覧 |
| `GET` | `/api/conversations/:id` | 会話詳細（メッセージ含む） |
| `GET` | `/api/analytics/usage` | 使用量統計 |
| `GET` | `/api/analytics/top-queries` | 上位クエリ |

> **EN:** FastAPI + Next.js separation over REST/SSE, PostgreSQL with pgvector and pg_trgm (GIN trigram index). No ANN index (HNSW) is currently in place — see Known Limitations.

---

## セットアップ / Setup

### 前提 / Prerequisites

- Python 3.12+
- Node.js 20+
- `pgvector` と `pg_trgm` 拡張が使える PostgreSQL

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
cp .env.example .env
# DATABASE_URL を設定（必須）
# OPENAI_API_KEY を設定（任意 — 未設定なら Demo モード）
```

```bash
# デモ用ワークスペース・ユーザー・文書を投入（API キー不要）
python -m seed.seed
```

```bash
uvicorn main:app --reload
# API: http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
```

```bash
cp .env.local.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000 を設定
```

```bash
npm run dev
# App: http://localhost:3000
```

> **EN:** Backend: venv → `pip install -r requirements.txt` → copy `.env.example` → seed → uvicorn. Frontend: `npm install` → copy `.env.local.example` → `npm run dev`. Demo mode needs no API key.

---

## テスト実行 / Running Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

**80 テスト**が 6 モジュールでコアロジックを検証します（外部 API・DB 接続は不要）:

| モジュール | 検証内容 |
|---|---|
| `test_search_service` | RRF 融合 — スコア式・重複排除・順位・k パラメータ感度／**並行検索のセッション分離**（2 クエリが別々の `AsyncSession` を使い、実際に並行実行されること） |
| `test_embedding_service` | 疑似埋め込み — 決定性・L2 正規化・次元数・大文字小文字非依存 |
| `test_ingest_service` | Markdown パース — 見出し検出・段落分割・本文保全／チャンク化 — オーバーラップ・インデックス |
| `test_security_service` | プロンプトインジェクション検知（16 種の攻撃入力）／サニタイズ — 長さ・空白・null バイト |
| `test_chat_service` | Demo モード応答生成 — 出典・ページ番号・上位 3 件制限・フォールバック／**会話の所有者検証**（他ユーザーの会話 ID 指定を拒否すること） |
| `test_auth_service` | bcrypt — 形式・照合・ソルトのランダム性・Unicode 対応 |

CI（GitHub Actions, `.github/workflows/ci.yml`）が push / PR ごとに backend の pytest と frontend の lint + build を実行します。

> **EN:** 80 unit tests across 6 modules, runnable without a database or API keys — including regression tests for the session-per-query concurrent search and the conversation ownership check. CI runs backend pytest plus frontend lint/build.

---

## 設計判断 / Design Decisions

| 判断 | 理由 |
|---|---|
| **ハイブリッド検索（ベクトル単独にしない）** | 本番 RAG は完全一致系クエリへのキーワードフォールバックが必須。ベクトル単独は「それっぽいが外す」を避けられない |
| **RRF（線形結合にしない）** | ランクベースの融合は 2 系統のスコア分布差に対して頑健。重みチューニング不要 |
| **並行検索はセッション分離** | SQLAlchemy の `AsyncSession` は単一セッションへの並行操作を非サポート。ベクトル/キーワード検索は**クエリごとに独立セッション**を張って `asyncio.gather()` で並行実行する |
| **会話はユーザー所有者検証** | 会話一覧・詳細・チャット継続のすべてで `user_id` スコープを強制し、他ユーザーの会話 ID を指定したアクセス（IDOR）を拒否 |
| **デュアルモード** | $0 でポートフォリオデモを公開しつつ、本番コードパス（検索・SSE・RAG）は共通のまま証明する |
| **SSE（WebSocket にしない）** | 単方向ストリーミングには SSE で十分。プロトコルが単純で障害モードが少ない |
| **セマンティックチャンキング** | 見出しを意識した分割は固定長分割より文書構造を保つ。500 トークン + 50 オーバーラップで検索精度と文脈保持のバランスを取る |
| **ワークスペース単位のクエリスコープ** | マルチテナント分離をアプリ層だけでなくクエリ層で担保 |
| **Cookie ベース i18n（パスベースにしない）** | 既存 URL 構造を保てる。認証必須 SaaS ではパスベースロケールの SEO 利点はほぼない |
| **モノレポ** | デプロイ・バージョニング・スタック横断の変更が単純になる |

> **EN:** Notable decisions: hybrid retrieval with RRF over vector-only or linear score mixing; concurrent search implemented with **one session per query** (SQLAlchemy's `AsyncSession` forbids concurrent use of a single session); conversation access always scoped to the requesting user; SSE over WebSocket for unidirectional streaming; heading-aware chunking (500 tokens, 50 overlap).

---

## 既知の制限 / Known Limitations

- **ANN 索引未導入** — ベクトル検索は HNSW / IVFFlat なしの逐次スキャン。現在のデータ規模では実用上問題ないが、チャンク数が増えたら HNSW 索引の追加（マイグレーション 1 本）が次の一手
- **レート制限・コスト上限なし** — トークン使用量の記録・可視化はあるが、ユーザー単位のレート制限や日次トークン上限による遮断は未実装。Live モードの公開運用では必須
- **Demo 埋め込みに意味的類似性はない** — 決定的ハッシュベースのため、Demo モードの検索品質は主に pg_trgm キーワード側が担う
- **インジェクション検知は正規表現ベースの簡易版** — 多層防御の一層であり、これ単体で LLM への攻撃を完封するものではない
- **Frontend の自動テストなし** — CI は lint + build のみ。バックエンド 80 テストに対して frontend はテスト未整備
- **`NEXTAUTH_SECRET` 未設定時はプロセスごとにランダム生成** — 開発時の利便性優先の挙動。複数ワーカー構成ではトークン検証が不整合になるため、本番では必ず明示設定する

> **EN:** Known gaps, stated honestly: no ANN index yet (sequential vector scan), no rate limiting or spend caps for live mode, demo embeddings carry no semantic similarity, regex-based injection detection is one defensive layer rather than a complete defense, no frontend tests, and `NEXTAUTH_SECRET` must be set explicitly in production.

---

## License

MIT

## Author

**[@mer-prog](https://github.com/mer-prog)**
