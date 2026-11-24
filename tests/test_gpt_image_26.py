"""GPT Image 2.6 命令契约测试。"""

import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import open_ai


class GptImage26CliTest(unittest.TestCase):
    def test_four_commands_submit_expected_payload(self):
        for variant in ("flare", "sunburst"):
            for mode in ("text", "image"):
                with self.subTest(variant=variant, mode=mode):
                    command = f"gpt-image-2.6-{variant}-{mode}-to-image"
                    args = ["open_ai.py", command, "run", "--prompt", "A room"]
                    expected = {
                        "prompt": "A room",
                        "width": 1024,
                        "height": 1024,
                        "quality": "low",
                        "n": 1,
                    }
                    if mode == "image":
                        args += ["--images", "reference.png", "https://example.test/second.png"]
                        expected["images"] = [
                            "https://example.test/uploaded.png",
                            "https://example.test/second.png",
                        ]
                    with mock.patch.object(sys, "argv", args), mock.patch.object(
                        open_ai, "DreamAPIClient"
                    ) as client, mock.patch.object(
                        open_ai, "resolve_local_file", side_effect=expected.get("images")
                    ) as resolve, mock.patch.object(open_ai, "print_result"):
                        open_ai.main()
                    client.return_value.run_task.assert_called_once_with(
                        f"/api/async/gpt_image_2.6/{variant}/{mode}_to_image",
                        expected,
                        timeout=600,
                        interval=5,
                        quiet=False,
                    )
                    if mode == "image":
                        self.assertEqual(
                            resolve.call_args_list,
                            [
                                mock.call("reference.png", quiet=False),
                                mock.call("https://example.test/second.png", quiet=False),
                            ],
                        )
                    else:
                        resolve.assert_not_called()

    def test_incompatible_input_is_rejected_before_submitting(self):
        cases = [
            ("flare-image-to-image", [], "the following arguments are required: --images"),
            ("flare-text-to-image", ["--images", "ref.png"], "unrecognized arguments: --images ref.png"),
            ("sunburst-text-to-image", ["--quality", "auto"], "invalid choice: 'auto'"),
        ]
        for mode, extra, error in cases:
            with self.subTest(mode=mode, extra=extra):
                args = ["open_ai.py", "gpt-image-2.6-" + mode, "run", "--prompt", "A room", *extra]
                stderr = io.StringIO()
                with mock.patch.object(sys, "argv", args), mock.patch.object(
                    open_ai, "DreamAPIClient"
                ) as client, contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as ex:
                    open_ai.main()
                self.assertEqual(ex.exception.code, 2)
                self.assertIn(error, stderr.getvalue())
                client.assert_not_called()
