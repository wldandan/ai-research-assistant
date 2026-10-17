"""Offline learning workflow for the independent AI research assistant course."""
from __future__ import annotations

import argparse
import importlib
import json
import os
from urllib.parse import urlsplit
import re
from typing import Callable, TypedDict

from research import build_report, search_notes
from langgraph.graph import END, START, StateGraph
from langsmith import tracing_context


class State(TypedDict):
    query: str
    evidence: list[dict]
    nodes: list[str]
    answer: str
    error: str
    status: str
    evidence_kind: str


def run(query: str, route: Callable[[dict], str]) -> dict:
    """Execute a fresh graph; the student's route is the actual conditional edge."""
    def search(state):
        try:
            rows = [row for row in search_notes(state['query'], limit=3)
                    if row['id'] in {'N01', 'N02'}]
            return {'evidence': rows, 'nodes': ['search']}
        except ValueError as error:
            return {'error': str(error), 'nodes': ['search']}

    def report(state):
        return {'answer': build_report(state['evidence']), 'status': 'report',
                'nodes': state['nodes'] + ['report']}

    def insufficient(state):
        return {'answer': build_report([]), 'status': 'insufficient',
                'nodes': state['nodes'] + ['insufficient']}

    def failed(state):
        return {'answer': '执行失败，请检查 error 字段。', 'status': 'error',
                'nodes': state['nodes'] + ['error']}

    graph = StateGraph(State)
    for name, action in [('search', search), ('report', report),
                         ('insufficient', insufficient), ('error', failed)]:
        graph.add_node(name, action)
    graph.add_edge(START, 'search')
    graph.add_conditional_edges('search', route,
                                {name: name for name in ('report', 'insufficient', 'error')})
    for name in ('report', 'insufficient', 'error'):
        graph.add_edge(name, END)
    with tracing_context(enabled=False):
        return graph.compile().invoke({'query': query, 'evidence': [], 'nodes': [],
                                       'answer': '', 'error': '', 'status': '',
                                       'evidence_kind': 'deterministic simulation'},
                                      config={'recursion_limit': 8, 'callbacks': []})


def check_citations(answer: str, evidence: list[dict]) -> bool:
    """Check IDs against this run only; this does NOT check semantic support."""
    cited = set(re.findall(r'\[(N\d+)\]', answer))
    available = {row['id'] for row in evidence}
    return bool(cited) and cited <= available


def check_result(result: dict) -> bool:
    """A narrow workflow contract, not a model accuracy or semantic score."""
    expected = 'error' if result['error'] else 'report' if result['evidence'] else 'insufficient'
    if result['status'] != expected or result['nodes'] != ['search', expected]:
        return False
    if expected == 'report':
        return check_citations(result['answer'], result['evidence'])
    return expected == 'error' or '资料不足' in result['answer']


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', default='agent loop')
    parser.add_argument('--solution', choices=['starter', 'reference'], default='starter')
    parser.add_argument('--live', action='store_true', help='Explicitly call a real model; requires key and model, may incur API costs')
    parser.add_argument('--provider', choices=['openai','minimax'], default='openai')
    args = parser.parse_args()
    if args.live:
        key_name = 'MINIMAX_API_KEY' if args.provider == 'minimax' else 'OPENAI_API_KEY'
        if not os.environ.get(key_name) or not os.environ.get('RESEARCH_MODEL'):
            print(json.dumps({'status':'configuration_required', 'error':f'Configure {key_name} and RESEARCH_MODEL; no offline fallback'}))
            return 1
        from openai import OpenAI
        from live_agent import run_live
        try:
            options = {'timeout':30, 'max_retries':0}
            if args.provider == 'minimax':
                base_url = os.environ.get('MINIMAX_BASE_URL', 'https://api.minimax.io/v1')
                address = urlsplit(base_url)
                if address.scheme != 'https' or not address.hostname or address.username or address.password or address.query or address.fragment:
                    raise ValueError('Invalid MiniMax base URL')
                options.update(api_key=os.environ['MINIMAX_API_KEY'], base_url=base_url, timeout=60)
            with OpenAI(**options) as client:
                result = run_live(args.query, model=os.environ['RESEARCH_MODEL'], client=client,
                                  protocol='chat' if args.provider == 'minimax' else 'responses')
            result['provider'] = args.provider
            result['evidence_kind'] = 'external model execution'
        except ValueError:
            result = {'status':'error', 'error':'Invalid query or model configuration'}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['status'] in {'report','insufficient'} else 1
    route = importlib.import_module(args.solution).route_after_search
    result = run(args.query, route)
    result['checks_passed'] = check_result(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['checks_passed'] and result['status'] != 'error' else 1


if __name__ == '__main__':
    raise SystemExit(main())
