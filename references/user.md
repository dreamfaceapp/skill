# User Dashboard

Check account balance and credit information.

Script: `scripts/user.py`

## Available Credits

- **Endpoint:** `GET /api/user/available_credits`
- **Command:** `python user.py credit`

### Options

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |

### Example

```bash
$ python user.py credit
Available credits: 150.5
```
