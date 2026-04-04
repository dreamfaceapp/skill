# Image Generation

Two tools for generating images using the Flux model.

Script: `scripts/image_gen.py`

## Flux Text to Image

Generate images from text descriptions.

- **Endpoint:** `POST /api/async/flux_text2image`
- **Command:** `python image_gen.py text2image run --prompt "..."`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--prompt` | string | Yes | Detailed text description of the image |
| `--width` | integer | No | Width in pixels (multiple of 16, max 1600, default: 1024) |
| `--height` | integer | No | Height in pixels (multiple of 16, max 1600, default: 1024) |
| `--num` | integer | No | Number of images (1-10, default: 1) |
| `--seed` | integer | No | Random seed for reproducibility |

### Tips

- Width and height must be multiples of 16
- Maximum dimension: 1600px per side
- Use detailed prompts including subject, style, lighting, and composition

---

## Flux Image to Image

Transform an existing image based on a text prompt.

- **Endpoint:** `POST /api/async/flux_image2image`
- **Command:** `python image_gen.py image2image run --image <url|path> --prompt "..."`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--image` | string | Yes | Reference image URL or local path |
| `--prompt` | string | Yes | Text description of desired modifications |
| `--width` | integer | No | Output width (multiple of 16, max 1600, default: 1024) |
| `--height` | integer | No | Output height (multiple of 16, max 1600, default: 1024) |
| `--num` | integer | No | Number of images (1-10) |
| `--seed` | integer | No | Random seed |

### Output

Returns one or more image URLs. Multiple images printed one per line.
