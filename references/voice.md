# Voice

Five voice tools: cloning, text-to-speech (three tiers), and voice browsing.

Script: `scripts/voice.py`

## Voice Clone

Clone a voice from an audio sample. Returns a `cloneId` for use with TTS Clone.

- **Endpoint:** `POST /api/async/voice_clone`
- **Command:** `python voice.py clone run --voice-url <url|path>`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--voice-url` | string | Yes | Audio sample URL or local path |

### Output

Prints the `cloneId` which can be used with `tts-clone`.

---

## TTS Clone

Text-to-speech using a previously cloned voice.

- **Endpoint:** `POST /api/async/do_tts_clone`
- **Command:** `python voice.py tts-clone run --clone-id <id> --text "..." --lang en`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--clone-id` | string | Yes | Cloned voice ID (from `voice clone`) |
| `--text` | string | Yes | Text to synthesize |
| `--lang` | string | Yes | Language: "en", "zh-CN", "es", etc. |

> **Important:** cloneId must come from a prior `voice clone` result. Never fabricate cloneId values.

---

## TTS Common

Text-to-speech with standard preset voices.

- **Endpoint:** `POST /api/async/do_tts_common`
- **Command:** `python voice.py tts-common run --audio-id <id> --text "..." --lang en`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--audio-id` | string | Yes | Voice ID from `voice list` (common type) |
| `--text` | string | Yes | Text to convert to speech |
| `--lang` | string | Yes | Language: "en", "zh-CN", "es", etc. |

> **Important:** audioId must be a REAL voice ID from `voice list`. Never fabricate values.

---

## TTS Pro

High-fidelity text-to-speech with premium voices. Better quality and more natural intonation than TTS Common.

- **Endpoint:** `POST /api/async/do_tts_pro`
- **Command:** `python voice.py tts-pro run --audio-id <id> --text "..." --lang en`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--audio-id` | string | Yes | Pro voice ID from `voice list` (pro type) |
| `--text` | string | Yes | Text to synthesize |
| `--lang` | string | Yes | Language: "en", "zh-CN", "es", etc. |

### Example Pro Voice IDs

| Name | Gender | audioId |
|------|--------|---------|
| Robert | Male | `35751531b9c64d7c94b7fe591401ab9d` |
| Grace | Female | `7b5f03827ac04ba49e85b4c87dc7ffb4` |

> Always use `voice list --type pro` to get current IDs.

---

## Voice List

List available voices for TTS. Reads from bundled catalog.

- **Command:** `python voice.py list [--type common|pro] [--language English] [--timbre male]`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--type` | string | No | Filter: "common" or "pro" |
| `--language` | string | No | Filter by language (e.g. "English", "Chinese") |
| `--timbre` | string | No | Filter by timbre (e.g. "male", "female") |
| `--json` | flag | No | Output as JSON |

### Output Format

Tab-separated: `audioId  name  type  language  timbre`

### Usage with TTS

```bash
# Find a female English pro voice
python voice.py list --type pro --language English --timbre female

# Use the audioId with TTS Pro
python voice.py tts-pro run --audio-id <audioId> --text "Hello world" --lang en
```
