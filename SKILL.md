---
name: dreamapi-skill
description: "25 AI-powered tools for video generation, talking avatars, image editing, voice cloning, and more — powered by DreamAPI. Describe what you want and the agent handles the rest."
metadata:
  tags: dreamapi, avatar, lipsync, video, image, voice, tts, flux, wan2.1, ai, api, text2image, image2video, face-swap, remove-bg, video-translate, voice-clone
  requires:
    bins: [python3]
  primaryEnv: DREAMAPI_API_KEY
---

# DreamAPI Skill

> 25 AI tools powered by [DreamAPI](https://api.newportai.com/) — from Newport AI.

## Execution Rule

> **Always use the Python scripts in `scripts/`. Do NOT use `curl` or direct HTTP calls.**

## User-Facing Reply Rules

> **Every user-facing reply MUST follow ALL rules below.**

1. **Keep replies short** — give the result or next step directly.
2. **Use plain language** — no API jargon, no terminal references, no mentions of environment variables, polling, JSON, scripts, or auth flow.
3. **Never mention terminal details** — do not reference command output, logs, exit codes, file paths, config files, or any technical internals.
4. **Always send the login link directly** — when login is needed, provide the DreamAPI Dashboard link: `https://api.newportai.com/`
5. **Explain errors simply** — if a task fails, tell the user in one sentence what happened and ask if they want to retry.
6. **Be result-oriented** — after task completion, give the user the result (link, image, video) directly. Do not describe intermediate steps.
7. **Give time estimates** — after submitting a task, tell the user the estimated wait time from the table below.

**Estimated Generation Time**

| Task Type | Estimated Time |
|-----------|---------------|
| Avatar (LipSync / DreamAvatar / Dreamact) | ~2–5 min |
| Image Generation (Flux) | ~30s–1 min |
| Image Editing (Colorize / Enhance / etc.) | ~30s–1 min |
| Video Generation (Wan2.1) | ~3–5 min |
| Video Editing (Swap Face / Matting) | ~2–5 min |
| Video Translate | ~3–5 min |
| Voice Clone | ~30s–1 min |
| TTS (Common / Pro / Clone) | ~10–30s |
| Remove Background | ~10–30s |

**Required login message template**

When authentication is needed, send the user this message (match user's language):

```text
To get started, you need a DreamAPI API key.

1. Go to: https://api.newportai.com/
2. Sign in with Google or GitHub
3. Copy your API key from the Dashboard

Once you have your key, just tell me and I'll set it up for you.
```

中文模板：

```text
开始之前，你需要一个 DreamAPI 的 API Key。

1. 打开 https://api.newportai.com/
2. 用 Google 或 GitHub 登录
3. 在 Dashboard 页面复制你的 API Key

拿到 Key 后告诉我，我帮你设置好。
```

## Prerequisites

- **Python 3.8+**
- Authenticated — see [references/auth.md](references/auth.md)
- Credits available — see [references/user.md](references/user.md)

```bash
pip install -r {baseDir}/scripts/requirements.txt
```

## Agent Workflow Rules

> **These rules apply to ALL generation modules.**

1. **Always start with `run`** — it submits the task and polls automatically until done.
2. **Do NOT ask the user to check the task status themselves.** The agent polls until completion.
3. **Only use `query`** when `run` has already timed out and you have a `taskId` to resume.
4. **If `query` also times out**, increase `--timeout` and try again with the same `taskId`.
5. **Do not resubmit** unless the task has actually failed.

```
Decision tree:
  → New request?           use `run`
  → run timed out?         use `query --task-id <id>`
  → query timed out?       use `query --task-id <id> --timeout 1200`
  → task status=fail?      resubmit with `run`
```

**Task Status Codes:**

| Code | Status | Description |
|------|--------|-------------|
| 0-2 | Processing | Task is queued or running |
| 3 | Success | Task completed |
| 4 | Failed | Task failed |

## Modules

| Module | Script | Reference | Description |
|--------|--------|-----------|-------------|
| Auth | `scripts/auth.py` | [auth.md](references/auth.md) | API key management — login, status, logout |
| Avatar | `scripts/avatar.py` | [avatar.md](references/avatar.md) | LipSync, LipSync 2.0, DreamAvatar 3.0 Fast, Dreamact |
| Image Gen | `scripts/image_gen.py` | [image_gen.md](references/image_gen.md) | Flux Text-to-Image, Flux Image-to-Image |
| Image Edit | `scripts/image_edit.py` | [image_edit.md](references/image_edit.md) | Colorize, Enhance, Outpainting, Inpainting, Swap Face, Remove BG |
| Video Gen | `scripts/video_gen.py` | [video_gen.md](references/video_gen.md) | Text-to-Video, Image-to-Video, Head-Tail-to-Video (Wan2.1) |
| Video Edit | `scripts/video_edit.py` | [video_edit.md](references/video_edit.md) | Swap Face Video, Video Matting, Composite |
| Video Translate | `scripts/video_translate.py` | [video_translate.md](references/video_translate.md) | Video Translate 2.0 (en/zh/es) |
| Voice | `scripts/voice.py` | [voice.md](references/voice.md) | Voice Clone, TTS Clone, TTS Common, TTS Pro, Voice List |
| User | `scripts/user.py` | [user.md](references/user.md) | Credit balance |

> **Read individual reference docs for usage, options, and examples.**
> Local files (image/audio/video) are auto-uploaded when passed as arguments.

## Tool Selection Guide

```
What does the user need?
│
├─ A talking face synced to audio?
│  ├─ Has a video + audio → avatar.py lipsync / lipsync2
│  └─ Has a photo + audio → avatar.py dreamavatar
│
├─ A character performing actions from a driving video?
│  → avatar.py dreamact
│
├─ Generate an image from text?
│  → image_gen.py text2image
│
├─ Transform an existing image?
│  → image_gen.py image2image
│
├─ Edit an image?
│  ├─ Colorize B&W photo → image_edit.py colorize
│  ├─ Enhance quality → image_edit.py enhance
│  ├─ Extend borders → image_edit.py outpainting
│  ├─ Fill/replace region → image_edit.py inpainting
│  ├─ Replace face → image_edit.py swap-face
│  └─ Remove background → image_edit.py remove-bg
│
├─ Generate a video from text?
│  → video_gen.py text2video
│
├─ Animate an image into video?
│  → video_gen.py image2video
│
├─ Create transition between two frames?
│  → video_gen.py head-tail
│
├─ Edit a video?
│  ├─ Replace face → video_edit.py swap-face
│  ├─ Remove background → video_edit.py matting
│  └─ Replace background → video_edit.py matting + composite
│
├─ Translate video speech?
│  → video_translate.py
│
├─ Text-to-speech?
│  ├─ With cloned voice → voice.py clone + tts-clone
│  ├─ Standard quality → voice.py tts-common
│  └─ Premium quality → voice.py tts-pro
│
├─ Browse available voices?
│  → voice.py list
│
├─ Check credit balance?
│  → user.py credit
│
└─ Outside capabilities?
   → Tell user this isn't supported yet
```

## Quick Reference

| User says... | Script & Command |
|-------------|-----------------|
| "Make a talking face video with this audio" | `avatar.py lipsync run` |
| "Generate an avatar from this photo and audio" | `avatar.py dreamavatar run` |
| "Make this character do the dance in this video" | `avatar.py dreamact run` |
| "Generate an image of..." | `image_gen.py text2image run` |
| "Modify this image to..." | `image_gen.py image2image run` |
| "Colorize this old photo" | `image_edit.py colorize run` |
| "Enhance this blurry image" | `image_edit.py enhance run` |
| "Extend this image" | `image_edit.py outpainting run` |
| "Fill in this area of the image" | `image_edit.py inpainting run` |
| "Swap the face in this photo" | `image_edit.py swap-face run` |
| "Remove the background" | `image_edit.py remove-bg run` |
| "Generate a video about..." | `video_gen.py text2video run` |
| "Animate this image into a video" | `video_gen.py image2video run` |
| "Create a transition between these two images" | `video_gen.py head-tail run` |
| "Swap the face in this video" | `video_edit.py swap-face run` |
| "Remove the video background" | `video_edit.py matting run` |
| "Replace the video background with..." | `video_edit.py matting run` + `composite run` |
| "Translate this video to Chinese" | `video_translate.py run` |
| "Clone this voice" | `voice.py clone run` |
| "Read this text with the cloned voice" | `voice.py tts-clone run` |
| "Convert this text to speech" | `voice.py tts-common run` or `tts-pro run` |
| "What voices are available?" | `voice.py list` |
| "How many credits do I have?" | `user.py credit` |

## Agent Behavior Protocol

### During Execution

1. **Local files auto-upload** — scripts detect local paths and upload via DreamAPI Storage automatically
2. **Parallelize independent tasks** — independent generation tasks can run concurrently via `submit`
3. **Keep consistency** — when generating multiple related outputs, use consistent parameters

### After Execution

Show the result URL first, then key metadata. Keep it clean.

**Result template:**

```text
[type emoji] [task type] complete

Result: <OUTPUT_URL>
• [key metadata]

Not happy with the result? Let me know and I'll adjust.
```

### Error Handling

See [references/error_handling.md](references/error_handling.md) for error codes and recovery.

## Capability Boundaries

| Category | Tools | Count |
|----------|-------|-------|
| Avatar | LipSync, LipSync 2.0, DreamAvatar 3.0 Fast, Dreamact | 4 |
| Image Generation | Flux Text-to-Image, Flux Image-to-Image | 2 |
| Image Editing | Colorize, Enhance, Outpainting, Inpainting, Swap Face, Remove BG | 6 |
| Video Generation | Text-to-Video, Image-to-Video, Head-Tail-to-Video | 3 |
| Video Editing | Swap Face Video, Video Matting, Composite | 3 |
| Video Translate | Video Translate 2.0 | 1 |
| Voice | Voice Clone, TTS Clone, TTS Common, TTS Pro, Voice List | 5 |
| **Total** | | **24** |

> **Never promise capabilities that don't exist as modules.**
