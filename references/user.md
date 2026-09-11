# User Dashboard

Check account balance and credit information.

Script: `scripts/user.py`

## Available Credits

- **Endpoint:** `POST /api/remaining_credits`
- **Content-Type:** `application/x-www-form-urlencoded`
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
