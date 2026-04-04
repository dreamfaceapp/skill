# Error Handling

## API Response Format

All DreamAPI responses follow this structure:

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

- `code: 0` = success
- Any other code = error

## Common Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | — |
| 10192 | Illegal parameter | Check required params and value formats |
| 401 | Unauthorized | API key invalid or expired — re-run `auth.py login` |
| 403 | Forbidden | Insufficient permissions |
| 429 | Rate limited | Wait and retry |
| 500 | Server error | Retry after a few seconds |

## Task-Level Failures

When a task's poll status is 4 (failed), the `task.reason` field contains the failure reason.

Common task failure reasons:
- Invalid input file format
- File too large or too long
- Content policy violation
- Server-side processing error

## Recovery Decision Tree

```
Error during submit?
  → Check error code and message
  → Fix parameters and retry

Error during polling?
  → Network error → retry poll with same taskId
  → Task status = 4 (failed) → check reason, fix input, resubmit
  → Timeout → increase --timeout and poll again

Auth error (401)?
  → Re-run: python auth.py login
  → Or re-set: export DREAMAPI_API_KEY="..."
```

## Agent Error Handling Rules

1. **Explain errors simply** — tell the user in one sentence what happened and ask if they want to retry.
2. **Never paste raw error messages** — translate technical details into plain language.
3. **Auto-retry on transient errors** — network timeouts, 429, 500 can be retried once.
4. **Do not retry on 401** — this means the API key is wrong, prompt user to re-authenticate.
