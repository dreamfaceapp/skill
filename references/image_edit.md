# Image Editing

Six tools for image manipulation and enhancement.

Script: `scripts/image_edit.py`

## Colorize

Add realistic colors to black-and-white photos. **Requires a human face in the image.**

- **Endpoint:** `POST /api/async/colorize`
- **Command:** `python image_edit.py colorize run --url <image_url>`
- **Parameters:** `--url` (required) — B&W image URL or local path

> Not suitable for landscapes, architecture, or objects without faces.

---

## Enhance

AI super-resolution — improve image quality and boost resolution (2-4x).

- **Endpoint:** `POST /api/async/enhance`
- **Command:** `python image_edit.py enhance run --image <url|path>`
- **Parameters:** `--image` (required) — Image URL or local path

> Best for low-resolution or blurry photos.

---

## Outpainting

Extend an image beyond its original borders with AI-generated content.

- **Endpoint:** `POST /api/async/outpainting`
- **Command:** `python image_edit.py outpainting run --url <url> --left 100 --right 100`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--url` | string | Yes | Source image URL or local path |
| `--left` | integer | No | Pixels to expand left (default: 0) |
| `--right` | integer | No | Pixels to expand right (default: 0) |
| `--top` | integer | No | Pixels to expand top (default: 0) |
| `--bottom` | integer | No | Pixels to expand bottom (default: 0) |

### Request Body

```json
{
  "url": "...",
  "outPaintSize": { "left": 0, "right": 0, "top": 0, "bottom": 0 }
}
```

---

## Inpainting

Fill or replace masked regions of an image using AI.

- **Endpoint:** `POST /api/async/inpainting`
- **Command:** `python image_edit.py inpainting run --url <url> --mask <url> --prompt "..."`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--url` | string | Yes | Original image URL or local path |
| `--mask` | string | Yes | Mask image URL (white areas = fill) |
| `--prompt` | string | Yes | What to generate in the masked area |

---

## Swap Face

Replace a face in the target image with another face.

- **Endpoint:** `POST /api/async/swap_face`
- **Command:** `python image_edit.py swap-face run --url <target> --face <source>`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--url` | string | Yes | Target image (must contain exactly one face) |
| `--face` | string | Yes | Source face image URL or local path |

---

## Remove Background

Remove the background from an image, leaving the subject on a transparent background.

- **Endpoint:** `POST /api/async/remove_background`
- **Command:** `python image_edit.py remove-bg run --url <url|path>`
- **Parameters:** `--url` (required) — Image URL or local path

> Works well with people, objects, and products.
