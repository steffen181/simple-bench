"""Counterexamples to treating incomplete/altered token likelihoods as accuracy."""
import importlib
import json
import pytest


def implementation():
    name = 'tracking_bench.bbh_likelihood'
    assert importlib.util.find_spec(name) is not None, 'likelihood implementation missing'
    return importlib.import_module(name)


def token(text, lp):
    return dict(token=text, bytes=list(text.encode()), logprob=lp)


def response(entries, text='A', reason='length'):
    return dict(http_status=200, body=json.dumps(dict(model='test', provider='Test',
        choices=[dict(finish_reason=reason, message=dict(content=text), logprobs=dict(content=[
            dict(**token(text, next((e['logprob'] for e in entries if e['token']==text), -5)), top_logprobs=entries)]))], usage=dict(cost=0.001))))


def test_candidate_winner_is_not_generated_token():
    result=implementation().decision(response([token('B',-0.7),token('A',-2),token('C',-3)]), 'ABC')
    assert result['prediction']=='B' and result['status']=='resolved'
    assert result['candidate_logprobs']=={'A':-2,'B':-0.7,'C':-3}


def test_missing_top_candidates_never_become_zero_or_false():
    api=implementation()
    result=api.decision(response([token('The',-0.1),token(' ', -1)],text='The'), 'ABC')
    assert result['prediction'] is None and result['status']=='unresolved'
    assert result['candidate_logprobs']=={'A':None,'B':None,'C':None}
    result=api.decision(response([token('B',-0.3),token('x',-2)]), 'ABC')
    assert result['prediction']=='B' and result['missing_candidates']==['A','C']


def test_tie_at_top_k_boundary_is_unresolved():
    result=implementation().decision(response([token('B',-1),token('x',-1)]), 'ABC')
    assert result['prediction'] is None


@pytest.mark.parametrize('entries',[[token(' A',-.1)], [token('(A)',-.1)],
    [token('A',float('nan'))], [token('A',1)], [token('A',-9999)],
    [token('A',-.1),token('A',-.2)], [dict(token='A',bytes=[66],logprob=-.1)]])
def test_no_whitespace_folding_duplicate_or_invalid_probability(entries):
    result=implementation().decision(response(entries), 'ABC')
    assert result['prediction'] is None


def test_refusals_and_missing_logprobs_cannot_score():
    api=implementation()
    for raw in [response([token('A',-.1)],reason='content_filter'),dict(http_status=429,body='{}'),
                dict(http_status=200,body='{}')]:
        assert api.decision(raw,'ABC')['prediction'] is None


def test_coverage_bounds_include_every_planned_question():
    result=implementation().summarize([
        dict(gold='A',prediction='A'),dict(gold='B',prediction='A'),dict(gold='C',prediction=None)])
    assert result==dict(planned=3,resolved=2,correct=1,coverage=2/3,accuracy=None,
                       accuracy_resolved=0.5,accuracy_lower=1/3,accuracy_upper=2/3)


def test_request_pins_route_without_bias_and_excludes_gold():
    model=dict(id='test',context_length=1000,supported_parameters=['max_tokens','temperature','top_p','logprobs','top_logprobs'],
               pricing=dict(prompt='0.000001',completion='0.000001'))
    api=implementation(); req=api.request([dict(role='user',content='Question')],model,'route')
    assert req['logprobs'] is True and req['top_logprobs']==20 and req['max_tokens']==1
    assert req['temperature']==1 and req['top_p']==1 and 'logit_bias' not in req
    assert req['provider']['only']==['route'] and req['provider']['require_parameters'] is True
    model['supported_parameters'].remove('logprobs')
    with pytest.raises(ValueError): api.request([dict(role='user',content='Question')],model,'route')


def test_prompt_uses_demonstrations_but_never_question_gold():
    api=implementation()
    demo=dict(input='Demo',target='(B)')
    q=dict(input='Question',target='(A)')
    messages=api.messages(q,[demo]);q['target']='(C)'
    assert messages==api.messages(q,[demo])
    assert messages[-1]==dict(role='user',content='Question')
    assert messages[-2]==dict(role='assistant',content='B')


def test_paid_attempt_stores_receipts_and_preserves_unknown_reservation(tmp_path):
    from tracking_bench.budget import Budget
    api=implementation(); ledger=Budget(tmp_path/'budget.json',mode='offline_fixture')
    class Transport:
        def complete(self,req):return dict(http_status=None,error='TimeoutError')
    out=tmp_path/'run';out.mkdir()
    api.attempt(out,'one',{'model':'test'},Transport(),ledger,'0.01',{'test':'1'})
    assert (out/'one.request.json').exists() and (out/'one.response.json').exists()
    assert ledger.snapshot()['reserved']=='0.01'
    with pytest.raises((ValueError,FileExistsError)):
        api.attempt(out,'one',{'model':'test'},Transport(),ledger,'0.01',{'test':'1'})
    assert len(ledger.snapshot()['attempts'])==1


def test_paid_attempt_records_usage_even_when_logprobs_missing(tmp_path):
    from tracking_bench.budget import Budget
    api=implementation(); ledger=Budget(tmp_path/'budget.json',mode='offline_fixture')
    class Transport:
        def complete(self,req):return dict(http_status=200,body=json.dumps(dict(usage=dict(cost=.003))))
    out=tmp_path/'run';out.mkdir()
    api.attempt(out,'one',{'model':'test'},Transport(),ledger,'0.01',{'test':'1'})
    assert ledger.snapshot()['spent']=='0.003' and ledger.snapshot()['reserved']=='0'




@pytest.mark.parametrize('mutation',['positive','text_mismatch','logprob_mismatch','reasoning'])
def test_contradictory_sample_or_reasoning_is_not_scored(mutation):
    raw=response([token('A',-.1),token('B',-3)])
    body=json.loads(raw['body']);choice=body['choices'][0]
    if mutation=='positive':choice['logprobs']['content'][0]['logprob']=1
    if mutation=='text_mismatch':choice['message']['content']='B'
    if mutation=='logprob_mismatch':choice['logprobs']['content'][0]['logprob']=-2
    if mutation=='reasoning':body['usage']['completion_tokens_details']={'reasoning_tokens':5}
    raw['body']=json.dumps(body)
    assert implementation().decision(raw,'ABC')['prediction'] is None


def test_over_ceiling_attempt_preserves_receipt(tmp_path):
    from tracking_bench.budget import Budget
    api=implementation();ledger=Budget(tmp_path/'ledger.json',mode='offline_fixture')
    class Transport:
        def complete(self,req):return response([token('A',-.1)])
    with pytest.raises(ValueError,match='ceiling'):
        api.attempt(tmp_path,'one',{},Transport(),ledger,'0.0001',{'test':'1'})
    assert (tmp_path/'one.receipt.json').exists()
    assert ledger.snapshot()['halted'] is True


def test_emitted_token_cannot_contradict_top_k_omission_bound():
    raw=response([token('B',-.3),token('x',-2)],text='A')
    data=json.loads(raw['body']);data['choices'][0]['logprobs']['content'][0]['logprob']=-.2
    raw['body']=json.dumps(data)
    assert implementation().decision(raw,'ABC')['prediction'] is None


def test_malformed_reasoning_telemetry_is_unresolved_not_exception():
    raw=response([token('A',-.1),token('B',-3)])
    data=json.loads(raw['body']);data['usage']['completion_tokens_details']=['x']
    raw['body']=json.dumps(data)
    assert implementation().decision(raw,'ABC')['prediction'] is None
