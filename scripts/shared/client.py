"""Reusable HTTP client for the DreamAPI with auth and task polling."""

import sys
import time
from typing import Any, Optional

import requests

from .config import load_api_key, BASE_URL

# Polling endpoint
POLL_ENDPOINT = "/api/getAsyncResult"

# Poll status codes
STATUS_SUCCESS = 3
STATUS_FAILED = 4
STATUS_PROCESSING = {0, 1, 2}  # queued / processing

DEFAULT_POLL_INTERVAL = 5  # seconds
DEFAULT_POLL_TIMEOUT = 600  # 10 minutes


class DreamAPIError(Exception):
    """Raised when the DreamAPI returns a non-zero response code."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class DreamAPIClient:
    """Authenticated HTTP client for DreamAPI endpoints.

    Usage::

        client = DreamAPIClient()
        resp = client.post("/api/async/colorize", json={"url": "..."})
        result = client.poll_task(task_id)
    """

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or load_api_key()

    @property
    def headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

    def _check(self, data: dict) -> dict:
        """Check API response and extract data payload."""
        code = data.get("code", -1)
        if code != 0:
            msg = data.get("message", "Unknown error")
            raise DreamAPIError(code, msg)
        return data.get("data", {})

    def post(self, path: str, json: Optional[dict] = None, **kwargs) -> dict:
        url = f"{BASE_URL}{path}" if path.startswith("/") else path
        resp = requests.post(url, headers=self.headers, json=json, timeout=30, **kwargs)
        resp.raise_for_status()
        return self._check(resp.json())

    def get(self, path: str, params: Optional[dict] = None, **kwargs) -> dict:
        url = f"{BASE_URL}{path}" if path.startswith("/") else path
        resp = requests.get(url, headers=self.headers, params=params, timeout=30, **kwargs)
        resp.raise_for_status()
        return self._check(resp.json())

    def submit_task(self, endpoint_path: str, body: dict, quiet: bool = False) -> str:
        """Submit an async task and return the taskId."""
        if not quiet:
            print(f"Submitting task to {endpoint_path}...", file=sys.stderr)

        data = self.post(endpoint_path, json=body)
        task_id = data.get("taskId", "")

        if not task_id:
            raise DreamAPIError(-1, "No taskId returned from submit")

        if not quiet:
            print(f"Task submitted. taskId: {task_id}", file=sys.stderr)
        return task_id

    def poll_task(
        self,
        task_id: str,
        *,
        interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_POLL_TIMEOUT,
        verbose: bool = True,
    ) -> dict:
        """Poll for task completion. Returns data dict on success.

        Keeps polling until status is SUCCESS (3) or FAILED (4),
        or until timeout is exceeded.
        """
        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                raise TimeoutError(
                    f"Task {task_id} did not complete within {timeout}s"
                )

            time.sleep(interval)

            data = self.post(POLL_ENDPOINT, json={"taskId": task_id})
            task_info = data.get("task", {})
            status = task_info.get("status")

            if verbose:
                print(
                    f"  [{elapsed:.0f}s] status: {status}",
                    file=sys.stderr,
                )

            if status == STATUS_SUCCESS:
                return data

            if status == STATUS_FAILED:
                reason = task_info.get("reason", "Unknown")
                raise DreamAPIError(-1, f"Task failed: {reason}")

        return {}

    def run_task(
        self,
        endpoint_path: str,
        body: dict,
        *,
        timeout: float = DEFAULT_POLL_TIMEOUT,
        interval: float = DEFAULT_POLL_INTERVAL,
        quiet: bool = False,
    ) -> dict:
        """Submit task + poll until done — full flow."""
        task_id = self.submit_task(endpoint_path, body, quiet=quiet)
        return self.poll_task(
            task_id,
            interval=interval,
            timeout=timeout,
            verbose=not quiet,
        )

    def extract_output(self, poll_data: dict) -> dict:
        """Extract meaningful output from poll response data.

        Returns dict with: task_id, output_url, output_type, and raw arrays.
        """
        result: dict[str, Any] = {}
        task = poll_data.get("task", {})
        result["task_id"] = task.get("taskId", "")

        images = poll_data.get("images", [])
        videos = poll_data.get("videos", [])
        audios = poll_data.get("audios", [])

        if images:
            result["images"] = [img.get("imageUrl", "") for img in images]
            result["output_url"] = result["images"][0]
            result["output_type"] = "image"

        if videos:
            result["videos"] = [vid.get("videoUrl", "") for vid in videos]
            result["output_url"] = result["videos"][0]
            result["output_type"] = "video"

        if audios:
            result["audios"] = [aud.get("audioUrl", "") for aud in audios]
            result["output_url"] = result["audios"][0]
            result["output_type"] = "audio"

        return result
