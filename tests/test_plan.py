import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/witcut/scripts/plan.py'
spec = importlib.util.spec_from_file_location('plan', SCRIPT)
plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan)


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.p = json.loads((ROOT / 'skills/witcut/examples/plans/product-demo.json').read_text())

    def rejects(self, mutate, text):
        mutate(self.p)
        errors, _ = plan.validate(self.p)
        self.assertTrue(any(text in e for e in errors), errors)

    def test_examples_and_derived_timeline(self):
        for path in (ROOT / 'skills/witcut/examples/plans').glob('*.json'):
            p = json.loads(path.read_text())
            self.assertEqual(plan.validate(p)[0], [])
            script, shots, materials = plan.artifacts(p)
            self.assertIn(p['brief']['takeaway'], script)
            self.assertEqual(shots['scenes'][-1]['timeline_end'], sum(s['duration'] for s in p['scenes']))
            self.assertFalse(materials['production_ready'])
            self.assertTrue(materials['items'])

    def test_range(self):
        self.rejects(lambda p: p['scenes'][0]['evidence'][0].update(end=31), 'invalid source range')

    def test_required_coverage(self):
        self.rejects(lambda p: p['scenes'].pop(), 'required operation omitted')

    def test_missing_source(self):
        self.rejects(lambda p: p['sources'].clear(), 'unknown source')

    def test_intended_missing(self):
        self.p['scenes'][0]['claim_state'] = 'intended'
        errors, missing = plan.validate(self.p)
        self.assertFalse(errors)
        self.assertTrue(any('intended' in m['need'] for m in missing))

    def test_fixture_cannot_prove_current(self):
        self.rejects(lambda p: p['scenes'][0].update(claim_state='current'), 'verified real evidence')

    def test_fixture_cannot_be_verified(self):
        self.rejects(lambda p: p['sources'][0].update(verification='verified'), 'fixture cannot claim')

    def test_independent_cannot_have_predecessors(self):
        self.rejects(lambda p: p['operations'][1].update(predecessors=['select-a']), 'independent operation')

    def test_latest_duration(self):
        self.p['brief']['min_seconds'] = self.p['brief']['max_seconds'] = 16
        self.assertFalse(plan.validate(self.p)[0])
        self.rejects(lambda p: p['brief'].update(max_seconds=15), 'duration outside')

    def test_stale_brief(self):
        self.rejects(lambda p: p['brief'].update(latest_revision='r3'), 'not latest revision')

    def test_dependency_cycle(self):
        self.p['operations'][0].update(relationship='sequential', predecessors=['select-b'])
        self.rejects(lambda p: p['operations'][1].update(relationship='sequential', predecessors=['select-a']), 'dependency cycle')

    def test_shape_errors_are_not_tracebacks(self):
        for value in [None, [], 5, {'version': '1'}, dict(self.p, unexpected=True)]:
            self.assertTrue(plan.validate(value)[0])
        self.rejects(lambda p: p['scenes'][0].update(duration=True), 'finite number')

    def test_oversized_number(self):
        self.rejects(lambda p: p['sources'][0].update(duration=10**400), 'finite number')

    def test_non_finite(self):
        self.rejects(lambda p: p['sources'][0].update(duration=float('nan')), 'finite number')

    def test_unseen_sequential_real_plan(self):
        self.p['sources'][0].update(kind='real',verification='verified',rights='unknown',provenance='Test assertion only; no actual capture bundled.')
        self.p['operations'][1].update(relationship='sequential',predecessors=['select-a'])
        self.p['scenes'][0]['claim_state']='current'
        errors, missing = plan.validate(self.p)
        self.assertFalse(errors)
        self.assertTrue(any('rights' in m['need'] for m in missing))
        self.p['scenes'].reverse()
        self.assertTrue(any('predecessor not shown' in e for e in plan.validate(self.p)[0]))

    def test_known_manual_operation_cannot_disappear(self):
        op = copy.deepcopy(self.p['operations'][0])
        op.update(id='manual-focus', observation='User must manually focus before capture.')
        self.p['operations'].append(op)
        self.assertTrue(any('omitted operation' in e for e in plan.validate(self.p)[0]))
        op['omission_reason'] = 'Not part of this brief; owner must review prerequisite impact.'
        self.assertFalse(plan.validate(self.p)[0])
        self.p['brief']['required_operations'].append('manual-focus')
        self.assertTrue(any('required operation omitted' in e for e in plan.validate(self.p)[0]))

    def test_audio_cannot_prove_documentary_visual(self):
        p = json.loads((ROOT / 'skills/witcut/examples/plans/podcast-to-video.json').read_text())
        p['sources'][0].update(kind='real', modality='audio', verification='verified', rights='cleared',
                              provenance='Hypothetical authorized audio-only interview, no camera footage.')
        p['scenes'][0].update(claim_state='current', visual='Actual factory equipment at the instant described.', needs=[])
        errors, missing = plan.validate(p)
        self.assertTrue(any('verified real evidence for visuals' in e for e in errors))
        self.assertTrue(any('visual evidence' in m['need'] for m in missing))
        p['scenes'][0]['evidence'][0]['role']='visual'
        self.assertTrue(any('visual evidence needs visual source' in e for e in plan.validate(p)[0]))

    def test_editorial_asset_is_not_documentary_evidence(self):
        self.p['sources'][0].update(kind='editorial', verification='verified', rights='cleared')
        self.assertFalse(plan.validate(self.p)[0])
        script, _, _ = plan.artifacts(self.p)
        self.assertIn('independent; predecessors: none', script)
        self.assertIn('(visual)', script)
        self.assertIn('editorial/visual', script)
        self.rejects(lambda p: p['scenes'][0].update(claim_state='current'), 'verified real evidence')

    def test_narrated_operation_is_not_shown(self):
        self.p['sources'].append(dict(id='voice', kind='real', duration=30,
            provenance='Hypothetical audio only.', verification='verified',
            rights='cleared', modality='audio'))
        self.p['operations'][0]['source_id'] = 'voice'
        self.p['scenes'][0]['evidence'].append(dict(source_id='voice', start=0,
            end=5, role='narration', output_start=0, output_end=5, playback='play'))
        self.assertTrue(any('played visual evidence' in e for e in plan.validate(self.p)[0]))

    def test_source_cannot_fit_into_short_scene(self):
        self.rejects(lambda p: p['scenes'][0].update(duration=0.1), 'output range outside scene')

    def test_unstated_time_compression_rejected(self):
        self.rejects(lambda p: p['scenes'][0]['evidence'][0].update(output_end=0.1), '1x source/output duration')

    def test_invalid_mapping(self):
        for value in (-1, float('nan'), True):
            p = copy.deepcopy(self.p)
            p['scenes'][0]['evidence'][0]['output_start'] = value
            self.assertTrue(plan.validate(p)[0])
        self.rejects(lambda p: p['scenes'][0]['evidence'][0].update(playback='speed-up'), 'unknown playback')

    def test_hold_and_reference_cannot_demonstrate_operation(self):
        for mode in ('hold', 'reference'):
            p = copy.deepcopy(self.p)
            p['scenes'][0]['evidence'][0]['playback'] = mode
            self.assertTrue(any('played visual evidence' in e for e in plan.validate(p)[0]))

    def test_script_reference_is_not_recorded_speech(self):
        p = json.loads((ROOT / 'skills/witcut/examples/plans/podcast-to-video.json').read_text())
        p['scenes'][0]['evidence'][0]['playback'] = 'play'
        self.assertTrue(any('script needs recording' in e for e in plan.validate(p)[0]))

    def test_same_scene_mapped_predecessor_order(self):
        self.p['operations'][1].update(relationship='sequential', predecessors=['select-a'])
        scene = self.p['scenes'][0]
        scene['duration'] = 16
        scene['operation_ids'].append('select-b')
        scene['evidence'].append(dict(self.p['scenes'][1]['evidence'][0]))
        self.p['scenes'].pop()
        self.assertTrue(any('mapped predecessor' in e for e in plan.validate(self.p)[0]))
        scene['evidence'][1].update(output_start=5, output_end=10)
        self.assertFalse(plan.validate(self.p)[0])
        scene['operation_ids'].reverse()
        self.assertFalse(plan.validate(self.p)[0])

    def test_duplicate_and_ambiguous_operation_coverage(self):
        p = copy.deepcopy(self.p)
        p['scenes'][0]['operation_ids'].append('select-a')
        self.assertTrue(any('duplicate operation' in e for e in plan.validate(p)[0]))
        p = copy.deepcopy(self.p)
        p['scenes'][0]['evidence'].append(copy.deepcopy(p['scenes'][0]['evidence'][0]))
        self.assertTrue(any('unambiguous played visual' in e for e in plan.validate(p)[0]))

    def test_script_reference_still_needs_recording(self):
        p = json.loads((ROOT / 'skills/witcut/examples/plans/podcast-to-video.json').read_text())
        p['scenes'][0]['needs'] = []
        errors, missing = plan.validate(p)
        self.assertFalse(errors)
        self.assertTrue(any('narration recording/playback' in m['need'] for m in missing))

    def test_old_schema_requires_explicit_migration(self):
        self.rejects(lambda p: p.update(version='1'), 'unsupported version')

    def test_cli_preserves_existing_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'out'
            fixture=ROOT/'skills/witcut/examples/plans/podcast-to-video.json'
            cmd=[sys.executable,str(SCRIPT),str(fixture),'--out',str(out)]
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            self.assertEqual(set(p.name for p in out.iterdir()), {'script.md','shot-plan.json','missing-materials.json'})
            before=(out/'script.md').read_bytes()
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,1)
            self.assertEqual((out/'script.md').read_bytes(),before)


if __name__ == '__main__':
    unittest.main()
