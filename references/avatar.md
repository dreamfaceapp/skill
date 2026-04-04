# Avatar

Four avatar tools for generating talking face and motion-driven videos.

Script: `scripts/avatar.py`

## LipSync (v1)

Audio-driven talking face generation. Syncs lip movements to provided audio.

- **Endpoint:** `POST /api/async/lipsync`
- **Command:** `python avatar.py lipsync run --src-video <url> --audio <url>`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--src-video` | string | Yes | Source video URL or local path |
| `--audio` | string | Yes | Driving audio URL or local path |
| `--video-width` | integer | No | Output width (0 = keep original) |
| `--video-height` | integer | No | Output height (0 = keep original) |
| `--video-enhance` | boolean | No | Enable enhancement (default: false) |

### Request Body Mapping

```json
{
  "srcVideoUrl": "...",
  "audioUrl": "...",
  "videoParams": {
    "video_width": 0,
    "video_height": 0,
    "video_enhance": false
  }
}
```

---

## LipSync 2.0

Improved lip sync with vocal audio separation support.

- **Endpoint:** `POST /api/async/lipsync/2.0`
- **Command:** `python avatar.py lipsync2 run --src-video <url> --audio <url>`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--src-video` | string | Yes | Source video URL or local path |
| `--audio` | string | Yes | Original audio URL or local path |
| `--vocal-audio` | string | No | Vocal-only audio (improves accuracy) |
| `--video-width` | integer | No | Output width (0 = original) |
| `--video-height` | integer | No | Output height (0 = original) |
| `--video-enhance` | integer | No | Enhancement level (0=off, 1=on, default: 1) |
| `--fps` | string | No | Frame rate (default: "25"). Use "original" to match input |

### Billing Note

When fps is "original": `(input FPS / 25) * 1` credit multiplier.

---

## DreamAvatar 3.0 Fast

Generate a talking avatar video from a portrait image + audio.

- **Endpoint:** `POST /api/async/dreamavatar/image_to_video/3.0fast`
- **Command:** `python avatar.py dreamavatar run --image <path> --audio <path> --prompt "..."`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--image` | string | Yes | Portrait image URL or local path (JPG/PNG/WEBP) |
| `--audio` | string | Yes | Audio URL or local path (MP3/WAV/MP4, max 3 min) |
| `--prompt` | string | Yes | Text prompt to guide generation style |
| `--resolution` | string | No | "480p" or "720p" (default: "480p") |

---

## Dreamact

Motion-driven avatar — character from reference images performs motions from a driving video.

- **Endpoint:** `POST /api/async/wan/dreamact/2.1`
- **Command:** `python avatar.py dreamact run --video <url> --images <url1> <url2>`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--video` | string | Yes | Driving video URL or local path (max 1 min) |
| `--images` | string[] | Yes | Reference image URLs or local paths |
| `--seed` | integer | No | Seed for reproducibility (default: 42) |

---

## Common Options (all subcommands)

| Option | Description |
|--------|-------------|
| `run` | Submit + poll until done (default workflow) |
| `submit` | Submit only, print taskId |
| `query --task-id <id>` | Poll existing taskId |
| `--timeout <sec>` | Max poll time (default: 600) |
| `--interval <sec>` | Poll interval (default: 5) |
| `--json` | Output full JSON response |
| `-q, --quiet` | Suppress status messages |
