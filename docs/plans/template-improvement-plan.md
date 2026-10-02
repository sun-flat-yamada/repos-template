---
title: "Repository Template Review & Improvement Plan"
description: "repos-template 全体（テンプレートエンジン、AIツール連携、権限ポリシーとガードフック、CI/CD、Gitフック、.gitignore、ドキュメント、.agents 資産、命名規則）のレビュー結果と、優先度付きの段階的改善計画。"
category: "plan"
type: "review"
status: "active"
date: 2026-10-01
updated: 2026-10-02
lang: "ja"
tags:
  - "review"
  - "improvement-plan"
  - "template"
  - "ai-sdlc"
  - "governance"
---

# リポジトリテンプレート総合レビューと改善計画

> - 対象: `main` @ `55cbb47`（追跡ファイル 115 件、約 8,800 行）
> - レビュー日: 2026-10-01
> - 2026-10-01 更新: §5 の判断が確定し、ロードマップに反映しました（Copier への移行を Phase 1 に前倒しするなど）。
> - 本書はテンプレート保守者向けの作業計画です。全項目の完了後は削除またはアーカイブし、派生プロジェクトには持ち込みません（A-5 参照）。

---

## 1. エグゼクティブサマリー

権限ポリシー（A/C/N の三層とルール ID）と、それを実装する `permission-guard.py` はよく設計されており、テストも揃っています。一方で、**テンプレートから生成した派生プロジェクトで壊れる箇所**、**`.agents/` ハブと各 AI ツールの実際の読み込み先がつながっていない点**、**ドキュメントの記述と実装の食い違い**が目立ちます。また、テンプレート自身を守る品質ゲート（スクリプトのテスト、適用 E2E、ワークフロー権限）が不足しています。

指摘は合計 48 件です（🔴 3 / 🟠 16 / 🟡 23 / ⚪ 6）。

### 維持すべき強み

- 三層の権限ポリシー、安定したルール ID、ADR-0001 による意思決定の記録。
- `permission-guard.py` は `bash -c`、`env`、`xargs`、heredoc、`git -C` などの表記ゆれを正規化します。21 件のテストに加え、境界ケース 30 件を試しても、force push、`curl | sh`、秘密ファイルの読み取り、`npm publish` などの N ティアは確実に拒否されました。
- `.claude/settings.json` のキーを公式ドキュメント（code.claude.com）と照合し、すべて有効であることを確認しました。対象は `sandbox.credentials`、`sandbox.filesystem.denyRead`、パラメータ一致ルール `Bash(dangerouslyDisableSandbox:true)`、gitignore 否定パターンなどです。
- 命名規則がバリデータ、pre-commit、CI の三か所で機械的に検証されています。
- 9 言語・5 ツールを網羅しています。

### 最優先の課題（上位 5 件）

1. **派生プロジェクトで壊れる（F-1、A-4）**: `.gitignore` が Dart の `lib/`・`bin/`、Go の `pkg/`、`Makefile`、ロックファイルを無視するため、対応言語の一部ではソースコードをコミットできません。さらに、プレースホルダー検査が大文字定数の補間を誤検知し、pre-commit がコミットを止めます。
2. **AI 連携が実際にはつながっていない（B-1、B-2）**: `.agents/skills/` は Claude Code の探索対象外で、`.gitignore` は `.claude/skills|commands|agents` を除外しています。ルートの `AGENTS.md` もありません。CLAUDE.md に書かれたスラッシュコマンドには実体がありません。
3. **設定ファイルの不整合（A-1、A-3）**: JSON 版の設定を使うと CODEOWNERS が `* @@sun-flat-yamada (Youhei Yamada)` という無効な行になります。YAML 版を使うと、SECURITY.md の脆弱性報告先が `example.com` のアドレスになります。
4. **ドキュメントと実装の乖離（G-1、G-2）**: Makefile がないのに `make check` を案内しています。「ブランチ保護の検証」「自動セマンティックリリース」も未実装です。PR テンプレートのフロントマターは全 PR の本文に混入します。
5. **テンプレート自身の品質ゲートが薄い（D-1〜D-4）**: スクリプトにテスト・lint・型検査がなく、適用 E2E テストもありません。ワークフローには `permissions:` がなく、Actions は SHA で固定されていません。

---

## 2. レビュー方法と検証ログ

追跡ファイルをすべて読んだうえで、次の検証を実行しました。

| 検証 | 結果 |
| :--- | :--- |
| `python3 tests/test-permission-guard.py` | 21 件すべて成功 |
| `python3 scripts/validate-filenames.py` | 118 ファイル、違反なし |
| `python3 scripts/validate-frontmatter.py` | 82 ファイル合格（ただし CI 未組み込み） |
| `git archive` で作業コピーを作り、`apply-template.py` → `--check`（YAML 設定） | 未解決 0 件。ただし内容に不備あり（A-3） |
| 同じ手順を `--config template.config.json` で実行 | CODEOWNERS と LICENSE が壊れる（A-1） |
| 適用後のコピーに、f-string で大文字定数を補間する Python ファイルを追加して `--check` | 誤検知で失敗（A-4） |
| `git check-ignore -v` で典型パス 15 件を確認 | 14 件が無視され、うち少なくとも 9 件は意図しない無視と判断（F-1〜F-3） |
| ガードフックに境界ケース 30 件を入力 | 4 系統の抜けを確認（C-1〜C-4） |
| code.claude.com の settings / permissions / skills ページと照合 | settings.json のキーは有効。スキルの探索先は `.claude/skills/` のみ（B-1） |

### 重大度の定義

| 記号 | 意味 |
| :--- | :--- |
| 🔴 Critical | 派生プロジェクトの基本機能が壊れる、または安全性ポリシーの前提が崩れる |
| 🟠 High | 誤動作・誤情報・保護の抜けがあり、早期対応が必要 |
| 🟡 Medium | 保守性・一貫性の問題 |
| ⚪ Low | 改善提案 |

---

## 3. 指摘事項

