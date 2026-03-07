
# Spec Management Rules

## Spec Files

- JP版: `README_{project}_{system-type}_JP.md` — 日本語仕様書
- EN版: `README_{project}_{system-type}_EN.md` — 英語仕様書
- 両ファイルは常にペアで管理し、内容を同期させる

## Format Standards

- セクション番号は付けない（`## Skills Demonstrated` であり `## 1. Skills Demonstrated` ではない）
- 見出しレベル: タイトル `#`、セクション `##`、サブセクション `###`
- コードブロックには言語指定を付ける
- Architecture Overview には ASCII 図を必ず含める
- Skills Demonstrated の項目名は標準リストから選択する:
  - Full-Stack Development / Frontend Development / Backend Development
  - API Design & Integration / Database Design & Management
  - Authentication & Authorization / AI/LLM Integration
  - Real-Time Communication / Cloud Architecture & Deployment
  - DevOps & CI/CD / Security Implementation / Payment Integration
  - Performance Optimization / Testing & Quality Assurance
  - UI/UX Design / Mobile Development / Data Visualization
  - System Architecture / Microservices Architecture / Event-Driven Architecture

## Required Sections (in order)

- Skills Demonstrated
- Tech Stack
- Architecture Overview (ASCII diagram required)
- Key Features
- Project Structure
- Setup
- Design Decisions
- Running Costs
- Author (@mer-prog)

## Optional Sections (add when applicable)

- API Endpoints / Database Schema / Payment Flow
- AI/ML Pipeline / Security / WebSocket Events
- Environment Variables / Deployment / Testing

## Language Rules

- JP版: 日本語で統一（技術用語のみ英語可）
- EN版: 英語で統一（日本語の混入禁止）

## Git Rules

- 新規作成: `docs: add {project-name} JP/EN spec`
- 更新: `docs: update {project-name} JP/EN spec`
- JP版とEN版は1コミットにまとめる
- 仕様書の変更は必ずコードベースの現状を反映させる（フルリジェネレート方式）
- Author セクションには必ず `@mer-prog` を記載する
