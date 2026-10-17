"""Build an offline teaching view from preserved public Demo evidence. No API calls."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_replay(root):
    paths = ['evidence/minimax-live-2026-10-17-batch.json',
             'evidence/minimax-live-2026-10-17-batch-initial.json', 'data/notes.json']
    final, initial, notes = [json.loads((root / p).read_text()) for p in paths]
    # The evidence files already contain only the public CLI projection. Export
    # only that projection's known teaching fields; never SDK/internal messages.
    def project(run):
        result = run['result']
        public = {k: result[k] for k in ('answer', 'evidence', 'tools', 'nodes',
                  'model_turns', 'status', 'error', 'budget', 'provider', 'evidence_kind')}
        public['tools'] = [{k: t[k] for k in ('name','call_id','arguments',
                          'output_type','status','output','source_ids')} for t in result['tools']]
        return {**{k:run[k] for k in ('scenario','query','exit_code','elapsed_seconds')}, 'result':public}
    return {'recorded_at_utc':final['recorded_at_utc'], 'model':final['model'],
            'revision':final['revision'], 'requested_budget':final['requested_budget'],
            'runs':[project(r) for r in final['runs']],
            'failure_recorded_at_utc':initial['recorded_at_utc'],
            'failure':project(next(r for r in initial['runs'] if r['scenario']=='no-evidence')),
            'notes':notes, 'source_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}}


def render_replay(payload):
    data = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return (HERE / 'replay-template.html').read_text().replace('__REPLAY_DATA__', data)


if __name__ == '__main__':
    target = HERE / 'materials'
    target.mkdir(exist_ok=True)
    payload = load_replay(ROOT)
    (target / 'replay.html').write_text(render_replay(payload))
    (target / 'source-manifest.json').write_text(json.dumps({k:payload[k] for k in
        ('recorded_at_utc','model','revision','requested_budget','source_sha256')},ensure_ascii=False,indent=2)+'\n')
    print('Built offline replay and source manifest')
