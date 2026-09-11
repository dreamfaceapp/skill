#!/usr/bin/env python3
"""DreamAPI User Dashboard — check available credits.

Usage:
    python user.py credit          # show available credits
    python user.py credit --json   # output as JSON
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient

CREDITS_ENDPOINT = "/api/remaining_credits"


def _available_credits(data):
    if isinstance(data, (int, float)):
        return data
    if isinstance(data, dict) and "available_credits" in data:
        return data["available_credits"]
    return data


def cmd_credit(args):
    """Show available credits."""
    client = DreamAPIClient()
    data = client.post_form(CREDITS_ENDPOINT)

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Available credits: {_available_credits(data)}")


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI User Dashboard — account and billing info.",
    )

    sub = parser.add_subparsers(dest="subcommand")
    sub.required = True

    p_credit = sub.add_parser("credit", help="Show available credits")
    p_credit.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    handlers = {
        "credit": cmd_credit,
    }
    handlers[args.subcommand](args)


if __name__ == "__main__":
    main()
