#!/usr/bin/env python3
"""DreamAPI Video Editing — Swap Face for Video, Video Matting, Composite After Matting, Video Watermark Remover.

Subcommands:
    swap-face        Replace faces in a video
    matting          Extract subject from video background (alpha channel)
    composite        Replace background of a matted video
    watermark-remover Remove watermarks from videos

Usage:
    python video_edit.py swap-face  run --src-video <url> --face <url|path>
    python video_edit.py matting    run --src-file <url>
    python video_edit.py composite  run --src-file <url> --alpha <url> --bg-type color --bg-color "232d84"
    python video_edit.py watermark-remover run --video <url>
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient
from shared.upload import resolve_local_file

SWAP_FACE_VIDEO_PATH = "/api/async/swap_face_for_video"
MATTING_PATH = "/api/async/image_matting_process_video"
COMPOSITE_PATH = "/api/async/image_matting_composite_video"
WATERMARK_REMOVER_PATH = "/api/async/video_watermark_remover"

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

    # Special handling for matting/composite results
    matting_result = data.get("mattingResult", {})
    if matting_result:
        if "mattingFileUrl" in matting_result:
            output["matting_file_url"] = matting_result["mattingFileUrl"]
            output["matting_alpha_url"] = matting_result.get("mattingAlphaFileUrl", "")
            output["output_url"] = matting_result["mattingFileUrl"]
        if "compositeFileUrl" in matting_result:
            output["composite_url"] = matting_result["compositeFileUrl"]
            output["output_url"] = matting_result["compositeFileUrl"]

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(output.get("output_url", ""))
        # For matting, also print alpha URL
        if "matting_alpha_url" in output and output["matting_alpha_url"]:
            print(f"  alpha: {output['matting_alpha_url']}")


# ---------------------------------------------------------------------------
# Swap Face for Video
# ---------------------------------------------------------------------------

def build_swap_face_body(args) -> dict:
    return {
        "srcVideoUrl": resolve_local_file(args.src_video, quiet=args.quiet),
        "srcImgUrl": resolve_local_file(args.face, quiet=args.quiet),
    }


def add_swap_face_args(p):
    p.add_argument("--src-video", required=True, help="Source video URL or path (max 5 min)")
    p.add_argument("--face", required=True, help="Face image URL or local path")


# ---------------------------------------------------------------------------
# Video Matting
# ---------------------------------------------------------------------------

def build_matting_body(args) -> dict:
    body = {"srcFileUrl": resolve_local_file(args.src_file, quiet=args.quiet)}
    if args.bit_rate:
        body["bitRate"] = args.bit_rate
    if args.remove_color_spill is not None:
        body["removeColorSpill"] = args.remove_color_spill
    return body


def add_matting_args(p):
    p.add_argument("--src-file", required=True, help="Source video URL (MP4 only)")
    p.add_argument("--bit-rate", default=None, help="Target bitrate (e.g. '16m')")
    p.add_argument("--remove-color-spill", type=bool, default=None,
                   help="Remove color fringes around subject")


# ---------------------------------------------------------------------------
# Composite After Matting
# ---------------------------------------------------------------------------

def build_composite_body(args) -> dict:
    body = {
        "srcFileUrl": resolve_local_file(args.src_file, quiet=args.quiet),
        "mattingAlphaFileUrl": args.alpha,
        "backgroundType": args.bg_type,
    }
    if args.bg_color:
        body["backgroundColor"] = args.bg_color
    if args.bg_url:
        body["backgroundUrl"] = resolve_local_file(args.bg_url, quiet=args.quiet)
    return body


def add_composite_args(p):
    p.add_argument("--src-file", required=True, help="Original source video URL")
    p.add_argument("--alpha", required=True, help="Alpha/matting video URL (from matting)")
    p.add_argument("--bg-type", required=True, choices=["color", "image", "video"],
                   help="Background type")
    p.add_argument("--bg-color", default=None, help="Hex color (e.g. '232d84') for color bg")
    p.add_argument("--bg-url", default=None, help="Background image/video URL or path")


# ---------------------------------------------------------------------------
# Video Watermark Remover
# ---------------------------------------------------------------------------

def build_watermark_remover_body(args) -> dict:
    body = {"video": resolve_local_file(args.video, quiet=args.quiet)}
    if args.prompt is not None:
        body["prompt"] = args.prompt
    if args.seed is not None:
        body["seed"] = args.seed
    return body


def add_watermark_remover_args(p):
    p.add_argument("--video", required=True, help="Video URL or path (max 2K resolution, 120s)")
    p.add_argument("--prompt", default=None, help="Optional prompt for watermark removal guidance")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducible results")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TOOLS = {
    "swap-face": {
        "endpoint": SWAP_FACE_VIDEO_PATH,
        "add_args": add_swap_face_args,
        "build_body": build_swap_face_body,
        "help": "Replace faces in a video",
    },
    "matting": {
        "endpoint": MATTING_PATH,
        "add_args": add_matting_args,
        "build_body": build_matting_body,
        "help": "Extract subject from video (alpha channel)",
    },
    "composite": {
        "endpoint": COMPOSITE_PATH,
        "add_args": add_composite_args,
        "build_body": build_composite_body,
        "help": "Replace background of matted video",
    },
    "watermark-remover": {
        "endpoint": WATERMARK_REMOVER_PATH,
        "add_args": add_watermark_remover_args,
        "build_body": build_watermark_remover_body,
        "help": "Remove watermarks from videos",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI Video Editing — swap face, matting, composite, watermark remover.",
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
