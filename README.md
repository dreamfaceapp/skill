# DreamAPI Skill

An AI agent skill that gives you access to 25 AI-powered tools for video generation, talking avatars, image editing, voice cloning, and more — all by simply describing what you want in natural language.

This skill follows the [Agent Skills specification](https://agentskills.io/specification) and works with any compatible AI coding assistant (Cursor, Claude Code, etc.).

## What Can You Do With This?

Install the skill, then just tell the AI what you need:

| You say... | You get... |
|------------|------------|
| "Generate a professional portrait photo" | An AI-generated image via Flux |
| "Animate this image into a short video" | A video clip via Wan2.1 |
| "Make a talking avatar from this photo and script" | A lip-synced avatar video |
| "Remove the background from this product photo" | A clean cutout PNG |
| "Swap the face in this video" | A face-swapped video |
| "Translate this video to Chinese" | A translated video with lip-sync |
| "Clone my voice from this audio" | A custom voice for TTS |
| "Read this text in a warm female voice" | A text-to-speech audio file |
| "Enhance this blurry old photo" | A sharpened, upscaled image |
| "Extend this image to the right" | An AI-outpainted image |

### Combined Workflows

The real power is chaining capabilities. Describe a goal and the AI orchestrates everything:

**Product marketing kit** — remove background from product photo, generate model showcase images, create a talking avatar video presenting the product, and produce TTS narration in multiple languages.

**Video localization** — translate a video to multiple languages with lip-sync, clone the speaker's voice for each language version.

**Portrait restoration** — colorize a B&W photo, enhance resolution, then animate it into a short video clip.

## Available Tools (25)

| Category | Tools | Script |
|----------|-------|--------|
| Avatar (4) | LipSync, LipSync 2.0, DreamAvatar 3.0 Fast, Dreamact | `scripts/avatar.py` |
| Image Generation (2) | Flux Text-to-Image, Flux Image-to-Image | `scripts/image_gen.py` |
| Image Editing (6) | Colorize, Enhance, Outpainting, Inpainting, Swap Face, Remove BG | `scripts/image_edit.py` |
| Video Generation (3) | Text-to-Video, Image-to-Video, Head-Tail-to-Video | `scripts/video_gen.py` |
| Video Editing (4) | Swap Face Video, Video Matting, Composite, Watermark Remover | `scripts/video_edit.py` |
| Video Translate (1) | Video Translate 2.0 | `scripts/video_translate.py` |
| Voice (5) | Voice Clone, TTS Clone, TTS Common, TTS Pro, Voice List | `scripts/voice.py` |

## Installation

```bash
npx skills add dreamapi/DreamAPI
```

## Configuration

Requires Python 3.8+ and a DreamAPI account.

### Get your API Key

1. Go to the [DreamAPI Dashboard](https://api.newportai.com/)
2. Sign in via Google or GitHub
3. Copy your API key

### Authenticate

```bash
pip install -r scripts/requirements.txt
python scripts/auth.py login
```

Or set the environment variable directly:

```bash
export DREAMAPI_API_KEY="your-api-key"
```

## Documentation

- [API Docs](https://api.newportai.com/api-docs) — Full API reference
- [Dashboard](https://api.newportai.com/) — Manage your account and API keys

## License

See [LICENSE.txt](LICENSE.txt).
