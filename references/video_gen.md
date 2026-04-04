# Video Generation

Three tools for generating videos using the Wan2.1 model.

Script: `scripts/video_gen.py`

## Text to Video

Generate a video from a text description.

- **Endpoint:** `POST /api/async/wan/text_to_video/2.1`
- **Command:** `python video_gen.py text2video run --prompt "..."`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--prompt` | string | Yes | Video description (max 1500 chars) |
| `--resolution` | string | No | "480p" or "720p" (default: "480p") |

### Tips

Describe the scene in detail: subject, action, camera movement, lighting, and style.

---

## Image to Video

Animate a static image into a video.

- **Endpoint:** `POST /api/async/wan/image_to_video/2.1`
- **Command:** `python video_gen.py image2video run --image <url|path> --prompt "..."`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--image` | string | Yes | Source image URL or local path |
| `--prompt` | string | Yes | Motion description (max 1500 chars) |
| `--resolution` | string | No | "480p" or "720p" (default: "480p") |

---

## Head-Tail to Video

Generate a smooth transition video between a starting frame and an ending frame.

- **Endpoint:** `POST /api/async/wan/head_tail_to_video/2.1`
- **Command:** `python video_gen.py head-tail run --first <url> --last <url> --prompt "..."`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--first` | string | Yes | Starting frame image URL or path |
| `--last` | string | Yes | Ending frame image URL or path |
| `--prompt` | string | Yes | Transition description (max 1500 chars) |

> Useful for scene transitions and morphing effects.
