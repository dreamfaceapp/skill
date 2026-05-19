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
