import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('render_fixture', ROOT / 'skills/witcut/scripts/render_fixture.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
AVAILABLE = bool(shutil.which('ffmpeg') and shutil.which('ffprobe') and fixture.FONT.is_file())
if AVAILABLE:
    AVAILABLE = ' flite ' in fixture.run(['ffmpeg', '-hide_banner', '-filters'])[0]


@unittest.skipUnless(AVAILABLE, 'Integration requires local FFmpeg libflite, ffprobe and DejaVuSans')
class RenderFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name) / 'fixture'
        cls.qa = fixture.generate(cls.root)
        cls.manifest = json.loads((cls.root / 'execution.json').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_candidate_has_speech_and_video_but_no_listening_claim(self):
        self.assertEqual({s['codec_type'] for s in self.qa['streams']}, {'video', 'audio'})
        self.assertEqual(self.qa['duration'], 12)
        self.assertEqual(self.qa['full_decode'], 'pass')
        self.assertNotIn('max_volume: -inf', self.qa['audio_signal_log'])
        self.assertIn('max_volume:', self.qa['audio_signal_log'])
        self.assertEqual(self.qa['listening'], 'not tested')
        self.assertEqual(self.qa['normal_speed_viewing'], 'not tested')
        self.assertIn('Only after', (self.root / 'narration.txt').read_text())

    def test_same_sources_and_manifest_reproduce_candidate_in_this_runtime(self):
        destination = self.root / 'reproduced.mp4'
        fixture.render(self.manifest, self.root, destination)
        self.assertEqual(fixture.sha(destination), self.qa['candidate_sha256'])

    def test_no_overwrite(self):
        before = fixture.sha(self.root / 'candidate.mp4')
        with self.assertRaises(FileExistsError):
            fixture.generate(self.root)
        self.assertEqual(fixture.sha(self.root / 'candidate.mp4'), before)

    def test_missing_mapping_rejected_before_render(self):
        manifest = copy.deepcopy(self.manifest)
        del manifest['clips'][0]['output_start']
        with self.assertRaisesRegex(ValueError, 'differs from plan projection'):
            fixture.validate_manifest(manifest, self.root)

    def test_short_output_cannot_silently_compress_operation(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['clips'][0]['output_end'] = 0.1
        with self.assertRaisesRegex(ValueError, 'differs from plan projection'):
            fixture.validate_manifest(manifest, self.root)

    def test_narration_cannot_replace_visual(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['clips'][0]['source_id'] = 'speech'
        manifest['clips'][0].update(end=1, output_end=1)
        with self.assertRaisesRegex(ValueError, 'differs from plan projection'):
            fixture.validate_manifest(manifest, self.root)

    def test_changed_source_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['sources'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'changed source'):
            fixture.validate_manifest(manifest, self.root)

    def test_hold_and_reference_rejected(self):
        for mode in ('hold', 'reference'):
            manifest = copy.deepcopy(self.manifest)
            manifest['clips'][0]['playback'] = mode
            with self.assertRaisesRegex(ValueError, 'differs from plan projection'):
                fixture.validate_manifest(manifest, self.root)

    def test_invalid_plan_path_is_reported(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['plan']['path'] = []
        with self.assertRaisesRegex(ValueError, 'Invalid plan path'):
            fixture.validate_manifest(manifest, self.root)

    def test_plan_is_mapping_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'copy'
            shutil.copytree(self.root, root)
            manifest = copy.deepcopy(self.manifest)
            path = root / 'plan-v2.json'
            plan = json.loads(path.read_text())
            ref = plan['scenes'][0]['evidence'][1]
            ref['output_start'] -= 0.5
            ref['output_end'] -= 0.5
            path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'changed plan'):
                fixture.validate_manifest(manifest, root)
            manifest['plan']['sha256'] = fixture.sha(path)
            with self.assertRaisesRegex(ValueError, 'differs from plan projection'):
                fixture.validate_manifest(manifest, root)
            manifest['clips'] = fixture.project(plan)
            destination = root / 'shifted.mp4'
            fixture.render(manifest, root, destination)
            self.assertNotEqual(fixture.sha(destination), self.qa['candidate_sha256'])

    def test_external_source_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['sources'][0]['path'] = '../external.mp4'
        with self.assertRaisesRegex(ValueError, 'external'):
            fixture.validate_manifest(manifest, self.root)


if __name__ == '__main__':
    unittest.main()
