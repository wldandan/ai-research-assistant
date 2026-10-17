"""Offline teaching replay must preserve real evidence and reveal it in order."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / 'lessons/01-evidence-first/build_materials.py'


class LessonMaterialsTests(unittest.TestCase):
    def builder(self):
        self.assertTrue(BUILDER.exists(), 'Lesson replay builder is not implemented')
        spec = importlib.util.spec_from_file_location('lesson_materials', BUILDER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_replay_preserves_all_three_runs_and_real_failure(self):
        payload = self.builder().load_replay(ROOT)
        source = json.loads((ROOT / 'evidence/minimax-live-2026-10-17-batch.json').read_text())
        self.assertEqual(payload['runs'], source['runs'])
        self.assertEqual(payload['failure']['result']['status'], 'failed')
        self.assertIn('[N01]', payload['failure']['result']['answer'])
        self.assertEqual(payload['failure']['result']['evidence'], [])
        self.assertEqual(len(payload['source_sha256']), 3)
        self.assertEqual(payload['model'], source['model'])
        initial = json.loads((ROOT / 'evidence/minimax-live-2026-10-17-batch-initial.json').read_text())
        self.assertEqual(payload.get('failure_recorded_at_utc'), initial['recorded_at_utc'])

    def test_replay_is_self_contained_and_does_not_execute_recorded_content(self):
        builder = self.builder()
        payload = builder.load_replay(ROOT)
        payload['runs'][0]['result']['answer'] = '</script><img src=x onerror=alert(1)>'
        html = builder.render_replay(payload)
        self.assertNotIn('</script><img', html)
        self.assertNotIn('innerHTML', html)
        self.assertNotIn('fetch(', html)
        self.assertNotIn('https://', html)
        self.assertIn('application/json', html)
        self.assertIn('textContent', html)
        self.assertIn('历史真实记录回放', html)

    def test_decision_precedes_answer_reveal_and_state_is_reset(self):
        html = self.builder().render_replay(self.builder().load_replay(ROOT))
        self.assertLess(html.index('先预测'), html.index('查看回答'))
        self.assertIn('先看参数', html)
        self.assertIn('再看证据', html)
        self.assertIn('手工构造', html)
        self.assertIn('step = 0', html)
        self.assertIn('keydown', html)
        self.assertIn('requestFullscreen', html)

if __name__ == '__main__':
    unittest.main()
