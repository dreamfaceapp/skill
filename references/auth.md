# Authentication

DreamAPI uses Bearer token (API Key) authentication.

## Get Your API Key

1. Go to the [DreamAPI Dashboard](https://api.newportai.com/)
2. Sign in via Google or GitHub
3. Navigate to **API Keys** section
4. Copy your API key

## Setup

### Option 1 — Interactive login (recommended)

```bash
pip install -r {baseDir}/scripts/requirements.txt
python {baseDir}/scripts/auth.py login
```

Paste your API key when prompted. It will be saved to `~/.dreamapi/credentials.json`.

### Option 2 — Environment variable

```bash
export DREAMAPI_API_KEY="your-api-key-here"
```

### Priority

The scripts check credentials in this order:
1. `DREAMAPI_API_KEY` environment variable
2. `~/.dreamapi/credentials.json` (set by `auth.py login`)

## Commands

| Command | Description |
|---------|-------------|
| `python auth.py login` | Save API key (interactive or `--key "sk-..."`) |
| `python auth.py login --key "sk-..."` | Save API key non-interactively |
| `python auth.py status` | Check current auth state and verify key |
| `python auth.py logout` | Remove saved credentials |

## Credential File Format

```json
{
  "api_key": "your-api-key",
  "created_at": "2025-01-01T00:00:00+00:00",
  "verified": true
}
```

Location: `~/.dreamapi/credentials.json` (mode 0600)
