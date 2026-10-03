---
title: "Fork Operations Guide"
description: "fork（または mirror 複製）先でテンプレートを運用するためのガイド。dual-branch 運用、upstream 同期手順、権限ポリシーとの対応、CI の扱い、制限環境でのセットアップをまとめる。"
category: "guide"
type: "operations"
status: "active"
date: 2026-10-03
updated: 2026-10-03
lang: "ja"
tags:
  - "fork"
  - "upstream-sync"
  - "git"
  - "ci"
  - "governance"
---

# fork 運用ガイド

本ガイドは、本テンプレートを fork した先で upstream の更新を取り込みながら運用する方法を説明します。決定の経緯は [ADR-0003](../adr/0003-adopt-dual-branch-fork-operation.md)、エージェント向け手順は [`fork-sync-ops`](../../.agents/skills/fork-sync-ops/SKILL.md) を参照してください。

> **注**: [`upstream-sync-guide.md`](upstream-sync-guide.md) は、本テンプレートが参照元（`github-copilot-dashboard`）の `change-dev` 系ファイルを追う仕組み（テンプレート保守者向け、`scripts/sync-upstream.py`）です。本ガイドは、fork 先が**本テンプレート**を追う運用（`main` のミラーと `fork/custom`、`scripts/verify-fork-health.py`）で、追跡対象も手順も別です。二重管理にはなりません。

---

## 1. カスタマイズ方法の使い分け

| 方法 | 対象 | upstream との衝突 |
| :--- | :--- | :--- |
| **ゼロコード** | `template.config.yaml`、リポジトリの Variables / Secrets | ほぼなし。まずこちらを検討する |
| **コードレベル** | ファイルの追加・変更 | `fork/custom` ブランチに集約し、差分を小さく保つ |

## 2. ブランチ構成（dual-branch）

| ブランチ | 役割 | 更新できる主体 |
| :--- | :--- | :--- |
| `main` | upstream の純粋なミラー（fast-forward のみ） | **人間のみ**（N-08: 保護ブランチ） |
| `fork/custom` | fork の既定ブランチ。fork 固有の変更をすべて載せる | エージェントまたは人間 |

## 3. 初期セットアップ

```bash
git remote add upstream <テンプレートの URL>   # C-HITL-01: 人間の承認が必要
git fetch upstream
git switch -c fork/custom main
python scripts/apply-template.py                # fork 固有の値を適用（fork/custom のみ）
python scripts/verify-fork-health.py
```

その後、GitHub の設定で `fork/custom` を既定ブランチにします。

## 4. 同期手順

1. `python scripts/verify-fork-health.py`（事前確認）
2. `git fetch upstream`
3. `git switch main && git merge --ff-only upstream/main`（失敗したら中止して報告。`reset --hard` はしない）
4. `git switch fork/custom && git merge main`（コンフリクトは fork 固有を残し、それ以外は upstream を採用）
5. 品質ゲート: `python scripts/validate-filenames.py` / `python scripts/validate-frontmatter.py` / `python tests/test-validate-frontmatter.py -v` / `python tests/test-permission-guard.py -v` / `python tests/test-verify-fork-health.py -v`
6. `git push -u origin fork/custom`（C-HITL-01）
7. **人間が** `git push origin main` を実行（N-08。エージェントは実行しない）

## 5. 権限ポリシーとの対応

| 操作 | ルール |
| :--- | :--- |
| `git remote add`、`git fetch upstream`、`git push origin fork/custom` | C-HITL-01（都度承認） |
| `git merge --ff-only` / `git merge main`（ローカル） | C-SBX-03 |
| `git push origin main` | N-08（人間のみ） |
| `git reset --hard`、force push | 手順で使用しない（C-HITL-03 / N-05） |
| `gh workflow disable/enable` | C-HITL-01（人間の承認の下で実施） |

## 6. CI の扱い

- `ci.yml`・`secret-scan.yml`・`template-check.yml` は `fork/custom` への push / PR でも動作します。
- `template-check.yml` はプレースホルダ未解決を警告にとどめます（失敗にはしません）。fork 側で `apply-template.py` 実行済みなら警告は出ません。
- `release.yml` はタグ `v*.*.*` で動作します。fork で不要な場合は、人間の承認の下で Actions を無効化します。
- `pr-hygiene.yml` は PR タイトルの type 接頭辞のみ検証します。

## 7. 健全性の検証

`python scripts/verify-fork-health.py [--strict]` は読み取り専用で、次を確認します。`upstream` リモート、現在ブランチ（`main`・detached は不可）、作業ツリーの清浄さ、`main` が `upstream/main` と一致または fast-forward 可能か、プレースホルダ残存。ネットワークには接続しないため、事前に `git fetch upstream` を実行してください。

## 8. upstream への貢献

`upstream/main` から topic ブランチを作り、汎用的なコミットだけを cherry-pick します。`git diff upstream/main --stat` で fork 固有の識別情報・秘密情報・固有パスが含まれていないことを確認してから PR を作成します。

## 9. 制限環境（社内ネットワーク・Enterprise）

- upstream へ直接到達できない場合は、承認済みの手段（社内ミラー、bundle ファイル）で `upstream` リモートまたは `git fetch <bundle>` を用意します。取得元は信頼できるものに限ります。
- パッケージレジストリや外部ホストへの通信は C-NET の許可リスト内に収めます。それ以外は C-HITL です。
- 資格情報はリポジトリに含めず、環境変数または Secrets で渡します（[セキュリティルール](../../.agents/rules/security-rules-general.md)）。
