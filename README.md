# DocuMind — AI ドキュメントインテリジェンス プラットフォーム

> ドキュメントをアップロード。質問を投げる。引用付きの回答を即座に取得。

**DocuMind** は、組織の内部ナレッジベースを会話型インターフェースに変換するフルスタック AI ドキュメントインテリジェンスプラットフォームです。Markdown、PDF、DOCX ファイルをアップロードすると、セマンティックチャンク分割・ベクトル埋め込み・インデックス作成を自動実行し、自然言語チャットによる即時検索を可能にします。

🔗 **ライブデモ:** [documind-pi.vercel.app](https://documind-pi.vercel.app)
📧 **デモ認証情報:** `admin@documind.dev` / `demo1234`

---

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────┐
│                  フロントエンド (Vercel)               │
│         Next.js 15 · React 19 · TypeScript          │
│      NextAuth.js · TanStack Query · Tailwind CSS    │
└────────────────────────┬────────────────────────────┘
                         │ REST + SSE
┌────────────────────────▼────────────────────────────┐
│                  バックエンド (Render)                 │
│           Python · FastAPI · SQLAlchemy              │
│        ハイブリッド検索エンジン · SSE ストリーミング       │
└────────────────────────┬────────────────────────────┘
                         │ asyncpg + SSL
┌────────────────────────▼────────────────────────────┐
│                データベース (Neon)                     │
│     PostgreSQL 17 · pgvector · pg_trgm              │
│        ベクトル埋め込み · 全文検索                      │
└─────────────────────────────────────────────────────┘
```

---

## 主要機能

### 🔍 ハイブリッド検索 (pgvector + pg_trgm + RRF)

DocuMind はベクトル検索だけに頼りません。**セマンティック検索**（pgvector によるコサイン類似度）と**キーワード検索**（pg_trgm によるトライグラムマッチング）を **Reciprocal Rank Fusion (k=60)** で統合し、高精度な検索結果を実現します。単一モダリティの検索を大幅に上回る性能を発揮します。

### 💬 ソース引用付き会話型 RAG

すべての回答に、元のドキュメントチャンクを指すインラインソース引用が含まれます。会話メモリ（直近5メッセージ＋要約）を保持し、文脈を踏まえたフォローアップ質問に対応します。

### 📡 リアルタイム SSE ストリーミング

チャット応答は Server-Sent Events でトークンごとにストリーミング配信され、ChatGPT ライクなレスポンシブ UX を提供します。ライブモード（OpenAI GPT-4o-mini）とデモモード（テンプレートベース）の両方で同一の SSE プロトコルを使用します。

### 📊 アナリティクスダッシュボード

トークン消費量、クエリレイテンシ、検索品質メトリクス、利用パターンを追跡するオブザーバビリティダッシュボードを内蔵。プロダクションレベルの運用設計を体現しています。

### 🔒 マルチテナント ワークスペースアーキテクチャ

ロールベースアクセス制御（admin/member）によるワークスペース完全分離で、組織間のデータセパレーションを保証します。

### 🔄 デュアルモードアーキテクチャ（デモ / ライブ）

| | デモモード | ライブモード |
|---|---|---|
| **埋め込み** | ハッシュベース疑似ベクトル（決定的・無料） | OpenAI `text-embedding-3-small` |
| **チャット** | 検索結果ベースのテンプレート応答 + 35ms 疑似SSE | GPT-4o-mini ストリーミング |
| **検索** | ✅ 実ハイブリッド検索（pgvector + pg_trgm） | ✅ 同一 |
| **コスト** | $0 | 従量課金（OpenAI API） |
| **有効化** | デフォルト（APIキー不要） | `OPENAI_API_KEY` 環境変数を設定 |

> デモモードはモックではありません — ハイブリッド検索エンジンは事前計算済み埋め込みに対して実際のコサイン類似度計算とトライグラムマッチングを実行します。

---

## 技術スタック

### バックエンド

| 技術 | 用途 |
|---|---|
| **Python 3.12** | バックエンド言語 |
| **FastAPI** | 非同期 REST API フレームワーク |
| **SQLAlchemy 2.0** | 型安全な非同期 ORM |
| **Alembic** | データベースマイグレーション管理 |
| **pgvector** | ベクトル類似度検索（コサイン距離） |
| **pg_trgm** | トライグラムベースのキーワード検索 |
| **asyncpg** | 高性能非同期 PostgreSQL ドライバ |
| **bcrypt** | パスワードハッシュ化 |
| **tiktoken** | OpenAI モデル用トークンカウント |

### フロントエンド

| 技術 | 用途 |
|---|---|
| **Next.js 15** | App Router 搭載 React フレームワーク |
| **React 19** | UI ライブラリ |
| **TypeScript** | 型安全な開発 |
| **NextAuth.js** | 認証（Credentials Provider） |
| **TanStack Query** | サーバーステート管理 & キャッシュ |
| **Tailwind CSS** | ユーティリティファーストスタイリング |
| **shadcn/ui** | アクセシブルコンポーネントライブラリ |
| **Recharts** | アナリティクスデータ可視化 |

### インフラストラクチャ

| サービス | 用途 |
|---|---|
| **Vercel** | フロントエンドホスティング（Edge Network） |
| **Render** | バックエンドホスティング（Python ランタイム） |
| **Neon** | サーバーレス PostgreSQL（pgvector 対応） |

---

## プロジェクト構成

```
documind/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI アプリ + シードエンドポイント
│   │   ├── config.py            # Pydantic 設定管理
│   │   ├── database.py          # 非同期 SQLAlchemy エンジン
│   │   ├── models/              # SQLAlchemy ORM モデル
│   │   │   ├── user.py
│   │   │   ├── workspace.py
│   │   │   ├── document.py
│   │   │   ├── chunk.py
│   │   │   ├── conversation.py
│   │   │   └── usage_log.py
│   │   ├── routers/             # API ルートハンドラ
│   │   │   ├── auth.py
│   │   │   ├── documents.py
│   │   │   ├── chat.py
│   │   │   ├── search.py
│   │   │   └── analytics.py
│   │   └── services/            # ビジネスロジック層
│   │       ├── embedding_service.py   # デュアルモード埋め込み
│   │       ├── ingest_service.py      # ドキュメント解析 + チャンク分割
│   │       ├── search_service.py      # ハイブリッド検索 (RRF)
│   │       └── chat_service.py        # RAG + SSE ストリーミング
│   ├── seed/
│   │   ├── seed.py              # データベースシーダー
│   │   └── data/                # サンプルドキュメント (Markdown)
│   ├── requirements.txt
│   └── main.py                  # Uvicorn エントリーポイント
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router ページ
│   │   ├── components/
│   │   │   ├── chat/            # チャットインターフェース
│   │   │   ├── documents/       # ドキュメント管理 UI
│   │   │   ├── analytics/       # ダッシュボードチャート
│   │   │   └── ui/              # shadcn/ui コンポーネント
│   │   ├── lib/
│   │   │   ├── api-client.ts    # バックエンド API 統合
│   │   │   └── auth.ts          # NextAuth 設定
│   │   └── types/               # TypeScript 型定義
│   ├── tailwind.config.ts
│   └── next.config.ts
│
└── .gitignore
```

---

## ハイブリッド検索の仕組み

```
ユーザークエリ: "リモートワークのポリシーは？"
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  セマンティック検索         キーワード検索
  (pgvector コサイン類似度)  (pg_trgm トライグラム)
        │                       │
  ベクトル類似度で          トライグラムマッチ
  ランキング               スコアでランキング
        │                       │
        └───────────┬───────────┘
                    ▼
         Reciprocal Rank Fusion
           score = Σ 1/(k + rank_i)
                  k = 60
                    │
                    ▼
          Top-N 統合結果
          ソースメタデータ付き
```

このアプローチにより：
- **セマンティッククエリ**（「休暇の考え方について説明して」）→ 埋め込み類似度を活用
- **完全一致クエリ**（「PTO ポリシー セクション 4.2」）→ トライグラムキーワードマッチングを活用
- **混合クエリ** → RRF スコア統合で両方の長所を取得

---

## セットアップ手順

### 前提条件

- Python 3.12+
- Node.js 20+
- PostgreSQL（pgvector および pg_trgm 拡張機能が必要）

### バックエンド

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
cp .env.example .env
# .env に DATABASE_URL を設定（任意で OPENAI_API_KEY も設定）
```

```bash
python -m seed.seed
# デモ用ワークスペース・ユーザー・ドキュメントを投入（APIキー不要）
```

```bash
uvicorn main:app --reload
# API: http://localhost:8000
```

### フロントエンド

```bash
cd frontend
npm install
```

```bash
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000 を設定
```

```bash
npm run dev
# アプリ: http://localhost:3000
```

---

## API エンドポイント

| メソッド | エンドポイント | 説明 |
|---|---|---|
| `POST` | `/api/auth/login` | ユーザー認証 |
| `POST` | `/api/auth/register` | ユーザー登録 |
| `GET` | `/api/documents` | ワークスペースのドキュメント一覧 |
| `POST` | `/api/documents/upload` | ドキュメントのアップロード & 取り込み |
| `DELETE` | `/api/documents/:id` | ドキュメント削除 |
| `POST` | `/api/chat` | チャットメッセージ送信（SSE ストリーム） |
| `GET` | `/api/conversations` | 会話一覧 |
| `POST` | `/api/search` | ハイブリッド検索クエリ |
| `GET` | `/api/analytics/usage` | 利用統計 |
| `GET` | `/api/mode` | 現在のモード（demo/live） |

---

## データベーススキーマ

```
workspaces ──┬── users (role: admin/member)
             ├── documents ── chunks (embedding: vector(1536))
             └── conversations ── messages (sources: jsonb)
                                  usage_logs (tokens, latency)
```

主要な設計判断：
- **`vector(1536)`** — OpenAI 互換の埋め込みベクトルを chunks テーブルに格納
- **GIN インデックス (pg_trgm)** — 高速トライグラムキーワード検索
- **HNSW インデックス (pgvector)** — 近似最近傍検索
- **JSONB sources** — messages テーブルで柔軟な引用情報を格納

---

## 設計判断の根拠

| 判断 | 根拠 |
|---|---|
| **モノレポ構成** | 単一リポジトリでデプロイとバージョン管理を簡素化 |
| **FastAPI + Next.js 分離** | ポリグロットアーキテクチャ（Python + TypeScript）の実践 |
| **ハイブリッド検索** | 本番 RAG システムには完全一致のためのキーワードフォールバックが不可欠 |
| **RRF（線形結合ではなく）** | ランクベース統合はスコア分布の差異に対してよりロバスト |
| **デュアルモード** | $0 でポートフォリオデモを運用しつつ、本番対応コードを証明 |
| **SSE（WebSocket ではなく）** | 単方向ストリーミングには十分なシンプルなプロトコル |
| **セマンティックチャンク分割** | 見出し認識分割により固定サイズ分割よりもドキュメント構造を保持 |

---

## 言語構成

- **Python** — 51.1%
- **TypeScript** — 47.7%
- **その他**（CSS, SQL）— 1.2%

---

## ライセンス

本プロジェクトはポートフォリオデモンストレーション目的で構築されています。

## 作者

[@mer-prog](https://github.com/mer-prog)
