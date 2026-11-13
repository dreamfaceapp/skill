"""Seedream 5.5 与 Seedance 2.5 样片请求的离线契约测试。"""
import argparse
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import byte_dance


class RequestContractTests(unittest.TestCase):
    def parse(self, tool, args):
        parser = argparse.ArgumentParser()
        byte_dance.TOOLS[tool]['add_args'](parser)
        parser.set_defaults(quiet=True)
        return parser.parse_args(args)

    def test_seedream55_text_and_image(self):
        tool = byte_dance.TOOLS['seedream-5.5']
        self.assertEqual(tool['endpoint'], '/api/async/seedream_5.5')
        text = tool['build_body'](self.parse('seedream-5.5', ['--prompt', 'cat', '--size', '1K']))
        self.assertEqual(text, {'model': 'seedream-5.5', 'prompt': 'cat', 'size': '1K'})
        with mock.patch.object(byte_dance, 'resolve_local_file', return_value='https://cdn.test/image.png') as upload:
            image = tool['build_body'](self.parse('seedream-5.5', ['--prompt', 'cat', '--image', 'local.png']))
        self.assertEqual(image['image'], ['https://cdn.test/image.png'])
        self.assertNotIn('images', image)
        upload.assert_called_once()

    def test_draft_text_and_first_frame(self):
        tool = byte_dance.TOOLS['seedance-2.5-draft']
        self.assertEqual(tool['endpoint'], '/api/async/seedance_2.5')
        args = self.parse('seedance-2.5-draft', ['--prompt', 'cat', '--resolution', '480p', '--duration', '4'])
        self.assertEqual(tool['build_body'](args)['draft'], True)
        with mock.patch.object(byte_dance, 'resolve_local_file', return_value='https://cdn.test/first.png'):
            args = self.parse('seedance-2.5-draft', ['--prompt', 'cat', '--resolution', '480p', '--duration', '4', '--image-url', 'first.png'])
            self.assertEqual(tool['build_body'](args)['imageUrl'], 'https://cdn.test/first.png')
        with self.assertRaises(SystemExit):
            self.parse('seedance-2.5-draft', ['--prompt', 'cat', '--resolution', '720p', '--duration', '4'])

    def test_draft_json_output_preserves_draft_ids(self):
        response = {'task': {'status': 3}, 'draftTaskIds': ['draft-id'], 'videos': []}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            byte_dance.print_result(response, argparse.Namespace(json=True), mock.Mock())
        self.assertEqual(json.loads(output.getvalue())['draftTaskIds'], ['draft-id'])

    def test_draft_reference_media_uses_documented_request_keys(self):
        args = self.parse('seedance-2.5-draft', ['--prompt', 'cat', '--resolution', '480p', '--duration', '4', '--images', 'i', '--videos', 'v', '--audios', 'a'])
        with mock.patch.object(byte_dance, 'resolve_local_file', side_effect=lambda value, quiet: value):
            body = byte_dance.TOOLS['seedance-2.5-draft']['build_body'](args)
        self.assertEqual((body['images'], body['videos'], body['audios']), (['i'], ['v'], ['a']))
        self.assertNotIn('image', body)

    def test_final_body_is_minimal_and_id_is_required(self):
        tool = byte_dance.TOOLS['seedance-2.5-draft-complete']
        args = self.parse('seedance-2.5-draft-complete', ['--draft-task-ids', 'draft-id'])
        self.assertEqual(tool['build_body'](args), {'model': 'seedance-2.5', 'resolution': '1080p', 'draftTaskIds': ['draft-id']})
        with self.assertRaises(SystemExit):
            self.parse('seedance-2.5-draft-complete', ['--draft-task-ids', 'a', 'b'])


if __name__ == '__main__':
    unittest.main()
