"""Upload local files to DreamAPI Storage and return a public URL.

DreamAPI storage uses a three-step flow:
1. Get Upload Policy — obtain authentication parameters for OSS upload
2. Upload — POST multipart form data to the OSS endpoint
3. Get Upload Result — retrieve the final public URL

Used internally by scripts to auto-upload local file paths.
"""

import os
import sys
from typing import Optional

import requests

from .client import DreamAPIClient

SUPPORTED_FORMATS = {
    "png", "jpg", "jpeg", "bmp", "webp", "gif",
    "mp3", "wav", "m4a", "aac", "flac",
    "mp4", "avi", "mov", "mkv", "webm",
}

# MIME type mapping
MIME_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "bmp": "image/bmp",
    "webp": "image/webp",
    "gif": "image/gif",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "m4a": "audio/mp4",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "mp4": "video/mp4",
    "avi": "video/x-msvideo",
    "mov": "video/quicktime",
    "mkv": "video/x-matroska",
    "webm": "video/webm",
}


def detect_format(file_path: str) -> str:
    """Return file extension if supported, else raise ValueError."""
    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )
    return ext


def parse_upload_policy(policy_data: dict, file_name: str) -> dict:
    """Normalize Get Upload Policy payloads (legacy dir/accessId or official key/OSSAccessKeyId)."""
    host = policy_data.get("host") or ""
    access_id = policy_data.get("accessId") or policy_data.get("OSSAccessKeyId") or ""
    policy = policy_data.get("policy") or ""
    signature = policy_data.get("signature") or ""
    callback = policy_data.get("callback") or ""
    req_id = policy_data.get("reqId") or ""
    full_key = policy_data.get("key") or ""
    upload_dir = policy_data.get("dir") or ""

    if full_key:
        key = full_key
    elif upload_dir:
        key = upload_dir + file_name
    else:
        key = ""

    if not all([host, key, access_id, policy, signature]):
        raise RuntimeError("Failed to get complete upload policy from response")

    return {
        "host": host,
        "key": key,
        "access_id": access_id,
        "policy": policy,
        "signature": signature,
        "callback": callback,
        "req_id": req_id,
    }


def upload_file(
    file_path: str,
    *,
    quiet: bool = False,
    client: Optional[DreamAPIClient] = None,
) -> str:
    """Upload a local file to DreamAPI Storage and return the public URL.

    Three-step flow:
    1. POST /api/file/v1/get_policy → OSS upload credentials
    2. POST multipart form to OSS endpoint
    3. POST /api/file/v1/policy_upload_finish → final public URL
    """
    if client is None:
        client = DreamAPIClient()

    fmt = detect_format(file_path)
    mime = MIME_TYPES.get(fmt, "application/octet-stream")
    file_name = os.path.basename(file_path)

    # Step 1: Get upload policy
    if not quiet:
        print(f"[1/3] Requesting upload policy...", file=sys.stderr)

    policy_data = client.post(
        "/api/file/v1/get_policy",
        json={"scene": "Dream-CN"},
    )
    parsed = parse_upload_policy(policy_data, file_name)

    # Step 2: Upload file
    if not quiet:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"[2/3] Uploading {file_name} ({size_mb:.2f} MB)...", file=sys.stderr)

    with open(file_path, "rb") as f:
        files = {
            "key": (None, parsed["key"]),
            "policy": (None, parsed["policy"]),
            "OSSAccessKeyId": (None, parsed["access_id"]),
            "signature": (None, parsed["signature"]),
            "callback": (None, parsed["callback"]),
            "success_action_status": (None, "200"),
            "file": (file_name, f.read(), mime),
        }

        resp = requests.post(parsed["host"], files=files, timeout=300)

    resp.raise_for_status()
    upload_result = resp.json()

    # Get reqId from upload response or policy response
    upload_req_id = upload_result.get("data", {}).get("reqId") or parsed["req_id"]

    if not upload_req_id:
        raise RuntimeError("Failed to get reqId from upload response")

    # Step 3: Get upload result
    if not quiet:
        print("[3/3] Verifying upload...", file=sys.stderr)

    result_data = client.post(
        "/api/file/v1/policy_upload_finish",
        json={"reqId": upload_req_id},
    )

    file_url = result_data.get("url", "")
    if not file_url:
        raise RuntimeError("Upload verification failed: no URL returned")

    if not quiet:
        print(f"Upload complete: {file_url}", file=sys.stderr)

    return file_url


def _is_http_url(file_ref: str) -> bool:
    lowered = file_ref.lower()
    return lowered.startswith("http://") or lowered.startswith("https://")


def _looks_like_local_path(file_ref: str) -> bool:
    if _is_http_url(file_ref):
        return False
    expanded = os.path.expanduser(file_ref)
    if os.path.isabs(expanded):
        return True
    if expanded.startswith(("./", "../")) or expanded in {".", ".."}:
        return True
    if os.sep in expanded or (os.altsep and os.altsep in expanded):
        return True
    ext = os.path.splitext(expanded)[1].lstrip(".").lower()
    return ext in SUPPORTED_FORMATS


def resolve_local_file(
    file_ref: str,
    *,
    quiet: bool = False,
    client: Optional[DreamAPIClient] = None,
) -> str:
    """If file_ref is a local path, upload it and return URL. Otherwise pass through."""
    if not file_ref or not str(file_ref).strip():
        raise ValueError("Empty file reference")
    file_ref = str(file_ref).strip()
    if _is_http_url(file_ref):
        return file_ref
    expanded = os.path.expanduser(file_ref)
    if os.path.isfile(expanded):
        if not quiet:
            print(f"Detected local file, uploading: {file_ref}", file=sys.stderr)
        return upload_file(expanded, quiet=quiet, client=client)
    if _looks_like_local_path(file_ref):
        raise FileNotFoundError(f"Local file not found: {file_ref}")
    return file_ref
