import inspect
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def completion(content=None, calls=None, finish=None):
    body={'role':'assistant','content':content,'reasoning_content':'private reasoning',
          'tool_calls':calls or []}
    message=SimpleNamespace(model_dump=lambda **kwargs: body)
    return SimpleNamespace(choices=[SimpleNamespace(message=message,finish_reason=finish or ('tool_calls' if calls else 'stop'))])


def tool(query='agent loop'):
    return {'id':'chat-tool-1','type':'function','function':{'name':'search_notes','arguments':json.dumps({'query':query,'limit':2})}}


class MiniMaxTests(unittest.TestCase):
    def api(self):
        import live_agent
        self.assertIn('protocol',inspect.signature(live_agent.run_live).parameters,'缺少MiniMax Chat协议')
        return live_agent

    def test_three_scenarios_with_model_selected_tool(self):
        api=self.api()
        for query,answer,status,source in [('agent loop','<think>private reasoning</think>[N01] 工具结果返回模型。','report','N01'),
            ('未知星系XYZ','资料不足，请补充资料。','insufficient',None),('memory','[N02] 会话应隔离。','report','N02')]:
            client=Mock()
            client.chat.completions.create.side_effect=[completion(calls=[tool(query)]),completion(answer)]
            result=api.run_live('用户自然语言问题',model='MiniMax-fixture',client=client,protocol='chat')
            self.assertEqual(result['status'],status)
            self.assertEqual(result['nodes'],['model','tools','model'])
            self.assertNotIn('private reasoning',json.dumps(result))
            if source: self.assertEqual(result['evidence'][0]['id'],source)
            second=client.chat.completions.create.call_args_list[1].kwargs
            self.assertEqual(second['messages'][2]['reasoning_content'],'private reasoning')
            self.assertEqual(second['messages'][2]['tool_calls'][0]['id'],'chat-tool-1')
            self.assertEqual(second['messages'][3]['tool_call_id'],'chat-tool-1')
            self.assertEqual(second['messages'][3]['role'],'tool')
            self.assertEqual(second['max_tokens'],4096)
            self.assertEqual(result['tools'][0]['output_type'],'tool')

    def test_length_and_parallel_tools_do_not_execute(self):
        api=self.api()
        for response in [completion('[N01] partial',finish='length'),completion(calls=[tool(),tool('memory')])]:
            client=Mock();client.chat.completions.create.return_value=response
            result=api.run_live('question',model='fixture',client=client,protocol='chat')
            self.assertEqual(result['status'],'error')
            self.assertEqual(result['tools'],[])

    def test_ignored_tool_and_turn_limit_are_observable(self):
        api=self.api()
        client=Mock();client.chat.completions.create.return_value=completion('无需搜索。')
        self.assertEqual(api.run_live('question',model='fixture',client=client,protocol='chat')['status'],'failed')
        client=Mock();client.chat.completions.create.return_value=completion(calls=[tool()])
        result=api.run_live('question',model='fixture',client=client,protocol='chat')
        self.assertEqual(result['status'],'budget_exhausted')
        self.assertEqual(client.chat.completions.create.call_count,4)
        self.assertEqual(len(result['tools']),3)

    def test_minimax_never_falls_back_to_openai_key(self):
        p=subprocess.run([sys.executable,str(ROOT/'demo.py'),'--live','--provider','minimax'],
            env=dict(os.environ,MINIMAX_API_KEY='',OPENAI_API_KEY='local-fixture-only',RESEARCH_MODEL='fixture'),text=True,capture_output=True)
        self.assertEqual(p.returncode,1)
        self.assertEqual(json.loads(p.stdout)['status'],'configuration_required')
        self.assertIn('MINIMAX_API_KEY',json.loads(p.stdout)['error'])

    def test_cli_uses_dedicated_key_base_and_timeout(self):
        import demo
        client=Mock()
        client.chat.completions.create.side_effect=[completion(calls=[tool()]),completion('[N01] 工具提供观察。')]
        with patch.dict(os.environ,{'MINIMAX_API_KEY':'minimax-local-fixture','OPENAI_API_KEY':'other-local-fixture',
            'MINIMAX_BASE_URL':'https://example.invalid/v1','RESEARCH_MODEL':'fixture'}), \
            patch.object(sys,'argv',['demo.py','--live','--provider','minimax']), \
            patch('openai.OpenAI') as factory, patch('sys.stdout',new_callable=io.StringIO) as output:
            factory.return_value.__enter__.return_value=client
            self.assertEqual(demo.main(),0)
            config=factory.call_args.kwargs
            self.assertEqual(config['api_key'],'minimax-local-fixture')
            self.assertEqual(config['base_url'],'https://example.invalid/v1')
            self.assertEqual(config['timeout'],60)
            self.assertEqual(config['max_retries'],0)
            self.assertNotIn('minimax-local-fixture',output.getvalue())

    def test_invalid_base_url_is_rejected_before_constructing_client(self):
        import demo
        for base in ('http://api.minimax.io/v1','file:///tmp/fake','https://user:password@example.invalid/v1','https://example.invalid/v1?secret=abc'):
            with patch.dict(os.environ,{'MINIMAX_API_KEY':'local-fixture','RESEARCH_MODEL':'fixture','MINIMAX_BASE_URL':base}), \
                patch.object(sys,'argv',['demo.py','--live','--provider','minimax']), \
                patch('openai.OpenAI') as factory, patch('sys.stdout',new_callable=io.StringIO) as output:
                self.assertEqual(demo.main(),1)
                factory.assert_not_called()
                self.assertEqual(json.loads(output.getvalue())['status'],'error')
                self.assertNotIn(base,output.getvalue())

    def test_real_sdk_chat_protocol_with_local_http_fixture(self):
        api=self.api()
        import httpx2
        import socket
        from openai import OpenAI
        requests=[]
        def send(client,request,**kwargs):
            self.assertTrue(request.url.path.endswith('/chat/completions'))
            requests.append(json.loads(request.content))
            msg={'role':'assistant','content':'<think>reasoning must persist</think>', 'tool_calls':[tool()]}
            if len(requests)>1: msg={'role':'assistant','content':'[N01] 观察进入下一轮。'}
            return httpx2.Response(200,json={'id':'chat-local','object':'chat.completion','created':0,'model':'fixture',
                'choices':[{'index':0,'message':msg,'finish_reason':'tool_calls' if len(requests)==1 else 'stop'}]},request=request)
        with patch.object(httpx2.Client,'send',new=send),patch.object(socket,'getaddrinfo',side_effect=AssertionError('No external network')):
            with OpenAI(api_key='local-fixture-not-real',base_url='https://example.invalid/v1',max_retries=0,timeout=60) as client:
                result=api.run_live('question',model='fixture',client=client,protocol='chat')
        self.assertEqual(result['status'],'report')
        self.assertIn('<think>',requests[1]['messages'][2]['content'])
        self.assertNotIn('reasoning must persist',json.dumps(result))


if __name__=='__main__': unittest.main()
