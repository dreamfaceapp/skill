#!/usr/bin/env python3
"""DreamAPI Image Generation — Flux Text-to-Image, Flux Image-to-Image.

Subcommands:
    text2image   Generate images from text prompts
    image2image  Transform an image with text guidance

Usage:
    python image_gen.py text2image run --prompt "..." [--width 1024] [--height 1024] [--num 1]
    python image_gen.py image2image run --image <url|path> --prompt "..." [options]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient
from shared.upload import resolve_local_file

TEXT2IMAGE_PATH = "/api/async/flux_text2image"
IMAGE2IMAGE_PATH = "/api/async/flux_image2image"

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
# Text to Image
# ---------------------------------------------------------------------------

def build_text2image_body(args) -> dict:
    body = {
        "prompt": args.prompt,
        "width": args.width,
        "height": args.height,
    }
    if args.num:
        body["num"] = args.num
    if args.seed is not None:
        body["seed"] = args.seed
    return body


def add_text2image_args(p):
    p.add_argument("--prompt", required=True, help="Text description of the image")
    p.add_argument("--width", type=int, default=1024, help="Width in pixels (multiple of 16, max 1600)")
    p.add_argument("--height", type=int, default=1024, help="Height in pixels (multiple of 16, max 1600)")
    p.add_argument("--num", type=int, default=None, help="Number of images (1-10)")
    p.add_argument("--seed", type=int, default=None, help="Random seed")


# ---------------------------------------------------------------------------
# Image to Image
# ---------------------------------------------------------------------------

def build_image2image_body(args) -> dict:
    body = {
        "imageUrl": resolve_local_file(args.image, quiet=args.quiet),
        "prompt": args.prompt,
        "width": args.width,
        "height": args.height,
    }
    if args.num:
        body["num"] = args.num
    if args.seed is not None:
        body["seed"] = args.seed
    return body


def add_image2image_args(p):
    p.add_argument("--image", required=True, help="Reference image URL or local path")
    p.add_argument("--prompt", required=True, help="Text description of modifications")
    p.add_argument("--width", type=int, default=1024, help="Output width")
    p.add_argument("--height", type=int, default=1024, help="Output height")
    p.add_argument("--num", type=int, default=None, help="Number of images (1-10)")
    p.add_argument("--seed", type=int, default=None, help="Random seed")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TOOLS = {
    "text2image": {
        "endpoint": TEXT2IMAGE_PATH,
        "add_args": add_text2image_args,
        "build_body": build_text2image_body,
        "help": "Generate images from text prompts (Flux)",
    },
    "image2image": {
        "endpoint": IMAGE2IMAGE_PATH,
        "add_args": add_image2image_args,
        "build_body": build_image2image_body,
        "help": "Transform an image with text guidance (Flux)",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI Image Generation — text-to-image and image-to-image.",
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
