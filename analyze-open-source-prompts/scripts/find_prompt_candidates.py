#!/usr/bin/env python3
"""Find candidate prompts, LLM calls, and tool schemas in a repository.

This script only surfaces candidates. A human or agent must still confirm
whether each hit is part of a real model call path.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".nuxt",
    ".turbo",
    ".cache",
}

TEXT_EXTENSIONS = {
    ".cjs",
    ".go",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".mjs",
    ".py",
    ".rs",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

FILENAME_PATTERNS = [
    ("filename", re.compile(r"prompt|template|instruction|system|agent|tool|schema", re.I)),
]

CONTENT_PATTERNS = [
    ("prompt-variable", re.compile(r"\b(system|user|developer)?_?prompts?\b|PromptTemplate|ChatPromptTemplate|instructions?\s*=", re.I)),
    ("model-api", re.compile(r"chat\.completions|responses\.create|openai\.ChatCompletion|anthropic\.messages|messages\.create|generate_content|streamText|generateText|completion\(", re.I)),
    ("framework", re.compile(r"langchain|langgraph|llama_index|crewai|autogen|litellm|google\.generativeai|create_react_agent|AgentExecutor|AssistantAgent", re.I)),
    ("tool-schema", re.compile(r"\btools?\b|tool_choice|function_call|input_schema|json_schema|zodToJsonSchema|server\.tool|list_tools|call_tool", re.I)),
    ("schema-shape", re.compile(r"\bproperties\b|\brequired\b|additionalProperties|z\.object|z\.string|z\.enum", re.I)),
]

SECRET_KEY_PATTERN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)(?:\s*=\s*|\s*:)")


@dataclass(frozen=True)
class Candidate:
    path: str
    line: int
    kind: str
    matched: str
    preview: str


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find candidate prompts, LLM calls, and tool schemas without printing secret values."
    )
    parser.add_argument("repo_root", help="Repository root to scan")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format",
    )
    parser.add_argument("--output", help="Write output to this path instead of stdout")
    return parser.parse_args(argv)


def iter_files(root: Path) -> Iterable[Path]:
    for current_root, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            path = Path(current_root) / name
            if should_scan(path):
                yield path


def should_scan(path: Path) -> bool:
    if path.name.startswith(".env"):
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def read_text(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw.decode("utf-8", errors="replace")
        except Exception:
            return None


def sanitize_preview(path: Path, line: str) -> str:
    stripped = line.strip()
    if path.name.startswith(".env"):
        match = SECRET_KEY_PATTERN.match(stripped)
        if match:
            return f"{match.group(1)}=<redacted>"
        return "<redacted-env-line>"
    return re.sub(r"\s+", " ", stripped)[:220]


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def collect_candidates(root: Path) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen: set[tuple[str, int, str, str]] = set()

    for path in iter_files(root):
        rel = relative(path, root)
        for kind, pattern in FILENAME_PATTERNS:
            if pattern.search(path.name):
                key = (rel, 0, kind, path.name)
                if key not in seen:
                    seen.add(key)
                    candidates.append(Candidate(rel, 0, kind, path.name, "filename match"))

        text = read_text(path)
        if text is None:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            if path.name.startswith(".env"):
                env_match = SECRET_KEY_PATTERN.match(line.strip())
                if env_match:
                    key_name = env_match.group(1)
                    key = (rel, line_number, "env-key", key_name)
                    if key not in seen:
                        seen.add(key)
                        candidates.append(
                            Candidate(
                                path=rel,
                                line=line_number,
                                kind="env-key",
                                matched=key_name,
                                preview=sanitize_preview(path, line),
                            )
                        )
                continue

            for kind, pattern in CONTENT_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                matched = match.group(0)
                key = (rel, line_number, kind, matched.lower())
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(
                    Candidate(
                        path=rel,
                        line=line_number,
                        kind=kind,
                        matched=matched,
                        preview=sanitize_preview(path, line),
                    )
                )

    return candidates


def render_markdown(candidates: list[Candidate], root: Path) -> str:
    lines = [
        "# Prompt Candidate Scan",
        "",
        f"- Root: `{root}`",
        f"- Candidates: {len(candidates)}",
        "",
        "| Kind | Location | Match | Preview |",
        "|------|----------|-------|---------|",
    ]
    for item in candidates:
        location = f"`{item.path}`" if item.line == 0 else f"`{item.path}:{item.line}`"
        lines.append(
            f"| {escape_md(item.kind)} | {location} | `{escape_md(item.matched)}` | {escape_md(item.preview)} |"
        )
    lines.append("")
    return "\n".join(lines)


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_json(candidates: list[Candidate], root: Path) -> str:
    payload = {
        "root": str(root),
        "count": len(candidates),
        "candidates": [asdict(item) for item in candidates],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.repo_root).expanduser().resolve()
    if not root.exists():
        print(f"error: repo root does not exist: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"error: repo root is not a directory: {root}", file=sys.stderr)
        return 2

    candidates = collect_candidates(root)
    if args.format == "json":
        output = render_json(candidates, root)
    else:
        output = render_markdown(candidates, root)

    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
