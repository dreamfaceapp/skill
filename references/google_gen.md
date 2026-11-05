# Google

Image generation tools powered by Google Gemini models.

Script: `scripts/google_gen.py`

## Nano Banana 2

Generate images using the Gemini 3.1 Flash Image Preview model with support for multiple resolutions up to 4K — fast and cost-efficient.

- **Endpoint:** `POST /api/async/google_gemini_image`
- **Command:** `python google_gen.py nano-banana-2 run --text "..." [options]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--text` | string | Yes | Text prompt describing the image to generate |
| `--image-size` | string | No | Output resolution: `"512"`, `"1K"`, `"2K"`, or `"4K"` (default: `"1K"`) |
| `--aspect-ratio` | string | No | Aspect ratio, e.g. `"16:9"`, `"1:1"`, `"4:3"` |
| `--images` | string[] | No | Reference image URLs or local paths |

### Pricing

| Resolution | Credits |
|------------|--------|
| 512 | 15 |
| 1K | 20 |
| 2K | 30 |
| 4K | 40 |

### Tips

- Lower resolutions are faster and cheaper. Use `512` for quick drafts, `4K` for final outputs.
- Reference images can be URLs or local file paths (auto-uploaded).

## Nano Banana Pro

Generate premium, high-fidelity images using the Gemini 3 Pro Image Preview model with support for 1K and 2K resolutions.

- **Endpoint:** `POST /api/async/google_gemini_image`
- **Command:** `python google_gen.py nano-banana-pro run --text "..." [options]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--text` | string | Yes | Text prompt describing the image to generate |
| `--image-size` | string | No | Output resolution: `"1K"` or `"2K"` (default: `"1K"`) |
| `--aspect-ratio` | string | No | Aspect ratio, e.g. `"16:9"`, `"1:1"`, `"4:3"` |
| `--images` | string[] | No | Reference image URLs or local paths |

### Pricing

| Resolution | Credits |
|------------|--------|
| 1K | 35 |
| 2K | 35 |

### Tips

- Both 1K and 2K cost the same credits (35). Use 2K for the best quality.
- Reference images can be URLs or local file paths (auto-uploaded).

## Nano Banana Lite

Generate 1K images with Gemini 3.1 Flash Lite Image. Use the same command for text-to-image and image-to-image: omit `--images` for text-to-image, or provide 1–14 reference images for image-to-image.

- **Endpoint:** `POST /api/async/google_gemini_image_lite`
- **Command (text-to-image):** `python google_gen.py nano-banana-lite run --text "..." [options]`
- **Command (image-to-image):** `python google_gen.py nano-banana-lite run --text "..." --images <image-url-or-path> [more images...] [options]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--text` | string | Yes | Prompt describing the image to generate or edit |
| `--image-size` | string | No | `1K` only (default: `1K`) |
| `--aspect-ratio` | string | No | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, or `21:9` (default: `9:16`) |
| `--images` | string[] | For image-to-image | 1–14 reference image URLs or local paths, in prompt order. Omit for text-to-image. Local files are auto-uploaded. |

The `model` request field is omitted; the API defaults to `gemini-3.1-flash-lite-image`. If supplied directly, it must use that exact model ID.

### Pricing

| Resolution | Credits per image |
|------------|-------------------|
| 1K | 10 |

Text-to-image and image-to-image use the same fixed price.
