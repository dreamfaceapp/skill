# Storage (File Upload)

DreamAPI provides a three-step file upload flow for uploading local files to cloud storage.

## Upload Flow

### Step 1: Get Upload Policy

- **Endpoint:** `POST /api/file/v1/get_policy`
- **Body:** `{"scene": "Dream-CN"}`
- Returns OSS credentials (`host`, `dir`, `accessId`, `policy`, `signature`, `callback`, `reqId`)

### Step 2: Upload File

- **Method:** `POST <host>` (multipart form to the OSS endpoint from step 1)
- Include policy fields plus the file binary

### Step 3: Get Upload Result

- **Endpoint:** `POST /api/file/v1/policy_upload_finish`
- **Body:** `{"reqId": "<reqId>"}`
- Returns: `url` (the public URL of the uploaded file)

## Automatic Upload

All scripts handle local file upload automatically. When you pass a local file path (e.g. `--image ./photo.jpg`), the script detects it and:

1. Uploads the file via the three-step flow
2. Uses the returned URL in the API request

You never need to call the storage API manually.

## Supported Formats

**Images:** png, jpg, jpeg, bmp, webp, gif
**Audio:** mp3, wav, m4a, aac, flac
**Video:** mp4, avi, mov, mkv, webm
