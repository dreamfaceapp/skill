#!/usr/bin/env python3
"""DreamAPI Image Editing — Colorize, Enhance, Outpainting, Inpainting, Swap Face, Remove BG.

Subcommands:
    colorize    Add color to B&W photos (requires human face)
    enhance     AI super-resolution / quality boost
    outpainting Extend image beyond its borders
    inpainting  Fill masked regions with AI-generated content
    swap-face   Replace face in target image
    remove-bg   Remove background from image

Usage:
    python image_edit.py colorize   run --url <image_url>
    python image_edit.py enhance    run --image <url|path>
    python image_edit.py outpainting run --url <url> --left 100 --right 100
    python image_edit.py inpainting run --url <url> --mask <url> --prompt "..."
    python image_edit.py swap-face  run --url <url> --face <url>
    python image_edit.py remove-bg  run --url <url|path>
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient
from shared.upload import resolve_local_file

COLORIZE_PATH = "/api/async/colorize"
ENHANCE_PATH = "/api/async/enhance"
OUTPAINTING_PATH = "/api/async/outpainting"
INPAINTING_PATH = "/api/async/inpainting"
SWAP_FACE_PATH = "/api/async/swap_face"
REMOVE_BG_PATH = "/api/async/remove_background"

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
# Tool definitions
# ---------------------------------------------------------------------------

def build_colorize_body(args) -> dict:
    return {"url": resolve_local_file(args.url, quiet=args.quiet)}


def add_colorize_args(p):
    p.add_argument("--url", required=True, help="B&W image URL or local path (must contain face)")


def build_enhance_body(args) -> dict:
    return {"imageUrl": resolve_local_file(args.image, quiet=args.quiet)}


def add_enhance_args(p):
    p.add_argument("--image", required=True, help="Image URL or local path to enhance")


def build_outpainting_body(args) -> dict:
    return {
        "url": resolve_local_file(args.url, quiet=args.quiet),
        "outPaintSize": {
            "left": args.left,
            "right": args.right,
            "top": args.top,
            "bottom": args.bottom,
        },
    }


def add_outpainting_args(p):
    p.add_argument("--url", required=True, help="Source image URL or local path")
    p.add_argument("--left", type=int, default=0, help="Pixels to expand left")
    p.add_argument("--right", type=int, default=0, help="Pixels to expand right")
    p.add_argument("--top", type=int, default=0, help="Pixels to expand top")
    p.add_argument("--bottom", type=int, default=0, help="Pixels to expand bottom")


def build_inpainting_body(args) -> dict:
    return {
        "url": resolve_local_file(args.url, quiet=args.quiet),
        "mask": resolve_local_file(args.mask, quiet=args.quiet),
        "prompt": args.prompt,
    }


def add_inpainting_args(p):
    p.add_argument("--url", required=True, help="Original image URL or local path")
    p.add_argument("--mask", required=True, help="Mask image URL (white=fill area)")
    p.add_argument("--prompt", required=True, help="What to generate in masked area")


def build_swap_face_body(args) -> dict:
    return {
        "url": resolve_local_file(args.url, quiet=args.quiet),
        "faceImgUrl": resolve_local_file(args.face, quiet=args.quiet),
    }


def add_swap_face_args(p):
    p.add_argument("--url", required=True, help="Target image (must contain one face)")
    p.add_argument("--face", required=True, help="Source face image URL or local path")


def build_remove_bg_body(args) -> dict:
    return {"url": resolve_local_file(args.url, quiet=args.quiet)}


def add_remove_bg_args(p):
    p.add_argument("--url", required=True, help="Image URL or local path")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TOOLS = {
    "colorize": {
        "endpoint": COLORIZE_PATH,
        "add_args": add_colorize_args,
        "build_body": build_colorize_body,
        "help": "Add color to B&W photos (requires human face)",
    },
    "enhance": {
        "endpoint": ENHANCE_PATH,
        "add_args": add_enhance_args,
        "build_body": build_enhance_body,
        "help": "AI super-resolution / quality boost",
    },
    "outpainting": {
        "endpoint": OUTPAINTING_PATH,
        "add_args": add_outpainting_args,
        "build_body": build_outpainting_body,
        "help": "Extend image beyond its borders",
    },
    "inpainting": {
        "endpoint": INPAINTING_PATH,
        "add_args": add_inpainting_args,
        "build_body": build_inpainting_body,
        "help": "Fill masked regions with AI content",
    },
    "swap-face": {
        "endpoint": SWAP_FACE_PATH,
        "add_args": add_swap_face_args,
        "build_body": build_swap_face_body,
        "help": "Replace face in target image",
    },
    "remove-bg": {
        "endpoint": REMOVE_BG_PATH,
        "add_args": add_remove_bg_args,
        "build_body": build_remove_bg_body,
        "help": "Remove background from image",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI Image Editing — colorize, enhance, outpainting, inpainting, swap face, remove bg.",
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
