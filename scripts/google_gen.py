#!/usr/bin/env python3
"""DreamAPI Google — Google Gemini image generation (Nano Banana 2 & Nano Banana Pro).

Subcommands:
    nano-banana-2   Generate images with Gemini 3.1 Flash Image Preview model
    nano-banana-pro Generate images with Gemini 3 Pro Image Preview model

Usage:
    python google_gen.py nano-banana-2 run --text "..." [options]
    python google_gen.py nano-banana-pro run --text "..." [options]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient
from shared.upload import resolve_local_file

GEMINI_IMAGE_PATH = "/api/async/google_gemini_image"

DEFAULT_TIMEOUT = 600
DEFAULT_INTERVAL = 5


def add_poll_args(p):
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)


def add_output_args(p):
    p.add_argument("--json", action="store_true", help="Output full JSON")
    p.add_argument("-q", "--quiet", action="store_true")


def print_result(data, args, client):
    output = client.extract_output(data)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(output.get("output_url", ""))


# ---------------------------------------------------------------------------
# Nano Banana 2 — Gemini 3.1 Flash Image Preview
# ---------------------------------------------------------------------------

def build_nano_banana_2_body(args) -> dict:
    body = {
        "model": "gemini-3.1-flash-image-preview",
        "text": args.text,
    }
    if args.image_size:
        body["imageSize"] = args.image_size
    if args.aspect_ratio:
        body["aspectRatio"] = args.aspect_ratio
    if args.images:
        body["images"] = [resolve_local_file(img, quiet=args.quiet) for img in args.images]
    return body


def add_nano_banana_2_args(p):
    p.add_argument("--text", required=True,
                   help="Text prompt describing the image to generate")
    p.add_argument("--image-size", default=None,
                   choices=["512", "1K", "2K", "4K"],
                   help="Output resolution (default: 1K)")
    p.add_argument("--aspect-ratio", default=None,
                   help="Aspect ratio, e.g. 16:9, 1:1, 4:3")
    p.add_argument("--images", nargs="+", default=None,
                   help="Reference image URLs or local paths")


# ---------------------------------------------------------------------------
# Nano Banana Pro — Gemini 3 Pro Image Preview
# ---------------------------------------------------------------------------

def build_nano_banana_pro_body(args) -> dict:
    body = {
        "model": "gemini-3-pro-image-preview",
        "text": args.text,
    }
    if args.image_size:
        body["imageSize"] = args.image_size
    if args.aspect_ratio:
        body["aspectRatio"] = args.aspect_ratio
    if args.images:
        body["images"] = [resolve_local_file(img, quiet=args.quiet) for img in args.images]
    return body


def add_nano_banana_pro_args(p):
    p.add_argument("--text", required=True,
                   help="Text prompt describing the image to generate")
    p.add_argument("--image-size", default=None,
                   choices=["1K", "2K"],
                   help="Output resolution (default: 1K)")
    p.add_argument("--aspect-ratio", default=None,
                   help="Aspect ratio, e.g. 16:9, 1:1, 4:3")
    p.add_argument("--images", nargs="+", default=None,
                   help="Reference image URLs or local paths")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TOOLS = {
    "nano-banana-2": {
        "endpoint": GEMINI_IMAGE_PATH,
        "add_args": add_nano_banana_2_args,
        "build_body": build_nano_banana_2_body,
        "help": "Generate images with Gemini 3.1 Flash Image Preview (Nano Banana 2)",
    },
    "nano-banana-pro": {
        "endpoint": GEMINI_IMAGE_PATH,
        "add_args": add_nano_banana_pro_args,
        "build_body": build_nano_banana_pro_body,
        "help": "Generate images with Gemini 3 Pro Image Preview (Nano Banana Pro)",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI Google — Google Gemini image generation.",
    )

    tool_sub = parser.add_subparsers(dest="tool")
    tool_sub.required = True

    for tool_name, tool_info in TOOLS.items():
        tool_parser = tool_sub.add_parser(tool_name, help=tool_info["help"])
        action_sub = tool_parser.add_subparsers(dest="action")
        action_sub.required = True

        p_run = action_sub.add_parser("run", help="Submit + poll until done")
        tool_info["add_args"](p_run)
        add_poll_args(p_run)
        add_output_args(p_run)

        p_submit = action_sub.add_parser("submit", help="Submit only")
        tool_info["add_args"](p_submit)
        add_output_args(p_submit)

        p_query = action_sub.add_parser("query", help="Poll existing taskId")
        p_query.add_argument("--task-id", required=True)
        add_poll_args(p_query)
        add_output_args(p_query)

    args = parser.parse_args()
    client = DreamAPIClient()
    tool_info = TOOLS[args.tool]

    if args.action == "run":
        body = tool_info["build_body"](args)
        data = client.run_task(tool_info["endpoint"], body, timeout=args.timeout,
                               interval=args.interval, quiet=args.quiet)
        print_result(data, args, client)
    elif args.action == "submit":
        body = tool_info["build_body"](args)
        task_id = client.submit_task(tool_info["endpoint"], body, quiet=args.quiet)
        print(task_id)
    elif args.action == "query":
        data = client.poll_task(args.task_id, timeout=args.timeout,
                                interval=args.interval, verbose=not args.quiet)
        print_result(data, args, client)


if __name__ == "__main__":
    main()
