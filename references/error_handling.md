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

HTTP status (transport) and body `code` (business) are different. Keep the original values; do not collapse them to `-1`.

| Code | Layer | Meaning | Action |
|------|-------|---------|--------|
| 0 | Body `code` | Success | — |
| 10192 | Body `code` | Illegal parameter | Check required params and value formats |
| 401 | HTTP or body | Unauthorized | API key invalid or expired — re-run `auth.py login` |
| 403 | HTTP | Forbidden | Insufficient permissions |
| 429 | HTTP | Rate limited | Wait and retry the **same** task with `query` if a `taskId` exists |
| 500 | HTTP | Server error | Retry after a few seconds; do not submit a new paid task on poll failure |

## Task-Level Failures

When a task's poll status is 4 (failed), keep `task.errorCode` and `task.reason`, and always keep `taskId`. The client raises `DreamAPIError` with that `errorCode` (not `-1`) and `task_id`.

Do not show `creditsConsumed` in user-facing replies.

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
  → Network error / 429 / 500 → retry poll with same taskId (once for transient errors)
  → Task status = 4 (failed) → keep errorCode + taskId, explain, ask before resubmit
  → Timeout → increase --timeout and poll the same taskId again

Auth error (401)?
  → Re-run: python auth.py login
  → Or re-set: export DREAMAPI_API_KEY="..."
```

## Agent Error Handling Rules

1. **Explain errors simply** — tell the user in one sentence what happened and ask if they want to retry.
2. **Never paste raw error messages** — translate technical details into plain language.
3. **Auto-retry on transient errors** — network timeouts, 429, 500 can be retried once **on the same taskId**.
4. **Do not retry on 401** — this means the API key is wrong, prompt user to re-authenticate.
5. **Paid generation failure (`status=4`)** — ask the user before submitting a new task.
