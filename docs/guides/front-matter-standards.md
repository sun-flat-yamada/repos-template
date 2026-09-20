---
title: "Markdown Front-Matter Standards & Best Practices"
description: "Guidelines and schema standards for YAML front-matter in markdown documentation, optimized for human readability, static site generators, and AI/RAG agent systems (2026 Edition)."
category: "guide"
type: "specification"
status: "active"
date: 2026-09-21
updated: 2026-09-21
lang: "ja"
tags:
  - "documentation"
  - "front-matter"
  - "markdown"
  - "metadata"
  - "standards"
  - "ai-readiness"
---

# Markdown Front-Matter 標準ガイドライン（2026年版）

本ドキュメントは、本リポジトリおよび派生プロジェクトにおける Markdown ファイルの **YAML Front-Matter（フロントマター）** の記述規格、スキーマ、およびベストプラクティスを定めたナレッジベースです。

---

## 1. 背景と目的

2026年現在、Markdown は人間の開発者が読むドキュメントにとどまらず、**LLM（大規模言語モデル）や自律型 AI エージェント、セマンティック検索（RAG: Retrieval-Augmented Generation）システムがコードベースを理解・探索するための主要なデータソース**となっています。

高品質な Front-Matter を付与することで、以下の恩恵が得られます：

1. **AI / RAG の「身分証明書（Identity Card）」**:
   - エージェントがファイル全文をスキャン・トークン消費することなく、フロントマターの `title` と高密度な `description` を参照することで、目的に合致するファイルを迅速かつ正確に選定・引用可能になります。
2. **静的サイトジェネレータ（SSG）との完全な親和性**:
   - VitePress, Astro, Docusaurus, Nextra, MkDocs などの主要 SSG ツールで自動的にパンくずリスト、サイドバー、SEO メタタグ（OGP）が生成されます。
3. **Docs-as-Code の品質ガバナンス**:
   - 最終更新日（`updated`）、文書ステータス（`status`）、担当言語（`lang`）などを明示することで、ドキュメントの鮮度と陳腐化を機械的に検知可能にします。

---

## 2. 構文仕様と技術的衛生（Technical Hygiene）

Front-Matter は Markdown ファイルの最上部に配置し、YAML 形式で記述します。

```yaml
---
title: "ドキュメントのタイトル"
description: "このドキュメントの目的と役割を明確に表す1〜3文の要約。"
category: "guide"
type: "reference"
status: "active"
date: 2026-09-21
updated: 2026-09-21
lang: "ja"
tags:
  - "keyword1"
  - "keyword2"
---
```

### 技術的衛生ルール
- **デリミタ**: ファイルの 1 行目から `---`（トリプルダッシュ）で開始し、`---` で閉じます。
- **文字列のエスケープ**: コロン（`:`）、角括弧（`[` `]`）、波括弧（`{` `}`）などの記号を含む文字列は、パースエラーを防ぐため**必ずダブルクォート（`"`）で囲みます**。
- **日付フォーマット**: 必ず **ISO 8601 形式（`YYYY-MM-DD`）** を使用します。
- **配列リスト**: `tags` や複数値属性は、インライン配列（`[tag1, tag2]`）または YAML リスト（`- item`）として記述します。
- **関心の分離**: レイアウト指定や独自の長文コンテンツを過度にフロントマターへ押し込まず、文書の「メタデータ（識別・分類・状態）」に専念させます。

---

## 3. 推奨スキーマ定義

### 3.1 共通コアフィールド（全ドキュメント推奨）

| フィールド | 型 | 必須 | 説明 | 記述例 |
| :--- | :--- | :---: | :--- | :--- |
| `title` | string | **必須** | 文書の固有かつ明確なタイトル。 | `"Getting Started Guide"` |
| `description` | string | **必須** | 文書の目的・対象を述べた 1〜3 文の要約。AI 引用の重要情報源。 | `"Step-by-step installation and initial configuration guide for developers."` |
| `category` | string | 任意 | 大分類（`guide`, `architecture`, `adr`, `governance`, `meta`, `rules` など）。 | `"architecture"` |
| `type` | string | 任意 | 文書タイプ（`overview`, `tutorial`, `reference`, `decision-record` など）。 | `"overview"` |
| `status` | string | 任意 | 文書のライフサイクル状態（`active`, `draft`, `proposed`, `accepted`, `deprecated`）。 | `"active"` |
| `date` | date | 任意 | 初回作成日（`YYYY-MM-DD`）。 | `2026-09-21` |
| `updated` | date | 任意 | 最終更新日（`YYYY-MM-DD`）。 | `2026-09-21` |
| `lang` | string | 任意 | 言語コード（`en`, `ja` など）。多言語併用リポジトリで必須。 | `"en"` |
| `tags` | array | 任意 | 検索・インデックス用タグのリスト。 | `["architecture", "design-patterns"]` |

### 3.2 AI エージェント向けスコープ・ファイルパターン制御フィールド（2026年標準）

2026年の最先端エージェント環境（Antigravity, Cursor MDC, Claude Code, GitHub Copilot）では、**プロンプトの過大化（Prompt Bloating / Dilution）を防ぎ、関連するファイルを操作している時のみ必要な指示を動的注入する「Scoped Rules」** が標準化されています。