### A. テンプレートエンジンと初期化フロー

#### A-1 🟠 設定ファイルの二重管理で値が食い違う

- **根拠**: `template.config.json:6,9-11` と `template.config.yaml:16,19-21` で、`REPOSITORY_OWNER`・`AUTHOR_NAME`・`AUTHOR_GITHUB`・`AUTHOR_EMAIL` の値が異なります。JSON 版の `AUTHOR_GITHUB` は `"@sun-flat-yamada (Youhei Yamada)"` です。
- **影響**: YAML が優先されるため普段は表に出ません。しかし JSON を使うと、`.github/CODEOWNERS:5` が `* @@sun-flat-yamada (Youhei Yamada)`（無効な所有者指定）に、`LICENSE:3` が `@@sun-flat-yamada (Youhei Yamada) (@sun-flat-yamada (Youhei Yamada))` になります（再現済み）。
- **対応**: 設定ファイルを YAML に一本化して JSON を削除します。両方を残す場合は、スキーマを定義して両者の一致を CI で検査します。

#### A-2 🟠 設定値を検証していない

- **根拠**: `apply-template.py` は値をそのまま置換します。`AUTHOR_GITHUB` の `@` 二重化、URL の形式、`PRIMARY_LANGUAGE` の許可値、`LICENSE_TYPE` のいずれも検査しません。
- **影響**: `LICENSE` は MIT 本文の固定ファイルです。`LICENSE_TYPE` を `Apache-2.0` にすると、バッジとライセンス本文が食い違います。
- **対応**: 設定のスキーマ検証を追加します（GitHub ユーザー名は `^[A-Za-z0-9-]+$`、URL は `https://github.com/` 形式、言語は列挙値、ライセンスは SPDX ID）。ライセンス本文は `LICENSE_TYPE` に応じてテンプレート群から選びます。

#### A-3 🟠 脆弱性の報告先がダミーアドレスになる

- **根拠**: `template.config.yaml:21` の `AUTHOR_EMAIL: "yamada.developer@example.com"` が、そのまま `SECURITY.md:38` に入ります（再現済み）。
- **対応**: Copier への移行（P1-1）で、メールを検証付きの質問にして解消します（決定 #3）。既定値を空にし、未設定なら適用を失敗させます。報告の主経路は GitHub Private Vulnerability Reporting とし、メールは任意項目にします。

#### A-4 🔴 プレースホルダー検査の誤検知で派生プロジェクトのコミットが止まる

- **根拠**: `scripts/apply-template.py:69` は、波括弧で囲まれた 3 文字以上の大文字・数字・`_` をすべて未解決のプレースホルダーとみなします。`.pre-commit-config.yaml:29-34` はこの検査を `always_run: true` で実行します。
- **影響**: Python の f-string、C# の補間文字列、Rust の `format!`、各種テンプレートエンジンで大文字定数を補間する正当なコードが検出され、pre-commit がコミットを拒否します。f-string で `MAX_RETRIES` を補間するファイルを追加すると、`--check` が失敗することを再現しました。
- **対応**: 検査対象を、設定ファイルに定義されたキー（またはキー一覧のマニフェスト）に限定します。あわせて、`--finalize` で pre-commit の検査フックと検査ワークフローを取り除きます。

#### A-5 🟡 `--finalize` の後片付けが不完全

- **根拠**: `apply-template.py:205-217` が削除するのは、設定ファイル 2 つと `setup.sh` / `setup.ps1` だけです。
- **残るもの**: `apply-template.py`、`template-check.yml`、pre-commit のプレースホルダーフック、README の「template.config.yaml を編集」の手順、CHANGELOG のテンプレート履歴、本書のようなテンプレート保守用の文書。
- **対応**: 削除・書き換えの対象をマニフェスト（例: `template.manifest.yaml`）で宣言し、finalize はそれに従って処理します。

#### A-6 🟡 テンプレート自身の README が未置換のまま表示される

- **影響**: テンプレートリポジトリのトップページにプレースホルダーがそのまま表示され、ライセンスバッジもリンク切れになっています。
- **対応**: `README.md` にはテンプレート自体の説明を書きます。派生プロジェクト用の README は `template/README.md` などに分けて置き、適用時に差し替えます。

#### A-7 🟡 全 9 言語ぶんの資産が派生プロジェクトに残る

- **影響**: 言語別の 45 ファイル（H-1）が `PRIMARY_LANGUAGE` と関係なく残り、エージェントのコンテキストを圧迫してノイズになります。
- **決定**: 対応しません（決定 #4: 全言語を維持）。重複の解消は H-1 で行います。

#### A-8 🟡 テンプレートの更新を派生リポジトリへ伝播できない

- **影響**: 一度置換すると元に戻せず、テンプレート側の改善（権限ポリシーの更新など）を取り込む手段がありません。
- **対応（決定 #3）**: Copier に移行し、`copier update` で差分を適用します。P1-1 で実施し、設計は ADR-0002 に記録します。

#### A-9 ⚪ 細かな不具合

- `apply-template.py:36` の `"*.egg-info"` は完全一致で比較されるため、機能しません。
- `setup.sh:26` の `--check` は最初の失敗で終了しますが、`setup.ps1` は両方の検査を実行して結果を集約します（挙動に差があります）。
- UTF-8 以外のファイルは、警告なしにスキップされます。

### B. AI ツール連携

#### B-1 🔴 `.agents/skills/` とスラッシュコマンドが Claude Code から見えない

- **根拠**:
  - Claude Code がプロジェクトのスキルを探すのは `.claude/skills/<name>/SKILL.md` だけです（公式ドキュメントで確認）。`.agents/skills/` は読み込まれません。
  - `.gitignore:194` の `.claude/*` によって、`.claude/skills/`・`.claude/commands/`・`.claude/agents/` はすべて無視されます（`git check-ignore` で確認）。
  - `CLAUDE.md` に書かれた `/status`・`/apply-template`・`/test`・`/check-names` などには、定義ファイルがありません。
