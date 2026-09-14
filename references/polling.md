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

1. **Single new request → `run`**.
2. **Parallel independent jobs → `submit` then `query`**.
3. **Never ask the user to check status manually.** The agent polls to completion.
4. **Timeouts and transient poll errors resume the same `taskId`** — do not submit a new paid task.
5. **`status=4`** — ask before resubmitting with `run`.

```
Decision tree:
  → Single new request?              use `run`
  → User asked for parallel jobs?    use `submit`, then `query --task-id`
  → run/query timed out?             use `query --task-id <id>` (same task)
  → poll hit 429/500/network once?   retry `query` with the same taskId
  → task status=4 (failed)?          ask the user, then `run` only if they confirm
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
