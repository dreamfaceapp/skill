#!/usr/bin/env python3
"""Offline checks for the skill-adoption fix table (items 1–12)."""

from __future__ import annotations

import argparse
import inspect
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from shared.client import DreamAPIClient, DreamAPIError  # noqa: E402
from shared.upload import (  # noqa: E402
    parse_upload_policy,
    resolve_local_file,
)
import auth as auth_mod  # noqa: E402
import byte_dance  # noqa: E402
import video_gen  # noqa: E402


class Item1ReadmeInstall(unittest.TestCase):
    def test_install_command_points_at_public_repo(self):
        text = (ROOT / "README.md").read_text()
        self.assertIn("npx skills add dreamfaceapp/skill", text)
        self.assertNotIn("npx skills add dreamapi/DreamAPI", text)
        self.assertIn("scripts/", text)
        self.assertIn("Python 3.10+", text)


class Item2GithubDescription(unittest.TestCase):
    def test_readme_tool_count_is_36(self):
        text = (ROOT / "README.md").read_text()
        self.assertIn("36 AI-powered tools", text)
        self.assertIn("## Available Tools (36)", text)


class Item3SeedanceMediaUpload(unittest.TestCase):
    def _args(self, **overrides):
        base = dict(
            prompt="a cat",
            resolution="720p",
            duration=5,
            images=None,
            videos=["https://cdn.example/ref.mp4"],
            audios=["https://cdn.example/ref.wav"],
            ratio="adaptive",
            seed=None,
            generate_audio=False,
            image_url=None,
            end_image_url=None,
            quiet=True,
        )
        base.update(overrides)
        return SimpleNamespace(**base)

    def test_https_videos_and_audios_pass_through_all_builders(self):
        args = self._args()
        for builder in (
            byte_dance.build_seedance_2_5_body,
            byte_dance.build_seedance_body,
            byte_dance.build_seedance_mini_body,
        ):
            body = builder(args)
            self.assertEqual(body["videos"], ["https://cdn.example/ref.mp4"])
            self.assertEqual(body["audios"], ["https://cdn.example/ref.wav"])
            self.assertNotIn("image", body)

    def test_missing_local_video_is_rejected_before_request(self):
        args = self._args(videos=["/tmp/does-not-exist-skill-audit.mp4"], audios=None)
        with self.assertRaises(FileNotFoundError):
            byte_dance.build_seedance_body(args)

    def test_existing_local_video_calls_resolve_upload(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as handle:
            handle.write(b"fake")
            path = handle.name
        try:
            args = self._args(videos=[path], audios=None)
            with mock.patch(
                "byte_dance.resolve_local_file",
                side_effect=lambda ref, quiet=False: f"https://uploaded.example/{os.path.basename(ref)}",
            ) as patched:
                body = byte_dance.build_seedance_2_5_body(args)
            patched.assert_called()
            self.assertTrue(body["videos"][0].startswith("https://uploaded.example/"))
        finally:
            os.unlink(path)


class Item4PollErrorCode(unittest.TestCase):
    def test_failed_poll_keeps_server_error_code_and_task_id(self):
        client = DreamAPIClient(api_key="sk-test")
        payload = {
            "task": {
                "taskId": "task-abc",
                "status": 4,
                "errorCode": -2008,
                "reason": "busy",
            }
        }
        with mock.patch.object(client, "post", return_value=payload), mock.patch(
            "shared.client.time.sleep"
        ):
            with self.assertRaises(DreamAPIError) as ctx:
                client.poll_task("task-abc", interval=0, timeout=5, verbose=False)
        self.assertEqual(ctx.exception.code, -2008)
        self.assertEqual(ctx.exception.task_id, "task-abc")
        self.assertIn("busy", ctx.exception.message)
        self.assertNotEqual(ctx.exception.code, -1)


class Item5UploadPolicy(unittest.TestCase):
    def test_official_key_and_oss_access_key_id(self):
        parsed = parse_upload_policy(
            {
                "host": "https://oss.example",
                "OSSAccessKeyId": "LTAIxxxx",
                "policy": "p",
                "signature": "s",
                "key": "tmp/dream/uuid-object",
                "callback": "cb",
                "reqId": "req-1",
            },
            "photo.jpg",
        )
        self.assertEqual(parsed["key"], "tmp/dream/uuid-object")
        self.assertEqual(parsed["access_id"], "LTAIxxxx")
        self.assertNotIn("photo.jpg", parsed["key"])

    def test_legacy_dir_and_access_id(self):
        parsed = parse_upload_policy(
            {
                "host": "https://oss.example",
                "accessId": "legacy-id",
                "policy": "p",
                "signature": "s",
                "dir": "tmp/dream/",
            },
            "photo.jpg",
        )
        self.assertEqual(parsed["key"], "tmp/dream/photo.jpg")
        self.assertEqual(parsed["access_id"], "legacy-id")

    def test_official_docs_shape_no_longer_raises_before_upload(self):
        parse_upload_policy(
            {
                "host": "https://dreamapi-oss.oss-cn-hongkong.aliyuncs.com",
                "OSSAccessKeyId": "LTAI5tF1QzxoHGvEcziVACyc",
                "policy": "eyJ",
                "signature": "sig",
                "key": "tmp/dream/2024-11-19/id/file",
                "callback": "eyJ",
                "reqId": "f6915012",
            },
            "local.mp4",
        )

    def test_incomplete_policy_still_fails(self):
        with self.assertRaises(RuntimeError):
            parse_upload_policy({"host": "https://x"}, "a.jpg")


class Item6MissingLocalPath(unittest.TestCase):
    def test_https_passthrough(self):
        url = "https://cdn.example/a.png"
        self.assertEqual(resolve_local_file(url, quiet=True), url)

    def test_missing_absolute_path_raises(self):
        with self.assertRaises(FileNotFoundError):
            resolve_local_file("/tmp/missing-skill-adoption.png", quiet=True)

    def test_missing_extension_path_raises(self):
        with self.assertRaises(FileNotFoundError):
            resolve_local_file("missing-local.jpg", quiet=True)

    def test_existing_file_uploads(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
            handle.write(b"png")
            path = handle.name
        try:
            with mock.patch(
                "shared.upload.upload_file", return_value="https://oss.example/x.png"
            ) as patched:
                out = resolve_local_file(path, quiet=True)
            patched.assert_called_once()
            self.assertEqual(out, "https://oss.example/x.png")
        finally:
            os.unlink(path)


class Item7DreamvideoDuration(unittest.TestCase):
    def test_cli_rejects_999(self):
        parser = argparse.ArgumentParser()
        video_gen.add_dreamvideo_text2video_args(parser)
        buf = io.StringIO()
        with self.assertRaises(SystemExit), mock.patch("sys.stderr", buf):
            parser.parse_args(["--prompt", "cat", "--duration", "999"])
        self.assertIn("3 and 15", buf.getvalue())

    def test_cli_accepts_5(self):
        parser = argparse.ArgumentParser()
        video_gen.add_dreamvideo_text2video_args(parser)
        args = parser.parse_args(["--prompt", "cat", "--duration", "5"])
        self.assertEqual(args.duration, 5)

    def test_omitted_resolution_is_not_sent(self):
        args = SimpleNamespace(
            prompt="cat", duration=None, resolution=None, aspect_ratio=None, seed=None
        )
        body = video_gen.build_dreamvideo_text2video_body(args)
        self.assertEqual(body, {"prompt": "cat"})
        self.assertNotIn("resolution", body)

    def test_programmatic_duration_out_of_range(self):
        args = SimpleNamespace(
            prompt="cat", duration=999, resolution=None, aspect_ratio=None, seed=None
        )
        with self.assertRaises(ValueError):
            video_gen.build_dreamvideo_text2video_body(args)


class Item8SkillFrontmatter(unittest.TestCase):
    def test_requires_is_a_string_and_compatibility_present(self):
        text = (ROOT / "SKILL.md").read_text()
        front = text.split("---", 2)[1]
        self.assertIn("compatibility: Requires Python 3.10+", front)
        self.assertIn("requires: python3", front)
        self.assertNotIn("bins:", front)
        self.assertNotIn("requires:\n    bins:", text)


class Item9WorkflowDocs(unittest.TestCase):
    def test_run_vs_submit_priority_is_documented(self):
        skill = (ROOT / "SKILL.md").read_text()
        self.assertIn("Single new generation → `run`", skill)
        self.assertIn("Parallel independent tasks → `submit` then `query`", skill)
        self.assertIn("ask before", skill.lower())
        polling = (ROOT / "references" / "polling.md").read_text()
        self.assertIn("ask the user, then `run` only if they confirm", polling)


class Item10ReplyRules(unittest.TestCase):
    def test_debug_exception_and_no_default_json_dump(self):
        skill = (ROOT / "SKILL.md").read_text()
        self.assertIn("Debugging exception", skill)
        self.assertIn("taskId", skill)
        self.assertIn("Never mention `creditsConsumed`", skill)
        self.assertIn("Do not dump raw logs", skill)


class Item11ExtractOutput(unittest.TestCase):
    def test_expire_kept_credits_hidden(self):
        client = DreamAPIClient(api_key="sk-test")
        data = {
            "task": {"taskId": "t1", "status": 3},
            "images": [{"imageUrl": "https://cdn.example/a.png", "expireAt": "2099-01-01"}],
            "creditsConsumed": 12,
            "expire": "2099-01-02",
        }
        out = client.extract_output(data)
        self.assertEqual(out["output_url"], "https://cdn.example/a.png")
        self.assertEqual(out["expire"], "2099-01-02")
        self.assertNotIn("creditsConsumed", out)
        self.assertNotIn("credits_consumed", out)


class Item12Auth(unittest.TestCase):
    def test_login_uses_getpass_not_input(self):
        source = inspect.getsource(auth_mod.cmd_login)
        self.assertIn("getpass.getpass", source)
        self.assertNotIn("input(", source)

    def test_unverified_key_is_not_saved_without_force(self):
        tmp = Path(tempfile.mkdtemp()) / "credentials.json"
        args = SimpleNamespace(key="sk-invalid", force=False)
        with mock.patch.object(auth_mod, "CRED_FILE", tmp), mock.patch.object(
            auth_mod, "_verify_api_key", return_value=None
        ):
            with self.assertRaises(SystemExit) as ctx:
                auth_mod.cmd_login(args)
        self.assertEqual(ctx.exception.code, 1)
        self.assertFalse(tmp.exists())

    def test_force_saves_unverified_key(self):
        tmp = Path(tempfile.mkdtemp()) / "credentials.json"
        args = SimpleNamespace(key="sk-invalid", force=True)
        with mock.patch.object(auth_mod, "CRED_FILE", tmp), mock.patch.object(
            auth_mod, "_verify_api_key", return_value=None
        ):
            auth_mod.cmd_login(args)
        self.assertTrue(tmp.exists())
        self.assertEqual(tmp.stat().st_mode & 0o777, 0o600)
        tmp.unlink()


if __name__ == "__main__":
    unittest.main()