- **対応**:
  - `.gitignore` に `!.claude/skills/`、`!.claude/agents/`、`!.claude/commands/` を追加します。
  - `.agents/skills/` から `.claude/skills/` を生成する同期スクリプトを用意し、差分を CI で検査します。シンボリックリンクは Windows で壊れやすいため、生成方式を推奨します。
  - CLAUDE.md に書かれたコマンドをスキルとして実装します。
  - SKILL.md の `globs` は、Claude Code では `paths` に相当します（H-2）。

#### B-2 🟠 ルートの `AGENTS.md` がない

- **根拠**: 権限ポリシー、`.claude/settings.json:150`、`.vscode/settings.json` はいずれも `AGENTS.md` を保護対象に挙げていますが、ファイル自体が存在しません。Codex CLI・Cursor・GitHub Copilot などは `AGENTS.md` を読み込みます。
- **対応**: `AGENTS.md` を全ツール共通の単一ソースにします。`CLAUDE.md` は `@AGENTS.md` を取り込み、Claude 固有の事項だけを書きます。Gemini CLI には、`.gemini/settings.json` の `context.fileName` に `AGENTS.md` を加えます。

#### B-3 🟠 ツール別の指示ファイルが重複し、内容も食い違う

- **根拠**:
  - 参照するルールがファイルごとに違います。`CLAUDE.md` は 5 ルール（`doc-rules-general.md` を含まない）、`.gemini/GEMINI.md` は 3 ルールと権限ポリシー、`copilot-instructions.md` はコーディングルールだけです。
  - `.cursorrules` は Cursor の旧形式です（現在は `.cursor/rules/*.mdc` または `AGENTS.md`）。Windsurf は `.cursorrules` を読みませんが、`README.md:99` には「Cursor / Windsurf」と書かれています。
- **対応**: B-2 で単一ソース化したあと、各ファイルを「AGENTS.md を参照し、固有の差分だけを書く」薄いアダプタにします。内容の同期は CI で検査します。

#### B-4 🟡 エージェント定義がどのツールのネイティブ形式にもなっていない

- **根拠**: `.agents/agents/*.agent.md` はペルソナ文書にとどまります。Claude Code のサブエージェント（`.claude/agents/*.md` に `name`・`description`・`tools` などを持つ形式）や、Copilot のカスタムエージェント（`.github/agents/*.agent.md`）としては登録されません。
- **対応**: B-1 と同じ同期スクリプトで、各ツール形式のアダプタを生成します。少なくとも Claude 用のサブエージェント（code-review、security-sentinel）を提供します。

#### B-5 🟡 指示ファイルのフロントマターがコンテキストの雑音になる

- **根拠**: `CLAUDE.md:1-15`、`.gemini/GEMINI.md`、`.github/copilot-instructions.md` の YAML はツールに解釈されず、本文としてコンテキストに入ります。
- **対応**: ツールが読む指示ファイルをフロントマター検査の対象外にして、フロントマターを削除します（G-1 と同じ例外リストを使います）。

### C. 権限ポリシーとガードフック

ガードは全体として堅牢です。以下は、境界ケースの入力で見つかった抜けです。

| ID | 重大度 | 入力例 | 現状 | 期待する判定 |
| :--- | :--- | :--- | :--- | :--- |
| C-1 | 🟠 | `git config core.hooksPath /dev/null`、`git config --unset core.hooksPath` | 判定なし。`.claude/settings.json:294` の deny は `git -c core.hooksPath` だけが対象で、ask にも該当しない | N-04 で拒否。ただし `install-hooks.py` が使う `.githooks` への設定だけは許可する |
| C-2 | 🟠 | `uv run python -m twine upload dist/*`（`poetry run`、`pnpm exec`、`python -m twine` も同じ系統） | 判定なし | N-10 で拒否。`strip_wrappers` にこれらのランナーを追加する |
| C-3 | 🟡 | `main` ブランチ上での `git push`、`git push origin`、`git push -u origin HEAD` | ask（C-HITL-01）止まり | 現在のブランチと upstream を解決して N-08 で判定する。または「サーバー側の保護に委ねる」と明記する |
| C-4 | 🟡 | `gh api -X PUT repos/o/r/pulls/1/merge`、`gh api -X DELETE repos/o/r` | ガードでは判定なし。Claude Code は `gh *` が ask なので実害は小さいが、ガードを共有する他のハーネスでは抜けになる | `gh api` のメソッドとエンドポイントから N-08 / N-07 で判定する |

#### C-5 🟡 Windows ではガードが無効になりうる（fail-open）

- **根拠**: `.claude/settings.json:471` は `python3` を呼び出します。Windows では `python3` がないことが多く、その場合フックは非ブロッキングのエラーになり、N ティアの検査が素通りします。テンプレートは `setup.ps1` で Windows を正式にサポートしています。
- **対応**: `python3` → `python` → `py -3` の順に試すランチャーを用意するか、OS ごとにフック設定を分けます。ガードが起動できないときに警告する SessionStart フックも追加します。

#### C-6 🟡 6 形式・約 1,500 行の手作業同期でドリフトが起きている

- **根拠**: Claude（478 行）、Codex rules（441 行）、Gemini policy（293 行）、Cursor（約 180 行）、VS Code（106 行）の設定を個別に保守しています。C-1 はその実例で、VS Code 側は `core.hooksPath` に承認を必須にしていますが、Claude 側は素通りします。
- **対応**: 「コマンド → 期待するティア」の共通テストデータ（例: `tests/permission-cases.yaml`）を作ります。ガード、VS Code の正規表現、Gemini の正規表現とプレフィックス、Codex のプレフィックス規則に同じデータを流し、期待どおりの判定になるかを検査します。長期的には、単一の機械可読ポリシーから各形式を生成します。

#### C-7 ⚪ その他の検討事項（要判断）

