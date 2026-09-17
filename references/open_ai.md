# OpenAI

Image generation tools powered by OpenAI models.

Script: `scripts/open_ai.py`

GPT Image 2 uses one endpoint (`/api/async/gpt_image`) for both text-to-image and image-to-image. GPT Image 2.5 uses **four separate endpoints** (Flare/Sunburst × text-to-image/image-to-image). Do not send `images` on 2.5 text-to-image routes. `quality=auto` is not supported on 2.5.

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

## GPT Image 2.5 Flare Text To Image

Faster GPT Image 2.5 variant. Text-to-image only.

- **Endpoint:** `POST /api/async/gpt_image_2.5/flare/text_to_image`
- **Command:** `python open_ai.py gpt-image-2.5-flare-text-to-image run --prompt "..."`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--prompt` | string | Yes | Text description of the image (max 4000 chars) |
| `--width` | integer | No | Width in pixels (multiple of 16, max 3840, aspect ≤ 3:1, 655360–8294400 pixels, default: 1024) |
| `--height` | integer | No | Height in pixels (same constraints as width, default: 1024) |
| `--quality` | string | No | `low`, `medium`, `high`, `xhigh`, `max` (no `auto`, default: `low`) |
| `--n` | integer | No | Number of images (1-10, default: 1) |

This route has **no** `--images` field.

## GPT Image 2.5 Flare Image To Image

Faster GPT Image 2.5 variant. Requires 1–4 reference images.

- **Endpoint:** `POST /api/async/gpt_image_2.5/flare/image_to_image`
- **Command:** `python open_ai.py gpt-image-2.5-flare-image-to-image run --prompt "..." --images <url-or-path>`

### Parameters

Same as Flare text-to-image, plus:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--images` | string[] | Yes | Reference image URLs or local paths (1–4). JSON key is `images`. |

## GPT Image 2.5 Sunburst Text To Image

Higher-quality GPT Image 2.5 variant. Text-to-image only.

- **Endpoint:** `POST /api/async/gpt_image_2.5/sunburst/text_to_image`
- **Command:** `python open_ai.py gpt-image-2.5-sunburst-text-to-image run --prompt "..."`

### Parameters

Same as Flare text-to-image (no `--images`).

## GPT Image 2.5 Sunburst Image To Image

Higher-quality GPT Image 2.5 variant. Requires 1–4 reference images.

- **Endpoint:** `POST /api/async/gpt_image_2.5/sunburst/image_to_image`
- **Command:** `python open_ai.py gpt-image-2.5-sunburst-image-to-image run --prompt "..." --images <url-or-path>`

### Parameters

Same as Flare image-to-image (`--images` required, JSON key `images`).

### Tips (GPT Image 2.5)

- Width and height must be multiples of 16; longer:shorter aspect ratio must not exceed 3:1
- Total pixels must be between 655,360 and 8,294,400; outputs above 3,686,400 pixels are experimental
- `quality` enum is five values only: `low`, `medium`, `high`, `xhigh`, `max`
- Flare is faster with quality comparable to GPT Image 2; Sunburst is the higher-quality 2.5 variant
- Supported reference formats: JPG, JPEG, PNG, WEBP, GIF

### Pricing (GPT Image 2.5)

Credits = ceil(sizeBase × qualityMultiplier) × n

| Factor | Dimension | Credit Multiplier |
| ------ | --------- | ----------------- |
| Size Tier 1 | pixels ≤ 1,048,576 (≤ 1024²) | Base 2 |
| Size Tier 2 | 1,048,576 < pixels ≤ 4,194,304 (≤ 2048²) | Base 4 |
| Size Tier 3 | pixels > 4,194,304 | Base 6 |
| Quality: low | — | × 1 |
| Quality: medium | — | × 2.5 |
| Quality: high | — | × 9 |
| Quality: xhigh | — | × 16 |
| Quality: max | — | × 36 |
| Image count (n) | — | × n |

#### Credit Examples

| Model Version | Resolution | Quality | Credits per Image |
| ------------- | ---------- | ------- | ----------------- |
| GPT Image 2.5 | 1024×1024 | low | 2 |
| GPT Image 2.5 | 1024×1024 | medium | 5 |
| GPT Image 2.5 | 1024×1024 | high | 18 |
| GPT Image 2.5 | 1024×1024 | xhigh | 32 |
| GPT Image 2.5 | 1024×1024 | max | 72 |
| GPT Image 2.5 | 1536×1024 | high | 36 |
| GPT Image 2.5 | 2048×2048 | low | 4 |
| GPT Image 2.5 | 2048×2048 | high | 36 |
| GPT Image 2.5 | 2880×2880 | low | 6 |
| GPT Image 2.5 | 2880×2880 | max | 216 |
