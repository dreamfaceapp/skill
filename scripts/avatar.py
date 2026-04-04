#!/usr/bin/env python3
"""DreamAPI Avatar tools — LipSync, LipSync 2.0, DreamAvatar 3.0 Fast, Dreamact.

Subcommands:
    lipsync      Audio-driven talking face (v1)
    lipsync2     Improved lip sync with vocal separation (v2.0)
    dreamavatar  Image + audio → talking avatar video (3.0 Fast)
    dreamact     Motion-driven avatar with driving video

Each subcommand supports: run (submit+poll), submit (submit only), query (poll existing task).

Usage:
    python avatar.py lipsync    run --src-video <url> --audio <url> [options]
    python avatar.py lipsync2   run --src-video <url> --audio <url> [options]
    python avatar.py dreamavatar run --image <url|path> --audio <url|path> --prompt "..." [options]
    python avatar.py dreamact   run --video <url|path> --images <url> [<url>...] [options]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient
from shared.upload import resolve_local_file

# Endpoints
LIPSYNC_PATH = "/api/async/lipsync"
LIPSYNC2_PATH = "/api/async/lipsync/2.0"
DREAMAVATAR_PATH = "/api/async/dreamavatar/image_to_video/3.0fast"
DREAMACT_PATH = "/api/async/wan/dreamact/2.1"

DEFAULT_TIMEOUT = 600
DEFAULT_INTERVAL = 5


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def add_poll_args(p):
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                   help=f"Max polling time in seconds (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                   help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL})")


def add_output_args(p):
    p.add_argument("--json", action="store_true", help="Output full JSON response")
    p.add_argument("-q", "--quiet", action="store_true", help="Suppress status messages")


def print_result(data: dict, args, client: DreamAPIClient):
    """Print task result."""
    output = client.extract_output(data)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        url = output.get("output_url", "")
        if url:
            print(url)
        else:
            print(json.dumps(output, indent=2, ensure_ascii=False))


def handle_run(client, endpoint, body, args):
    data = client.run_task(endpoint, body, timeout=args.timeout,
                           interval=args.interval, quiet=args.quiet)
    print_result(data, args, client)


def handle_submit(client, endpoint, body, args):
    task_id = client.submit_task(endpoint, body, quiet=args.quiet)
    print(task_id)


def handle_query(client, args):
    data = client.poll_task(args.task_id, timeout=args.timeout,
                            interval=args.interval, verbose=not args.quiet)
    print_result(data, args, client)


# ---------------------------------------------------------------------------
# LipSync
# ---------------------------------------------------------------------------

def build_lipsync_body(args) -> dict:
    body = {
        "srcVideoUrl": resolve_local_file(args.src_video, quiet=args.quiet),
        "audioUrl": resolve_local_file(args.audio, quiet=args.quiet),
        "videoParams": {
            "video_width": args.video_width,
            "video_height": args.video_height,
            "video_enhance": args.video_enhance,
        },
    }
    return body


def add_lipsync_args(p):
    p.add_argument("--src-video", required=True, help="Source video URL or local path")
    p.add_argument("--audio", required=True, help="Driving audio URL or local path")
    p.add_argument("--video-width", type=int, default=0, help="Output width (0=original)")
    p.add_argument("--video-height", type=int, default=0, help="Output height (0=original)")
    p.add_argument("--video-enhance", type=bool, default=False, help="Enable enhancement")


# ---------------------------------------------------------------------------
# LipSync 2.0
# ---------------------------------------------------------------------------

def build_lipsync2_body(args) -> dict:
    body = {
        "srcVideoUrl": resolve_local_file(args.src_video, quiet=args.quiet),
        "audioUrl": resolve_local_file(args.audio, quiet=args.quiet),
        "videoParams": {
            "video_width": args.video_width,
            "video_height": args.video_height,
            "video_enhance": args.video_enhance,
        },
    }
    if args.vocal_audio:
        body["vocalAudioUrl"] = resolve_local_file(args.vocal_audio, quiet=args.quiet)
    if args.fps:
        body["fps"] = args.fps
    return body


def add_lipsync2_args(p):
    p.add_argument("--src-video", required=True, help="Source video URL or local path")
    p.add_argument("--audio", required=True, help="Original audio URL or local path")
    p.add_argument("--vocal-audio", default=None, help="Vocal-only audio URL (optional)")
    p.add_argument("--video-width", type=int, default=0, help="Output width (0=original)")
    p.add_argument("--video-height", type=int, default=0, help="Output height (0=original)")
    p.add_argument("--video-enhance", type=int, default=1, help="Enhancement level (0=off, 1=on)")
    p.add_argument("--fps", default=None, help="Frame rate (default: 25)")


# ---------------------------------------------------------------------------
# DreamAvatar 3.0 Fast
# ---------------------------------------------------------------------------

def build_dreamavatar_body(args) -> dict:
    body = {
        "image": resolve_local_file(args.image, quiet=args.quiet),
        "audio": resolve_local_file(args.audio, quiet=args.quiet),
        "prompt": args.prompt,
    }
    if args.resolution:
        body["resolution"] = args.resolution
    return body


def add_dreamavatar_args(p):
    p.add_argument("--image", required=True, help="Portrait image URL or local path")
    p.add_argument("--audio", required=True, help="Audio URL or local path (max 3 min)")
    p.add_argument("--prompt", required=True, help="Text prompt to guide generation style")
    p.add_argument("--resolution", choices=["480p", "720p"], default=None,
                   help="Output resolution (default: 480p)")


# ---------------------------------------------------------------------------
# Dreamact
# ---------------------------------------------------------------------------

def build_dreamact_body(args) -> dict:
    body = {
        "video": resolve_local_file(args.video, quiet=args.quiet),
        "images": [resolve_local_file(img, quiet=args.quiet) for img in args.images],
    }
    if args.seed is not None:
        body["seed"] = args.seed
    return body


def add_dreamact_args(p):
    p.add_argument("--video", required=True, help="Driving video URL or local path (max 1 min)")
    p.add_argument("--images", nargs="+", required=True,
                   help="Reference image URLs or local paths")
    p.add_argument("--seed", type=int, default=None, help="Seed for reproducibility")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TOOLS = {
    "lipsync": {
        "endpoint": LIPSYNC_PATH,
        "add_args": add_lipsync_args,
        "build_body": build_lipsync_body,
        "help": "Audio-driven talking face (v1)",
    },
    "lipsync2": {
        "endpoint": LIPSYNC2_PATH,
        "add_args": add_lipsync2_args,
        "build_body": build_lipsync2_body,
        "help": "Improved lip sync with vocal separation (v2.0)",
    },
    "dreamavatar": {
        "endpoint": DREAMAVATAR_PATH,
        "add_args": add_dreamavatar_args,
        "build_body": build_dreamavatar_body,
        "help": "Image + audio → talking avatar video (3.0 Fast)",
    },
    "dreamact": {
        "endpoint": DREAMACT_PATH,
        "add_args": add_dreamact_args,
        "build_body": build_dreamact_body,
        "help": "Motion-driven avatar with driving video",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI Avatar — talking face, avatar, and motion-driven video tools.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    tool_sub = parser.add_subparsers(dest="tool")
    tool_sub.required = True

    for tool_name, tool_info in TOOLS.items():
        tool_parser = tool_sub.add_parser(tool_name, help=tool_info["help"])
        action_sub = tool_parser.add_subparsers(dest="action")
        action_sub.required = True

        # run
        p_run = action_sub.add_parser("run", help="Submit + poll until done (default)")
        tool_info["add_args"](p_run)
        add_poll_args(p_run)
        add_output_args(p_run)

        # submit
        p_submit = action_sub.add_parser("submit", help="Submit only, print taskId")
        tool_info["add_args"](p_submit)
        add_output_args(p_submit)

        # query
        p_query = action_sub.add_parser("query", help="Poll existing taskId")
        p_query.add_argument("--task-id", required=True, help="taskId to poll")
        add_poll_args(p_query)
        add_output_args(p_query)

    args = parser.parse_args()
    client = DreamAPIClient()
    tool_info = TOOLS[args.tool]

    if args.action == "run":
        body = tool_info["build_body"](args)
        handle_run(client, tool_info["endpoint"], body, args)
    elif args.action == "submit":
        body = tool_info["build_body"](args)
        handle_submit(client, tool_info["endpoint"], body, args)
    elif args.action == "query":
        handle_query(client, args)


if __name__ == "__main__":
    main()
