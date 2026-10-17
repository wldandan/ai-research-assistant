import copy
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class DemoTests(unittest.TestCase):
    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('demo'), '最小 Demo 尚未实现')
        import demo
        import reference
        return demo, reference

    def test_three_cases_use_actual_graph_and_current_evidence(self):
        demo, reference = self.api()
        for query, status, source in [('agent loop', 'report', 'N01'), ('不存在的天文星系XYZ', 'insufficient', None), ('memory', 'report', 'N02')]:
            with self.subTest(query=query), patch.object(socket, 'getaddrinfo', side_effect=AssertionError('offline only')):
                result = demo.run(query, reference.route_after_search)
                self.assertEqual(result['status'], status)
                self.assertEqual(result['nodes'], ['search', status])
                self.assertEqual(result['evidence_kind'], 'deterministic simulation')
                if source:
                    self.assertEqual(result['evidence'][0]['id'], source)
                    self.assertIn(f'[{source}]', result['answer'])
                else:
                    self.assertEqual(result['evidence'], [])
                    self.assertIn('资料不足', result['answer'])

    def test_starter_change_affects_real_graph_not_only_function(self):
        demo, reference = self.api()
        import starter
        before = demo.run('不存在的天文星系XYZ', starter.route_after_search)
        after = demo.run('不存在的天文星系XYZ', reference.route_after_search)
        self.assertEqual(before['nodes'], ['search', 'report'])
        self.assertEqual(after['nodes'], ['search', 'insufficient'])
        self.assertFalse(demo.check_result(before))
        self.assertTrue(demo.check_result(after))

    def test_error_is_distinct_from_missing_evidence(self):
        demo, reference = self.api()
        for query in ['', '   ', 'x' * 501]:
            with self.subTest(query=query):
                result = demo.run(query, reference.route_after_search)
                self.assertEqual(result['status'], 'error')
                self.assertEqual(result['nodes'], ['search', 'error'])
                self.assertTrue(result['error'])

    def test_reference_error_priority_and_input_unchanged(self):
        _, reference = self.api()
        state = {'error': 'failure', 'evidence': [{'id': 'N01'}]}
        before = copy.deepcopy(state)
        self.assertEqual(reference.route_after_search(state), 'error')
        self.assertEqual(state, before)

    def test_citation_check_rejects_unknown_and_unretrieved_ids(self):
        demo, reference = self.api()
        result = demo.run('agent loop', reference.route_after_search)
        self.assertTrue(demo.check_citations(result['answer'], result['evidence']))
        self.assertFalse(demo.check_citations('[N99] invented', result['evidence']))
        self.assertFalse(demo.check_citations('[N02] other source', result['evidence']))
        self.assertFalse(demo.check_citations('no citation', result['evidence']))
        # A real ID does not establish semantic support; manual review remains necessary.
        self.assertTrue(demo.check_citations('[N01] Agent never uses tools.', result['evidence']))

    def test_student_route_injection_controls_execution(self):
        demo, _ = self.api()
        def changed_route(state):
            return 'insufficient'
        result = demo.run('memory', changed_route)
        self.assertEqual(result['nodes'], ['search', 'insufficient'])
        self.assertFalse(demo.check_result(result))

    def test_excluded_notes_do_not_enter_results(self):
        demo, reference = self.api()
        for query in ('injection', 'approval'):
            result = demo.run(query, reference.route_after_search)
            self.assertEqual(result['evidence'], [])
            self.assertEqual(result['status'], 'insufficient')

    def test_user_tracing_environment_cannot_enable_remote_callbacks(self):
        demo, reference = self.api()
        import os
        from langsmith.utils import tracing_is_enabled
        original_search = demo.search_notes
        observed = []
        def inspect_search(*args, **kwargs):
            observed.append(tracing_is_enabled())
            return original_search(*args, **kwargs)
        with patch.dict(os.environ, {'LANGSMITH_TRACING': 'true', 'LANGCHAIN_TRACING_V2': 'true'}), patch.object(demo, 'search_notes', side_effect=inspect_search):
            result = demo.run('memory', reference.route_after_search)
            self.assertEqual(observed, [False])
            self.assertEqual(result['status'], 'report')

    def test_cli_uses_real_starter_and_meaningful_exit_status(self):
        self.api()
        for solution, code in [('starter', 1), ('reference', 0)]:
            result = subprocess.run([sys.executable, str(ROOT / 'demo.py'), '--query', '不存在的天文星系XYZ', '--solution', solution], capture_output=True, text=True)
            self.assertEqual(result.returncode, code, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output['checks_passed'], code == 0)


if __name__ == '__main__':
    unittest.main()
