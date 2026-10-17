"""Prove the course can travel without its parent course or workspace."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class IndependenceTests(unittest.TestCase):
    def test_only_this_course_runs_from_a_foreign_working_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            isolated = Path(folder) / 'course'
            shutil.copytree(ROOT, isolated, ignore=shutil.ignore_patterns('.venv', '.git', '__pycache__', '.coverage'))
            env = dict(os.environ, PYTHONPATH='', LANGSMITH_TRACING='false', LANGCHAIN_TRACING_V2='false')
            for query, status in [('agent loop','report'), ('不存在的天文星系XYZ','insufficient'), ('memory','report')]:
                p = subprocess.run([sys.executable, '-E', str(isolated/'demo.py'), '--solution', 'reference', '--query', query],
                                   cwd=folder, env=env, text=True, capture_output=True)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertEqual(json.loads(p.stdout)['status'], status)

    def test_course_owns_the_required_notes_and_search_module(self):
        self.assertTrue((ROOT/'research.py').is_file(), '课程仍缺少自有检索模块')
        self.assertTrue((ROOT/'data/notes.json').is_file(), '课程仍缺少随课语料')
        notes = json.loads((ROOT/'data/notes.json').read_text())
        self.assertEqual({row['id'] for row in notes}, {'N01','N02'})


if __name__ == '__main__':
    unittest.main()
