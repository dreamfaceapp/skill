# Polling

All DreamAPI generation tasks are asynchronous. After submitting a task, you receive a `taskId` and must poll for the result.

## Polling Endpoint

- **Endpoint:** `POST /api/getAsyncResult`
- **Body:** `{"taskId": "<taskId>"}`

## Task Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 0 | Queued | Task is waiting to be processed |
| 1 | Processing | Task is actively running |
| 2 | Processing | Task is still running (alternate code) |
| 3 | Success | Task completed successfully |
| 4 | Failed | Task failed |

## How It Works

The `run` action in every script handles polling automatically:

1. Submit the task → receive `taskId`
2. Poll every `--interval` seconds (default: 5)
3. Continue until status = 3 (success) or 4 (failed)
4. Timeout after `--timeout` seconds (default: 600)

## Agent Workflow Rules

1. **Always use `run`** for new requests — it submits and polls automatically.
2. **Never ask the user to check status manually.** The agent polls to completion.
3. **Only use `query`** when `run` timed out and you have a `taskId` to resume.
4. **If `query` also times out**, increase `--timeout` and try again with the same `taskId`.
5. **Do not resubmit** unless the task status is actually "failed" (code 4).

```
Decision tree:
  → New request?           use `run`
  → run timed out?         use `query --task-id <id>`
  → query timed out?       use `query --task-id <id> --timeout 1200`
  → task status=fail?      resubmit with `run`
```

## Response Format (Success)

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task": {
      "taskId": "abc123",
      "status": 3
    },
    "images": [{"imageUrl": "https://..."}],
    "videos": [{"videoUrl": "https://..."}],
    "audios": [{"audioUrl": "https://..."}]
  }
}
```

Only the relevant array (images, videos, or audios) is populated depending on the task type.
