# Video Generation

Five tools for generating videos: Wan2.1 (text / image / head-tail) and DreamVideo 3.0 (text / image).

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

---

## DreamVideo 3.0 Text to Video

Generate a video directly from a text prompt. Output supports `480P` and `720P`, duration 3–15 seconds.

- **Endpoint:** `POST /api/async/dreamvideo_3.0/text_to_video`
- **Command:** `python video_gen.py dreamvideo-text2video run --prompt "..."`
- **Pricing:** `480P` = 2 credits/second, `720P` = 4 credits/second. If `--duration` is omitted, billing uses 5 seconds.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--prompt` | string | Yes | Text prompt describing the video |
| `--duration` | int | No | Duration in seconds, range 3–15 (default: `5`) |
| `--resolution` | string | No | `480P` or `720P` (default: `720P`) |
| `--aspect-ratio` | string | No | `auto`, `9:16`, `3:4`, `1:1`, `4:3`, `16:9` (default: `auto`) |
| `--seed` | int | No | Generation seed (default: `42`) |

---

## DreamVideo 3.0 Image to Video

Generate a video from one or more images plus a prompt. One image is used as the first frame (image-to-video). Two or more images are processed as first-last frame generation using only the first two images.

- **Endpoint:** `POST /api/async/dreamvideo_3.0/image_to_video`
- **Command:** `python video_gen.py dreamvideo-image2video run --images <url1> [url2] --prompt "..."`
- **Pricing:** `480P` = 2 credits/second, `720P` = 4 credits/second. If `--duration` is omitted, billing uses 5 seconds.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--images` | string[] | Yes | One or more image URLs or local paths. One image = i2v; two or more = first-last (only first two used). JPEG / PNG / WebP |
| `--prompt` | string | Yes | Text prompt describing the video |
| `--duration` | int | No | Duration in seconds, range 3–15 (default: `5`) |
| `--resolution` | string | No | `480P` or `720P` (default: `720P`) |
| `--aspect-ratio` | string | No | `auto`, `9:16`, `3:4`, `1:1`, `4:3`, `16:9` (default: `auto`) |
| `--seed` | int | No | Generation seed (default: `42`) |

### Tips

- Each input image must satisfy **longer side / shorter side ≤ 4:1** (4:1 and 1:4 are allowed; 5:1 and 1:5 are not). There is no maximum pixel length on the longer side.
- If the ratio exceeds 4:1, submit may still succeed; polling then returns `status=4` with `errorCode=10192`.
