#!/usr/bin/env python3
"""Offline, read-only heuristics for selected GitHub Actions maintainer risks.

Not a YAML parser, vulnerability scanner, CI policy engine, or security verdict.
Never prints workflow content; inputs remain local and are not executed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

MAX_FILES = 100
MAX_DIRECTORY_ENTRIES = 1_000
MAX_FILE_BYTES = 262_144
SHA40 = re.compile(r"[a-fA-F0-9]{40}\Z")
DOCKER_DIGEST = re.compile(r"docker://[^\s@]+@sha256:[a-fA-F0-9]{64}\Z")
USES = re.compile(r"^\s*(?:-\s*)?uses\s*:\s*(\S+)")
PERMISSIONS = re.compile(r"^\s*permissions\s*:")
WRITE_ALL = re.compile(r"^\s*permissions\s*:\s*['\"]?write-all['\"]?\s*$")
RISKY_EVENT = re.compile(r"\b(pull_request_target|workflow_run)\b")
EVENT_KEY = re.compile(r"^\s*(pull_request_target|workflow_run)\s*:")
ON_LINE = re.compile(r"^\s*on\s*:")
UNTRUSTED_EXPRESSION = re.compile(
    r"\$\{\{\s*(?:github\.head_ref\b|github\.event\."
    r"(?:pull_request\.(?:title|body)|issue\.(?:title|body)|comment\.body)\b)",
    re.I,
)
PR_REF = re.compile(r"^\s*ref\s*:.*\$\{\{\s*github\."
                    r"(?:head_ref|event\.pull_request\.head\.)", re.I)
UNSAFE_CHECKOUT = re.compile(r"^\s*allow-unsafe-pr-checkout\s*:\s*true\s*$", re.I)


def _finding(code: str, path: str, line: int) -> dict[str, Any]:
    return {"code": code, "file": path, "line": line, "level": "REVIEW"}


def review_text(path: str, text: str) -> list[dict[str, Any]]:
    """Search deliberately limited textual patterns, with no claim of completeness."""
    findings: list[dict[str, Any]] = []
    has_permissions = False
    for number, raw in enumerate(text.splitlines(), 1):
        # Full-line and conventional space-hash YAML comments are ignored.
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        line = re.split(r"\s+#", raw, maxsplit=1)[0]
        if PERMISSIONS.match(line):
            has_permissions = True
        if WRITE_ALL.match(line):
            findings.append(_finding("BROAD_WRITE_ALL", path, number))
        if EVENT_KEY.match(line) or (ON_LINE.match(line) and RISKY_EVENT.search(line)):
            findings.append(_finding("PRIVILEGED_TRIGGER_REVIEW", path, number))
        if UNTRUSTED_EXPRESSION.search(line):
            findings.append(_finding("UNTRUSTED_EXPRESSION_REVIEW", path, number))
        if PR_REF.match(line):
            findings.append(_finding("UNTRUSTED_CHECKOUT_REF_REVIEW", path, number))
        if UNSAFE_CHECKOUT.match(line):
            findings.append(_finding("UNSAFE_PR_CHECKOUT_OPT_IN", path, number))
        matched = USES.match(line)
        if matched:
            value = matched.group(1).strip("'\"")
            if value.startswith("./"):
                continue  # Local actions still require normal code review.
            if value.startswith("docker://"):
                if not DOCKER_DIGEST.fullmatch(value):
                    findings.append(_finding("MUTABLE_CONTAINER_REFERENCE", path, number))
            elif "${{" in value:
                findings.append(_finding("DYNAMIC_ACTION_REFERENCE", path, number))
            elif "@" not in value or not SHA40.fullmatch(value.rsplit("@", 1)[-1]):
                findings.append(_finding("UNPINNED_ACTION", path, number))
    if not has_permissions:
        findings.append(_finding("NO_EXPLICIT_PERMISSIONS_FOUND", path, 0))
    return findings


def audit_root(root: Path) -> tuple[dict[str, Any], int]:
    """Read only .github/workflows direct YAML children; refuse symlink traversal."""
    report: dict[str, Any] = {
        "tool": "maintainer-workflow-review", "version": "0.1.1",
        "method": "conservative textual heuristics; not YAML parsing or a safety certificate",
        "workflow_count": 0, "findings": [],
    }
    try:
        if not root.is_dir() or root.is_symlink():
            return {**report, "outcome": "NOT_ASSESSED", "error": "INVALID_ROOT"}, 2
        base = root / ".github"
        folder = base / "workflows"
        if base.is_symlink() or folder.is_symlink():
            return {**report, "outcome": "NOT_ASSESSED", "error": "SYMLINK_DIRECTORY"}, 2
        if not folder.is_dir():
            return {**report, "outcome": "NOT_ASSESSED", "error": "NO_WORKFLOW_DIRECTORY"}, 2
        paths = []
        # scandir streams entries; Path.iterdir may eagerly materialize a directory.
        with os.scandir(folder) as entries:
            for count, entry in enumerate(entries, 1):
                if count > MAX_DIRECTORY_ENTRIES:
                    return {**report, "outcome": "NOT_ASSESSED", "error": "TOO_MANY_ENTRIES"}, 2
                path = folder / entry.name
                if path.suffix.lower() in {".yml", ".yaml"}:
                    paths.append(path)
                    if len(paths) > MAX_FILES:
                        return {**report, "outcome": "NOT_ASSESSED", "error": "TOO_MANY_FILES"}, 2
        if not paths:
            return {**report, "outcome": "NOT_ASSESSED", "error": "NO_WORKFLOWS"}, 2
        paths.sort(key=lambda path: path.name)
    except OSError:
        return {**report, "outcome": "NOT_ASSESSED", "error": "UNREADABLE_WORKFLOW_DIRECTORY"}, 2
    for path in paths:
        try:
            if path.is_symlink() or not path.is_file():
                return {**report, "outcome": "NOT_ASSESSED", "error": "INVALID_WORKFLOW_ENTRY"}, 2
            if path.stat().st_size > MAX_FILE_BYTES:
                return {**report, "outcome": "NOT_ASSESSED", "error": "FILE_TOO_LARGE"}, 2
            # Bound the actual allocation even if the file grows after stat().
            with path.open("rb") as handle:
                payload = handle.read(MAX_FILE_BYTES + 1)
            if len(payload) > MAX_FILE_BYTES:
                return {**report, "outcome": "NOT_ASSESSED", "error": "FILE_TOO_LARGE"}, 2
            text = payload.decode("utf-8", errors="strict")
        except (OSError, UnicodeDecodeError):
            return {**report, "outcome": "NOT_ASSESSED", "error": "UNREADABLE_WORKFLOW"}, 2
        report["findings"].extend(review_text(f".github/workflows/{path.name}", text))
        report["workflow_count"] += 1
    report["outcome"] = "REVIEW_REQUIRED" if report["findings"] else "NO_RULE_MATCHES"
    return report, (1 if report["findings"] else 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="local repository root (default: current directory)")
    args = parser.parse_args()
    result, status = audit_root(Path(args.root))
    print(json.dumps(result, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
