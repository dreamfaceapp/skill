# ByteDance

Video generation and image generation tools powered by ByteDance models.

Script: `scripts/byte_dance.py`

## Seedance 2.5

Generate videos using the Seedance 2.5 model with support for text prompts, reference images, reference videos, and audio.

- **Endpoint:** `POST /api/async/seedance_2.5`
- **Command:** `python byte_dance.py seedance-2.5 run --prompt "..." --resolution <480p|720p> --duration <4-30> [options]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--prompt` | string | Yes | Video description (max 1500 chars) |
| `--resolution` | string | Yes | Output resolution: "480p" or "720p" only |
| `--duration` | integer | Yes | Video duration in seconds (4-30) |
| `--images` | string | No | Reference image URLs or local paths (max 9) |
| `--image-url` | string | No | First-frame image URL or local path (JPEG/PNG/WebP). Enables image-to-video mode |
| `--end-image-url` | string | No | Last-frame image URL or local path. Only valid with `--image-url` |
| `--videos` | string | No | Reference video URLs (max 10, each 2-30s, total max 30s) |
| `--audios` | string | No | Audio URLs (max 3) |
| `--ratio` | string | No | Aspect ratio (default: adaptive) |
| `--seed` | integer | No | Random seed for reproducible results |
| `--generate-audio` | boolean | No | Generate audio for the video (default: false) |

### Tips

- Seedance 2.5 supports only 480p and 720p resolutions. It does not support 1080p or 4k.
- Video duration range is 4-30 seconds.
- Provide `--image-url` to generate from a first frame (image-to-video). Add `--end-image-url` for first-last frame transition. `--end-image-url` without `--image-url` returns error 10192.
- The model does not support reference images or videos containing real human faces.
- Audio is only effective when images or videos are provided.
- Use `--seed` for reproducible results.

### Model Pricing

| Model Version | Resolution | Output Video Credits / Second | Reference Video Credits / Second |
|---------------|------------|-------------------------------|----------------------------------|
| seedance-2.5 | 480p | 45 | 23 |
| seedance-2.5 | 720p | 100 | 34 |

Reference To Video billing formula:

`Credits = Output Video Credits × Duration (seconds) + Reference Video Credits × Total Reference Video Duration (seconds)`

The reference video duration is the sum of the durations of all reference videos in `--videos` (up to 10 videos, each 2-30 seconds, total max 30 seconds). Text/Image To Video are billed by output duration only.

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
| `--image-url` | string | No | First-frame image URL or local path (JPEG/PNG/WebP). Enables image-to-video mode |
| `--end-image-url` | string | No | Last-frame image URL or local path. Only valid with `--image-url` |
| `--videos` | string | No | Reference video URLs (max 3, total max 15s) |
| `--audios` | string | No | Audio URLs (max 3) |
| `--ratio` | string | No | Aspect ratio (default: adaptive) |
| `--seed` | integer | No | Random seed for reproducible results |
| `--generate-audio` | boolean | No | Generate audio for the video (default: false) |

### Tips

- Provide `--image-url` to generate from a first frame (image-to-video). Add `--end-image-url` for first-last frame transition. `--end-image-url` without `--image-url` returns error 10192.
- The model does not support reference images or videos containing real human faces.
- Audio is only effective when images or videos are provided.
- Use `--seed` for reproducible results.

### Model Pricing

| Model Version | Resolution | Output Video Credits / Second | Reference Video Credits / Second |
|---------------|------------|-------------------------------|----------------------------------|
| seedance-2.0 | 480p | 30 | 10 |
| seedance-2.0 | 720p | 67 | 23 |
| seedance-2.0 | 1080p | 165 | 55 |
| seedance-2.0 | 4k | 340 | 114 |
| seedance-2.0-fast | 480p | 25 | 9 |
| seedance-2.0-fast | 720p | 53 | 18 |

Reference To Video billing formula:

`Credits = Output Video Credits × Duration (seconds) + Reference Video Credits × Total Reference Video Duration (seconds)`

The reference video duration is the sum of the durations of all reference videos in `--videos` (max 3 videos, total max 15 seconds). Text/Image To Video are billed by output duration only.

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
| `--image-url` | string | No | First-frame image URL or local path (JPEG/PNG/WebP). Enables image-to-video mode |
| `--end-image-url` | string | No | Last-frame image URL or local path. Only valid with `--image-url` |
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

## Seedream

Generate high-quality images from text prompts using the Seedream model. Supports multiple model versions for different quality and speed requirements, with both text-to-image and image-to-image generation modes via reference images.

- **Endpoint:** `POST /api/async/seedream`
- **Command:** `python byte_dance.py seedream run --prompt "..." [--image <url>] [options]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--model` | string | No | Model version (default: seedream-5.0-pro). Options: `seedream-5.0-pro`, `seedream-5.0-lite`, `seedream-4.5`, `seedream-4.0` |
| `--prompt` | string | Yes | Text prompt describing the image content. Supports Chinese and English |
| `--image` | string[] | No | Reference image URLs or local paths for img2img (max 10). Request body field is `image` (array). Formats: jpeg, png, webp, bmp, tiff, gif, heic, heif |
| `--size` | string | No | Output size. Custom `"WIDTHxHEIGHT"` is **total pixels** (width×height), not a per-edge minimum. **5.0 Pro:** floor **1280×720 = 921,600**, ceiling **4,624,220**; keywords `1K` / `1.5K` / `2K` only (no `3K`/`4K`). **4.5 / 5.0 Lite:** floor **2560×1440 = 3,686,400** (so `1920x1080` / `1024x1024` / `1K` fail; `2048x2048` is OK). Lite tiers: `2K`/`3K`/`4K`. 4.5 tiers: `2K`/`4K`. **4.0:** floor **1280×720 = 921,600**; tiers `1K`/`2K`/`4K`. |
| `--seed` | integer | No | Random seed for reproducible results (default: -1 for random) |

### Tips

- Use `--model` to select the desired model version. `seedream-5.0-pro` offers the highest quality.
- Seedream img2img uses `--image` and sends JSON field `image`. Seedance video reference images use `--images` and send JSON field `images`. Do not mix them.
- **Size floors differ by model.** 4.5 and 5.0 Lite do not accept 1K or any custom size below 3,686,400 total pixels. Do not copy Pro/4.0 sizes (`1280x720`, `1024x1024`, `1344x768`) onto Lite/4.5.
- Custom `WIDTHxHEIGHT` is checked as width×height. `2048x2048` (4.19M) meets the Lite/4.5 floor; `2560x1440` is the documented 16:9 minimum example.
- **seedream-5.0-pro keywords are `1K` / `1.5K` / `2K` only.** Do not send `3K` or `4K` on Pro. Pro custom sizes cannot exceed 4,624,220 total pixels.
- Pro billing is by total pixels, not by keyword name: ≤ 2,360,000 (typical `1K` / `1.5K`) costs 12 credits; > 2,360,000 (`2K`) costs 24 credits. Other Seedream models have a flat per-image price.
- Use `--seed` for reproducible results.
- Supported image formats for reference images: jpeg, png, webp, bmp, tiff, gif, heic, heif. Max 30MB per image.

### Model Pricing

| Model Version | Credits per Image |
|---------------|------------------|
| seedream-5.0-pro (1K / 1.5K, ≤ 2,360,000 pixels) | 12 |
| seedream-5.0-pro (2K, > 2,360,000 pixels) | 24 |
| seedream-5.0-lite | 9 |
| seedream-4.5 | 10 |
| seedream-4.0 | 8 |