- タグの push（`git push origin v1.0.0`）は `release.yml` を起動するため、実質的にはリリース操作です。しかし現在は通常の C-HITL-01 と同じ扱いです。専用のメッセージか専用のルールを検討します。
- Cursor・Gemini CLI・Codex にもフックの仕組みがあります。現在ガードにつながっているのは Claude Code と VS Code（`chat.useClaudeHooks`）だけなので、接続できるか検証して検討します。
- `permissions.disableAutoMode` と `sandbox.allowUnsandboxedCommands` は設定しないことに決定しました（決定 #6）。理由は ADR-0001 の追記に記録しています。

### D. CI/CD とサプライチェーン

#### D-1 🟠 ワークフローに `permissions:` がない

- **根拠**: `ci.yml`・`pr-hygiene.yml`・`secret-scan.yml`・`template-check.yml` は既定のトークン権限で動きます。既定値はリポジトリや組織の設定次第で write になります。
- **対応**: 各ワークフローの先頭に `permissions: contents: read` を書きます。`pr-hygiene` には `pull-requests: read` を加え、`release.yml` の `contents: write` はジョブ単位に限定します。

#### D-2 🟠 Actions がタグ参照で、SHA に固定されていない

- **対応**: セキュリティを売りにするテンプレートとして、`uses:` をコミット SHA で固定し（バージョンはコメントで併記）、Dependabot で更新します。CI に `actionlint` と `zizmor` を追加します。

#### D-3 🟠 テンプレート自身のコードに品質ゲートがない

- **根拠**:
  - `ci.yml:28` の `py_compile` は `validate-frontmatter.py` を対象に含みません。`validate-frontmatter.py` は CI でも pre-commit でも実行されていません。
  - テストがあるのはガードだけで、`apply-template.py`・`validate-filenames.py`・`validate-frontmatter.py`・`install-hooks.py` にはテストがありません。
  - リポジトリ自身のルール（`coding-rules-python.md` の ruff と `mypy --strict`）がスクリプトに適用されていません。`.githooks/*` と `setup.sh` には shellcheck が、Markdown にはリンク検査がありません。
- **対応**: 上記をすべて CI に追加します。テストは pytest が自動で見つけられるファイル名にします（I-1）。

#### D-4 🟠 テンプレート適用の E2E テストがない

- **根拠**: `ci.yml:41` は `--dry-run` を実行するだけで、適用結果を検証しません。A-1・A-3・A-4 は、どれもこの種の E2E テストで見つかった問題です。
- **対応**: CI に次の流れを追加します。一時ディレクトリに展開 → 設定を適用 → `--check` が 0 件 → 命名とフロントマターを検査 → CODEOWNERS の構文を検査 → finalize 後に不要物が残っていないかを検査。

#### D-5 🟡 `template-check.yml` が常に成功する

- **根拠**: `template-check.yml:23` は `|| echo "::warning::..."` で失敗を握りつぶします。テンプレートリポジトリでは常に警告が出て、派生プロジェクトでは決してブロックしません。
- **対応**: テンプレートリポジトリではジョブをスキップし（リポジトリ名で `if:` 判定）、派生プロジェクトでは失敗扱いにします。あるいは D-4 に統合して、このワークフローを削除します。

#### D-6 🟡 Dependabot の設定が実態と合っていない

- **根拠**: `dependabot.yml:13,23` で設定している pip と npm にはマニフェストがなく、更新時にエラーになります。pre-commit のフックのバージョン（`v4.6.0`、gitleaks `v8.18.4`）は更新の対象外です。
- **対応**: Dependabot の設定は、`PRIMARY_LANGUAGE` に応じて適用時に生成します。pre-commit のフックは、Dependabot の対応状況を確認して設定するか、定期的に `pre-commit autoupdate` を実行して PR を作るワークフローで更新します。

#### D-7 🟡 リリース自動化の記述と実装が食い違う

- **根拠**: `README.md:42` は「automated semantic releases」と書いていますが、`release.yml` はタグの push で下書きリリースを作るだけです。CHANGELOG も手作業で更新しています。
- **対応（決定 #5）**: release-please を採用し、CHANGELOG の生成まで自動化します。採用しない場合は README の記述を実態に合わせます。

#### D-8 🟡 サーバー側の保護（ブランチ保護・ルールセット）が提供されていない

- **根拠**: 権限ポリシー（原則 4、N-08）と CODEOWNERS はブランチ保護を前提にしていますが、その設定を配布する仕組みがありません。`README.md:42` の「branch protection verification」も実装されていません。
- **対応**: `.github/rulesets/main.json`（GitHub ルールセットのエクスポート形式）と適用手順を提供します。メンテナーが 1 人だけの場合、コードオーナーのレビューを必須にすると自分の PR を承認できなくなるため、その点を手順に明記します。

#### D-9 ⚪ 細部

- スクリプトは「Python 3.8+」と謳っていますが、3.8 と 3.9 はサポートが終了しています。最小バージョンを 3.10 にし、CI を複数のバージョン（例: 3.10 と 3.13）と Windows・macOS のランナーでも実行します（`setup.ps1` とフックの確認のため）。
- gitleaks-action は、組織所有のリポジトリではライセンスキーを求める場合があります。現行版の条件を確認して README に書くか、gitleaks の CLI を直接実行します。
- `README.md:28` の CI バッジは「Passing」と固定された画像です。ワークフローの実際の状態を示すバッジに置き換えます。

### E. Git フック

#### E-1 🟠 二系統のフックが衝突する

- **根拠**:
  - `install-hooks.py` は `core.hooksPath=.githooks` を設定しますが、`.pre-commit-config.yaml` は `pre-commit install` を前提にしています。pre-commit は `core.hooksPath` が設定されているとインストールを拒否するため、両立しません。
  - 検査内容も別物です。`.githooks` は簡易な正規表現と命名検査、pre-commit は gitleaks・プレースホルダー検査・YAML/JSON 検査を行います。
  - `SECURITY.md:63-64` には「`.githooks` がプレースホルダーを検査する」と書かれていますが、実装されていません。
- **対応（決定 #2）**: pre-commit フレームワークに一本化し（commit-msg の検査も pre-commit で実行）、`.githooks` を廃止します。または、`.githooks` から pre-commit を呼び出す形に統合します。

