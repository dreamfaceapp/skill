"""Load DreamAPI credentials.

Priority order:
1. Environment variable DREAMAPI_API_KEY  (CI / quick setup)
2. Credential file ~/.dreamapi/credentials.json  (set by auth.py login)
3. Error — prompts user to run auth.py login
"""

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

CRED_FILE = Path.home() / ".dreamapi" / "credentials.json"
BASE_URL = "https://api.newportai.com"


def _load_from_file() -> str | None:
    """Read api_key from the local credentials file, or return None."""
    if not CRED_FILE.exists():
        return None
    try:
        data = json.loads(CRED_FILE.read_text())
        api_key = data.get("api_key", "").strip()
        if api_key:
            return api_key
    except (json.JSONDecodeError, OSError):
        pass
    return None


def load_api_key() -> str:
    """Return the DreamAPI API key, or exit with a helpful error message."""
    # Priority 1: environment variable
    api_key = os.environ.get("DREAMAPI_API_KEY", "").strip()
    if api_key:
        return api_key

    # Priority 2: credential file set by auth.py login
    api_key = _load_from_file()
    if api_key:
        return api_key

    # Priority 3: error with actionable message
    print(
        "Error: DreamAPI API key not found.\n\n"
        "Option 1 — Log in with the auth module (recommended):\n"
        "  python scripts/auth.py login\n\n"
        "Option 2 — Set environment variable manually:\n"
        '  export DREAMAPI_API_KEY="<your-api-key>"\n\n'
        "Get your API key from: https://api.newportai.com/\n",
        file=sys.stderr,
    )
    sys.exit(1)
