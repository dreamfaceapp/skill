#!/usr/bin/env python3
"""DreamAPI ByteDance — Seedance 2.5/2.0 video generation and Seedream image generation.

Subcommands:
    seedance-2.5  Generate video with text/image/video/audio inputs (Seedance 2.5, 480p/720p only)
    seedance       Generate video with text/image/video/audio inputs (Seedance 2.0)
    seedance-mini  Generate video with text/image inputs at lowest cost (Seedance 2.0 Mini)
    seedream       Generate high-quality images from text prompts (Seedream 4.0/4.5/5.0 Lite/5.0 Pro)

Usage:
    python byte_dance.py seedance-2.5 run --prompt "..." --resolution <480p|720p> --duration <4-30> [--image-url <url>] [--end-image-url <url>] [options]
    python byte_dance.py seedance run --prompt "..." --resolution <480p|720p|1080p|4k> --duration <4-15> [--image-url <url>] [--end-image-url <url>] [options]
    python byte_dance.py seedance-mini run --prompt "..." --resolution <480p|720p> --duration <4-15> [--image-url <url>] [--end-image-url <url>] [options]
    python byte_dance.py seedream run --prompt "..." [options]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient
from shared.upload import resolve_local_file

SEEDANCE_2_5_PATH = "/api/async/seedance_2.5"
SEEDANCE_PATH = "/api/async/seedance_2.0"
SEEDREAM_PATH = "/api/async/seedream"

DEFAULT_TIMEOUT = 600
DEFAULT_INTERVAL = 5


def add_poll_args(p):
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)


def add_output_args(p):
    p.add_argument("--json", action="store_true", help="Output full JSON")
    p.add_argument("-q", "--quiet", action="store_true")


def add_seedance_frame_args(p):
    p.add_argument("--image-url", default=None, dest="image_url",
                   help="First-frame image URL or local path (JPEG/PNG/WebP). Enables image-to-video mode.")
    p.add_argument("--end-image-url", default=None, dest="end_image_url",
                   help="Last-frame image URL or local path. Only valid with --image-url (JPEG/PNG/WebP).")


def apply_seedance_frame_body(body: dict, args) -> dict:
    if args.image_url is not None:
        body["imageUrl"] = resolve_local_file(args.image_url, quiet=args.quiet)
    if args.end_image_url is not None:
        body["endImageUrl"] = resolve_local_file(args.end_image_url, quiet=args.quiet)
    return body


def print_result(data, args, client):
    output = client.extract_output(data)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(output.get("output_url", ""))


# ---------------------------------------------------------------------------
# Seedance 2.5
# ---------------------------------------------------------------------------

def build_seedance_2_5_body(args) -> dict:
    body = {
        "model": "seedance-2.5",
        "prompt": args.prompt,
        "resolution": args.resolution,
        "duration": args.duration,
    }
    if args.images:
        body["images"] = [resolve_local_file(img, quiet=args.quiet) for img in args.images]
    if args.videos:
        body["videos"] = args.videos
    if args.audios:
        body["audios"] = args.audios
    if args.ratio:
        body["ratio"] = args.ratio
    if args.seed is not None:
        body["seed"] = args.seed
    if args.generate_audio:
        body["generateAudio"] = True
    return apply_seedance_frame_body(body, args)


def add_seedance_2_5_args(p):
    p.add_argument("--prompt", required=True, help="Video description (max 1500 chars)")
    p.add_argument("--resolution", required=True, choices=["480p", "720p"],
                   help="Output resolution (480p or 720p only)")
    p.add_argument("--duration", required=True, type=int,
                   help="Video duration in seconds (4-30)")
    p.add_argument("--images", nargs="+", default=None,
                   help="Reference image URLs or local paths (max 9)")
    add_seedance_frame_args(p)
    p.add_argument("--videos", nargs="+", default=None,
                   help="Reference video URLs (max 3, total max 15s)")
    p.add_argument("--audios", nargs="+", default=None,
                   help="Audio URLs (max 3)")
    p.add_argument("--ratio", default="adaptive",
                   help="Aspect ratio (default: adaptive)")
    p.add_argument("--seed", type=int, default=None,
                   help="Random seed for reproducible results")
    p.add_argument("--generate-audio", action="store_true",
                   help="Generate audio for the video")


# ---------------------------------------------------------------------------
# Seedance 2.0
# ---------------------------------------------------------------------------

def build_seedance_body(args) -> dict:
    body = {
        "model": "seedance-2.0",
        "prompt": args.prompt,
        "resolution": args.resolution,
        "duration": args.duration,
    }
    if args.images:
        body["images"] = [resolve_local_file(img, quiet=args.quiet) for img in args.images]
    if args.videos:
        body["videos"] = args.videos
    if args.audios:
        body["audios"] = args.audios
    if args.ratio:
        body["ratio"] = args.ratio
    if args.seed is not None:
        body["seed"] = args.seed
    if args.generate_audio:
        body["generateAudio"] = True
    return apply_seedance_frame_body(body, args)


def add_seedance_args(p):
    p.add_argument("--prompt", required=True, help="Video description (max 1500 chars)")
    p.add_argument("--resolution", required=True, choices=["480p", "720p", "1080p", "4k"],
                   help="Output resolution")
    p.add_argument("--duration", required=True, type=int,
                   help="Video duration in seconds (4-15)")
    p.add_argument("--images", nargs="+", default=None,
                   help="Reference image URLs or local paths (max 9)")
    add_seedance_frame_args(p)
    p.add_argument("--videos", nargs="+", default=None,
                   help="Reference video URLs (max 3, total max 15s)")
    p.add_argument("--audios", nargs="+", default=None,
                   help="Audio URLs (max 3)")
    p.add_argument("--ratio", default="adaptive",
                   help="Aspect ratio (default: adaptive)")
    p.add_argument("--seed", type=int, default=None,
                   help="Random seed for reproducible results")
    p.add_argument("--generate-audio", action="store_true",
                   help="Generate audio for the video")


# ---------------------------------------------------------------------------
# Seedance 2.0 Mini
# ---------------------------------------------------------------------------

def build_seedance_mini_body(args) -> dict:
    body = {
        "model": "seedance-2.0-mini",
        "prompt": args.prompt,
        "resolution": args.resolution,
        "duration": args.duration,
    }
    if args.images:
        body["images"] = [resolve_local_file(img, quiet=args.quiet) for img in args.images]
    if args.videos:
        body["videos"] = args.videos
    if args.audios:
        body["audios"] = args.audios
    if args.ratio:
        body["ratio"] = args.ratio
    if args.seed is not None:
        body["seed"] = args.seed
    if args.generate_audio:
        body["generateAudio"] = True
    return apply_seedance_frame_body(body, args)


def add_seedance_mini_args(p):
    p.add_argument("--prompt", required=True, help="Video description (max 1500 chars)")
    p.add_argument("--resolution", required=True, choices=["480p", "720p"],
                   help="Output resolution (480p or 720p only)")
    p.add_argument("--duration", required=True, type=int,
                   help="Video duration in seconds (4-15)")
    p.add_argument("--images", nargs="+", default=None,
                   help="Reference image URLs or local paths (max 9)")
    add_seedance_frame_args(p)
    p.add_argument("--videos", nargs="+", default=None,
                   help="Reference video URLs (max 3, total max 15s)")
    p.add_argument("--audios", nargs="+", default=None,
                   help="Audio URLs (max 3)")
    p.add_argument("--ratio", default="adaptive",
                   help="Aspect ratio (default: adaptive)")
    p.add_argument("--seed", type=int, default=None,
                   help="Random seed for reproducible results")
    p.add_argument("--generate-audio", action="store_true",
                   help="Generate audio for the video")


# ---------------------------------------------------------------------------
# Seedream
# ---------------------------------------------------------------------------

# Total-pixel floors are width*height, not each edge. 2048x2048 is valid for
# Lite/4.5; 1920x1080 is not. Tiers and ranges follow Ark 图片生成 API.
SEEDREAM_SIZE_LIMITS = {
    "seedream-5.0-pro": {
        "min_pixels": 921600,
        "max_pixels": 4624220,
        "tiers": frozenset({"1K", "1.5K", "2K"}),
    },
    "seedream-5.0-lite": {
        "min_pixels": 3686400,
        "max_pixels": 16777216,
        "tiers": frozenset({"2K", "3K", "4K"}),
    },
    "seedream-4.5": {
        "min_pixels": 3686400,
        "max_pixels": 16777216,
        "tiers": frozenset({"2K", "4K"}),
    },
    "seedream-4.0": {
        "min_pixels": 921600,
        "max_pixels": 16777216,
        "tiers": frozenset({"1K", "2K", "4K"}),
    },
}

SEEDREAM_SIZE_HELP = (
    'Image size. Custom WIDTHxHEIGHT is total pixels (not each edge). '
    'seedream-5.0-pro: min 1280x720 (921,600 px), max 4,624,220 px; '
    'tiers 1K/1.5K/2K only (no 3K/4K). Typical 1K/1.5K bill at 12 credits. '
    'seedream-4.0: min 1280x720 (921,600 px); tiers 1K/2K/4K. '
    'seedream-5.0-lite / seedream-4.5: min 2560x1440 (3,686,400 px), no 1K; '
    'tiers 2K/3K/4K (Lite) or 2K/4K (4.5). '
    'Do not use 1024x1024 or 1920x1080 on Lite/4.5.'
)


def seedream_size_error(model: str, size: str) -> str | None:
    """Return an error message if size is illegal for this Seedream model."""
    limits = SEEDREAM_SIZE_LIMITS.get(model)
    if limits is None:
        return f"Unknown Seedream model: {model}"

    normalized = size.strip().upper().replace(" ", "")
    if normalized in limits["tiers"]:
        return None

    parts = normalized.lower().replace("*", "x").split("x")
    if len(parts) != 2:
        allowed = ", ".join(sorted(limits["tiers"]))
        return (
            f"Invalid --size {size!r} for {model}. "
            f"Use WIDTHxHEIGHT or one of: {allowed}."
        )

    try:
        width = int(parts[0])
        height = int(parts[1])
    except ValueError:
        return f"Invalid --size {size!r}: width and height must be integers."

    total = width * height
    min_pixels = limits["min_pixels"]
    max_pixels = limits["max_pixels"]
    if total < min_pixels or total > max_pixels:
        return (
            f"--size {size} is {total} pixels, outside {model} range "
            f"[{min_pixels}, {max_pixels}]."
        )
    return None


def build_seedream_body(args) -> dict:
    body = {
        "model": args.model,
        "prompt": args.prompt,
    }
    if args.image:
        body["image"] = [resolve_local_file(img, quiet=args.quiet) for img in args.image]
    if args.size:
        size_err = seedream_size_error(args.model, args.size)
        if size_err is not None:
            print(size_err, file=sys.stderr)
            sys.exit(1)
        body["size"] = args.size
    if args.seed is not None:
        body["seed"] = args.seed
    return body


def add_seedream_args(p):
    p.add_argument("--model", default="seedream-5.0-pro",
                   choices=["seedream-5.0-pro", "seedream-5.0-lite", "seedream-4.5", "seedream-4.0"],
                   help="Model version (default: seedream-5.0-pro)")
    p.add_argument("--prompt", required=True,
                   help="Text prompt describing the image content to generate. Supports Chinese and English.")
    p.add_argument("--image", nargs="+", default=None,
                   help="Reference image URLs or local paths for img2img (max 10). API field: image (array). Formats: jpeg, png, webp, bmp, tiff, gif, heic, heif.")
    p.add_argument("--size", default=None, help=SEEDREAM_SIZE_HELP)
    p.add_argument("--seed", type=int, default=None,
                   help="Random seed for reproducible results (default: -1 for random)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TOOLS = {
    "seedance-2.5": {
        "endpoint": SEEDANCE_2_5_PATH,
        "add_args": add_seedance_2_5_args,
        "build_body": build_seedance_2_5_body,
        "help": "Generate video with text/image/video/audio inputs (Seedance 2.5, 480p/720p only)",
    },
    "seedance": {
        "endpoint": SEEDANCE_PATH,
        "add_args": add_seedance_args,
        "build_body": build_seedance_body,
        "help": "Generate video with text/image/video/audio inputs (Seedance 2.0)",
    },
    "seedance-mini": {
        "endpoint": SEEDANCE_PATH,
        "add_args": add_seedance_mini_args,
        "build_body": build_seedance_mini_body,
        "help": "Generate video at lowest cost with text/image inputs (Seedance 2.0 Mini)",
    },
    "seedream": {
        "endpoint": SEEDREAM_PATH,
        "add_args": add_seedream_args,
        "build_body": build_seedream_body,
        "help": "Generate high-quality images from text prompts (Seedream 4.0/4.5/5.0 Lite/5.0 Pro)",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI ByteDance — Seedance 2.5/2.0 video generation, Seedance 2.0 Mini, and Seedream image generation.",
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