#### E-2 🟡 `.githooks/pre-commit` の秘密検出が狭い

- **根拠**:
  - `.githooks/pre-commit:31` が検出するのは `AKIA…`、`ghp_…`、PEM ヘッダだけです。`github_pat_`、`gho_` / `ghs_`、`sk-ant-`、`sk-`、`xox[baprs]-`、`AIza` などを見逃します。
  - `:17` の `for FILE in $STAGED_FILES` は、空白を含むパスを分割してしまいます。
  - `:19` の `id_rsa*` はリポジトリ直下のファイルにしか一致せず、`id_ed25519` は対象外です。
- **対応**: gitleaks がある環境では `gitleaks protect --staged`（新しい版では `gitleaks git --staged`）を実行し、正規表現による検出は代替手段に回します。

#### E-3 🟡 trailing-whitespace フックが Markdown の改行を壊す

- **根拠**: `.editorconfig:32-33` は Markdown の行末空白を残す設定ですが、`.pre-commit-config.yaml:11` の `trailing-whitespace` は既定でそれを削除します。README は行末の 2 スペースで改行しています（`README.md:24`、`:159`）。
- **対応**: フックに `args: [--markdown-linebreak-ext=md]` を追加します。

#### E-4 ⚪ commit-msg フックが正当なメッセージを拒否する

- `git revert` が既定で作る `Revert "…"` や、`fixup!` / `squash!` / `amend!` を拒否します。また、git-workflow スキルが求めるヘッダ長（72 文字）を検査していません。

### F. `.gitignore`

#### F-1 🔴 対応言語のソースや必須ファイルを無視する

`git check-ignore -v` の結果:

| パス | 無視するパターン | 影響 |
| :--- | :--- | :--- |
| `lib/main.dart`、`packages/web/lib/index.ts` | `.gitignore:94` の `lib/`（Python 節） | Dart の `lib/` や JS/TS の `lib/` 配下をコミットできない |
| `bin/app.dart` | `.gitignore:180` の `bin/`（C# 節） | Dart の実行エントリである `bin/` をコミットできない |
| `pkg/foo/foo.go` | `.gitignore:148` の `/pkg/` | Go でよく使う `pkg/` 構成をコミットできない |
| `Makefile` | `.gitignore:174` | ドキュメントは `make check` を案内しているのに、Makefile を追加できない |
| `src/Testing/a.cs` | `.gitignore:173` の `Testing/` | CMake 用の規則が任意の階層に効いてしまう |

- **対応**: 全言語の規則は残したまま（決定 #4）、言語間で衝突するパターンを削除するかアンカーを付けます（P0-1）。全言語共通の規則はルートに固定し、`/build/` のようにアンカーを付けます。

#### F-2 🟠 ロックファイルを無視している

- **根拠**: `Cargo.lock`（`:138`）と `pubspec.lock`（`:155`）が無視されています。これは権限ポリシー C-SBX-02 の「ロックファイルに忠実なインストール」（`cargo build --locked`、`dart pub get --enforce-lockfile`）と矛盾し、ビルドの再現性も失われます。
- **対応**: アプリケーションではロックファイルをコミットします。ライブラリでの扱いは各エコシステムの指針に従い、言語ルールに明記します。

#### F-3 🟠 `.claude/*` が共有すべき設定まで無視する

- 詳細は B-1 を参照してください。`!.claude/skills/`、`!.claude/agents/`、`!.claude/commands/` を追加します。

#### F-4 ⚪ その他

- `*.asc` は公開鍵（`KEYS.asc` など）まで無視します。ただし秘密鍵の書き出しにも使われる拡張子のため、安全側に倒して無視を維持します（P0-1 で判断）。
- `env/` と `out/` は範囲が広すぎるため、アンカーを付けます。

### G. ドキュメントの整合性

#### G-1 🟠 フロントマターが表示や入力を汚す

- **根拠**:
  - `.github/PULL_REQUEST_TEMPLATE.md:1-15` のフロントマターは GitHub に解釈されないため、すべての PR 本文にそのまま入ります。
  - `README.md` のフロントマターは、GitHub 上でページ冒頭の表として描画されます。
  - `README.md:2` の `$schema: ".aegis/schemas/frontmatter.schema.json"` は存在しないパスです。README は `language` と `doc_type` を使っており、規約（`lang`）とも合いません。
- **対応**: PR テンプレート、README 類、CHANGELOG、CODE_OF_CONDUCT、ツールの指示ファイル（B-5）を「フロントマター必須」の対象外にします。`validate-frontmatter.py` には例外リストを実装します。

#### G-2 🟠 実在しない機能やパスに言及している

| 記述 | 場所 | 実態 |
| :--- | :--- | :--- |
| `make check` / `make check-names` | `CONTRIBUTING.md:50`、`.github/PULL_REQUEST_TEMPLATE.md:39`、`naming-rules-general.md:101` | Makefile がなく、`.gitignore` で無視もされている |
| 「branch protection verification」「automated semantic releases」 | `README.md:42` | 未実装（D-7、D-8） |
| `.githooks` によるプレースホルダー検査 | `SECURITY.md:63-64` | 未実装（E-1） |
| `.cursorrules` で Windsurf に対応 | `README.md:99` | Windsurf は `.cursorrules` を読まない |
| `/status`・`/test` などのコマンド | `CLAUDE.md` | 定義がない（B-1） |
| `.agents/skills/languages/` | `workflow-spec-to-code.md:31` | 存在しない（実際は `toolchain-<lang>`） |
| `docs/adr/0001-record-architecture-decisions.md` | `naming-rules-general.md` の例 | 実在する ADR-0001 は権限ポリシー |
| 「Merge is physically blocked」 | `code-review.agent.md:33` | 強制する仕組みがない |

- **対応**: 機能を実装するか、記述を直します。D-3 にリンク・パス検査を加えて再発を防ぎます。

#### G-3 🟡 ブランチ名の規則が一致しない

