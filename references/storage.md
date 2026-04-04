# Storage (File Upload)

DreamAPI provides a three-step file upload flow for uploading local files to cloud storage.

## Upload Flow

### Step 1: Get Upload Policy

- **Endpoint:** `GET /api/getUploadPolicy?fileName=<name>`
- Returns: `uploadUrl` (presigned URL) and `fileKey`

### Step 2: Upload File

- **Method:** `PUT <uploadUrl>`
- Upload the file binary to the presigned URL with appropriate Content-Type header

### Step 3: Get Upload Result

- **Endpoint:** `POST /api/getUploadResult`
- **Body:** `{"fileKey": "<fileKey>"}`
- Returns: `fileUrl` (the public URL of the uploaded file)

## Automatic Upload

All scripts handle local file upload automatically. When you pass a local file path (e.g. `--image ./photo.jpg`), the script detects it and:

1. Uploads the file via the three-step flow
2. Uses the returned URL in the API request

You never need to call the storage API manually.

## Supported Formats

**Images:** png, jpg, jpeg, bmp, webp, gif
**Audio:** mp3, wav, m4a, aac, flac
**Video:** mp4, avi, mov, mkv, webm
