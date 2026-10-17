"""Provider/model-neutral contracts for bounded tool-call batches."""
import json
import inspect
import os
import subprocess
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def item(identity, query='agent loop', name='search_notes', arguments=None):
    return {'type':'function_call','call_id':identity,'name':name,
            'arguments':json.dumps({'query':query,'limit':2}) if arguments is None else arguments}


def reply(protocol, calls, answer=''):
    if protocol == 'responses':
        return SimpleNamespace(status='completed',output=calls,output_text=answer)
    message={'role':'assistant','content':answer,'reasoning_content':'private fixture reasoning',
             'tool_calls':[{'type':'function','id':c['call_id'],
                            'function':{'name':c['name'],'arguments':c['arguments']}} for c in calls]}
    return SimpleNamespace(choices=[SimpleNamespace(finish_reason='tool_calls' if calls else 'stop',
        message=SimpleNamespace(model_dump=lambda **kwargs:message))])


class ToolBatchTests(unittest.TestCase):
    def run_case(self, protocol, rounds, **limits):
        import live_agent
        client=Mock()
        create=client.responses.create if protocol=='responses' else client.chat.completions.create
        create.side_effect=[reply(protocol,calls,answer) for calls,answer in rounds]
        for key in limits:
            self.assertIn(key,inspect.signature(live_agent.run_live).parameters,'缺少可配置调用预算')
        result=live_agent.run_live('用户问题',model='arbitrary-provider-model',client=client,protocol=protocol,**limits)
        self.assertTrue(all(c.kwargs['model']=='arbitrary-provider-model' for c in create.call_args_list))
        return result,create

    def test_two_tools_execute_and_both_ids_return_before_next_model_call(self):
        for protocol in ('chat','responses'):
            with self.subTest(protocol=protocol):
                result,create=self.run_case(protocol,[([item('a'),item('b','memory')],''),([], '[N01] 工具观察。[N02] 会话隔离。')])
                self.assertEqual(result['status'],'report')
                self.assertEqual([t['call_id'] for t in result['tools']],['a','b'])
                self.assertEqual({r['id'] for r in result['evidence']},{'N01','N02'})
                request=create.call_args_list[1].kwargs
                history=request['messages'] if protocol=='chat' else request['input']
                outputs=[m for m in history if m.get('role')=='tool' or m.get('type')=='function_call_output']
                self.assertEqual([m.get('tool_call_id',m.get('call_id')) for m in outputs],['a','b'])
                self.assertNotIn('private fixture reasoning',json.dumps(result))

    def test_exact_default_budget_can_finish_after_a_three_tool_batch(self):
        for protocol in ('chat','responses'):
            result,create=self.run_case(protocol,[([item('a'),item('b','memory'),item('c','unknownXYZ')],''),([], '[N01] 观察。[N02] 会话。')])
            self.assertEqual(result['status'],'report')
            self.assertEqual(len(result['tools']),3)
            self.assertEqual(create.call_args_list[1].kwargs['tool_choice'],'none')

    def test_oversized_batch_is_rejected_before_any_execution(self):
        for protocol in ('chat','responses'):
            result,_=self.run_case(protocol,[([item(str(i)) for i in range(4)],'')])
            self.assertEqual(result['status'],'budget_exhausted')
            self.assertEqual(result['tools'],[])

    def test_remaining_budget_is_checked_for_the_entire_next_batch(self):
        for protocol in ('chat','responses'):
            result,_=self.run_case(protocol,[([item('first')],''),([item(str(i)) for i in range(3)],'')])
            self.assertEqual(result['status'],'budget_exhausted')
            self.assertEqual(len(result['tools']),1)

    def test_invalid_batch_member_causes_no_partial_execution(self):
        import live_agent
        invalid=[item('bad',name='send_report'),item('bad',arguments='bad json'),
                 item('bad',arguments='{"query":"memory","limit":true}'),item('good')]
        for protocol in ('chat','responses'):
            for bad in invalid:
                with self.subTest(protocol=protocol,bad=bad['name']), patch.object(live_agent,'search_notes') as search:
                    result,_=self.run_case(protocol,[([item('good'),bad],'')])
                    self.assertEqual(result['status'],'error')
                    self.assertEqual(result['tools'],[])
                    search.assert_not_called()

    def test_call_id_reuse_across_rounds_is_rejected(self):
        for protocol in ('chat','responses'):
            result,_=self.run_case(protocol,[([item('same')],''),([item('same','memory')],'')])
            self.assertEqual(result['status'],'error')
            self.assertEqual(len(result['tools']),1)

    def test_configurable_limits_remain_model_independent(self):
        for protocol in ('chat','responses'):
            result,_=self.run_case(protocol,[([item('a'),item('b'),item('c')],'')],max_tool_calls=2)
            self.assertEqual(result['status'],'budget_exhausted')
            self.assertEqual(result['tools'],[])
            result,_=self.run_case(protocol,[([item('a')],'')],max_model_turns=1)
            self.assertEqual(result['status'],'budget_exhausted')
            self.assertEqual(result['tools'],[])

    def test_invalid_limits_fail_before_a_request(self):
        import live_agent
        for limits in ({'max_tool_calls':0},{'max_model_turns':True}):
            client=Mock()
            for key in limits:
                self.assertIn(key,inspect.signature(live_agent.run_live).parameters,'缺少可配置调用预算')
            with self.assertRaises(ValueError):
                live_agent.run_live('question',model='arbitrary',client=client,**limits)
            client.responses.create.assert_not_called()

    def test_cli_accepts_explicit_budget_without_provider_credentials(self):
        root=Path(__file__).resolve().parents[1]
        p=subprocess.run([sys.executable,str(root/'demo.py'),'--live','--max-model-turns','2','--max-tool-calls','2'],
                         env=dict(os.environ,OPENAI_API_KEY='',RESEARCH_MODEL=''),text=True,capture_output=True)
        self.assertEqual(p.returncode,1)
        self.assertEqual(json.loads(p.stdout)['status'],'configuration_required')

    def test_runtime_tool_failure_retains_actual_attempt_count(self):
        import live_agent
        search_original=live_agent.search_notes
        def search(query,limit):
            if query=='memory': raise OSError('private filesystem details')
            return search_original(query,limit)
        for protocol in ('chat','responses'):
            with patch.object(live_agent,'search_notes',side_effect=search):
                result,_=self.run_case(protocol,[([item('a'),item('b','memory')],'')])
                self.assertEqual(result['status'],'error')
                self.assertEqual(len(result['tools']),2)
                self.assertEqual(result['tools'][-1]['status'],'error')
                self.assertNotIn('private filesystem details',json.dumps(result))


if __name__=='__main__':unittest.main()
