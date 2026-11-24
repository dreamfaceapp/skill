"""DreamVideo 3.0 参考生 CLI 契约。"""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import video_gen


class DreamVideoReferenceCliTest(unittest.TestCase):
    def invoke(self, options):
        argv = ["video_gen.py", "dreamvideo-3.0-reference-to-video", "run", "--prompt", "A scene"]
        with mock.patch.object(sys, "argv", argv + options):
            video_gen.main()

    def test_cli_resolves_reference_arrays_in_order_and_preserves_false(self):
        files = ["a.png", "b.png", "clip.mp4", "voice.wav"]
        urls = [f"https://example.test/{f}" for f in files]
        with mock.patch.object(video_gen, "DreamAPIClient") as client, mock.patch.object(
            video_gen, "resolve_local_file", side_effect=urls
        ) as resolve, mock.patch.object(video_gen, "print_result"):
            self.invoke([
                "--images", *files[:2], "--videos", files[2], "--audios", files[3],
                "--no-enable-video-audio", "--duration", "1", "--resolution", "720P",
                "--aspect-ratio", "21:9", "--seed", "42",
            ])
        self.assertEqual(resolve.call_args_list, [mock.call(f, quiet=False) for f in files])
        endpoint, body = client.return_value.run_task.call_args.args
        self.assertEqual(endpoint, "/api/async/dreamvideo_3.0/reference_to_video")
        self.assertEqual(body, {
            "prompt": "A scene", "duration": 1, "resolution": "720P", "aspectRatio": "21:9",
            "seed": 42, "images": urls[:2], "videos": urls[2:3], "audios": urls[3:],
            "enableVideoAudio": False,
        })

    def test_invalid_media_is_rejected_before_upload(self):
        cases = [
            (["--audios", "voice.wav"], "at least one reference image or video"),
            (["--images", *(["ref.png"] * 10)], "at most 9 reference images"),
            (["--videos", *(["clip.mp4"] * 4)], "at most 3 reference videos"),
            (["--images", "ref.png", "--audios", *(["voice.wav"] * 4)], "at most 3 reference audios"),
            (["--images", *(["ref.png"] * 9), "--videos", "clip.mp4",
              "--audios", *(["voice.wav"] * 3)], "at most 12 references in total"),
        ]
        for args, reason in cases:
            with self.subTest(args=args):
                stderr = io.StringIO()
                with mock.patch.object(video_gen, "DreamAPIClient") as client, mock.patch.object(
                    video_gen, "resolve_local_file"
                ) as upload, contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
                    self.invoke(args)
                self.assertIn(reason, stderr.getvalue())
                upload.assert_not_called()
                client.return_value.run_task.assert_not_called()

    def test_omits_unspecified_options(self):
        with mock.patch.object(video_gen, "DreamAPIClient") as client, mock.patch.object(
            video_gen, "resolve_local_file", return_value="https://example.test/ref.png"
        ), mock.patch.object(video_gen, "print_result"):
            self.invoke(["--images", "ref.png"])
        self.assertEqual(client.return_value.run_task.call_args.args[1], {
            "prompt": "A scene", "images": ["https://example.test/ref.png"],
        })

    def test_existing_dreamvideo_modes_keep_duration_and_ratio_constraints(self):
        for command in ("dreamvideo-text2video", "dreamvideo-image2video"):
            base = ["video_gen.py", command, "run", "--prompt", "A scene"]
            if command == "dreamvideo-image2video":
                base += ["--images", "ref.png"]
            for extra, reason in [
                (["--duration", "1"], "duration must be between 3 and 15"),
                (["--aspect-ratio", "21:9"], "invalid choice: '21:9'"),
            ]:
                with self.subTest(command=command, options=extra):
                    stderr = io.StringIO()
                    with mock.patch.object(sys, "argv", base + extra), contextlib.redirect_stderr(
                        stderr
                    ), self.assertRaises(SystemExit):
                        video_gen.main()
                    self.assertIn(reason, stderr.getvalue())
