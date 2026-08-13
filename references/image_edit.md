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

---

## Virtual Try-On

Transfer clothing onto a model image. Supports upper garments, lower garments, and one-piece outfits. You must provide at least one clothing item, and at most two (upper + lower). When using one-piece (`--overall`), do not provide `--upper` or `--lower`.

- **Endpoint:** `POST /api/async/tryon_clothes`
- **Command:** `python image_edit.py try-on run --model <url|path> --upper <url|path> --lower <url|path>`
- **Cost:** 8 credits per task

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--model` | string | Yes | Model image URL or local path |
| `--upper` | string | No | Upper garment image (shirt, jacket, top) |
| `--lower` | string | No | Lower garment image (pants, skirt, shorts) |
| `--overall` | string | No | One-piece garment (dress, jumpsuit) |
| `--prompt` | string | No | Text prompt to guide generation |
| `--enable-shoes` | bool | No | Enable shoe generation (default: true) |
| `--width` | int | No | Output width in pixels (default: 768) |
| `--height` | int | No | Output height in pixels (default: 1378) |

> **Constraint:** At least one of `--upper`, `--lower`, or `--overall` is required. Provide at most two (upper + lower for two-piece). When `--overall` is set, `--upper` and `--lower` must be empty.
