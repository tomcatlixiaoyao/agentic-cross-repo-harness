#!/usr/bin/env python3
"""Scan a prospective public repository for common private-content indicators."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", "dist", "build"}
SKIP_FILES = {"scan_public.py"}
TEXT_SUFFIXES = {
    "",
    ".md",
    ".txt",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
    ".sh",
    ".ps1",
    ".mdc",
    ".gitignore",
}

PATTERNS = {
    "company/internal domain marker": re.compile(
        r"(?i)(?:iqiyi|qiyi|\.qae(?:/|\b)|\.domain(?:/|\b)|jsessionid)"
    ),
    "machine-specific absolute path": re.compile(
        r"(?i)(?:\b[A-Z]:[\\/]|/Users/[^/\s]+|/home/[^/\s]+)"
    ),
    "private key material": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "assigned secret-like value": re.compile(
        r"(?i)(?:app_secret|api_key|access_token|client_secret|password)\s*[:=]\s*[\"']?[A-Za-z0-9_+/=-]{16,}"
    ),
}


def scan(root: Path) -> list[str]:
    root = root.resolve()
    findings: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        suffix = path.suffix.lower() or (".gitignore" if path.name == ".gitignore" else "")
        if path.name.startswith(".env"):
            suffix = ".env"
        if suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(f"{relative}:{line_number}: {label}")
    return findings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    findings = scan(args.root)
    if findings:
        print("Public-content scan failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Public-content scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
