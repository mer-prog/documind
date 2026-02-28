<div align="center">

# DocuMind — AI ドキュメント検索プラットフォーム

**ドキュメントをアップロード。質問を投げる。引用付きの回答を即座に取得。**

[![Live Demo](https://img.shields.io/badge/Live_Demo-documind--pi.vercel.app-000?style=for-the-badge&logo=vercel)](https://documind-pi.vercel.app)

</div>

---

## 1. 証明するスキルセット

| カテゴリ | 実装内容 |
|---|---|
| **ハイブリッド検索** | pgvector コサイン類似度 + pg_trgm トライグラム一致を Reciprocal Rank Fusion (k=60) で統合。`asyncio.gather()` で並行実行 |
| **デュアルモード設計** | SHA-256 ハッシュベース擬似埋め込みによる $0 デモモードと、OpenAI `text-embedding-3-small` + `gpt-4o-mini` によるライブモードを環境変数1つで切替 |
| **SSE ストリーミング** | Server-Sent Events によるトークン単位のリアルタイムストリーミング。`sse-starlette` + `@microsoft/fetch-event-source` で実装 |
| **マルチテナント分離** | ワークスペース単位のデータ分離。全テーブル・全クエリに `workspace_id` スコープを適用。RBAC (admin/member) |
| **多言語対応 (i18n)** | `next-intl` による日英切替。Cookie ベースロケール、`localStorage` 永続化、日付・数値・通貨のロケール対応フォーマット |
| **セマンティックチャンキング** | 見出し認識型分割 (Markdown / PDF / DOCX)。500 トークンチャンク + 50 トークンオーバーラップ。`tiktoken` (cl100k_base) でトークンカウント |
| **会話メモリ管理** | 直近5メッセージ保持 + 古いメッセージの自動要約 (ライブモード時 GPT による要約生成) |
| **セキュリティ** | プロンプトインジェクション検知 (14パターンの正規表現マッチ)、入力サニタイズ (長さ制限4000文字、空白正規化、NULL バイト除去)、bcrypt パスワードハッシュ化 |
| **分析ダッシュボード** | トークン消費量・クエリ数・レイテンシの日次集計と可視化。`Recharts` による折れ線グラフ・棒グラフ |
| **非同期アーキテクチャ** | FastAPI + SQLAlchemy 2.0 async + asyncpg による完全非同期バックエンド。コネクションプール (pool_size=20, max_overflow=10) |
| **CI/CD** | GitHub Actions で pytest (バックエンド77テスト) + ESLint + Next.js ビルドを自動実行 |

---

## 2. 技術スタック（バージョン込み）

### バックエンド

| 技術 | 用途 |
|---|---|
| Python 3.12 | コア言語 |
| FastAPI | 非同期 REST API フレームワーク |
| SQLAlchemy 2.0 (asyncio) | 型安全な非同期 ORM |
| asyncpg | 高性能非同期 PostgreSQL ドライバ |
| Alembic | データベースマイグレーション管理 |
| pgvector | ベクトル類似検索 (コサイン距離) |
| pg_trgm | トライグラムベースのキーワード検索 |
| Pydantic >= 2.0 | リクエスト/レスポンスのスキーマバリデーション |
| pydantic-settings | 環境変数ベースの設定管理 |
| python-jose (cryptography) | JWT トークンの生成・検証 |
| bcrypt | パスワードハッシュ化 |
| openai | OpenAI API クライアント (ライブモード時) |
| tiktoken | OpenAI 互換トークンカウント (cl100k_base) |
| PyMuPDF (fitz) | PDF ドキュメントパース |
| python-docx | DOCX ドキュメントパース |
| sse-starlette | Server-Sent Events レスポンス |
| httpx | 非同期 HTTP クライアント |
| python-dotenv | .env ファイル読み込み |
| python-multipart | マルチパートフォームデータ解析 |

### フロントエンド

| 技術 | 用途 |
|---|---|
| Next.js 15 (App Router) | React フレームワーク |
| React 19 | UI ライブラリ |
| TypeScript 5.7 | 型安全な開発 |
| NextAuth.js v5 (beta.25) | 認証 (Credentials Provider) |
| TanStack Query 5 | サーバーステート管理・キャッシュ (staleTime: 60秒) |
| Tailwind CSS 3.4 | ユーティリティファースト CSS |
| shadcn/ui + Radix UI | アクセシブルコンポーネントライブラリ |
| Recharts 2.15 | 分析データ可視化 (折れ線・棒グラフ) |
| next-intl 4.8 | 国際化 (i18n) — 日本語/英語切替 |
| Zod 3.24 | ランタイムスキーマバリデーション |
| lucide-react | アイコンライブラリ |
| @microsoft/fetch-event-source | SSE クライアント |
| class-variance-authority | コンポーネントバリアントスタイリング |
| tailwind-merge / clsx | CSS クラス結合ユーティリティ |
| tailwindcss-animate | アニメーションプラグイン |

### インフラストラクチャ

| サービス | 用途 |
|---|---|
| Vercel | フロントエンドホスティング (Edge Network) |
| Render | バックエンドホスティング (Python ランタイム、free プラン) |
| Neon | サーバーレス PostgreSQL 17 (pgvector 対応) |

---

## 3. アーキテクチャ図（ASCII）

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vercel)                       │
│              Next.js 15 · React 19 · TypeScript 5.7         │
│     NextAuth.js v5 · TanStack Query 5 · Tailwind CSS 3.4   │
│                  next-intl (日英切替 i18n)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API + SSE (Server-Sent Events)
┌──────────────────────────▼──────────────────────────────────┐
│                     Backend (Render)                         │
│               Python 3.12 · FastAPI · SQLAlchemy 2.0        │
│     ハイブリッド検索エンジン · SSE ストリーミング · RAG パイプライン  │
│          セキュリティ (インジェクション検知 + bcrypt)              │
└──────────────────────────┬──────────────────────────────────┘
                           │ asyncpg + SSL
┌──────────────────────────▼──────────────────────────────────┐
│                   Database (Neon)                            │
│          PostgreSQL 17 · pgvector · pg_trgm                 │
│   vector(1536) 埋め込み · GIN インデックス · HNSW / IVFFlat    │
└─────────────────────────────────────────────────────────────┘
```

### 検索パイプライン

```
ユーザークエリ: 「リモートワークのポリシーは？」
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  セマンティック検索          キーワード検索
  pgvector コサイン類似度     pg_trgm トライグラム
  1 - (embedding <=> query)   similarity() > 0.05
  上位20件取得                上位20件取得
        │                       │
        └───────────┬───────────┘
                    ▼
          Reciprocal Rank Fusion
            score = Σ 1/(k + rank_i)
                   k = 60
                    │
                    ▼
           上位N件の統合結果
          ソースメタデータ付き
```

### チャットパイプライン (RAG)

```
ユーザーメッセージ
     │
     ▼
セキュリティチェック (14パターンのインジェクション検知)
     │
     ▼
入力サニタイズ (4000文字制限、空白正規化、NULLバイト除去)
     │
     ▼
ハイブリッド検索 (ベクトル + キーワード + RRF)
     │
     ▼
コンテキスト構築 (検索結果 + 会話履歴5件 + 要約)
     │
     ├─── ライブモード: OpenAI GPT-4o-mini ストリーミング
     │
     └─── デモモード: テンプレートベース疑似 SSE (35ms/単語)
     │
     ▼
SSE でトークン単位配信 → アシスタントメッセージ保存 → 分析ログ更新
```

---

## 4. 主要機能の詳細

### 4.1 ハイブリッド検索エンジン

- **ベクトル検索**: `pgvector` の `<=>` 演算子によるコサイン距離計算。`embedding IS NOT NULL` かつ `workspace_id` でフィルタリング
- **キーワード検索**: `pg_trgm` の `similarity()` 関数。閾値 0.05 以上の結果を取得。GIN インデックス (`gin_trgm_ops`) で高速化
- **RRF 統合**: `score = Σ 1/(rank + 1 + k)` (k=60)。ベクトル検索とキーワード検索の結果を rank ベースで統合。スコア分布の違いに頑健
- **並行実行**: `asyncio.gather()` でベクトル検索とキーワード検索を同時実行

### 4.2 デュアルモード設計

| | デモモード | ライブモード |
|---|---|---|
| **埋め込み** | SHA-256 ハッシュベース擬似ベクトル (無料) | OpenAI `text-embedding-3-small` |
| **チャット** | テンプレート応答 + 35ms 疑似 SSE | GPT-4o-mini ストリーミング |
| **検索** | 実際のハイブリッド検索 (pgvector + pg_trgm) | 同一 |
| **コスト** | $0 | OpenAI API 従量課金 |
| **切替方法** | デフォルト (API キー不要) | 環境変数 `OPENAI_API_KEY` を設定 |

擬似埋め込み生成アルゴリズム (`embedding_service.py`):
1. テキストを小文字化して単語分割
2. 各次元について `SHA-256("{先頭10単語}_{次元インデックス}")` のハッシュ値を計算
3. `(hash % 10000) / 5000 - 1.0` で -1.0 〜 1.0 の範囲に正規化
4. L2 正規化 (ベクトルのノルムを 1 に)

### 4.3 SSE ストリーミング

- バックエンド: `sse-starlette` の `EventSourceResponse` でイベント生成
- フロントエンド: `@microsoft/fetch-event-source` でイベント受信
- イベントタイプ: `conversation_id` → `sources` → `token` (複数) → `done` / `error`
- 接続切断検知: `request.is_disconnected()` でクライアント切断を検知し、ストリームを中断

### 4.4 セマンティックチャンキング

- **Markdown パース**: 見出し (`#{1,3}`) で分割 → 段落 (`\n\s*\n`) でさらに分割
- **PDF パース**: PyMuPDF でページ単位テキスト抽出 → 段落分割 (20文字以上のみ)
- **DOCX パース**: python-docx で Heading スタイル検出 → テキスト蓄積・分割
- **チャンク分割**: 500 トークン以下はそのまま、超過分は文境界 (`[.!?]\s+`) で分割
- **オーバーラップ**: 各チャンク末尾から 50 トークン分を次チャンクの先頭に付加

### 4.5 多言語対応 (i18n)

- **ライブラリ**: `next-intl` 4.8 (App Router 対応)
- **ロケール切替**: Cookie ベース (URL パス変更なし)。`getRequestConfig` でサーバーサイドロケール解決
- **永続化**: `localStorage` に保存 → 再訪問時に復元 → Cookie に同期
- **翻訳ファイル**: `ja.json` (132行) / `en.json` (132行)。ネームスペース: common, nav, auth, dashboard, documents, chat, analytics, settings, language
- **切替 UI**: LanguageToggle コンポーネント。44x44px ボタン、国旗絵文字 (🇯🇵/🇺🇸)、150ms フェードトランジション、`router.refresh()` でリロードなし切替
- **ロケール対応フォーマット**: `Intl.DateTimeFormat` (日付)、`Intl.NumberFormat` (数値・通貨)。ja-JP / en-US

### 4.6 認証システム

- **フロントエンド**: NextAuth.js v5 (Credentials Provider) → JWT セッション戦略
- **トークン生成**: `jose` の `SignJWT` で HS256 署名。ペイロードに `sub`, `email`, `name`, `workspace_id` を含む。有効期限 24時間
- **バックエンド検証**: `python-jose` で JWT デコード → ユーザー検索 → `get_current_user` 依存注入
- **パスワード**: bcrypt でハッシュ化・検証。ソルトはランダム生成
- **ルート保護**: NextAuth ミドルウェアで `/dashboard/*` を保護。未認証ユーザーは `/login` にリダイレクト
- **トークンキャッシュ**: フロントエンド側で 50分間キャッシュ (1時間トークンに対して)

### 4.7 分析ダッシュボード

- **日次集計テーブル** (`daily_analytics`): `workspace_id` + `date` のユニーク制約
- **メトリクス**: クエリ数、プロンプトトークン数、コンプリーショントークン数、平均レイテンシ (ミリ秒)、クエリテキスト一覧 (JSONB)
- **可視化**: トークン使用量 (積み上げ面グラフ)、日別クエリ数 (棒グラフ)、平均レイテンシ (折れ線グラフ)、上位クエリ (プログレスバー)

---

## 5. API エンドポイント一覧

| メソッド | エンドポイント | 説明 | 認証 | リクエスト | レスポンス |
|---|---|---|---|---|---|
| `POST` | `/api/auth/login` | ユーザー認証 | 不要 | `{ email, password }` | `UserResponse` |
| `POST` | `/api/auth/register` | ユーザー登録 (ワークスペース自動作成) | 不要 | `{ name, email, password }` | `UserResponse` |
| `POST` | `/api/auth/verify` | JWT トークン検証 | Bearer | — | `UserResponse` |
| `GET` | `/api/documents` | ドキュメント一覧取得 | Bearer | `?skip=0&limit=50` | `DocumentListResponse` |
| `POST` | `/api/documents` | ドキュメントアップロード (multipart) | Bearer | `FormData (file)` | `DocumentResponse` |
| `DELETE` | `/api/documents/:id` | ドキュメント削除 (カスケード) | Bearer | — | 204 No Content |
| `POST` | `/api/documents/:id/ingest` | ドキュメント処理 (パース→チャンク→埋め込み) | Bearer | — | `IngestResponse` |
| `POST` | `/api/chat` | チャットメッセージ送信 (SSE ストリーム) | Bearer | `{ message, conversation_id? }` | SSE EventStream |
| `GET` | `/api/conversations` | 会話一覧取得 | Bearer | — | `ConversationSummary[]` |
| `GET` | `/api/conversations/:id` | 会話詳細取得 (メッセージ付き) | Bearer | — | `ConversationDetail` |
| `GET` | `/api/analytics/usage` | 使用統計取得 | Bearer | `?days=30` (1-365) | `UsageResponse` |
| `GET` | `/api/analytics/top-queries` | 上位クエリランキング | Bearer | `?days=30&limit=10` | `TopQueriesResponse` |
| `GET` | `/health` | ヘルスチェック | 不要 | — | `{ status: "healthy" }` |
| `GET` | `/api/mode` | 動作モード取得 | 不要 | — | `{ mode, model }` |
| `POST` | `/api/seed` | デモデータ投入 (管理者のみ) | Bearer (admin) | — | `{ status }` |

**対応ファイル形式**: Markdown (.md), PDF (.pdf), DOCX (.docx)
**最大アップロードサイズ**: 20 MB

---

## 6. データベース設計

### ER 図

```
workspaces ──┬── users (role: admin | member)
             │     └── conversations ── messages (sources: JSONB)
             ├── documents ── chunks (embedding: vector(1536))
             ├── usage_logs (prompt_tokens, completion_tokens)
             └── daily_analytics (集計メトリクス, query_texts: JSONB)
```

### テーブル詳細

#### workspaces
| カラム | 型 | 制約 |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| api_key_hash | VARCHAR(255) | NULLABLE |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### users
| カラム | 型 | 制約 |
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
| カラム | 型 | 制約 |
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
| カラム | 型 | 制約 |
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

**インデックス**:
- `idx_chunk_content_trgm`: GIN インデックス (`gin_trgm_ops`) — トライグラムキーワード検索用
- `idx_chunk_embedding_ivfflat`: IVFFlat インデックス (`vector_cosine_ops`, lists=100) — ベクトル近似最近傍探索用

#### conversations
| カラム | 型 | 制約 |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users.id, INDEX |
| workspace_id | UUID | FK → workspaces.id |
| title | VARCHAR(512) | DEFAULT 'New Conversation' |
| summary | TEXT | NULLABLE (古いメッセージの要約) |
| message_count | INTEGER | DEFAULT 0 |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### messages
| カラム | 型 | 制約 |
|---|---|---|
| id | UUID | PK |
| conversation_id | UUID | FK → conversations.id (CASCADE), INDEX |
| role | VARCHAR(20) | NOT NULL (user / assistant) |
| content | TEXT | NOT NULL |
| token_count | INTEGER | DEFAULT 0 |
| sources | JSONB | NULLABLE (引用メタデータ) |
| latency_ms | INTEGER | NULLABLE |
| created_at | TIMESTAMP | NOT NULL |

#### daily_analytics
| カラム | 型 | 制約 |
|---|---|---|
| id | SERIAL | PK |
| workspace_id | UUID | FK → workspaces.id |
| date | DATE | INDEX |
| total_queries | INTEGER | DEFAULT 0 |
| total_tokens_prompt | INTEGER | DEFAULT 0 |
| total_tokens_completion | INTEGER | DEFAULT 0 |
| average_latency_ms | FLOAT | DEFAULT 0 |
| query_texts | JSONB | NULLABLE |

**ユニーク制約**: `(workspace_id, date)` — ワークスペース×日付で一意

### マイグレーション

- `001_initial_schema.py`: 全テーブル作成、pgvector/pg_trgm 拡張の有効化、GIN インデックス作成
- `002_add_workspace_id_to_chunks.py`: chunks テーブルに `workspace_id` カラム追加

---

## 7. デザインシステム

### カラーパレット

| 名称 | 値 | 用途 |
|---|---|---|
| Primary | `#4F46E5` (Indigo 600) | ボタン、アクティブ状態、チャート線 |
| Primary 50-900 | Indigo スケール | ホバー、背景、フォーカス |
| Success | `#10B981` (Emerald 500) | 完了状態、成功表示 |
| Background | `slate-50` | ページ背景 |
| Foreground | `slate-900` | 本文テキスト |
| Muted | CSS 変数 (`--muted`) | 補助テキスト |
| Destructive | CSS 変数 (`--destructive`) | 削除アクション |

### フォント

- **Inter** (Google Fonts) — `latin` サブセット
- 全体に `bg-slate-50 text-slate-900` を適用

### コンポーネント構成

shadcn/ui ベースのコンポーネント:
- `Button` (4バリアント: default, destructive, outline, ghost)
- `Card` (CardHeader, CardContent, CardTitle, CardDescription)
- `Input`, `Textarea`, `Label`
- `Tabs` (TabsList, TabsTrigger, TabsContent)
- `Badge` (5バリアント: default, secondary, destructive, outline, success)
- `ScrollArea`, `Separator`, `Skeleton`

カスタムコンポーネント:
- `LanguageToggle` — 44x44px、150ms フェードトランジション、国旗絵文字表示
- `StatCard` — ダッシュボード統計カード (アイコン、タイトル、値、説明)
- `ChatInterface` — SSE ストリーミング対応チャット画面
- `MessageBubble` — ユーザー/アシスタントのメッセージ表示 (引用付き)
- `SourceCitation` — ドキュメント引用カード (ドキュメント名、ページ番号、スニペット)
- `DocumentCard` — ドキュメント状態表示 (ステータスバッジ、チャンク数、ファイルサイズ)

---

## 8. プロジェクト構成（行数付き）

```
documind/
├── backend/                               # Python バックエンド (3,179行)
│   ├── app/
│   │   ├── main.py                        # FastAPI アプリ + CORS + シードエンドポイント (209行)
│   │   ├── config.py                      # Pydantic Settings 設定 (32行)
│   │   ├── database.py                    # 非同期 SQLAlchemy エンジン + セッション (28行)
│   │   ├── dependencies.py                # 認証依存注入 (30行)
│   │   ├── models/                        # SQLAlchemy ORM モデル
│   │   │   ├── base.py                    #   DeclarativeBase + TimestampMixin (24行)
│   │   │   ├── workspace.py               #   ワークスペース (22行)
│   │   │   ├── user.py                    #   ユーザー + ロール (25行)
│   │   │   ├── document.py                #   ドキュメントメタデータ + コンテンツハッシュ (38行)
│   │   │   ├── chunk.py                   #   テキストチャンク + vector(1536) (40行)
│   │   │   ├── conversation.py            #   会話セッション + 要約 (29行)
│   │   │   ├── message.py                 #   メッセージ + JSONB ソース (28行)
│   │   │   ├── usage_log.py               #   トークン消費ログ (19行)
│   │   │   └── analytics.py               #   日次集計メトリクス (27行)
│   │   ├── schemas/                       # Pydantic リクエスト/レスポンススキーマ
│   │   │   ├── auth.py                    #   ログイン/登録/トークン (33行)
│   │   │   ├── chat.py                    #   チャットリクエスト + SSE イベント (23行)
│   │   │   ├── document.py                #   ドキュメント一覧/レスポンス (29行)
│   │   │   ├── conversation.py            #   会話サマリー/詳細 (33行)
│   │   │   └── analytics.py               #   使用統計/上位クエリ (24行)
│   │   ├── routers/                       # API エンドポイントハンドラ
│   │   │   ├── auth.py                    #   ログイン/登録/検証 (34行)
│   │   │   ├── documents.py               #   アップロード/一覧/削除/処理 (143行)
│   │   │   ├── chat.py                    #   SSE ストリーミングチャット (41行)
│   │   │   ├── conversations.py           #   会話管理 (61行)
│   │   │   └── analytics.py               #   使用統計 + 上位クエリ (95行)
│   │   └── services/                      # ビジネスロジック層
│   │       ├── auth_service.py            #   ユーザー認証 + 登録 (71行)
│   │       ├── security_service.py        #   インジェクション検知 + サニタイズ (39行)
│   │       ├── embedding_service.py       #   デュアルモード埋め込み生成 (69行)
│   │       ├── ingest_service.py          #   ドキュメントパース + チャンキング (311行)
│   │       ├── search_service.py          #   ハイブリッド検索 (ベクトル+キーワード+RRF) (162行)
│   │       └── chat_service.py            #   RAG パイプライン + SSE ストリーミング (355行)
│   ├── alembic/                           # データベースマイグレーション
│   │   └── versions/
│   │       ├── 001_initial_schema.py      #   初期スキーマ (198行)
│   │       └── 002_add_workspace_id_to_chunks.py  # chunks に workspace_id 追加 (32行)
│   ├── seed/                              # デモデータシーダー
│   │   ├── seed.py                        #   シードスクリプト (297行)
│   │   └── data/                          #   サンプルドキュメント (Markdown)
│   │       ├── company-handbook.md
│   │       ├── product-roadmap.md
│   │       └── api-documentation.md
│   ├── tests/                             # pytest テスト (77テスト)
│   │   ├── test_search_service.py         #   RRF 統合テスト (104行)
│   │   ├── test_ingest_service.py         #   パース+チャンキングテスト (134行)
│   │   ├── test_security_service.py       #   インジェクション検知テスト (82行)
│   │   ├── test_embedding_service.py      #   擬似埋め込みテスト (58行)
│   │   ├── test_chat_service.py           #   デモモード応答テスト (59行)
│   │   └── test_auth_service.py           #   bcrypt ハッシュテスト (63行)
│   ├── requirements.txt                   # 本番依存 (18パッケージ)
│   ├── requirements-dev.txt               # 開発依存 (pytest 等)
│   └── render.yaml                        # Render.com デプロイ設定
│
├── frontend/                              # TypeScript フロントエンド (2,875行)
│   ├── src/
│   │   ├── app/                           # Next.js 15 App Router
│   │   │   ├── layout.tsx                 #   ルートレイアウト + NextIntlClientProvider (35行)
│   │   │   ├── page.tsx                   #   ルートページ (/ → /dashboard リダイレクト) (5行)
│   │   │   ├── globals.css                #   グローバルスタイル + CSS 変数
│   │   │   ├── (auth)/                    #   認証ページグループ
│   │   │   │   ├── layout.tsx             #     認証レイアウト + LanguageToggle (16行)
│   │   │   │   ├── login/page.tsx         #     ログインページ (5行)
│   │   │   │   └── register/page.tsx      #     登録ページ (5行)
│   │   │   ├── dashboard/                 #   認証保護ルート
│   │   │   │   ├── layout.tsx             #     Sidebar + Header レイアウト (18行)
│   │   │   │   ├── page.tsx               #     ダッシュボードホーム (57行)
│   │   │   │   ├── chat/page.tsx          #     チャットインターフェース (32行)
│   │   │   │   ├── chat/[id]/page.tsx     #     会話詳細 (24行)
│   │   │   │   ├── documents/page.tsx     #     ドキュメント管理 (24行)
│   │   │   │   ├── analytics/page.tsx     #     分析ダッシュボード (40行)
│   │   │   │   └── settings/page.tsx      #     設定画面 (105行)
│   │   │   └── api/auth/                  #   NextAuth API ルート
│   │   │       ├── [...nextauth]/route.ts #     NextAuth ハンドラ (2行)
│   │   │       └── token/route.ts         #     バックエンド用トークンエンドポイント (30行)
│   │   ├── components/
│   │   │   ├── language-toggle.tsx         #   言語切替ボタン (60行)
│   │   │   ├── auth/
│   │   │   │   ├── login-form.tsx         #     ログインフォーム (102行)
│   │   │   │   └── register-form.tsx      #     登録フォーム (154行)
│   │   │   ├── chat/
│   │   │   │   ├── chat-interface.tsx      #     メインチャット画面 (101行)
│   │   │   │   ├── chat-input.tsx         #     メッセージ入力 (85行)
│   │   │   │   ├── conversation-list.tsx  #     会話リスト (68行)
│   │   │   │   ├── message-bubble.tsx     #     メッセージバブル (51行)
│   │   │   │   ├── source-citation.tsx    #     引用カード (46行)
│   │   │   │   ├── empty-state.tsx        #     空状態 + サンプル質問 (46行)
│   │   │   │   └── thinking-indicator.tsx #     思考中インジケーター (27行)
│   │   │   ├── documents/
│   │   │   │   ├── document-card.tsx      #     ドキュメントカード (82行)
│   │   │   │   ├── document-list.tsx      #     ドキュメント一覧 (46行)
│   │   │   │   └── upload-dialog.tsx      #     アップロードダイアログ (63行)
│   │   │   ├── analytics/
│   │   │   │   ├── token-usage-chart.tsx  #     トークン使用量チャート (81行)
│   │   │   │   ├── query-count-chart.tsx  #     クエリ数チャート (66行)
│   │   │   │   ├── latency-chart.tsx      #     レイテンシチャート (74行)
│   │   │   │   └── top-queries-list.tsx   #     上位クエリリスト (48行)
│   │   │   ├── dashboard/
│   │   │   │   ├── sidebar.tsx            #     サイドバーナビゲーション (100行)
│   │   │   │   ├── header.tsx             #     ヘッダー + LanguageToggle (29行)
│   │   │   │   └── stat-card.tsx          #     統計カード (32行)
│   │   │   └── ui/                        #   shadcn/ui プリミティブ (10コンポーネント)
│   │   ├── hooks/
│   │   │   ├── use-chat.ts                #   チャットステート管理 (78行)
│   │   │   ├── use-sse.ts                 #   SSE クライアント (84行)
│   │   │   ├── use-documents.ts           #   ドキュメント CRUD (45行)
│   │   │   ├── use-conversations.ts       #   会話取得 (22行)
│   │   │   └── use-analytics.ts           #   分析データ取得 (23行)
│   │   ├── i18n/
│   │   │   ├── config.ts                  #   ロケール定義 (ja, en) (3行)
│   │   │   └── request.ts                 #   サーバーサイドロケール解決 (17行)
│   │   ├── messages/
│   │   │   ├── ja.json                    #   日本語翻訳 (132行)
│   │   │   └── en.json                    #   英語翻訳 (132行)
│   │   ├── lib/
│   │   │   ├── api-client.ts              #   Fetch ラッパー + 認証ヘッダー (119行)
│   │   │   ├── auth.ts                    #   NextAuth 設定 + JWT コールバック (83行)
│   │   │   ├── auth.config.ts             #   ルート保護設定 (19行)
│   │   │   └── utils.ts                   #   ユーティリティ関数 (95行)
│   │   ├── providers/
│   │   │   ├── auth-provider.tsx           #   SessionProvider ラッパー (7行)
│   │   │   └── query-provider.tsx          #   QueryClient ラッパー (22行)
│   │   └── types/
│   │       ├── chat.ts                    #   チャット型定義 (24行)
│   │       ├── document.ts                #   ドキュメント型定義 (22行)
│   │       ├── conversation.ts            #   会話型定義 (22行)
│   │       ├── analytics.ts               #   分析型定義 (22行)
│   │       └── next-auth.d.ts             #   NextAuth 型拡張 (57行)
│   ├── middleware.ts                      #   NextAuth ルート保護ミドルウェア (8行)
│   ├── next.config.ts                     #   Next.js + next-intl プラグイン設定 (10行)
│   ├── tailwind.config.ts                 #   Tailwind CSS カスタム設定 (71行)
│   └── package.json                       #   依存関係 (49行)
│
├── .github/workflows/ci.yml              # GitHub Actions CI パイプライン (60行)
├── README.md                              # プロジェクト概要 (407行)
└── LICENSE                                # MIT ライセンス
```

**コード行数合計**: Python 3,179行 + TypeScript 2,875行 = 6,054行

---

## 9. セットアップ手順

### 前提条件

- Python 3.12 以上
- Node.js 20 以上
- PostgreSQL 17 (`pgvector` + `pg_trgm` 拡張が必要)

### バックエンド

```bash
cd backend

# 仮想環境の作成と有効化
python -m venv .venv
source .venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .env を編集:
#   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/documind  (必須)
#   NEXTAUTH_SECRET=your-secret                                          (必須)
#   OPENAI_API_KEY=sk-...                                               (任意 — 省略でデモモード)

# データベースマイグレーション
alembic upgrade head

# デモデータ投入 (API キー不要)
python -m seed.seed
# OpenAI 埋め込みを使う場合: python -m seed.seed --use-openai

# サーバー起動
uvicorn app.main:app --reload
# API: http://localhost:8000
```

### フロントエンド

```bash
cd frontend

# 依存パッケージのインストール
npm install

# 環境変数の設定
cp .env.local.example .env.local
# .env.local を編集:
#   NEXTAUTH_SECRET=your-secret            (バックエンドと同じ値)
#   NEXTAUTH_URL=http://localhost:3000
#   NEXT_PUBLIC_API_URL=http://localhost:8000

# 開発サーバー起動
npm run dev
# アプリ: http://localhost:3000
```

### デモ認証情報

- メールアドレス: `admin@documind.dev`
- パスワード: `demo1234`

### テスト実行

```bash
cd backend
pip install -r requirements-dev.txt
pytest
# 77 テスト — 6 モジュール
```

### 環境変数一覧

| 変数名 | 必須 | 説明 | デフォルト |
|---|---|---|---|
| `DATABASE_URL` | はい | PostgreSQL 接続文字列 (asyncpg) | `postgresql+asyncpg://user:password@localhost:5432/documind` |
| `NEXTAUTH_SECRET` | はい | JWT 署名シークレット | (起動時にランダム生成、本番では必ず設定) |
| `OPENAI_API_KEY` | いいえ | OpenAI API キー (省略でデモモード) | `None` |
| `CORS_ORIGINS` | いいえ | 許可オリジン (カンマ区切り) | `http://localhost:3000` |
| `EMBEDDING_MODEL` | いいえ | 埋め込みモデル | `text-embedding-3-small` |
| `EMBEDDING_DIMENSIONS` | いいえ | 埋め込みベクトル次元数 | `1536` |
| `CHAT_MODEL` | いいえ | チャットモデル | `gpt-4o-mini` |
| `CHUNK_SIZE` | いいえ | チャンクサイズ (トークン数) | `500` |
| `CHUNK_OVERLAP` | いいえ | チャンクオーバーラップ (トークン数) | `50` |
| `RRF_K` | いいえ | RRF パラメータ | `60` |
| `CONVERSATION_MEMORY_LIMIT` | いいえ | 会話メモリ保持数 | `5` |
| `MAX_UPLOAD_SIZE_MB` | いいえ | 最大アップロードサイズ | `20` |
| `NEXT_PUBLIC_API_URL` | はい | バックエンド API URL | `http://localhost:8000` |
| `NEXTAUTH_URL` | はい | フロントエンド URL | `http://localhost:3000` |

---

## 10. 設計判断の根拠

| 設計判断 | 根拠 |
|---|---|
| **モノレポ構成** | デプロイ・バージョニング・クロススタック リファクタリングの簡素化 |
| **FastAPI + Next.js 分離** | Python (ML/バックエンド) + TypeScript (フロントエンド) のポリグロットアーキテクチャを実証 |
| **ベクトル検索のみでなくハイブリッド検索** | 本番 RAG システムには完全一致のキーワードフォールバックが必要。セマンティック検索だけでは不十分 |
| **線形結合でなく RRF** | ランクベースの統合はスコア分布の違いに頑健。チューニングパラメータが k のみでシンプル |
| **デュアルモード設計** | $0 でポートフォリオデモを動作させつつ、本番コードパスを証明 |
| **WebSocket でなく SSE** | 単方向ストリーミングには SSE で十分。プロトコルがシンプルで障害モードが少ない |
| **セマンティックチャンキング** | 見出し認識型分割は固定サイズ分割よりドキュメント構造を保持 |
| **500トークンチャンク + 50トークンオーバーラップ** | 検索精度のための粒度とコンテキスト断片化のバランス |
| **asyncio.gather による並行検索** | ベクトル検索とキーワード検索の逐次実行ボトルネックを排除 |
| **ワークスペーススコープのクエリ** | アプリケーション層だけでなくクエリ層でマルチテナント分離を実現 |
| **パスベースでなく Cookie ベースの i18n** | 既存 URL 構造を維持。認証済み SaaS アプリではパスベースロケールの SEO メリットは無視できる |
| **IVFFlat インデックス (lists=100)** | データ投入後に作成。HNSW より構築が速く、中規模データセットに適切 |
| **50分トークンキャッシュ** | 1時間有効トークンに対して冗長な `/api/auth/token` 呼び出しを排除 |
| **TanStack Query (staleTime=60秒)** | サーバーステートのキャッシュと自動無効化。手動ステート管理の複雑さを排除 |

---

## 11. ランニングコスト

### デモモード ($0 構成)

| サービス | プラン | コスト |
|---|---|---|
| Vercel | Hobby (無料) | $0 |
| Render | Free | $0 |
| Neon | Free Tier (0.5 GiB ストレージ) | $0 |
| OpenAI | 不使用 | $0 |
| **合計** | | **$0/月** |

### ライブモード (OpenAI 使用時)

| サービス | 想定コスト |
|---|---|
| Vercel | $0 (Hobby) 〜 $20/月 (Pro) |
| Render | $0 (Free) 〜 $7/月 (Starter) |
| Neon | $0 (Free) 〜 $19/月 (Launch) |
| OpenAI `text-embedding-3-small` | 〜$0.02 / 100万トークン |
| OpenAI `gpt-4o-mini` | 〜$0.15 / 100万入力トークン, $0.60 / 100万出力トークン |
| **合計** | **$0 〜 $50/月** (使用量依存) |

---

## 12. 作者

**[@mer-prog](https://github.com/mer-prog)**

---

## ライセンス

MIT
