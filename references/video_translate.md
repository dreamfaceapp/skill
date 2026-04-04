# Video Translate

Translate spoken language in a video to another language with optional lip-sync.

Script: `scripts/video_translate.py`

## Video Translate 2.0

- **Endpoint:** `POST /api/async/video_translate/2.0`
- **Command:** `python video_translate.py run --video <url> --source en --target zh`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--video` | string | Yes | Video URL or local path |
| `--source` | string | Yes | Source language: "en", "zh", "es" |
| `--target` | string | Yes | Target language: "en", "zh", "es" |
| `--lip-sync` | boolean | No | Enable lip-sync (default: true) |

### Supported Languages

| Code | Language |
|------|----------|
| `en` | English |
| `zh` | Chinese |
| `es` | Spanish |

### Example

```bash
# Translate English video to Chinese with lip-sync
python video_translate.py run --video video.mp4 --source en --target zh

# Translate without lip-sync
python video_translate.py run --video video.mp4 --source en --target es --lip-sync false
```
