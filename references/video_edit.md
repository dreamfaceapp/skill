# Video Editing

Three tools for video manipulation: face swap, matting, and compositing.

Script: `scripts/video_edit.py`

## Swap Face for Video

Replace faces in a video with a face from a source image.

- **Endpoint:** `POST /api/async/swap_face_for_video`
- **Command:** `python video_edit.py swap-face run --src-video <url> --face <url|path>`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--src-video` | string | Yes | Source video URL or local path (max 5 min) |
| `--face` | string | Yes | Face image URL or local path |

---

## Video Matting

Extract the portrait or main subject from a video, removing the background. Produces a video with an alpha channel (transparent background).

- **Endpoint:** `POST /api/async/image_matting_process_video`
- **Command:** `python video_edit.py matting run --src-file <url>`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--src-file` | string | Yes | Source video URL (MP4 only) |
| `--bit-rate` | string | No | Target bitrate (e.g. "16m", default: "16m") |
| `--remove-color-spill` | boolean | No | Remove color fringes around subject |

### Output

Returns two URLs:
- **matting_file_url** — The matted video (subject only)
- **matting_alpha_url** — The alpha channel video (for composite step)

---

## Composite After Matting

Replace the background of a previously matted video.

- **Endpoint:** `POST /api/async/image_matting_composite_video`
- **Command:** `python video_edit.py composite run --src-file <url> --alpha <url> --bg-type color --bg-color "232d84"`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--src-file` | string | Yes | Original source video URL |
| `--alpha` | string | Yes | Alpha/matting video URL (from matting) |
| `--bg-type` | string | Yes | Background type: "color", "image", or "video" |
| `--bg-color` | string | No | Hex color code (e.g. "232d84") for color background |
| `--bg-url` | string | No | Background image or video URL |

### Background Type Rules

- `--bg-type color` → must provide `--bg-color`
- `--bg-type image` → must provide `--bg-url` (image URL)
- `--bg-type video` → must provide `--bg-url` (video URL)

### Workflow

The typical video background replacement workflow is:

```
1. video_edit.py matting run --src-file <video>
   → get matting_file_url + matting_alpha_url

2. video_edit.py composite run \
     --src-file <original_video> \
     --alpha <matting_alpha_url> \
     --bg-type image --bg-url <new_background>
   → get composite video
```
