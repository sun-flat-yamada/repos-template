---
title: "Language Policy Guide - {PROJECT_NAME}"
description: "出力言語（応答・PR・コミット・コード）の現行方針、コミットを日本語に変更する場合の修正対象、ツール別の設定箇所、矛盾回避の注意点をまとめたガイド。"
category: "guide"
type: "policy"
status: "active"
date: 2026-10-03
updated: 2026-10-03
lang: "ja"
tags:
  - "language"
  - "commit"
  - "pull-request"
  - "ai"
  - "governance"
---

# 言語ポリシーガイド - {PROJECT_NAME}

本ガイドは、人間の貢献者と AI エージェントが「何を何語で書くか」を統一するための補足資料です。正本は [`.agents/rules/git-rules-commit.md`](../../.agents/rules/git-rules-commit.md) の §3 であり、本ガイドと矛盾する場合は正本を優先します。

---

## 1. 現行方針

| 対象 | 言語 | 備考 |
| :--- | :--- | :--- |
| AI エージェントからユーザーへの応答 | 日本語 | 技術用語・エラーメッセージは原文（英語）のまま |
| PR タイトル | 英語の type プレフィックス + 日本語の説明 | 例: `feat(auth): ログイン失敗時のリトライを追加` |
| PR 説明（`.github/PULL_REQUEST_TEMPLATE.md` の記入内容を含む） | 日本語 | 技術用語・識別子・エラーメッセージは英語のまま |
| コミットメッセージ | 英語（Conventional Commits） | `.githooks/commit-msg` が型プレフィックスを検証 |
| コード・識別子・コメント | 英語 | 各言語ルール（`.agents/rules/languages/`）に従う |

PR タイトルの検証（`.github/workflows/pr-hygiene.yml`）が見るのは type プレフィックスのみで、コロン以降の言語は検証しません。`.githooks/commit-msg` も 1 行目の `<type>(<scope>): <subject>` 形式のみを検証するため、現状でも技術的には日本語のコミットメッセージを書けます。

---

## 2. コミットを日本語にする場合に同時に直すファイル

方針を変更する際は、次のファイルを **同一 PR で** 更新してください。1 つでも漏れると、ツールごとに異なる言語で出力される原因になります。

### 2.1 正本

- `.agents/rules/git-rules-commit.md`（§3 Language of Commits and Pull Requests）

### 2.2 エージェント向け指示

- `CLAUDE.md`（Directives の `Output Language`）
- `.cursorrules`
- `.github/copilot-instructions.md`
- `.gemini/GEMINI.md`
- `.agents/skills/git-workflow/SKILL.md`（コミット書式の説明）
- `.agents/workflows/workflow-spec-to-code.md`（Commit 手順の記述）

### 2.3 人間向けドキュメント・テンプレート

- `CONTRIBUTING.md`（Commit Message Conventions）
- `docs/guides/getting-started.md`（コミット手順）
- `.github/PULL_REQUEST_TEMPLATE.md`（コミット規約のチェック項目）
- `README.md` / `README.ja.md`（言語に関する記述がある場合）
- 本ガイド（§1 の表）

### 2.4 検証・自動化

- `.githooks/commit-msg`: 現行の正規表現は subject に任意の文字列（`.+`）を許可しており、日本語でも通過します。文字種を制限する変更が必要な場合のみ修正します。
- `.github/workflows/pr-hygiene.yml`: type のみ検証。通常は変更不要です。
- `.claude/hooks/permission-guard.py` とそのテスト（`tests/test-permission-guard.py`）: 言語には依存しませんが、コミットメッセージ内のコマンド文字列を検査する場合があるため、方針変更後にテストを実行してください。

### 2.5 変更時の確認コマンド

```bash
python scripts/validate-frontmatter.py
python scripts/validate-filenames.py
python tests/test-permission-guard.py
```

---

## 3. ツール別の設定箇所

| ツール | 設定ファイル | 該当箇所 |
| :--- | :--- | :--- |
| Claude Code | `CLAUDE.md` | `Directives` の `Output Language` |
| Claude Code（個人設定） | `~/.claude/CLAUDE.md` | 全プロジェクト共通の `Language policy`（リポジトリ側と矛盾させない） |
| Cursor | `.cursorrules` | 末尾の `Output Language` |
| GitHub Copilot | `.github/copilot-instructions.md` | `Core Directives` の `Output Language` |
| Gemini CLI / Antigravity | `.gemini/GEMINI.md` | 末尾の `Output Language` |
| Codex CLI など | `AGENTS.md`（存在する場合） | 同様の `Output Language` 行を追加 |

各ファイルの `Output Language` 行は同一の文言に揃え、詳細は `.agents/rules/git-rules-commit.md` を参照する形にしています。

---

## 4. 矛盾回避の注意

1. **正本は 1 か所**: 言語方針の詳細は `git-rules-commit.md` にのみ記述し、他のファイルは要約と参照に留めます。
2. **個人設定とリポジトリ設定の衝突**: 個人のグローバル設定（例: `~/.claude/CLAUDE.md`）が「コミットは英語」等を定めている場合、リポジトリ側が異なる方針を取ると指示が衝突します。リポジトリ方針が優先される運用か、個人設定が「リポジトリの規約に従う」となっているかを確認してください。
3. **PR タイトルの type は英語固定**: `pr-hygiene` が検証するため、`feat` 等の type は翻訳しません。
4. **コード内コメントは英語のまま**: 日本語のドキュメント（`lang: "ja"` のガイド等）とコード内コメントの言語は別の規則です。
5. **技術用語・エラーメッセージは原文**: 翻訳すると検索性が落ちるため、識別子・コマンド・エラー文言は英語のまま残します。
6. **更新日の更新**: front matter を持つファイル（`.github/copilot-instructions.md`、`.gemini/GEMINI.md` など）を変更したら `updated` を更新します（`docs/guides/front-matter-standards.md` 参照）。
