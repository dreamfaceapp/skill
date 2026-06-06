#!/usr/bin/env python3
"""DreamAPI OpenAI — GPT Image 2 image generation.

Subcommands:
    gpt-image  Generate images using OpenAI's gpt-image-2 model

Usage:
    python open_ai.py gpt-image run --prompt "..." [--width 1024] [--height 1024] [--quality low] [--n 1] [--images <urls>]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient
from shared.upload import resolve_local_file

GPT_IMAGE_PATH = "/api/async/gpt_image"

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
        urls = output.get("images", [output.get("output_url", "")])
        for url in urls:
            print(url)


# ---------------------------------------------------------------------------
# GPT Image 2
# ---------------------------------------------------------------------------

def build_gpt_image_body(args) -> dict:
    body = {
        "prompt": args.prompt,
        "width": args.width,
        "height": args.height,
    }
    if args.quality:
        body["quality"] = args.quality
    if args.n:
        body["n"] = args.n
    if args.images:
        body["images"] = args.images
    return body


def add_gpt_image_args(p):
    p.add_argument("--prompt", required=True, help="Text description of the image (max 4000 chars)")
    p.add_argument("--width", type=int, default=1024,
                   help="Width in pixels (multiple of 16, 16-3840, default: 1024)")
    p.add_argument("--height", type=int, default=1024,
                   help="Height in pixels (multiple of 16, 16-3840, default: 1024)")
    p.add_argument("--quality", default="low", choices=["low", "medium", "high"],
                   help="Quality level (default: low)")
    p.add_argument("--n", type=int, default=1,
                   help="Number of images to generate (1-10, default: 1)")
    p.add_argument("--images", nargs="+", default=None,
                   help="Publicly accessible reference image URLs for image-to-image editing (max 4)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TOOLS = {
    "gpt-image": {
        "endpoint": GPT_IMAGE_PATH,
        "add_args": add_gpt_image_args,
        "build_body": build_gpt_image_body,
        "help": "Generate images using OpenAI's gpt-image-2 model",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI OpenAI — GPT Image 2 image generation.",
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
