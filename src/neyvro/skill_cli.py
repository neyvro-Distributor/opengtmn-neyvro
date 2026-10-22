"""CLI for the canonical Neyvro Agent Skills library."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .skill_library import build, discover, deterministic_build, load, search, validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="neyvro-skills")
    parser.add_argument("--root", default="skills", help="canonical skill directory")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list skill metadata")
    load_parser = sub.add_parser("load", help="load one exact skill")
    load_parser.add_argument("name")
    search_parser = sub.add_parser("search", help="search metadata and content")
    search_parser.add_argument("query", nargs="+")
    sub.add_parser("validate", help="validate all skills")
    build_parser = sub.add_parser("build", help="generate deterministic artifacts")
    build_parser.add_argument("--output", default=".")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            print(json.dumps([skill.index_record() for skill in discover(args.root)], indent=2))
        elif args.command == "load":
            print(load(args.name, args.root).markdown, end="")
        elif args.command == "search":
            for skill, score in search(" ".join(args.query), args.root):
                print(f"{score}\t{skill.name}\t{skill.description}")
        elif args.command == "validate":
            errors = validate(args.root)
            if errors:
                for error in errors:
                    print(f"FAIL {error}")
                return 1
            skills = discover(args.root)
            print(f"All {len(skills)} skills valid")
        elif args.command == "build":
            build(args.root, args.output)
            if not deterministic_build(args.root, args.output):
                print("FAIL generated artifacts are not deterministic", file=sys.stderr)
                return 1
            print(f"Built {len(discover(args.root))} skills")
    except (OSError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
