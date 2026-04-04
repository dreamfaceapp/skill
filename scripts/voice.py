#!/usr/bin/env python3
"""DreamAPI Voice — Clone, TTS Clone, TTS Common, TTS Pro, Voice List.

Subcommands:
    clone       Clone a voice from audio sample → returns cloneId
    tts-clone   Text-to-speech with cloned voice
    tts-common  Text-to-speech with standard voices
    tts-pro     Text-to-speech with premium voices
    list        List available voice IDs

Usage:
    python voice.py clone      run --voice-url <url|path>
    python voice.py tts-clone  run --clone-id <id> --text "..." --lang en
    python voice.py tts-common run --audio-id <id> --text "..." --lang en
    python voice.py tts-pro    run --audio-id <id> --text "..." --lang en
    python voice.py list       [--type common|pro] [--language English] [--timbre male|female]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from shared.client import DreamAPIClient
from shared.upload import resolve_local_file

VOICE_CLONE_PATH = "/api/async/voice_clone"
TTS_CLONE_PATH = "/api/async/do_tts_clone"
TTS_COMMON_PATH = "/api/async/do_tts_common"
TTS_PRO_PATH = "/api/async/do_tts_pro"

DEFAULT_TIMEOUT = 300
DEFAULT_INTERVAL = 3


def add_poll_args(p):
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)


def add_output_args(p):
    p.add_argument("--json", action="store_true", help="Output full JSON")
    p.add_argument("-q", "--quiet", action="store_true")


def print_result(data, args, client):
    output = client.extract_output(data)

    # Voice clone returns cloneId
    clone_id = data.get("cloneId", "")
    if clone_id:
        output["clone_id"] = clone_id

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        if clone_id:
            print(f"cloneId: {clone_id}")
        else:
            print(output.get("output_url", ""))


# ---------------------------------------------------------------------------
# Voice Clone
# ---------------------------------------------------------------------------

def build_clone_body(args) -> dict:
    return {"voiceUrl": resolve_local_file(args.voice_url, quiet=args.quiet)}


def add_clone_args(p):
    p.add_argument("--voice-url", required=True, help="Audio sample URL or local path")


# ---------------------------------------------------------------------------
# TTS Clone
# ---------------------------------------------------------------------------

def build_tts_clone_body(args) -> dict:
    return {
        "cloneId": args.clone_id,
        "text": args.text,
        "lan": args.lang,
    }


def add_tts_clone_args(p):
    p.add_argument("--clone-id", required=True, help="Cloned voice ID (from voice clone)")
    p.add_argument("--text", required=True, help="Text to synthesize")
    p.add_argument("--lang", required=True, help="Language: en, zh-CN, es, etc.")


# ---------------------------------------------------------------------------
# TTS Common
# ---------------------------------------------------------------------------

def build_tts_common_body(args) -> dict:
    return {
        "audioId": args.audio_id,
        "text": args.text,
        "lan": args.lang,
    }


def add_tts_common_args(p):
    p.add_argument("--audio-id", required=True, help="Voice ID (from voice list)")
    p.add_argument("--text", required=True, help="Text to synthesize")
    p.add_argument("--lang", required=True, help="Language: en, zh-CN, es, etc.")


# ---------------------------------------------------------------------------
# TTS Pro
# ---------------------------------------------------------------------------

def build_tts_pro_body(args) -> dict:
    return {
        "audioId": args.audio_id,
        "text": args.text,
        "lan": args.lang,
    }


def add_tts_pro_args(p):
    p.add_argument("--audio-id", required=True, help="Pro voice ID (from voice list)")
    p.add_argument("--text", required=True, help="Text to synthesize")
    p.add_argument("--lang", required=True, help="Language: en, zh-CN, es, etc.")


# ---------------------------------------------------------------------------
# Voice List (sync, no polling)
# ---------------------------------------------------------------------------

def cmd_list(args):
    """List available voices — reads from bundled catalog or API."""
    # Try bundled catalog first
    catalog_path = os.path.join(os.path.dirname(__file__), "voice_catalog.json")
    voices = []

    if os.path.exists(catalog_path):
        with open(catalog_path, "r") as f:
            voices = json.load(f)
    else:
        # Fallback: could call API if available
        print("Voice catalog not found. Check scripts/voice_catalog.json", file=sys.stderr)
        sys.exit(1)

    # Apply filters
    if args.type:
        voices = [v for v in voices if v.get("type") == args.type]
    if args.language:
        voices = [v for v in voices if v.get("language") == args.language]
    if args.timbre:
        voices = [v for v in voices if v.get("timbre") == args.timbre]

    # Rename 'id' to 'audioId' for consistency with TTS tools
    for v in voices:
        if "id" in v:
            v["audioId"] = v.pop("id")

    if args.json:
        print(json.dumps(voices, indent=2, ensure_ascii=False))
    else:
        if not args.quiet:
            print(f"Voices: {len(voices)}", file=sys.stderr)
        for v in voices:
            aid = v.get("audioId", "")
            name = v.get("name", "")
            vtype = v.get("type", "")
            lang = v.get("language", "")
            timbre = v.get("timbre", "")
            print(f"{aid}\t{name}\t{vtype}\t{lang}\t{timbre}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

ASYNC_TOOLS = {
    "clone": {
        "endpoint": VOICE_CLONE_PATH,
        "add_args": add_clone_args,
        "build_body": build_clone_body,
        "help": "Clone a voice from audio sample",
    },
    "tts-clone": {
        "endpoint": TTS_CLONE_PATH,
        "add_args": add_tts_clone_args,
        "build_body": build_tts_clone_body,
        "help": "TTS with cloned voice",
    },
    "tts-common": {
        "endpoint": TTS_COMMON_PATH,
        "add_args": add_tts_common_args,
        "build_body": build_tts_common_body,
        "help": "TTS with standard voices",
    },
    "tts-pro": {
        "endpoint": TTS_PRO_PATH,
        "add_args": add_tts_pro_args,
        "build_body": build_tts_pro_body,
        "help": "TTS with premium Pro voices",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI Voice — clone, TTS, and voice management.",
    )

    tool_sub = parser.add_subparsers(dest="tool")
    tool_sub.required = True

    # Async tools (clone, tts-*)
    for tool_name, tool_info in ASYNC_TOOLS.items():
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

    # Voice list (sync, no polling)
    p_list = tool_sub.add_parser("list", help="List available voices")
    p_list.add_argument("--type", choices=["common", "pro"], default=None,
                        help="Filter by voice type")
    p_list.add_argument("--language", default=None, help="Filter by language (e.g. English)")
    p_list.add_argument("--timbre", default=None, help="Filter by timbre (e.g. male, female)")
    p_list.add_argument("--json", action="store_true")
    p_list.add_argument("-q", "--quiet", action="store_true")

    args = parser.parse_args()

    # Voice list is a special case — no async flow
    if args.tool == "list":
        cmd_list(args)
        return

    client = DreamAPIClient()
    tool_info = ASYNC_TOOLS[args.tool]

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
