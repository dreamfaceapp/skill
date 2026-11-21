"""Seedance 2.5 Flash CLI 请求契约。"""

import argparse
import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import byte_dance


class Seedance25FlashTests(unittest.TestCase):
    def setUp(self):
        self.tool = byte_dance.TOOLS["seedance-2.5-flash"]
        self.parser = argparse.ArgumentParser()
        self.tool["add_args"](self.parser)
        self.parser.set_defaults(quiet=True)
        self.base = ["--prompt", "A quiet park", "--resolution", "720p", "--duration", "5"]

    def body(self, extra=()):
        return self.tool["build_body"](self.parser.parse_args(self.base + list(extra)))

    def test_text_uses_flash_endpoint_without_media(self):
        self.assertEqual(self.tool["endpoint"], "/api/async/seedance_2.5_flash")
        self.assertEqual(self.body(), {
            "model": "seedance-2.5-flash",
            "prompt": "A quiet park",
            "resolution": "720p",
            "duration": 5,
            "ratio": "adaptive",
        })

    def test_first_frame_and_first_last_frame(self):
        first = "https://cdn.test/first.png"
        last = "https://cdn.test/last.png"
        for extra in (("--image-url", first), ("--image-url", first, "--end-image-url", last)):
            body = self.body((*extra, "--ratio", "16:9", "--generate-audio"))
            self.assertEqual(body["imageUrl"], first)
            self.assertEqual(body.get("endImageUrl"), last if len(extra) == 4 else None)
            self.assertEqual(body["ratio"], "adaptive")
            self.assertIs(body["generateAudio"], True)
            self.assertNotIn("images", body)

    def test_references_keep_input_order(self):
        images = ["https://cdn.test/2.png", "https://cdn.test/1.png"]
        videos = ["https://cdn.test/ref.mp4"]
        audios = ["https://cdn.test/ref.mp3"]
        body = self.body(["--images", *images, "--videos", *videos, "--audios", *audios,
                          "--ratio", "16:9", "--no-generate-audio"])
        self.assertEqual(body["images"], images)
        self.assertEqual(body["videos"], videos)
        self.assertEqual(body["audios"], audios)
        self.assertEqual(body["ratio"], "16:9")
        self.assertIs(body["generateAudio"], False)
        self.assertNotIn("imageUrl", body)

    def test_resolution_and_duration_limits(self):
        for resolution in ("1080p", "4k"):
            with self.subTest(resolution=resolution), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    self.body(["--resolution", resolution])
        for value in ("3", "31"):
            with self.subTest(duration=value), self.assertRaises(ValueError):
                self.body(["--duration", value])
        self.assertEqual(self.body(["--duration", "4"])["duration"], 4)
        self.assertEqual(self.body(["--duration", "30"])["duration"], 30)

    def test_rejects_invalid_media_before_upload(self):
        cases = [
            ["--end-image-url", "last.png"],
            ["--image-url", "first.png", "--images", "reference.png"],
            ["--images"] + ["ref.png"] * 11,
            ["--videos"] + ["ref.mp4"] * 6,
            ["--audios"] + ["ref.mp3"] * 6,
        ]
        with mock.patch.object(byte_dance, "resolve_local_file") as upload:
            for flags in cases:
                with self.subTest(flags=flags), self.assertRaises(ValueError):
                    self.body(flags)
            upload.assert_not_called()
