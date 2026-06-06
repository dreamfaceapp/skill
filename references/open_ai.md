# OpenAI

Image generation tools powered by OpenAI models.

Script: `scripts/open_ai.py`

## GPT Image 2

Generate high-quality images from text prompts using OpenAI's gpt-image-2 model with customizable quality levels and sizes. Supports image-to-image editing via reference images, batch generation up to 10, and flexible aspect ratios with resolutions up to 3840×3840.

- **Endpoint:** `POST /api/async/gpt_image`
- **Command:** `python open_ai.py gpt-image run --prompt "..." [--width 1024] [--height 1024] [--quality low] [--n 1]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--prompt` | string | Yes | Text description of the image (max 4000 chars) |
| `--width` | integer | No | Width in pixels (multiple of 16, 16-3840, default: 1024) |
| `--height` | integer | No | Height in pixels (multiple of 16, 16-3840, default: 1024) |
| `--quality` | string | No | Quality level: `low`, `medium`, `high` (default: `low`) |
| `--n` | integer | No | Number of images to generate (1-10, default: 1) |
| `--images` | string[] | No | Publicly accessible reference image URLs for image-to-image editing (max 4) |

### Tips

- Width and height must be multiples of 16
- Lower quality generates faster results with fewer credits
- When `--images` are provided, the API performs image-to-image editing based on the reference images
- Supported image formats for references: JPG, JPEG, PNG, WEBP, GIF
- Use detailed prompts including subject, style, lighting, and composition for best results

### Pricing

Credits = sizeBase × qualityMultiplier × n

| Factor | Dimension | Credit Multiplier |
| ------ | --------- | ----------------- |
| Size Tier 1 | pixels ≤ 1,048,576 (≤ 1024²) | Base × 2 |
| Size Tier 2 | 1,048,576 < pixels ≤ 4,194,304 (≤ 2048²) | Base × 4 |
| Size Tier 3 | pixels > 4,194,304 | Base × 6 |
| Quality: low | — | × 1 |
| Quality: medium | — | × 9 |
| Quality: high | — | × 36 |
| Image count (n) | — | × n |

#### Credit Examples

| Model Version | Resolution | Credits per Image |
| ------------- | ---------- | ----------------- |
| GPT-image-2 (low) | 1024×1024 | 2.0 |
| GPT-image-2 (medium) | 1024×1024 | 18.0 |
| GPT-image-2 (high) | 1024×1024 | 72.0 |
| GPT-image-2 (low) | 2048×2048 | 4.0 |
| GPT-image-2 (medium) | 2048×2048 | 36.0 |
| GPT-image-2 (high) | 2048×2048 | 144.0 |
| GPT-image-2 (low) | 2880×2880 | 6.0 |
| GPT-image-2 (medium) | 2880×2880 | 54.0 |
| GPT-image-2 (high) | 2880×2880 | 216.0 |
