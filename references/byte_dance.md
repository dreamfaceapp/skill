# ByteDance

Video generation tools powered by ByteDance models.

Script: `scripts/byte_dance.py`

## Seedance 2.0

Generate videos using the Seedance 2.0 model with support for text prompts, reference images, reference videos, and audio.

- **Endpoint:** `POST /api/async/seedance_2.0`
- **Command:** `python byte_dance.py seedance run --prompt "..." --resolution <480p|720p> --duration <4-15> [options]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--prompt` | string | Yes | Video description (max 1500 chars) |
| `--resolution` | string | Yes | Output resolution: "480p" or "720p" |
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