| フィールド | 型 | 任意 | 説明 | 記述例 |
| :--- | :--- | :---: | :--- | :--- |
| `globs` | array | 任意 | ルールやスキルが適用されるファイルパスの glob パターンリスト。 | `["**/*.py", "**/pyproject.toml"]` |
| `alwaysApply` | boolean | 任意 | ファイルパスに関わらず常時適用するかどうか（デフォルト: `false`）。真に全域で強制すべき規約のみ `true` に設定。 | `true` または `false` |

---

## 4. 文書種別ごとのベストプラクティス

### 4.1 プロジェクト管理・ガバナンス文書（Root Docs）
対象: `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md` 等
- **観点**: プロジェクト全体の窓口となるため、リポジトリの目的、ライセンス、セキュリティポリシー、コントリビューション基準を明確に表現する。
- **例**:
  ```yaml
  ---
  title: "Security Policy"
  description: "Vulnerability reporting guidelines, disclosure policies, and supported versions for the project."
  category: "governance"
  type: "policy"
  status: "active"
  date: 2026-09-21
  updated: 2026-09-21
  lang: "en"
  tags:
    - "security"
    - "vulnerability"
    - "policy"
  ---
  ```

### 4.2 技術解説・設計文書（Architecture & Guides）
対象: `docs/architecture/*.md`, `docs/guides/*.md`
- **観点**: システム構造、依存関係、セットアップ手順を対象者（オーディエンス）に合わせて記述。
- **例**:
  ```yaml
  ---
  title: "Architecture Overview"
  description: "Architectural philosophy, layered model, and multi-agent ecosystem design for the repository template."
  category: "architecture"
  type: "overview"
  status: "active"
  date: 2026-09-21
  updated: 2026-09-21
  lang: "en"
  tags:
    - "architecture"
    - "clean-architecture"
    - "agents"
  ---
  ```

### 4.3 意思決定記録（Architectural Decision Records: ADR）
対象: `docs/adr/*.md`
- **観点**: ADR 番号、ステータス（`proposed`, `accepted`, `superseded`）、決定日をフロントマターで管理し、一覧自動生成や意思決定追跡を容易にする。
- **例**:
  ```yaml
  ---
  title: "ADR-0000: Use Markdown Architectural Decision Records"
  description: "Decision to adopt Michael Nygard-style Markdown Architectural Decision Records (ADRs) within docs/adr/."
  category: "adr"
  type: "decision-record"
  status: "accepted"
  date: 2026-09-20
  updated: 2026-09-20
  lang: "en"
  tags:
    - "adr"
    - "architecture"
    - "governance"
  ---
  ```

### 4.4 AI エージェント定義・ルール文書（Agent Rules & Profiles）
対象: `.agents/rules/*.md`, `.agents/agents/*.agent.md`, `.agents/agents/languages/*.md`
- **観点**: 各エージェントやルールが「どのような役割・責任・適用範囲」を持つのかを構造化メタデータとして明示し、`globs` や `alwaysApply` を用いて適切なコンテキストでのみ自動読み込みを制御する。
- **グローバルルールの例**（常時適用）:
  ```yaml
  ---
  title: "General Coding Rules"
  description: "Universal coding conventions, defensive engineering practices, error management, and code hygiene."
  category: "rules"
  type: "specification"
  status: "active"
  alwaysApply: true
  globs:
    - "**/*"
  tags:
    - "rules"
    - "coding"
    - "hygiene"
  ---
  ```
- **言語固有ルールの例**（Python のみ適用）:
  ```yaml
  ---
  title: "Language Coding Rules: Python"
  description: "Language-specific style guidelines, static analysis requirements, and best practices for Python."
  category: "rules"
  type: "specification"
  status: "active"
  alwaysApply: false
  globs:
    - "**/*.py"
    - "**/pyproject.toml"
    - "**/requirements*.txt"
  tags:
    - "rules"
    - "language-rules"
    - "python"
  ---
  ```

### 4.5 Agent Skills 定義文書（SKILL.md）
対象: `.agents/skills/*/SKILL.md`
- **観点**: エージェントランタイム必須の `name` と `description` をトップレベルの先頭に配置し、下流のディスカバリ互換性を100%保証した上で、タグ分類用 `tags` や適用ファイル制御用 `globs` などの拡張メタデータを付与する。
- **例**:
  ```yaml
  ---
  name: "code-review-python"
  description: "Audits Python source code diffs against language-specific idioms, memory safety, static analysis, and code-review-profile-python.md."
  category: "skill"
  type: "code-review"
  status: "active"
  alwaysApply: false
  globs:
    - "**/*.py"
    - "**/pyproject.toml"
  tags:
    - "code-review"
    - "python"
    - "quality-gate"
  ---
  ```

---

## 5. よくあるアンチパターン（避けるべき記述）

1. ❌ **低情報密度の `description`**:
   - 悪い例: `description: "This document describes the getting started guide."`
   - 良い例: `description: "Step-by-step instructions for repository initialization, prerequisite installation, and local development workflows."`
2. ❌ **コロンや特殊文字のクォート忘れ**:
   - 悪い例: `title: ADR-0001: Adopt TypeScript 5.8` （コロンにより YAML パーサーが不正なマッピングと誤認識）
   - 良い例: `title: "ADR-0001: Adopt TypeScript 5.8"`
3. ❌ **非標準の日付表記**:
   - 悪い例: `date: 09/21/2026` または `date: 2026年9月21日`
   - 良い例: `date: 2026-09-21`
4. ❌ **本文（# H1）と Front-Matter（title）の完全な乖離**:
   - フロントマターの `title` と 本文の最上位見出しは、読者と検索システム双方の混乱を避けるため整合性を保つ必要があります。
