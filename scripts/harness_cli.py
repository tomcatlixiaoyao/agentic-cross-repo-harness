#!/usr/bin/env python3
"""Single entry point for initializing, checking, and diagnosing a Harness."""

from __future__ import annotations

import sys

import check_harness
import discover_harness
import doctor_harness
import init_harness
from harness_lib import HARNESS_VERSION


USAGE = """usage: harness <command> [options]

commands:
  discover  scan sibling Git repositories and draft a manifest
  init      generate a control repository
  check     validate a generated control repository
  doctor    explain coding-agent and repository readiness

Run 'harness <command> --help' for command-specific options.
"""


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print(USAGE)
        return 0
    if args[0] == "--version":
        print(f"harness {HARNESS_VERSION}")
        return 0
    command, command_args = args[0], args[1:]
    handlers = {
        "discover": discover_harness.main,
        "init": init_harness.main,
        "check": check_harness.main,
        "doctor": doctor_harness.main,
    }
    handler = handlers.get(command)
    if handler is None:
        print(f"error: unknown command: {command}\n", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    return handler(command_args)


if __name__ == "__main__":
    raise SystemExit(main())
