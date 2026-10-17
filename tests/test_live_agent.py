import importlib.util
import json
import os
import subprocess
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def response(items, text=''):
    return SimpleNamespace(output=items, output_text=text, status='completed')


def call(query='agent loop', name='search_notes', arguments=None):
    return {'type':'function_call', 'name':name, 'call_id':'tool-1',
            'arguments': json.dumps({'query':query,'limit':2}) if arguments is None else arguments}


class LiveAgentTests(unittest.TestCase):
    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('live_agent'), '真实模型 Agent 尚未实现')
        import live_agent
        return live_agent

    def test_live_cli_without_credentials_has_no_silent_offline_fallback(self):
        env = dict(os.environ, OPENAI_API_KEY='', RESEARCH_MODEL='')
        root = Path(__file__).resolve().parents[1]
        p = subprocess.run([sys.executable,str(root/'demo.py'),'--live'], env=env, text=True, capture_output=True)
        self.assertEqual(p.returncode, 1)
        output = json.loads(p.stdout)
        self.assertEqual(output['status'],'configuration_required')
        self.assertIn('OPENAI_API_KEY',output['error'])

    def test_model_chosen_tool_is_executed_and_returned_by_call_id(self):
        api = self.api()
        client = Mock()
        client.responses.create.side_effect = [response([call()]), response([], '[N01] 工具结果进入下一次决策。')]
        result = api.run_live('解释 Agent 循环', model='test-fixture', client=client)
        self.assertEqual(result['nodes'], ['model', 'tools', 'model'])
        self.assertEqual(result['status'], 'report')
        self.assertEqual(result['tools'][0]['arguments']['query'], 'agent loop')
        self.assertIn('call_id', result['tools'][0])
        self.assertEqual(result['tools'][0]['call_id'], 'tool-1')
        self.assertEqual(result['tools'][0]['output_type'], 'function_call_output')
        self.assertEqual(result['tools'][0]['output'][0]['id'], 'N01')
        self.assertEqual(result['evidence'][0]['id'], 'N01')
        second = client.responses.create.call_args_list[1].kwargs
        self.assertEqual(second['input'][1]['type'], 'function_call')
        self.assertEqual(second['input'][2]['call_id'], 'tool-1')
        self.assertIn('N01', second['input'][2]['output'])
        self.assertEqual(second['tool_choice'], 'auto')
        self.assertFalse(second['store'])
        self.assertEqual(second['max_output_tokens'], 600)

    def test_skipping_tool_is_observed_as_failed_not_fake_search(self):
        api = self.api()
        client=Mock()
        client.responses.create.return_value=response([], '我知道答案。')
        result=api.run_live('question',model='test-fixture',client=client)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['tools'], [])
        self.assertEqual(result['nodes'], ['model'])

    def test_false_or_missing_citation_fails(self):
        api = self.api()
        for answer in ('[N99] 假引用', '没有引用'):
            client=Mock()
            client.responses.create.side_effect=[response([call()]),response([],answer)]
            self.assertEqual(api.run_live('question',model='test-fixture',client=client)['status'],'failed')

    def test_no_evidence_and_excluded_notes(self):
        api = self.api()
        for query in ('未知XYZ','injection'):
            client=Mock()
            client.responses.create.side_effect=[response([call(query)]),response([], '资料不足，请补充材料。')]
            result=api.run_live('question',model='test-fixture',client=client)
            self.assertEqual(result['status'],'insufficient')
            self.assertEqual(result['evidence'],[])

    def test_invalid_or_unknown_tool_rejected(self):
        api = self.api()
        for item in (call(name='send_report'),call(arguments='{"query":"memory","limit":true}'),call(arguments='bad json')):
            client=Mock()
            client.responses.create.return_value=response([item])
            result=api.run_live('question',model='test-fixture',client=client)
            self.assertEqual(result['status'],'error')
            self.assertEqual(client.responses.create.call_count,1)

    def test_incomplete_response_never_succeeds_or_executes_pending_tool(self):
        api = self.api()
        for items, text in [([], '[N01] truncated'), ([call()], '')]:
            client=Mock()
            incomplete=response(items,text)
            incomplete.status='incomplete'
            client.responses.create.side_effect=[response([call()]),incomplete] if text else [incomplete]
            result=api.run_live('question',model='test-fixture',client=client)
            self.assertEqual(result['status'],'error')
            self.assertIn('incomplete',result['error'])
            self.assertEqual(len(result['tools']),1 if text else 0)

    def test_turn_cap_stops_before_executing_last_tool(self):
        api = self.api()
        client=Mock()
        client.responses.create.return_value=response([call()])
        result=api.run_live('question',model='test-fixture',client=client)
        self.assertEqual(result['status'],'budget_exhausted')
        self.assertEqual(client.responses.create.call_count,4)
        self.assertEqual(len(result['tools']),3)

    def test_real_sdk_serializes_two_requests_with_local_http_fixture(self):
        api = self.api()
        import httpx2
        import socket
        from openai import OpenAI
        from unittest.mock import patch
        requests = []
        def send(client, request, **kwargs):
            requests.append(json.loads(request.content))
            output = [dict(call(), id='fc-1', status='completed')] if len(requests)==1 else [
                {'type':'message','id':'msg-1','status':'completed','role':'assistant',
                 'content':[{'type':'output_text','text':'[N01] 工具观察进入下一轮。','annotations':[]}]}]
            return httpx2.Response(200, json={'id':'resp-fixture','object':'response','created_at':0,
                'model':'test-fixture','status':'completed','output':output},request=request)
        with patch.object(httpx2.Client,'send',new=send), patch.object(socket,'getaddrinfo',side_effect=AssertionError('No network')):
            with OpenAI(api_key='local-fixture-not-real',timeout=30,max_retries=0) as client:
                result=api.run_live('question',model='test-fixture',client=client)
        self.assertEqual(result['status'],'report')
        self.assertEqual(len(requests),2)
        self.assertEqual(requests[1]['input'][-1]['type'],'function_call_output')
        self.assertEqual(requests[1]['input'][-1]['call_id'],'tool-1')
        self.assertFalse(requests[0]['store'])

    def test_client_failure_is_explicit_and_does_not_leak_exception_secrets(self):
        api = self.api()
        client=Mock()
        client.responses.create.side_effect=RuntimeError('secret credential')
        result=api.run_live('question',model='test-fixture',client=client)
        self.assertEqual(result['status'],'error')
        self.assertNotIn('secret credential',json.dumps(result))


if __name__=='__main__': unittest.main()
