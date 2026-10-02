#!/usr/bin/env python3
"""
.claude/hooks/permission-guard.py
==============================================================================
PreToolUse guard hook for the AI agent permission policy.

Enforces the never-allow tier (N-*) and normalizes a few conditional (C-HITL-*)
actions of .agents/rules/permission-rules-general.md for command forms that
pattern-based permission rules miss (wrappers such as `bash -c`, `env`, `xargs`,
git global options like `git -C <dir> push`, flag permutations, heredocs).

Input : a hook event as JSON on stdin (`tool_name`, `tool_input`).
Output: a PreToolUse decision as JSON on stdout, or nothing to defer to the
        normal permission flow. The exit code is always 0.

This hook is a guardrail, not a security boundary: keep the OS sandbox and the
deny rules in .claude/settings.json enabled. Zero dependencies (Python 3.8+).
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from typing import Callable, Dict, List, Optional, Sequence, TextIO, Tuple

Decision = Tuple[str, str]  # (permission decision, reason starting with "[RULE-ID]")

DENY = "deny"
ASK = "ask"
POLICY_FILE = ".agents/rules/permission-rules-general.md"
MAX_NESTING_DEPTH = 4

OPERATOR_CHARS = frozenset("();<>|&\n`")
REDIRECT_OPERATORS = frozenset({"<", ">", ">>", ">&", "<&", "&>", "&>>", ">|", "<>", "<<", "<<-", "<<<"})
PIPE_OPERATORS = frozenset({"|", "|&"})
SUBSTITUTION_OPERATORS = frozenset({"(", "<(", ">("})
ENV_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
HEREDOC_START = re.compile(r"(?<!<)<<(?!<)(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")

SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh", "ash", "fish"})
INTERPRETERS = SHELLS | {
    "python", "python3", "node", "perl", "ruby", "php", "pwsh", "powershell",
    "iex", "invoke-expression", "source", ".", "eval",
}
DOWNLOADERS = frozenset({"curl", "wget", "iwr", "irm", "invoke-webrequest", "invoke-restmethod", "aria2c"})
PRIVILEGE_COMMANDS = frozenset({"sudo", "su", "doas", "pkexec", "runas"})
SIMPLE_WRAPPERS = frozenset({"command", "builtin", "exec", "nohup", "time", "noglob", "setsid", "chronic", "unbuffer", "caffeinate"})
VALUE_WRAPPERS = {  # wrapper -> options that consume the next token
    "env": {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"},
    "nice": {"-n", "--adjustment"},
    "ionice": {"-c", "-n", "-p", "-t"},
    "stdbuf": {"-i", "-o", "-e"},
    "timeout": {"-s", "--signal", "-k", "--kill-after"},
    "xargs": {"-n", "-I", "-L", "-d", "-P", "-s", "-E", "-a", "--max-args", "--delimiter", "--max-procs", "--arg-file"},
    "watch": {"-n", "--interval", "-d"},
    "flock": {"-w", "--timeout", "-E", "--conflict-exit-code"},
}
WRAPPERS_WITH_OPERAND = {"timeout": 1, "flock": 1}  # positional operands before the wrapped command
RUNNERS = {  # runner -> (subcommands that run the next command, or () for the runner itself; options taking a value)
    "uv": ({"run"}, {"--with", "--python", "-p", "--project", "--directory", "--package", "--extra", "--group", "--env-file", "--index"}),
    "uvx": ((), {"--with", "--from", "--python", "-p", "--index"}),
    "poetry": ({"run"}, {"--directory", "-C", "--project", "-P"}),
    "pdm": ({"run"}, {"--project", "-p"}),
    "hatch": ({"run"}, set()),
    "pipx": ({"run"}, {"--spec", "--python", "--index-url", "-i"}),
    "conda": ({"run"}, {"--name", "-n", "--prefix", "-p"}),
    "npx": ((), {"--package", "-p"}),
    "pnpx": ((), {"--package", "-p"}),
    "bunx": ((), {"--package", "-p"}),
    "npm": ({"exec", "x"}, {"--package", "-p", "--workspace", "-w"}),
    "pnpm": ({"exec", "dlx"}, {"--package", "--dir", "-C", "--filter", "-F"}),
    "yarn": ({"exec", "dlx"}, {"--package", "-p"}),
    "bun": ({"x"}, {"--package", "-p"}),
}
PYTHON_PROGRAM = re.compile(r"^(python[0-9.]*|py)$")

AGENT_BYPASS_FLAGS = frozenset({
    "--dangerously-skip-permissions", "--allow-dangerously-skip-permissions",
    "--dangerously-bypass-approvals-and-sandbox", "--yolo", "--trust-all-tools",
    "--allow-all-tools", "danger-full-access",
})
AGENT_BYPASS_OPTION_VALUES = {"--permission-mode": "bypasspermissions", "--approval-mode": "yolo", "--sandbox": "danger-full-access"}

PROTECTED_BRANCHES = frozenset({"main", "master", "trunk", "production", "prod"})
RELEASE_BRANCH = re.compile(r"^release([/-]v?\d|/|$)")
GIT_GLOBAL_VALUE_OPTIONS = frozenset({
    "-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env", "--super-prefix",
})
GIT_PUSH_VALUE_OPTIONS = frozenset({"-o", "--push-option", "--repo", "--receive-pack", "--exec"})
GIT_COMMIT_VALUE_SHORT = frozenset("mFcCt")
GIT_CONFIG_READ_ACTIONS = frozenset({"--get", "--get-all", "--get-regexp", "get", "--list", "-l", "list"})
GIT_CONFIG_UNSET_ACTIONS = frozenset({"--unset", "--unset-all", "unset"})

ENV_EXAMPLE_SUFFIXES = frozenset({"example", "sample", "template"})
SECRET_PATH_PATTERNS = tuple(re.compile(pattern) for pattern in (
    r"(^|/)\.ssh(/|$)", r"(^|/)id_(rsa|dsa|ecdsa|ed25519)$", r"(^|/)\.gnupg(/|$)",
    r"(^|/)\.aws(/|$)", r"(^|/)\.azure(/|$)", r"(^|/)\.config/gcloud(/|$)", r"(^|/)\.kube(/|$)",
    r"(^|/)\.docker/config\.json$", r"(^|/)\.config/gh(/|$)", r"(^|/)\.git-credentials$",
    r"(^|/)[._]netrc$", r"(^|/)\.npmrc$", r"(^|/)\.pypirc$", r"(^|/)\.gem/credentials$",
    r"(^|/)\.cargo/credentials(\.toml)?$", r"(^|/)\.claude/\.credentials\.json$",
    r"(^|/)\.codex/auth\.json$", r"(^|/)\.gemini/oauth_creds\.json$",
    r"\.(pem|key|p12|pfx|jks|keystore|kdbx)$", r"\.tfstate(\.backup)?$",
    r"(^|/)(credentials|client_secret[^/]*|service[-_]account[^/]*)\.json$",
    r"(^|/)\.(bash|zsh|sh)_history$", r"^/proc/[^/]+/environ$",
))
PATTERN_FIRST_PROGRAMS = frozenset({"grep", "egrep", "fgrep", "rg", "ag", "ack"})
LITERAL_PRINTERS = frozenset({"echo", "printf"})

AGENT_CONFIG_PATH = re.compile(
    r"(^|/)(\.claude/settings(\.local)?\.json|\.vscode/(settings|mcp)\.json|User/settings\.json"
    r"|\.cursor/(cli|permissions|mcp)\.json|\.gemini/settings\.json|\.codex/config\.toml|\.mcp\.json)$"
)
GUARDRAIL_DISABLING_SETTINGS = tuple(re.compile(pattern) for pattern in (
    r'"chat\.tools\.(global\.)?autoApprove"\s*:\s*true',
    r'"chat\.tools\.terminal\.ignoreDefaultAutoApproveRules"\s*:\s*true',
    r'"defaultMode"\s*:\s*"bypassPermissions"',
    r'"enableAllProjectMcpServers"\s*:\s*true',
    r'"skipDangerousModePermissionPrompt"\s*:\s*true',
    r'"disableYoloMode"\s*:\s*false',
    r'sandbox_mode\s*=\s*"danger-full-access"',
    r'approval_policy\s*=\s*"never"',
))

EXFIL_HOSTS = (
    "169.254.169.254", "metadata.google.internal", "webhook.site", "pastebin.com", "paste.ee",
    "hastebin.com", "transfer.sh", "0x0.st", "termbin.com", "requestbin", "pipedream.net",
    "ngrok.io", "ngrok-free.app", "ngrok.app", "trycloudflare.com", "interact.sh", "oast.fun",
    "oast.pro", "oast.live", "burpcollaborator.net",
)
NETWORK_TOOLS = DOWNLOADERS | {
    "http", "https", "xh", "nc", "ncat", "netcat", "socat", "ssh", "scp", "sftp", "rsync", "ftp",
    "telnet", "ping", "dig", "nslookup", "host",
}
TUNNEL_PROGRAMS = frozenset({"ngrok", "localtunnel", "lt", "bore"})
PUBLISH_SUBCOMMANDS = {
    "npm": {"publish", "unpublish", "deprecate", "dist-tag", "owner", "token", "adduser", "login"},
    "pnpm": {"publish"}, "bun": {"publish"}, "twine": {"upload"}, "uv": {"publish"},
    "poetry": {"publish"}, "cargo": {"publish", "yank", "owner", "login"}, "nuget": {"push", "delete"},
    "gem": {"push", "yank", "owner"}, "docker": {"push", "login"}, "podman": {"push", "login"},
    "mvn": {"deploy"}, "gradle": {"publish"},
}
PUBLISH_SUBCOMMAND_PAIRS = {
    "yarn": {("publish",), ("npm", "publish"), ("npm", "login")}, "dotnet": {("nuget", "push"), ("nuget", "delete")},
    "dart": {("pub", "publish")}, "flutter": {("pub", "publish")},
}
DESTRUCTIVE_SQL = re.compile(r"\b(drop\s+(database|schema|table)|truncate\s+(table\s+)?\w|dropdatabase\s*\()", re.IGNORECASE)
SQL_CLIENTS = frozenset({"psql", "mysql", "mariadb", "sqlcmd", "sqlite3", "mongosh", "mongo", "cockroach"})
CLOUD_DELETE_PREFIXES = ("delete-", "terminate-", "deregister-", "remove-")
IAM_GRANT_PREFIXES = ("create-", "attach-", "put-", "update-", "add-")
CONTAINER_ESCAPE_FLAGS = frozenset({
    "--privileged", "--pid=host", "--net=host", "--network=host", "--ipc=host", "--userns=host",
    "--cap-add=all", "--cap-add=sys_admin",
})
CONTAINER_HOST_NAMESPACE_OPTIONS = {"--pid": "host", "--net": "host", "--network": "host", "--ipc": "host", "--cap-add": "all"}
SYSTEM_DIRS_ANY_DEPTH = re.compile(r"^/(bin|boot|dev|etc|lib|lib32|lib64|proc|sbin|sys|usr|System|Library)(/|$)")
SHALLOW_ROOT_PATH = re.compile(r"^/[^/]+(/[^/]+)?$")
SHALLOW_ROOT_DIRS = frozenset({"home", "Users", "var", "opt", "srv", "root", "mnt", "media", "Volumes", "private"})
CRITICAL_TARGETS = frozenset({"/", "/*", "~", "~/*", "$HOME", "${HOME}", "$HOME/*", "${HOME}/*", ".", "./*", "*", "..", "../*"})
VARIABLE_GLOB = re.compile(r"^\$\{?[A-Za-z0-9_@*]+\}?/\*?$")  # "$DIR/*" expands to "/*" when DIR is empty
WINDOWS_CRITICAL = re.compile(r"^[A-Za-z]:[\\/]?(\*|(Windows|Users|Program Files[^\\/]*)[\\/]?)?$", re.IGNORECASE)
DOWNLOADER_SUBSTITUTION = re.compile(r"(\$\(|`)\s*(curl|wget|iwr|irm)\b", re.IGNORECASE)


class Segment:
    """One simple command: its words, redirect targets, and the operator before it."""

    def __init__(self, op_before: str) -> None:
        self.op_before = op_before
        self.words: List[str] = []
        self.redirect_targets: List[str] = []


def finding(decision: str, rule_id: str, message: str) -> Decision:
    return decision, f"[{rule_id}] {message} Policy: " + POLICY_FILE


def strongest(results: Sequence[Optional[Decision]]) -> Optional[Decision]:
    """Return the first deny, else the first ask, else None."""
    for wanted in (DENY, ASK):
        for result in results:
            if result and result[0] == wanted:
                return result
    return None


# ----------------------------------------------------------------------------
# Tokenizing
# ----------------------------------------------------------------------------
def is_operator(token: str) -> bool:
    return bool(token) and all(char in OPERATOR_CHARS for char in token)


def tokenize(command: str) -> List[str]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n`")
    lexer.whitespace_split = True
    lexer.whitespace = " \t\r"
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError:  # unbalanced quotes: fall back to a coarse split
        return re.findall(r"[;&|\n()`<>]+|[^\s;&|\n()`<>]+", command)


def outside_quotes(line: str, position: int) -> bool:
    quote = ""
    escaped = False
    for char in line[:position]:
        if escaped:
            escaped = False
        elif char == "\\" and quote != "'":
            escaped = True
        elif quote:
            quote = "" if char == quote else quote
        elif char in "'\"":
            quote = char
    return not quote


def receives_shell(prefix: str) -> bool:
    words = strip_privilege(strip_wrappers(re.split(r"[;&|]", prefix)[-1].split()))
    return bool(words) and program_name(words[0]) in SHELLS


def extract_heredocs(command: str) -> Tuple[str, List[str]]:
    """Drop heredoc bodies; return bodies fed to a shell for separate inspection."""
    lines = command.split("\n")
    kept: List[str] = []
    shell_bodies: List[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        kept.append(line)
        index += 1
        for match in HEREDOC_START.finditer(line):
            if not outside_quotes(line, match.start()):
                continue
            body, end = read_heredoc_body(lines, index, match.group(3), match.group(1) == "-")
            if end is None:
                continue  # unterminated: keep analysing the following lines as commands
            index = end
            if receives_shell(line[: match.start()]):
                shell_bodies.append("\n".join(body))
    return "\n".join(kept), shell_bodies


def read_heredoc_body(lines: List[str], start: int, delimiter: str, strip_tabs: bool) -> Tuple[List[str], Optional[int]]:
    for index in range(start, len(lines)):
        candidate = lines[index].lstrip("\t") if strip_tabs else lines[index]
        if candidate == delimiter:
            return lines[start:index], index + 1
    return [], None


def split_segments(tokens: Sequence[str]) -> List[Segment]:
    segments = [Segment("start")]
    expecting_redirect_target = False
    for token in tokens:
        current = segments[-1]
        if expecting_redirect_target and not is_operator(token):
            current.redirect_targets.append(token)
            expecting_redirect_target = False
        elif token in REDIRECT_OPERATORS:
            if current.words and current.words[-1].isdigit():
                current.words.pop()  # file descriptor such as the 2 in 2>&1
            expecting_redirect_target = True
        elif is_operator(token):
            segments.append(Segment(classify_separator(token)))
            expecting_redirect_target = False
        else:
            current.words.append(token)
    return [segment for segment in segments if segment.words or segment.redirect_targets]


def classify_separator(token: str) -> str:
    if token in PIPE_OPERATORS:
        return "pipe"
    if token in SUBSTITUTION_OPERATORS or token == "`":
        return "substitution"
    return "sequence"


# ----------------------------------------------------------------------------
# Command normalization
# ----------------------------------------------------------------------------
def program_name(word: str) -> str:
    return word.replace("\\", "/").rsplit("/", 1)[-1].lower()


def skip_options(words: List[str], value_options: Sequence[str]) -> List[str]:
    index = 0
    while index < len(words) and words[index].startswith("-") and words[index] != "-":
        consumes_value = words[index] in value_options
        index += 2 if consumes_value else 1
        if words[index - (2 if consumes_value else 1)] == "--":
            break
    return words[index:]


def strip_runner(name: str, words: Sequence[str]) -> Optional[List[str]]:
    """Return the command a runner such as `uv run` or `npx` executes, or None."""
    subcommands, value_options = RUNNERS[name]
    rest = list(words[1:])
    if subcommands:
        if not rest or rest[0] not in subcommands:
            return None
        rest = rest[1:]
    return skip_options(rest, tuple(value_options))


def strip_wrappers(words: Sequence[str]) -> List[str]:
    """Remove env assignments, exec wrappers (env, timeout, xargs, ...), and runners (uv run, npx, ...)."""
    remaining = list(words)
    while remaining:
        name = program_name(remaining[0])
        if ENV_ASSIGNMENT.match(remaining[0]):
            remaining = remaining[1:]
        elif name in SIMPLE_WRAPPERS:
            remaining = skip_options(remaining[1:], ())
        elif name in VALUE_WRAPPERS:
            remaining = skip_options(remaining[1:], tuple(VALUE_WRAPPERS[name]))
            remaining = remaining[WRAPPERS_WITH_OPERAND.get(name, 0):]
        elif name in RUNNERS:
            executed = strip_runner(name, remaining)
            if executed is None:
                break
            remaining = executed
        else:
            break
    return remaining


def python_module(prog: str, args: List[str]) -> Tuple[str, List[str]]:
    """Treat `python -m <module> <args>` as `<module> <args>`."""
    if not PYTHON_PROGRAM.match(prog):
        return prog, args
    for index, arg in enumerate(args):
        if arg == "-m" and index + 1 < len(args):
            return program_name(args[index + 1]), args[index + 2:]
        if not arg.startswith("-"):
            break
    return prog, args


def strip_privilege(words: Sequence[str]) -> List[str]:
    remaining = list(words)
    while remaining and program_name(remaining[0]) in PRIVILEGE_COMMANDS:
        remaining = strip_wrappers(skip_options(remaining[1:], ("-u", "-g", "-C", "-p")))
    return remaining


def positional(args: Sequence[str]) -> List[str]:
    return [arg for arg in args if not arg.startswith("-")]


def short_flags(arg: str) -> str:
    return arg[1:] if re.match(r"^-[A-Za-z]+$", arg) else ""


def has_short_flag(args: Sequence[str], letter: str) -> bool:
    return any(letter in short_flags(arg) for arg in args)


# ----------------------------------------------------------------------------
# Path classification
# ----------------------------------------------------------------------------
def normalize_path(path: str) -> str:
    return path.strip("'\"").replace("\\", "/")


def is_secret_path(path: str) -> bool:
    normalized = normalize_path(path)
    basename = normalized.rstrip("/").rsplit("/", 1)[-1]
    if basename == ".env" or (basename.endswith(".env") and len(basename) > len(".env")):
        return True
    if basename.startswith(".env.") and basename[len(".env."):] not in ENV_EXAMPLE_SUFFIXES:
        return True
    return any(pattern.search(normalized) for pattern in SECRET_PATH_PATTERNS)


def is_critical_target(target: str) -> bool:
    normalized = normalize_path(target)
    trimmed = normalized.rstrip("/") or "/"
    if normalized in CRITICAL_TARGETS or trimmed in CRITICAL_TARGETS or VARIABLE_GLOB.match(normalized):
        return True
    if WINDOWS_CRITICAL.match(target) or SYSTEM_DIRS_ANY_DEPTH.match(trimmed):
        return True
    shallow = SHALLOW_ROOT_PATH.match(trimmed)
    return bool(shallow) and (trimmed.count("/") == 1 or trimmed.split("/")[1] in SHALLOW_ROOT_DIRS)


# ----------------------------------------------------------------------------
# Segment checks: each returns a Decision or None
# ----------------------------------------------------------------------------
def check_privilege(prog: str, args: List[str], tokens: List[str]) -> Optional[Decision]:
    if prog in PRIVILEGE_COMMANDS:
        return finding(DENY, "N-03", f"Privilege escalation via `{prog}` is never allowed.")
    launch_agent = prog == "launchctl" and positional(args)[:1] in (["load"], ["bootstrap"], ["submit"], ["enable"])
    if prog == "crontab" or launch_agent or (prog == "systemctl" and "enable" in args):
        return finding(DENY, "N-03", "Installing persistence on the host is never allowed.")
    return None


def check_agent_bypass(prog: str, args: List[str], tokens: List[str]) -> Optional[Decision]:
    lowered = [token.lower() for token in tokens]
    flagged = any(token in AGENT_BYPASS_FLAGS for token in lowered)
    for option, value in AGENT_BYPASS_OPTION_VALUES.items():
        pairs = zip(lowered, lowered[1:] + [""])
        flagged = flagged or any(t == f"{option}={value}" or (t == option and n == value) for t, n in pairs)
    if prog == "cursor-agent" and ("--force" in args or "-f" in args):
        flagged = True
    if flagged:
        return finding(DENY, "N-04", "Running an agent with approvals or sandbox disabled is never allowed.")
    return None


def secret_candidates(prog: str, args: List[str], redirect_targets: List[str]) -> List[str]:
    operands = [] if prog in LITERAL_PRINTERS else list(args)
    if prog in PATTERN_FIRST_PROGRAMS and not any(a in ("-e", "--regexp", "-f", "--file") for a in operands):
        first = next((i for i, a in enumerate(operands) if not a.startswith("-")), None)
        operands = operands if first is None else operands[:first] + operands[first + 1:]
    parts: List[str] = []
    for token in operands + list(redirect_targets):
        parts.extend(part.lstrip("@") for part in re.split(r"[=,]", token) if part)
    return parts


def check_secret_access(prog: str, args: List[str], redirect_targets: List[str]) -> Optional[Decision]:
    if any(is_secret_path(candidate) for candidate in secret_candidates(prog, args, redirect_targets)):
        return finding(DENY, "N-01", "Reading, writing, or copying secret files is never allowed.")
    return None


def git_subcommand(args: List[str]) -> Tuple[str, List[str], List[str]]:
    """Split `git <global options> <subcommand> <args>`; also return `-c` values."""
    configs: List[str] = []
    index = 0
    while index < len(args) and args[index].startswith("-"):
        option = args[index]
        if option in GIT_GLOBAL_VALUE_OPTIONS and index + 1 < len(args):
            if option == "-c":
                configs.append(args[index + 1])
            index += 2
        else:
            index += 1
    if index >= len(args):
        return "", [], configs
    return args[index].lower(), args[index + 1:], configs


def push_refspecs(args: List[str]) -> List[str]:
    remaining = skip_options(list(args), tuple(GIT_PUSH_VALUE_OPTIONS))
    operands = [arg for arg in remaining if not arg.startswith("-")]
    return operands[1:]  # the first operand is the remote


def is_protected_ref(refspec: str) -> bool:
    destination = refspec.lstrip("+").rsplit(":", 1)[-1]
    if destination.startswith("refs/heads/"):
        destination = destination[len("refs/heads/"):]
    return destination in PROTECTED_BRANCHES or bool(RELEASE_BRANCH.match(destination))


LEASE_PREFIX = "--force-with-lease"
LEASE_EXPECTATION = re.compile(r"^--force-with-lease=(?P<branch>[^:=\s]+):[0-9a-f]{7,64}$")
FORCE_PUSH_FLAGS = frozenset({"--force", "-f", "--mirror", "--delete", "-d", "--prune"})


def branch_name(ref: str) -> str:
    return ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref


def is_safe_force_with_lease(args: List[str], refspecs: List[str]) -> bool:
    """True for exactly one `--force-with-lease=<branch>:<sha>` plus `--force-if-includes`
    that rewrites only that same branch (a bare name, no `+`, `:`, or extra refs)."""
    leases = [a for a in args if a == LEASE_PREFIX or a.startswith(LEASE_PREFIX + "=")]
    expectation = LEASE_EXPECTATION.match(leases[0]) if len(leases) == 1 else None
    if not expectation or "--force-if-includes" not in args or len(refspecs) != 1:
        return False
    return branch_name(refspecs[0]) == branch_name(expectation.group("branch"))


def check_git_push(args: List[str]) -> Decision:
    refspecs = push_refspecs(args)
    uses_lease = "--force-if-includes" in args or any(a.startswith(LEASE_PREFIX) for a in args)
    rewrites_remote = any(a in FORCE_PUSH_FLAGS for a in args)
    rewrites_remote = rewrites_remote or has_short_flag(args, "f") or has_short_flag(args, "d")
    if rewrites_remote or any(ref.startswith(("+", ":")) for ref in refspecs):
        return finding(DENY, "N-05", "Force push and remote ref deletion are never allowed.")
    lease_branches = [a.split("=", 1)[1].rsplit(":", 1)[0] for a in args if a.startswith(LEASE_PREFIX + "=")]
    if any(is_protected_ref(ref) for ref in refspecs + lease_branches):
        return finding(DENY, "N-08", "Pushing directly to a protected branch is never allowed; open a pull request.")
    if uses_lease:
        if not is_safe_force_with_lease(args, refspecs):
            return finding(
                DENY, "N-05",
                "Only `--force-with-lease=<branch>:<sha> --force-if-includes <remote> <branch>` "
                "on a feature branch may be approved.",
            )
        return finding(ASK, "C-HITL-01", "Force push with an explicit lease on a feature branch requires human approval.")
    return finding(ASK, "C-HITL-01", "`git push` requires human approval.")


def commit_skips_hooks(args: List[str]) -> bool:
    index = 0
    while index < len(args):
        arg = args[index]
        letters = short_flags(arg)
        if arg == "--no-verify" or "n" in letters:
            return True
        index += 2 if letters and letters[-1] in GIT_COMMIT_VALUE_SHORT else 1
    return False


def check_git_local(subcommand: str, args: List[str]) -> Optional[Decision]:
    destructive = (
        (subcommand == "reset" and "--hard" in args)
        or (subcommand == "clean" and ("--force" in args or has_short_flag(args, "f")))
        or (subcommand == "branch" and has_short_flag(args, "D"))
        or (subcommand == "stash" and positional(args)[:1] in (["drop"], ["clear"]))
        or subcommand in ("filter-branch", "filter-repo")
    )
    if destructive:
        return finding(ASK, "C-HITL-03", f"Destructive `git {subcommand}` requires human approval.")
    return None


def changes_hooks_path(config_args: List[str]) -> bool:
    """True when `git config <config_args>` sets or unsets core.hooksPath; reading it is fine."""
    lowered = [arg.lower() for arg in config_args]
    if "core.hookspath" not in lowered:
        return False
    index = lowered.index("core.hookspath")
    before = set(lowered[:index])
    if before & GIT_CONFIG_READ_ACTIONS:
        return False
    return bool(before & GIT_CONFIG_UNSET_ACTIONS) or index + 1 < len(lowered)


def check_git(prog: str, args: List[str], tokens: List[str]) -> Optional[Decision]:
    if prog != "git":
        return None
    subcommand, sub_args, configs = git_subcommand(args)
    hooks_overridden = any(config.lower().startswith("core.hookspath") for config in configs)
    if hooks_overridden or (subcommand == "config" and changes_hooks_path(sub_args)):
        return finding(DENY, "N-04", "Overriding git hooks is never allowed.")
    skips_hooks = "--no-verify" in sub_args or (subcommand == "commit" and commit_skips_hooks(sub_args))
    if skips_hooks and subcommand in ("commit", "push", "merge", "rebase", "am", "cherry-pick"):
        return finding(DENY, "N-04", "Bypassing git hooks with --no-verify is never allowed.")
    if subcommand == "push":
        return check_git_push(sub_args)
    return check_git_local(subcommand, sub_args)


def check_github_cli(prog: str, args: List[str], tokens: List[str]) -> Optional[Decision]:
    if prog != "gh":
        return None
    words = positional(args)
    pair = tuple(words[:2])
    if pair == ("pr", "merge") or (pair == ("pr", "review") and any(a in ("--approve", "-a") for a in args)):
        return finding(DENY, "N-08", "Merging or approving pull requests is a human decision.")
    if pair == ("auth", "token") or (pair == ("auth", "status") and any(a in ("--show-token", "-t") for a in args)):
        return finding(DENY, "N-01", "Printing credentials is never allowed.")
    if pair == ("repo", "delete") or words[:1] in (["secret"], ["variable"]):
        return finding(DENY, "N-07", "Deleting repositories or managing secrets is never allowed.")
    if pair == ("gist", "create"):
        return finding(DENY, "N-09", "Uploading content to gists is never allowed.")
    if words[:1] == ["release"] and pair[1:] in (("create",), ("upload",), ("delete",), ("edit",)):
        return finding(DENY, "N-10", "Publishing releases is done by CI, never by an agent.")
    return None


def check_recursive_delete(prog: str, args: List[str], tokens: List[str]) -> Optional[Decision]:
    windows_recursive = prog in ("rmdir", "rd", "del", "erase") and any(a.lower() == "/s" for a in args)
    if windows_recursive:
        targets = [a for a in args if not a.startswith("/") or len(a) > 2]
        if any(is_critical_target(t) for t in targets):
            return finding(DENY, "N-05", "Recursive deletion of a drive or system directory is never allowed.")
        return finding(ASK, "C-HITL-03", "Recursive deletion requires human approval.")
    if prog != "rm" or not ("--recursive" in args or has_short_flag(args, "r") or has_short_flag(args, "R")):
        return None
    if any(is_critical_target(target) for target in positional(args)):
        return finding(DENY, "N-05", "Recursive deletion of root, home, workspace, or system paths is never allowed.")
    return finding(ASK, "C-HITL-03", "Recursive deletion requires human approval.")


def check_system_destruction(prog: str, args: List[str], tokens: List[str]) -> Optional[Decision]:
    disk_tool = prog.startswith("mkfs") or prog in ("fdisk", "sfdisk", "parted", "wipefs")
    disk_tool = disk_tool or (prog == "dd" and any(a.startswith("of=/dev/") for a in args))
    disk_tool = disk_tool or (prog == "diskutil" and any(a.lower() in ("erasedisk", "partitiondisk", "zerodisk") for a in args))
    power = prog in ("shutdown", "reboot", "halt", "poweroff") or (prog == "init" and args[:1] in (["0"], ["6"]))
    recursive_mode = prog in ("chmod", "chown", "chgrp") and ("-R" in args or "--recursive" in args)
    if disk_tool or power or (recursive_mode and any(is_critical_target(t) for t in positional(args)[1:])):
        return finding(DENY, "N-05", f"Irreversible system operation `{prog}` is never allowed.")
    return None


def check_publish(prog: str, args: List[str], tokens: List[str]) -> Optional[Decision]:
    words = positional(args)
    published = prog in PUBLISH_SUBCOMMANDS and words[:1] and words[0] in PUBLISH_SUBCOMMANDS[prog]
    pairs = PUBLISH_SUBCOMMAND_PAIRS.get(prog, set())
    published = published or any(tuple(words[: len(pair)]) == pair for pair in pairs)
    if published:
        return finding(DENY, "N-10", "Publishing packages or managing registry credentials is done by CI, never by an agent.")
    return None


def check_exfiltration(prog: str, args: List[str], tokens: List[str]) -> Optional[Decision]:
    lowered = [token.lower() for token in tokens]
    tunnel = prog in TUNNEL_PROGRAMS or (prog == "cloudflared" and "tunnel" in lowered)
    tunnel = tunnel or (prog == "ssh" and any(a.startswith("-R") for a in args))
    reverse_shell = prog in ("nc", "ncat", "netcat") and any(a in ("-e", "-c", "--exec", "--sh-exec") for a in args)
    reverse_shell = reverse_shell or (prog == "socat" and any(m in t for t in lowered for m in ("exec:", "system:")))
    reverse_shell = reverse_shell or any("/dev/tcp/" in t or "/dev/udp/" in t for t in lowered)
    exfil_host = prog in NETWORK_TOOLS and any(host in t for t in lowered for host in EXFIL_HOSTS)
    if tunnel or reverse_shell or exfil_host:
        return finding(DENY, "N-09", "Tunnels, reverse shells, and exfiltration endpoints are never allowed.")
    return None


SECRET_READ_SUBCOMMANDS = {  # program -> subcommand prefixes that print secrets or tokens
    "aws": ("secretsmanager get-secret-value", "configure get", "configure export-credentials"),
    "gcloud": ("auth print-", "secrets versions access"),
    "az": ("keyvault secret show", "account get-access-token"),
}


def reads_cloud_secret(prog: str, words: List[str], args: List[str]) -> bool:
    joined = " ".join(words[:3])
    if prog == "kubectl":
        return words[:1] == ["get"] and len(words) > 1 and words[1].startswith("secret")
    if prog == "aws" and words[:1] == ["ssm"] and "--with-decryption" in args:
        return True
    return joined.startswith(SECRET_READ_SUBCOMMANDS.get(prog, ()))


def destroys_iac(prog: str, first: List[str], args: List[str]) -> bool:
    if prog in ("terraform", "tofu", "terragrunt"):
        unattended = any(a in ("-destroy", "-auto-approve", "--auto-approve") for a in args)
        return first == ["destroy"] or (first == ["apply"] and unattended)
    if prog == "pulumi" and first == ["up"]:
        return "--yes" in args or "-y" in args
    return prog in ("pulumi", "cdk") and first == ["destroy"]


def destroys_cloud_resources(prog: str, words: List[str], args: List[str]) -> bool:
    if prog == "kubectl":
        namespace = words[1:2] in (["namespace"], ["namespaces"], ["ns"])
        return words[:1] == ["delete"] and (namespace or any(a in ("--all", "-A", "--all-namespaces") for a in args))
    if prog == "aws":
        bucket = words[:2] == ["s3", "rb"] or (words[:2] == ["s3", "rm"] and "--recursive" in args)
        iam_grant = words[:1] == ["iam"] and any(w.startswith(IAM_GRANT_PREFIXES) for w in words[1:2])
        return bucket or iam_grant or any(w.startswith(CLOUD_DELETE_PREFIXES) for w in words)
    if prog in ("gcloud", "az"):
        return "delete" in words or "add-iam-policy-binding" in words or words[:3] == ["role", "assignment", "create"]
    return False


def destroys_data(prog: str, args: List[str]) -> bool:
    if prog == "redis-cli":
        return any(a.upper() in ("FLUSHALL", "FLUSHDB") for a in args)
    return prog == "dropdb" or (prog in SQL_CLIENTS and bool(DESTRUCTIVE_SQL.search(" ".join(args))))


def check_infrastructure(prog: str, args: List[str], tokens: List[str]) -> Optional[Decision]:
    words = positional(args)
    if reads_cloud_secret(prog, words, args):
        return finding(DENY, "N-01", "Reading secrets from secret managers or printing tokens is never allowed.")
    if destroys_iac(prog, words[:1], args) or destroys_cloud_resources(prog, words, args) or destroys_data(prog, args):
        return finding(DENY, "N-07", "Destroying infrastructure or data, or granting IAM permissions, is never allowed.")
    return None


def mount_specs(args: List[str]) -> List[str]:
    specs = []
    for option, value in zip(args, args[1:] + [""]):
        if option in ("-v", "--volume", "--mount"):
            specs.append(value)
        elif option.startswith(("--volume=", "--mount=")):
            specs.append(option.split("=", 1)[1])
    return specs


def mounts_host_root(args: List[str]) -> bool:
    for spec in mount_specs(args):
        source = spec.split(":", 1)[0].replace("source=", "").replace("src=", "")
        if source == "/" or "docker.sock" in spec:
            return True
    return False


def check_container_escape(prog: str, args: List[str], tokens: List[str]) -> Optional[Decision]:
    if prog not in ("docker", "podman", "nerdctl") or positional(args)[:1] not in (["run"], ["create"]):
        return None
    lowered = [a.lower() for a in args]
    pairs = zip(lowered, lowered[1:] + [""])
    escape = any(a in CONTAINER_ESCAPE_FLAGS for a in lowered)
    escape = escape or any(CONTAINER_HOST_NAMESPACE_OPTIONS.get(a) == n for a, n in pairs) or mounts_host_root(args)
    if escape:
        return finding(DENY, "N-11", "Privileged containers and host mounts are never allowed.")
    return None


def check_nested_scripts(prog: str, args: List[str], depth: int) -> Optional[Decision]:
    script = ""
    if prog in SHELLS:
        flag_index = next((i for i, a in enumerate(args) if "c" in short_flags(a)), None)
        if flag_index is not None and flag_index + 1 < len(args):
            script = args[flag_index + 1]
    elif prog == "eval":
        script = " ".join(args)
    if not script:
        return None
    if DOWNLOADER_SUBSTITUTION.search(script):
        return finding(DENY, "N-06", "Executing downloaded code is never allowed.")
    return evaluate_command(script, depth + 1)


SEGMENT_CHECKS: Tuple[Callable[[str, List[str], List[str]], Optional[Decision]], ...] = (
    check_privilege, check_agent_bypass, check_git, check_github_cli, check_recursive_delete,
    check_system_destruction, check_publish, check_exfiltration, check_infrastructure, check_container_escape,
)


def evaluate_segment(segment: Segment, depth: int) -> Optional[Decision]:
    words = strip_wrappers(segment.words)
    if not words:
        return check_secret_access("", [], segment.redirect_targets)
    prog, args = python_module(program_name(words[0]), words[1:])
    tokens = words + segment.redirect_targets
    results: List[Optional[Decision]] = [check_privilege(prog, args, tokens), check_agent_bypass(prog, args, tokens)]
    results.append(check_secret_access(prog, args, segment.redirect_targets))
    results.extend(check(prog, args, tokens) for check in SEGMENT_CHECKS[2:])
    results.append(check_nested_scripts(prog, args, depth))
    return strongest(results)


def check_remote_execution(segments: Sequence[Segment]) -> Optional[Decision]:
    """Deny downloader output piped or substituted into an interpreter."""
    downloader_in_pipeline = False
    previous_program = ""
    for segment in segments:
        words = strip_privilege(strip_wrappers(segment.words))
        prog = program_name(words[0]) if words else ""
        if segment.op_before != "pipe":
            downloader_in_pipeline = False
        piped_into_interpreter = segment.op_before == "pipe" and downloader_in_pipeline and prog in INTERPRETERS
        substituted = segment.op_before == "substitution" and prog in DOWNLOADERS and previous_program in INTERPRETERS
        if piped_into_interpreter or substituted:
            return finding(DENY, "N-06", "Executing downloaded code is never allowed.")
        downloader_in_pipeline = downloader_in_pipeline or prog in DOWNLOADERS
        previous_program = prog
    return None


# ----------------------------------------------------------------------------
# Public entry points
# ----------------------------------------------------------------------------
def evaluate_command(command: str, depth: int = 0) -> Optional[Decision]:
    """Evaluate a shell command line against the N-tier and C-HITL rules."""
    if depth > MAX_NESTING_DEPTH or not command.strip():
        return None
    command, shell_bodies = extract_heredocs(command)
    segments = split_segments(tokenize(command))
    results: List[Optional[Decision]] = [check_remote_execution(segments)]
    results.extend(evaluate_segment(segment, depth) for segment in segments)
    results.extend(evaluate_command(body, depth + 1) for body in shell_bodies)
    return strongest(results)


def evaluate_file_write(path: str, content: str) -> Optional[Decision]:
    """Evaluate a file path (and the text written to it) for N-01 and N-04."""
    if is_secret_path(path):
        return finding(DENY, "N-01", "Reading or writing secret files is never allowed.")
    if AGENT_CONFIG_PATH.search(normalize_path(path)) and any(p.search(content) for p in GUARDRAIL_DISABLING_SETTINGS):
        return finding(DENY, "N-04", "Writing settings that disable approvals or the sandbox is never allowed.")
    return None


def written_text(tool_input: Dict[str, object]) -> str:
    texts = [tool_input.get(key) for key in ("content", "new_string", "newString", "code", "new_source", "text")]
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        texts.extend(edit.get("new_string") for edit in edits if isinstance(edit, dict))
    return "\n".join(text for text in texts if isinstance(text, str))


def evaluate_event(event: Dict[str, object]) -> Optional[Decision]:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    command = tool_input.get("command")
    if isinstance(command, str):
        return evaluate_command(command)
    path_keys = ("file_path", "filePath", "notebook_path", "path")
    path = next((tool_input[key] for key in path_keys if isinstance(tool_input.get(key), str)), None)
    return evaluate_file_write(path, written_text(tool_input)) if path else None


def main(stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
    try:
        event = json.load(stdin)
    except (ValueError, OSError):
        return 0
    result = evaluate_event(event) if isinstance(event, dict) else None
    if result:
        decision, reason = result
        output = {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": reason}
        json.dump({"hookSpecificOutput": output}, stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
