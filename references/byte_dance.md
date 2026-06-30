# ByteDance

Video generation and image generation tools powered by ByteDance models.

Script: `scripts/byte_dance.py`

## Seedance 2.0

Generate videos using the Seedance 2.0 model with support for text prompts, reference images, reference videos, and audio.

- **Endpoint:** `POST /api/async/seedance_2.0`
- **Command:** `python byte_dance.py seedance run --prompt "..." --resolution <480p|720p|1080p|4k> --duration <4-15> [options]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--prompt` | string | Yes | Video description (max 1500 chars) |
| `--resolution` | string | Yes | Output resolution: "480p", "720p", "1080p", or "4k" |
| `--duration` | integer | Yes | Video duration in seconds (4-15) |
| `--images` | string | No | Reference image URLs or local paths (max 9) |
| `--videos` | string | No | Reference video URLs (max 3, total max 15s) |
| `--audios` | string | No | Audio URLs (max 3) |
| `--ratio` | string | No | Aspect ratio (default: adaptive) |
| `--seed` | integer | No | Random seed for reproducible results |
| `--generate-audio` | boolean | No | Generate audio for the video (default: false) |

### Tips

- The model does not support reference images or videos containing real human faces.
- Audio is only effective when images or videos are provided.
- Use `--seed` for reproducible results.

### Model Pricing

| Model Version | Resolution | Credits / Second |
|---------------|------------|------------------|
| seedance-2.0 | 480p | 30 |
| seedance-2.0 | 720p | 70 |
| seedance-2.0 | 1080p | 156 |
| seedance-2.0 | 4k | 369 |
| seedance-2.0-fast | 480p | 24 |
| seedance-2.0-fast | 720p | 53 |

## Seedance 2.0 Mini

Generate videos at the lowest cost using the Seedance 2.0 Mini model, ideal for quick iterations, previews, and budget-conscious projects.

- **Endpoint:** `POST /api/async/seedance_2.0` (shared with Seedance 2.0)
- **Command:** `python byte_dance.py seedance-mini run --prompt "..." --resolution <480p|720p> --duration <4-15> [options]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--prompt` | string | Yes | Video description (max 1500 chars) |
| `--resolution` | string | Yes | Output resolution: "480p" or "720p" only |
| `--duration` | integer | Yes | Video duration in seconds (4-15) |
| `--images` | string | No | Reference image URLs or local paths (max 9) |
| `--videos` | string | No | Reference video URLs (max 3, total max 15s) |
| `--audios` | string | No | Audio URLs (max 3) |
| `--ratio` | string | No | Aspect ratio (default: adaptive) |
| `--seed` | integer | No | Random seed for reproducible results |
| `--generate-audio` | boolean | No | Generate audio for the video (default: false) |

### Tips

- Seedance 2.0 Mini supports only 480p and 720p resolutions. It does not support 1080p or 4k.
- All other parameters and behavior are identical to Seedance 2.0.
- The model does not support reference images or videos containing real human faces.

### Model Pricing

| Model Version | Resolution | Credits / Second |
|---------------|------------|------------------|
| seedance-2.0-mini | 480p | 15 |
| seedance-2.0-mini | 720p | 33 |

## Seedream 4.5

Generate high-quality images from text prompts using the Seedream model with support for reference images, custom sizes, and seed control.

- **Endpoint:** `POST /api/async/seedream`
- **Command:** `python byte_dance.py seedream run --prompt "..." [options]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--model` | string | No | Model version (default: seedream-4.5) |
| `--prompt` | string | Yes | Text prompt describing the image content |
| `--images` | string | No | Reference image URLs or local paths for style guidance |
| `--size` | string | No | Image dimensions (default: 2048x2048, range: 1024x1024 to 4096x4096) |
| `--seed` | integer | No | Random seed for reproducible results (default: -1 for random) |

### Tips

- Use `--model` to specify a different model version if needed.
- Use `--seed` for reproducible results.
- Image size must be between 1024x1024 and 4096x4096.

### Model Pricing

| Model Version | Credits per Image |
|---------------|------------------|
| seedream-4.0 | 6 credits |
| seedream-4.5 | 8 credits |
| seedream-5.0-lite | 7 credits |
