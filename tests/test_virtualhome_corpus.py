import copy
import json
from pathlib import Path
import tempfile
import unittest

from virtualhome_corpus.core import (validate_config, plan_episodes, make_program,
    parse_action_export, frame_files, endpoint_rule, canonical_hash)
from virtualhome_corpus.runner import corpus_lock, check_video

CONFIG = Path(__file__).resolve().parents[1] / 'configs/virtualhome-household-v1.json'


class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads(CONFIG.read_text())

    def test_plan_keeps_variants_in_group(self):
        plan = plan_episodes(self.cfg)
        self.assertEqual(len(plan), 24)
        self.assertEqual(len({x['episode_id'] for x in plan}), 24)
        for group in self.cfg['groups']:
            rows = [x for x in plan if x['group']['id'] == group['id']]
            self.assertEqual(len(rows), 6)
            self.assertEqual({x['group']['split'] for x in rows}, {group['split']})

    def test_config_rejects_bad_partitions_and_dimensions(self):
        for mutate in [lambda c: c['groups'].append(c['groups'][0]),
                       lambda c: c.update(width=641),
                       lambda c: c.update(variants=['missing']),
                       lambda c: c.update(boundary_guard_frames=0)]:
            c = copy.deepcopy(self.cfg); mutate(c)
            with self.assertRaises(ValueError): validate_config(c)

    def test_program_preserves_real_violation(self):
        target = {'id': 8, 'class_name': 'fridge'}
        neighbor = {'id': 9, 'class_name': 'microwave'}
        dest = {'id': 10, 'class_name': 'livingroom'}
        normal = make_program(target, neighbor, dest, 'closed_before_leaving')
        skipped = make_program(target, neighbor, dest, 'closure_omitted')
        reopened = make_program(target, neighbor, dest, 'reopened_before_leaving')
        self.assertTrue(any('[Close]' in line for line in normal))
        self.assertFalse(any('[Close]' in line for line in skipped))
        self.assertEqual(sum('[Open]' in line for line in reopened), 2)
        self.assertIn('<livingroom>', reopened[-1])

    def test_inserted_walk_and_terminal_endpoint(self):
        program = ['walk to TV', 'switch on', 'switch off', 'leave']
        raw = '0 WALK 0 35\n1 WALK 36 49\n1 SWITCHON 50 66\n2 WALK 67 67\n2 SWITCHOFF 68 84\n3 WALK 85 143\n'
        rows = parse_action_export(raw, program, 143, 10, 2)
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[1]['program_index'], rows[2]['program_index'])
        self.assertIsNone(rows[3]['interior'])
        self.assertEqual(rows[-1]['interior']['end_frame_exclusive'], 141)
        self.assertTrue(all(r['endpoint_convention'] == 'unresolved' for r in rows))

    def test_invalid_action_rows_rejected(self):
        for raw in ['0 WALK 0 100', '2 WALK 0 5', '0 WALK 0 10\n0 OPEN 4 12', 'bad', '']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_action_export(raw, ['walk'], 20, 10, 1)

    def test_missing_mismatched_and_noncontiguous_frames(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for name in ['Action_0000_0_normal.png', 'Action_0000_0_graph.json']:
                (d / name).touch()
            self.assertEqual(len(frame_files(d)[0]), 1)
            (d / 'Action_0002_0_normal.png').touch()
            with self.assertRaises(ValueError): frame_files(d)
            (d / 'Action_0002_0_graph.json').touch()
            with self.assertRaises(ValueError): frame_files(d)

    def test_endpoint_checks_actual_graph(self):
        graph = {'nodes': [{'id': 8, 'states': ['CLOSED']}],
                 'edges': [{'from_id': 1, 'to_id': 10, 'relation_type': 'INSIDE'}]}
        self.assertEqual(endpoint_rule(graph, 1, 8, 10, True)['verdict'], 'PASS')
        with self.assertRaises(ValueError): endpoint_rule(graph, 1, 8, 10, False)
        graph['nodes'][0]['states'] = ['OPEN']
        self.assertEqual(endpoint_rule(graph, 1, 8, 10, False)['verdict'], 'VIOLATION')
        with self.assertRaises(ValueError): endpoint_rule(graph, 2, 8, 10, False)
        graph['nodes'][0]['states'] = ['OPEN', 'CLOSED']
        with self.assertRaises(ValueError): endpoint_rule(graph, 1, 8, 10, False)

    def test_provenance_changes_with_sampling(self):
        other = copy.deepcopy(self.cfg); other['fps'] = 20
        self.assertNotEqual(canonical_hash(self.cfg), canonical_hash(other))

    def test_lock_excludes_second_writer(self):
        with tempfile.TemporaryDirectory() as tmp, corpus_lock(Path(tmp)):
            with self.assertRaises(RuntimeError):
                with corpus_lock(Path(tmp)): pass

    def test_video_metadata_mismatch_rejected(self):
        meta = {'streams': [{'nb_frames': '100', 'width': 640, 'height': 480, 'r_frame_rate': '10/1'}],
                'format': {'duration': '10.0'}}
        check_video(meta, 100, self.cfg)
        for key, bad in [('nb_frames', '99'), ('width', 320), ('r_frame_rate', '20/1')]:
            changed = copy.deepcopy(meta); changed['streams'][0][key] = bad
            with self.assertRaises(RuntimeError): check_video(changed, 100, self.cfg)


if __name__ == '__main__':
    unittest.main()