- `CONTRIBUTING.md:37` は `feature/…`、`git-rules-commit.md` は `feat/…` としています。

#### G-4 🟡 日付・履歴のメタデータが派生プロジェクトに引き継がれる

- **根拠**:
  - フロントマターの `date` / `updated`（2026-09-20 など）が固定値です。README・CHANGELOG・ADR-0000 の日付は、年だけが置換される固定の月日です。
  - CHANGELOG にはテンプレートの履歴と `[1.0.0]` のリリースが含まれ、`SECURITY.md:25` のサポート対象バージョンは `1.0.x` になっています。
- **対応**: 適用時に CHANGELOG を `## [Unreleased]` だけにリセットし、日付を適用日に更新します。あるいは `date` / `updated` を廃止して、git の履歴を正とします。

#### G-5 🟡 Markdown のコードフェンスの入れ子が崩れている

- `code-review.agent.md:43-57` では、```` ```markdown ```` のブロックの中に ```` ```python ```` が入っているため表示が崩れます。外側のフェンスをバッククォート 4 つか `~~~` にします。

#### G-6 ⚪ その他

- `CLAUDE.md` が `doc-rules-general.md` を取り込んでいません。
- `ai-permission-guide.md` と `front-matter-standards.md` は日本語のみで、ほかの文書は英語です。どの文書を二言語で持つかという言語方針を doc-rules に明記します。
- Issue テンプレートが使う `triage` ラベルや Discussions へのリンクは、事前の準備が必要です。ラベル定義ファイルか、準備の手順を用意します。

### H. `.agents/` 資産の品質と保守性

#### H-1 🟡 言語別の資産が大量に重複している

- **根拠**:
  - 1 言語あたり 5 ファイル（`coding-rules`、`coding-profile`、`code-review-profile`、`code-review-<lang>` スキル、`toolchain-<lang>` スキル）× 9 言語で 45 ファイルあり、ルールとプロファイルの内容が重なっています。
  - `code-review-<lang>` スキルは機械的に複製されたもので、Python や JS にも「memory safety」と書かれ、言語名も大文字（`PYTHON`）のままです。
  - `code-review-python/SKILL.md:24` の `ruff check . and mypy --strict . and pytest` は、コマンドとして成立しません。
- **対応**: 言語ごとに、ルール・レビュー観点・ツールチェーンを 1 つの参照文書にまとめます。汎用の `code-review` / `toolchain` スキルが、必要なときにその文書を読み込む形にします（段階的な開示）。A-7 の言語削減とあわせて実施します。

#### H-2 🟡 SKILL.md のフロントマターが仕様やツールと合っていない

- **根拠**:
  - Agent Skills の仕様と Claude Code が解釈するのは `name`・`description` などです（Claude Code はさらに `paths`・`metadata` なども解釈します）。`globs`・`alwaysApply`・`category`・`status`・`tags` は、仕様にないトップレベルの項目です。それなのに、`validate-frontmatter.py:54` は `tags` を必須にしています。
  - `description` に「いつ使うか」が書かれていません。これはスキルが選ばれる精度に直結します。
- **対応**: 独自の項目は `metadata:` の下に移し、Claude Code 向けには `paths` を使います。`description` には起動条件を書き、バリデータを仕様に合わせて直します。

#### H-3 🟡 ルールと実装・手順が矛盾している

- リポジトリ自身の Python スクリプトが、`coding-rules-python.md`（3.10 以降の構文、`mypy --strict`）に従っていません（`typing.List` などを使い、型検査もしていません）。
- `toolchain-python/SKILL.md:24` は `uv sync` ですが、権限ポリシー C-SBX-02 は `uv sync --locked` を求めています。
- `git-workflow/SKILL.md:27` はコミット前に `apply-template.py --check` を実行するよう求めていますが、テンプレートリポジトリでは常に失敗します。

### I. 命名規則

#### I-1 🟡 汎用の命名規則が言語の慣習と衝突し、しかも検査されていない

- **根拠**:
  - `naming-rules-general.md` §6 は「小文字・数字・ハイフン・ドットのみ」と定めています。しかしこれは、Python のモジュールや `__init__.py`、pytest がテストを見つける規則（`test_*.py`）と衝突します。Dart（snake_case 必須）、C#（PascalCase）、Go（`_test.go`）、Rust（snake_case のモジュール）とも衝突します。
  - `tests/test-permission-guard.py:8` 自身が、「ハイフンを含む名前のため unittest の自動発見で import できない」と注記しています。
  - 一方、`validate-filenames.py` はこの規則を実装しておらず（空白だけを検査）、`ALLOWED_ROOT_UPPERCASE`（`:40`）は定義されているだけで使われていません。
- **対応（決定 #7）**: 汎用規則の適用範囲を、`.agents/`・`docs/`・`scripts/` などソースコード以外の領域に限定し、ソースコードの命名は言語ルールに委ねます。適用範囲内の規則は実装してテストし、Python のテストは `test_*.py` に改名します。

---

## 4. 改善計画（ロードマップ）

### 進め方の原則

- 1 フェーズを複数の小さな PR に分けます。各 PR は目的を 1 つに絞り、Conventional Commits に従います。
- `.claude/`・`.agents/`・`.github/`・`.githooks/`・`CLAUDE.md`・`.gitignore`・`.pre-commit-config.yaml` の変更は C-HITL-05 に当たるため、人間のレビューを必須にします。
- TDD の要件に従い、スクリプトの修正は失敗するテストを書くところから始めます。

### Phase 0: すぐに直すもの（目安 1〜2 日、低リスク）

