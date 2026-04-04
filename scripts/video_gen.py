#!/usr/bin/env python3
"""DreamAPI Video Generation — Text-to-Video, Image-to-Video, Head-Tail-to-Video (Wan2.1).

Subcommands:
    text2video   Generate video from text description
    image2video  Animate a static image into video
    head-tail    Generate transition between two frames

Usage:
    python video_gen.py text2video  run --prompt "..." [--resolution 480p]
    python video_gen.py image2video run --image <url|path> --prompt "..."
    python video_gen.py head-tail   run --first <url> --last <url> --prompt "..."
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient
from shared.upload import resolve_local_file

TEXT2VIDEO_PATH = "/api/async/wan/text_to_video/2.1"
IMAGE2VIDEO_PATH = "/api/async/wan/image_to_video/2.1"
HEADTAIL_PATH = "/api/async/wan/head_tail_to_video/2.1"

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
# Text to Video
# ---------------------------------------------------------------------------

def build_text2video_body(args) -> dict:
    body = {"prompt": args.prompt}
    if args.resolution:
        body["resolution"] = args.resolution
    return body


def add_text2video_args(p):
    p.add_argument("--prompt", required=True, help="Video description (max 1500 chars)")
    p.add_argument("--resolution", choices=["480p", "720p"], default=None,
                   help="Output resolution (default: 480p)")


# ---------------------------------------------------------------------------
# Image to Video
# ---------------------------------------------------------------------------

def build_image2video_body(args) -> dict:
    body = {
        "image": resolve_local_file(args.image, quiet=args.quiet),
        "prompt": args.prompt,
    }
    if args.resolution:
        body["resolution"] = args.resolution
    return body


def add_image2video_args(p):
    p.add_argument("--image", required=True, help="Source image URL or local path")
    p.add_argument("--prompt", required=True, help="Motion description (max 1500 chars)")
    p.add_argument("--resolution", choices=["480p", "720p"], default=None,
                   help="Output resolution (default: 480p)")


# ---------------------------------------------------------------------------
# Head-Tail to Video
# ---------------------------------------------------------------------------

def build_headtail_body(args) -> dict:
    return {
        "firstImage": resolve_local_file(args.first, quiet=args.quiet),
        "lastImage": resolve_local_file(args.last, quiet=args.quiet),
        "prompt": args.prompt,
    }


def add_headtail_args(p):
    p.add_argument("--first", required=True, help="Starting frame image URL or path")
    p.add_argument("--last", required=True, help="Ending frame image URL or path")
    p.add_argument("--prompt", required=True, help="Transition description (max 1500 chars)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TOOLS = {
    "text2video": {
        "endpoint": TEXT2VIDEO_PATH,
        "add_args": add_text2video_args,
        "build_body": build_text2video_body,
        "help": "Generate video from text description (Wan2.1)",
    },
    "image2video": {
        "endpoint": IMAGE2VIDEO_PATH,
        "add_args": add_image2video_args,
        "build_body": build_image2video_body,
        "help": "Animate a static image into video (Wan2.1)",
    },
    "head-tail": {
        "endpoint": HEADTAIL_PATH,
        "add_args": add_headtail_args,
        "build_body": build_headtail_body,
        "help": "Generate transition between two frames (Wan2.1)",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI Video Generation — text-to-video, image-to-video, head-tail.",
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
