#!/usr/bin/env python3
"""DreamAPI Authentication CLI — manage API key credentials.

DreamAPI uses Bearer token authentication. Get your API key from:
https://api.newportai.com/

Subcommands:
    login   — Save your API key to ~/.dreamapi/credentials.json
    status  — Check current authentication state
    logout  — Remove saved credentials

Usage:
    python auth.py login
    python auth.py status
    python auth.py logout
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

CRED_FILE = Path.home() / ".dreamapi" / "credentials.json"
DASHBOARD_URL = "https://api.newportai.com/"
CREDITS_ENDPOINT = "/api/user/available_credits"


# ---------------------------------------------------------------------------
# Credential file helpers
# ---------------------------------------------------------------------------

def _save_credentials(api_key: str, extra: dict | None = None) -> None:
    """Persist API key to credentials file."""
    CRED_FILE.parent.mkdir(parents=True, exist_ok=True)

    creds = {
        "api_key": api_key,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        creds.update(extra)

    CRED_FILE.write_text(json.dumps(creds, indent=2))
    CRED_FILE.chmod(0o600)


def _load_credentials() -> dict | None:
    if not CRED_FILE.exists():
        return None
    try:
        return json.loads(CRED_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _delete_credentials() -> bool:
    if CRED_FILE.exists():
        CRED_FILE.unlink()
        return True
    return False


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "***"
    return key[:4] + "..." + key[-4:]


def _verify_api_key(api_key: str) -> dict | None:
    """Verify API key by calling the credits endpoint. Returns data or None."""
    try:
        resp = requests.get(
            f"{DASHBOARD_URL.rstrip('/')}{CREDITS_ENDPOINT}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data", {})
    except requests.RequestException:
        pass
    return None


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_login(args) -> None:
    """Save API key — user pastes it interactively or via --key flag."""
    api_key = args.key

    if not api_key:
        print()
        print("  DreamAPI Authentication")
        print("  ─────────────────────────────────────────")
        print(f"  Get your API key from: {DASHBOARD_URL}")
        print("  Go to Dashboard → API Keys → Copy your key")
        print()
        api_key = input("  Paste your API key here: ").strip()

    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        sys.exit(1)

    # Verify the key
    print()
    print("  Verifying API key...", end="", flush=True)
    result = _verify_api_key(api_key)

    if result is not None:
        print(" OK")
        credits_info = result.get("credits", result)
        _save_credentials(api_key, extra={"verified": True})

        print()
        print("  Logged in successfully!")
        print(f"  api_key:  {_mask_key(api_key)}")
        if isinstance(credits_info, (int, float)):
            print(f"  credits:  {credits_info}")
        print(f"  Saved to: {CRED_FILE}")
        print()
    else:
        # Save anyway but warn — the endpoint might not be available
        print(" (could not verify, saving anyway)")
        _save_credentials(api_key, extra={"verified": False})

        print()
        print("  API key saved (verification skipped).")
        print(f"  api_key:  {_mask_key(api_key)}")
        print(f"  Saved to: {CRED_FILE}")
        print()
        print("  If tasks fail with auth errors, double-check your key at:")
        print(f"  {DASHBOARD_URL}")
        print()


def cmd_status(args) -> None:
    """Show current authentication state."""
    # Check environment variable first
    env_key = os.environ.get("DREAMAPI_API_KEY", "").strip()
    if env_key:
        print("Authenticated via environment variable")
        print(f"  DREAMAPI_API_KEY: {_mask_key(env_key)}")
        print()

        result = _verify_api_key(env_key)
        if result is not None:
            print("  Status: Valid")
            credits_info = result.get("credits", result)
            if isinstance(credits_info, (int, float)):
                print(f"  Credits: {credits_info}")
        else:
            print("  Status: Could not verify")
        return

    # Check credential file
    creds = _load_credentials()
    if creds is None:
        print("Not logged in.")
        print()
        print("Run: python scripts/auth.py login")
        print(f"Or:  export DREAMAPI_API_KEY=\"<your-key>\"")
        sys.exit(1)

    api_key = creds.get("api_key", "")
    created_at = creds.get("created_at", "(unknown)")

    print("Authenticated via credentials file")
    print(f"  api_key:    {_mask_key(api_key)}")
    print(f"  authorized: {created_at}")
    print(f"  file:       {CRED_FILE}")

    result = _verify_api_key(api_key)
    if result is not None:
        print("  Status: Valid")
        credits_info = result.get("credits", result)
        if isinstance(credits_info, (int, float)):
            print(f"  Credits: {credits_info}")
    else:
        print("  Status: Could not verify")


def cmd_logout(args) -> None:
    """Remove saved credentials."""
    if _delete_credentials():
        print(f"Logged out. Removed {CRED_FILE}")
    else:
        print("Not logged in (no credentials file found).")

    env_key = os.environ.get("DREAMAPI_API_KEY", "").strip()
    if env_key:
        print()
        print("Note: DREAMAPI_API_KEY environment variable is still set.")
        print("To fully log out, also run: unset DREAMAPI_API_KEY")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="DreamAPI Authentication — manage your API key.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Subcommands:
  login   Save your API key (interactive or via --key)
  status  Check current authentication state
  logout  Remove saved credentials

Examples:
  python auth.py login                      # interactive: paste your key
  python auth.py login --key "sk-abc..."    # non-interactive
  python auth.py status                     # check if authenticated
  python auth.py logout                     # remove credentials
""",
    )
    sub = parser.add_subparsers(dest="subcommand")
    sub.required = True

    p_login = sub.add_parser("login", help="Save your API key")
    p_login.add_argument(
        "--key", default=None,
        help="API key (skip interactive prompt)",
    )

    sub.add_parser("status", help="Check current authentication state")
    sub.add_parser("logout", help="Remove saved credentials")

    args = parser.parse_args()

    handlers = {
        "login": cmd_login,
        "status": cmd_status,
        "logout": cmd_logout,
    }
    handlers[args.subcommand](args)


if __name__ == "__main__":
    main()