| PR | 内容 | 対象 ID | 完了条件 |
| :--- | :--- | :--- | :--- |
| P0-1 | `.gitignore` の修正（`lib/`・`bin/`・`/pkg/`・`Makefile`・`Testing/` にアンカーを付けるか削除、ロックファイルを追跡対象に、`.claude/` 配下の `skills/`・`agents/`・`commands/` の例外を追加） | F-1〜F-4 | §2 の 15 パスで `git check-ignore` の結果が期待どおりになる |
| P0-2 | PR テンプレートのフロントマターを削除。README の `$schema` を削除して `lang` に統一。`validate-frontmatter.py` に例外リストを追加 | G-1 | 新しい PR の本文に YAML が入らない |
| P0-3 | 設定ファイルを YAML に一本化（JSON を削除）。A-3 は Copier 移行（P1-1）の質問と検証で解消する | A-1 | JSON が削除され、ドキュメントの「(or .json)」表記も更新されている |
| P0-4 | すべてのワークフローに最小限の `permissions:` を追加 | D-1 | すべてのワークフローで権限が明示されている |
| P0-5 | ガードの修正。`git config` による `core.hooksPath` の変更・削除を N-04 で、ランナー経由の publish を N-10 で拒否する（テストを先に書く）。ポリシー §5 に従い、各ツールの設定も同じ PR で更新する | C-1、C-2 | 追加したテストが失敗から成功に変わり、既存のテストもすべて成功する |
| P0-6 | 文書の誤記修正（`make check`、Windsurf、`skills/languages`、ブランチ名、入れ子のフェンス）と `--markdown-linebreak-ext=md` の追加 | G-2（一部）、G-3、G-5、E-3 | リンク・パス検査で問題が 0 件 |

**状態（2026-10-02）**: P0-1〜P0-6 を 1 つの PR で実装しました（作業ブランチが 1 本のため、項目ごとにコミットを分けています）。

### Phase 1: Copier への移行とテンプレート自身の品質ゲート（目安 1〜2 週間）

決定 #3 により、独自のテンプレートエンジン（`apply-template.py`）を改修する代わりに Copier へ移行します。A-1〜A-6、A-8、A-9、G-4 は、Copier の質問・検証・除外・更新の仕組みでまとめて解消します。

| PR | 内容 | 対象 ID |
| :--- | :--- | :--- |
| P1-1 | Copier へ移行（ADR-0002 を書く）。`copier.yml` の質問と検証（GitHub ユーザー名・URL・メール・主言語・SPDX ライセンス）、回答に応じたライセンス本文の選択、テンプレート保守用ファイル（本書など）の除外。`apply-template.py`・`template.config.yaml`・`setup.sh` / `setup.ps1`・`template-check.yml`・プレースホルダー検査フックを廃止 | A-1〜A-6、A-8、A-9、G-4 |
| P1-2 | `copier copy` と `copier update` の E2E テストを CI に追加（回答ファイルで生成 → 命名・フロントマター・CODEOWNERS を検査 → pre-commit を実行） | D-4、D-5 |
| P1-3 | スクリプト群のユニットテスト（pytest）と、ruff・mypy・shellcheck・actionlint・リンク検査を CI に追加 | D-3、H-3 |
| P1-4 | フックを pre-commit に一本化（決定 #2。commit-msg ステージも含める）。`.githooks/` と `install-hooks.py` を廃止し、秘密の検出は gitleaks に任せる | E-1、E-2、E-4 |

**ADR-0002 で決めること**: テンプレート本体を `_subdirectory` に分けるか、ルートをそのままテンプレートにして保守用ファイルを `_exclude` で除くか。前者はテンプレートリポジトリ自身の README と CI を分けやすい一方、`.github/` や `.claude/` がテンプレート用と保守用の二重管理になります。後者は二重管理を避けられますが、置換が必要なファイルに `.jinja` 接尾辞を付ける必要があります。

**完了条件**: 「`copier copy` で新規作成 → 初回コミット → CI が緑」が手作業での修正なしに通り、`copier update` でテンプレートの変更を派生リポジトリに取り込めること。

### Phase 2: AI 連携を実際に効かせる（目安 1〜2 週間）

| PR | 内容 | 対象 ID |
| :--- | :--- | :--- |
| P2-1 | ルートに `AGENTS.md` を単一ソースとして新設。CLAUDE.md・GEMINI（`context.fileName`）・Copilot・Cursor の指示ファイルをアダプタ化し、フロントマターを削除 | B-2、B-3、B-5 |
| P2-2 | `.agents/` から各ツール形式（`.claude/skills/`、`.claude/agents/`、必要に応じて `.github/agents/`）を生成するスクリプトと、CI での差分検査。CLAUDE.md に書かれたコマンドをスキルとして実装 | B-1、B-4 |
| P2-3 | SKILL.md のフロントマターを仕様に合わせる（`metadata`、`paths`、起動条件を含む `description`）。バリデータも修正 | H-2 |
| P2-4 | 権限ポリシーの共通テストデータと、各ツール設定との整合テスト | C-6 |
| P2-5 | ガードの強化（暗黙の push 先の解決、`gh api` による破壊的操作の検出、Windows 用ランチャー、SessionStart での起動確認） | C-3、C-4、C-5 |

**完了条件**: Claude Code のスキル・サブエージェント・コマンドの一覧に、このリポジトリの定義が表示されること。Codex・Cursor・Copilot・Gemini が同じ `AGENTS.md` を読み込むこと。共通テストデータに対して、すべてのツール設定が期待どおりに判定すること。

### Phase 3: 保守性と運用を成熟させる（継続）

| PR | 内容 | 対象 ID |
| :--- | :--- | :--- |
| P3-1 | 言語資産を統合（45 ファイル → 9 ファイル程度）。全 9 言語は維持する（決定 #4） | H-1 |
| P3-2 | Actions の SHA 固定と zizmor の導入。Dependabot の設定を Copier の回答（主言語）に応じて生成し、pre-commit の更新も対象にする | D-2、D-6 |
| P3-3 | release-please を導入（決定 #5）。`release.yml` を置き換え、CHANGELOG を自動生成 | D-7 |
| P3-4 | ルールセットの JSON と適用手順を提供 | D-8 |
| P3-5 | 命名規則をソースコード以外の領域に限定して実装し（決定 #7）、Python のテストを `test_*.py` に改名 | I-1 |
| P3-6 | Python の最小バージョンを 3.10 に。複数 OS・複数バージョンで CI を実行し、CI バッジを置き換え、gitleaks のライセンス条件を明記 | D-9 |
| P3-7 | タグ push の扱いと、他ツールへのガード接続を検討（モード制限は決定 #6 で決着済み） | C-7 |

