#!/usr/bin/env python3
"""DreamAPI Video Translate 2.0 — translate video speech to another language.

Supports English, Chinese, and Spanish with optional lip-sync.

Usage:
    python video_translate.py run --video <url> --source en --target zh [--lip-sync]
    python video_translate.py submit --video <url> --source en --target zh
    python video_translate.py query --task-id <id>
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient
from shared.upload import resolve_local_file

ENDPOINT = "/api/async/video_translate/2.0"
DEFAULT_TIMEOUT = 600
DEFAULT_INTERVAL = 5


def build_body(args) -> dict:
    return {
        "videoUrl": resolve_local_file(args.video, quiet=args.quiet),
        "sourceLanguage": args.source,
        "targetLanguage": args.target,
        "enableLipSync": args.lip_sync,
    }


def print_result(data, args, client):
    output = client.extract_output(data)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(output.get("output_url", ""))


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI Video Translate 2.0 — translate video speech.",
    )

    sub = parser.add_subparsers(dest="action")
    sub.required = True

    # run
    p_run = sub.add_parser("run", help="Submit + poll until done")
    p_run.add_argument("--video", required=True, help="Video URL or local path")
    p_run.add_argument("--source", required=True, choices=["en", "zh", "es"],
                       help="Source language")
    p_run.add_argument("--target", required=True, choices=["en", "zh", "es"],
                       help="Target language")
    p_run.add_argument("--lip-sync", type=bool, default=True,
                       help="Enable lip-sync (default: true)")
    p_run.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p_run.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    p_run.add_argument("--json", action="store_true")
    p_run.add_argument("-q", "--quiet", action="store_true")

    # submit
    p_submit = sub.add_parser("submit", help="Submit only")
    p_submit.add_argument("--video", required=True)
    p_submit.add_argument("--source", required=True, choices=["en", "zh", "es"])
    p_submit.add_argument("--target", required=True, choices=["en", "zh", "es"])
    p_submit.add_argument("--lip-sync", type=bool, default=True)
    p_submit.add_argument("--json", action="store_true")
    p_submit.add_argument("-q", "--quiet", action="store_true")

    # query
    p_query = sub.add_parser("query", help="Poll existing taskId")
    p_query.add_argument("--task-id", required=True)
    p_query.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p_query.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    p_query.add_argument("--json", action="store_true")
    p_query.add_argument("-q", "--quiet", action="store_true")

    args = parser.parse_args()
    client = DreamAPIClient()

    if args.action == "run":
        body = build_body(args)
        data = client.run_task(ENDPOINT, body, timeout=args.timeout,
                               interval=args.interval, quiet=args.quiet)
        print_result(data, args, client)
    elif args.action == "submit":
        body = build_body(args)
        task_id = client.submit_task(ENDPOINT, body, quiet=args.quiet)
        print(task_id)
    elif args.action == "query":
        data = client.poll_task(args.task_id, timeout=args.timeout,
                                interval=args.interval, verbose=not args.quiet)
        print_result(data, args, client)


if __name__ == "__main__":
    main()