---

## 5. 判断事項と決定（2026-10-01）

| # | 論点 | 決定 | 計画への反映 |
| :--- | :--- | :--- | :--- |
| 1 | 設定ファイルの形式 | YAML のみ | P0-3 で JSON を削除。Copier 移行後は `copier.yml`（YAML）に置き換わる |
| 2 | Git フックの体系 | pre-commit フレームワーク | P1-4 で `.githooks/` と `install-hooks.py` を廃止 |
| 3 | テンプレートの方式 | Copier | Phase 3 から Phase 1 に前倒し（P1-1）。独自エンジンの改修（旧 P1-1〜P1-3、旧 P1-5）は行わない |
| 4 | 言語資産の扱い | 全言語を維持 | A-7 は対応しない。H-1 は重複の統合だけを行う |
| 5 | リリース自動化 | release-please | P3-3 |
| 6 | Claude Code のモード制限 | `disableAutoMode`・`allowUnsandboxedCommands` を設定しない | 理由と影響（ルールに該当しない操作は auto mode では分類器が判定する）を ADR-0001 の追記に記録 |
| 7 | 命名規則の適用範囲 | ソースコード以外の領域のみ | P3-5 |

---

## 6. 付録: 指摘一覧

| ID | 重大度 | 概要 | フェーズ |
| :--- | :--- | :--- | :--- |
| A-1 | 🟠 | 設定ファイルの二重管理と値の食い違い | P0 |
| A-2 | 🟠 | 設定値の検証がなく、ライセンス本文が固定 | P1（Copier） |
| A-3 | 🟠 | 脆弱性の報告先がダミーアドレス | P1（Copier） |
| A-4 | 🔴 | プレースホルダー検査の誤検知でコミットが止まる | P1（Copier） |
| A-5 | 🟡 | finalize の後片付けが不完全 | P1（Copier） |
| A-6 | 🟡 | テンプレート自身の README が未置換表示 | P1（Copier） |
| A-7 | 🟡 | 全言語の資産が派生プロジェクトに残る | 対応しない（決定 #4） |
| A-8 | 🟡 | テンプレート更新を伝播できない | P1（Copier） |
| A-9 | ⚪ | `*.egg-info` の除外が効かない、setup スクリプトの挙動差 | P1（Copier で廃止） |
| B-1 | 🔴 | スキルとコマンドが Claude Code から見えない | P0 / P2 |
| B-2 | 🟠 | `AGENTS.md` がない | P2 |
| B-3 | 🟠 | 指示ファイルの重複と食い違い | P2 |
| B-4 | 🟡 | エージェント定義がネイティブ形式でない | P2 |
| B-5 | 🟡 | 指示ファイルのフロントマター | P2 |
| C-1 | 🟠 | `git config core.hooksPath` がガードを素通り | P0 |
| C-2 | 🟠 | ランナー経由の publish がガードを素通り | P0 |
| C-3 | 🟡 | 暗黙の push 先を判定できない | P2 |
| C-4 | 🟡 | `gh api` による破壊的操作を検出しない | P2 |
| C-5 | 🟡 | Windows でガードが fail-open | P2 |
| C-6 | 🟡 | 6 形式の手作業同期によるドリフト | P2 |
| C-7 | ⚪ | タグ push、他ツールのフック、モード制限 | P3（モード制限は決定 #6 で決着） |
| D-1 | 🟠 | ワークフローの権限が明示されていない | P0 |
| D-2 | 🟠 | Actions が SHA で固定されていない | P3 |
| D-3 | 🟠 | スクリプトのテスト・lint・型検査がない | P1 |
| D-4 | 🟠 | テンプレート適用の E2E テストがない | P1 |
| D-5 | 🟡 | `template-check.yml` が常に成功する | P1 |
| D-6 | 🟡 | Dependabot の設定が実態と合わない | P3 |
| D-7 | 🟡 | リリース自動化の記述と実装が食い違う | P3 |
| D-8 | 🟡 | ルールセットが提供されていない | P3 |
| D-9 | ⚪ | Python の最小バージョン、CI の実行環境、バッジ、gitleaks のライセンス | P3 |
| E-1 | 🟠 | 二系統のフックが衝突する | P1 |
| E-2 | 🟡 | 秘密の検出範囲が狭い | P1 |
| E-3 | 🟡 | Markdown の改行が削除される | P0 |
| E-4 | ⚪ | commit-msg フックが正当なメッセージを拒否する | P1 |
| F-1 | 🔴 | 対応言語のソースを無視する | P0 |
| F-2 | 🟠 | ロックファイルを無視する | P0 |
| F-3 | 🟠 | `.claude/` の共有設定まで無視する | P0 |
| F-4 | ⚪ | `*.asc`、`env/`、`out/` の範囲が広すぎる | P0 |
| G-1 | 🟠 | フロントマターが PR 本文や README を汚す | P0 |
| G-2 | 🟠 | 実在しない機能やパスへの言及 | P0 / 各フェーズ |
| G-3 | 🟡 | ブランチ名の規則が一致しない | P0 |
| G-4 | 🟡 | 日付・履歴のメタデータが引き継がれる | P1（Copier） |
| G-5 | 🟡 | コードフェンスの入れ子が崩れる | P0 |
| G-6 | ⚪ | 取り込み漏れ、言語方針、ラベルの準備 | P2 |
| H-1 | 🟡 | 言語別資産の大量重複 | P3 |
| H-2 | 🟡 | SKILL.md のフロントマターが仕様と合わない | P2 |
| H-3 | 🟡 | ルールと実装・手順の矛盾 | P1 |
| I-1 | 🟡 | 命名規則が言語の慣習と衝突し、検査もされていない | P3 |
