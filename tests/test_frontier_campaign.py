import importlib,json
from pathlib import Path
import pytest
from tracking_bench.ladder import replay_text


def mod():return importlib.import_module('tracking_bench.frontier_campaign')

def inputs():
    models=[];endpoints={}
    for mid,route,provider in [('openai/gpt-6-luna','openai','OpenAI'),('anthropic/claude-sonnet-5','anthropic','Anthropic')]:
        models.append(dict(id=mid,canonical_slug=mid,reasoning={'mandatory':False},supported_parameters=['reasoning','max_tokens']))
        endpoints[mid]={'data':{'endpoints':[dict(tag=route,provider_name=provider,supported_parameters=['reasoning','max_tokens'],context_length=1000000,pricing={'prompt':'0.0000001','completion':'0.0000001'})]}}
    return {'data':models},endpoints


class Fixture:
    def __init__(self,cost=.00001,reasoning=0):self.cost=cost;self.reasoning=reasoning;self.calls=0
    def complete(self,request):
        self.calls+=1
        return dict(http_status=200,body=json.dumps(dict(model=request['model'],provider='OpenAI' if request['model'].startswith('openai/') else 'Anthropic',choices=[dict(finish_reason='stop',message={'content':replay_text(request['messages'][0]['content'])})],usage=dict(cost=self.cost,prompt_tokens=50,completion_tokens=1,completion_tokens_details={'reasoning_tokens':self.reasoning}))))


def test_frozen_gate_audit_and_changed_response_rejected(tmp_path):
    m=mod();catalog,endpoints=inputs();m.freeze({'mode':'offline_fixture','accept_input_bound_assumption':False},catalog,endpoints,tmp_path/'campaign')
    result=m.execute_phase(tmp_path/'campaign','gate',transport=Fixture())
    assert result['status']=='COMPLETE' and result['observed']==8
    assert m.audit_campaign(tmp_path/'campaign')['status']=='PASS'
    with pytest.raises(ValueError):m.execute_phase(tmp_path/'campaign','gate',transport=Fixture())
    f=next((tmp_path/'campaign/blocks').glob('*/responses/*.json'));f.write_text('{}')
    with pytest.raises(ValueError):m.audit_campaign(tmp_path/'campaign')


def test_reasoning_or_uncertain_cost_stops_and_reservation_stays(tmp_path):
    m=mod();catalog,endpoints=inputs();m.freeze({'mode':'offline_fixture'},catalog,endpoints,tmp_path/'campaign')
    fixture=Fixture(cost=None);result=m.execute_phase(tmp_path/'campaign','gate',transport=fixture)
    assert result['status']=='STOPPED' and fixture.calls==1
    assert float(m.audit_campaign(tmp_path/'campaign')['budget']['reserved'])>0
    with pytest.raises(ValueError):m.execute_phase(tmp_path/'campaign','smoke',transport=fixture)


def test_selection_keeps_models_paired_and_handles_no_boundary():
    m=mod();rows=[]
    for model,values in [('a',[1.,1.,.75,.5]),('b',[1.,1.,1.,1.])]:
        rows.extend(dict(model=model,n=n,k=32,r=16,accuracy=a,complete=True) for n,a in zip([3,5,7,10],values))
    selected=m.select_frontier(rows)
    assert selected['models']['a']['boundary_n']==7 and selected['models']['b']['boundary_n'] is None
    assert {c['n'] for c in selected['cells']}=={3,5,7,10}
    assert len(m.select_frontier([dict(r,complete=False) for r in rows])['cells'])==0


def test_live_requires_explicit_estimate_acceptance(tmp_path):
    m=mod();catalog,endpoints=inputs()
    with pytest.raises(ValueError):m.freeze({'mode':'live','accept_input_bound_assumption':False},catalog,endpoints,tmp_path/'campaign')


def test_full_fixture_campaign_freezes_population_before_confirmation(tmp_path):
    m=mod();catalog,endpoints=inputs();root=tmp_path/'c';m.freeze({'mode':'offline_fixture'},catalog,endpoints,root)
    fixture=Fixture();m.execute_phase(root,'gate',transport=fixture);m.execute_phase(root,'smoke',transport=fixture)
    assert m.execute_phase(root,'confirm',transport=fixture)['status']=='COMPLETE'
    audit=m.audit_campaign(root);assert audit['status']=='PASS'
    from tracking_bench.common import read_json
    population=read_json(root/'confirmation-population.json');assert len(population)>=3
    assert all(len(block['cases'])==8 for block in population)
    dev={c['canonical_id'] for folder in (root/'blocks').iterdir() if 'confirm' not in folder.name for c in read_json(folder/'cases.json')}
    confirm={c['canonical_id'] for block in population for c in block['cases']};assert dev.isdisjoint(confirm)
    from tracking_bench.frontier_analysis import analyze_campaign
    from tracking_bench.dashboard import export
    result=analyze_campaign(root);export(result,tmp_path/'dashboard')
    assert result['selection']['models']['openai/gpt-6-luna']['boundary_n'] is None


def test_v2_cli(tmp_path):
    from tracking_bench.cli import main
    assert main(['generate','--version','v2','--entities','10','--steps','8','--relevant-updates','4','--per-cell','1','--out',str(tmp_path/'cases.json')])==0


@pytest.mark.parametrize('body',[[],{'usage':None},{'usage':'invalid'}])
def test_malformed_provider_response_still_audits(tmp_path,body):
    m=mod();catalog,endpoints=inputs();root=tmp_path/'c'
    m.freeze({'mode':'offline_fixture'},catalog,endpoints,root)
    class Broken:
        def complete(self,request):return {'http_status':502,'body':json.dumps(body)}
    result=m.execute_phase(root,'gate',transport=Broken())
    assert result['status']=='STOPPED' and result['observed']==1
    assert float(m.audit_campaign(root)['budget']['reserved'])>0


def test_boundary_cannot_bridge_invalid_or_missing_levels_or_axes():
    base=dict(model='a',k=32,r=16,complete=True,format_ok=True)
    rows=[dict(base,n=n,accuracy=a) for n,a in [(3,1),(5,.5),(7,.5),(10,.5)]]
    rows[2]['format_ok']=False
    assert mod().select_frontier(rows)['models']['a']['boundary_n'] is None
    assert mod().select_frontier([rows[0],rows[1],rows[3]])['models']['a']['boundary_n'] is None
    assert mod().select_frontier([rows[0],dict(base,n=64,accuracy=.5),dict(base,n=64,k=64,r=32,accuracy=.5)])['models']['a']['boundary_n'] is None


def test_confirmation_budget_stop_preserves_full_denominator(tmp_path,monkeypatch):
    m=mod();catalog,endpoints=inputs();root=tmp_path/'c';m.freeze({'mode':'offline_fixture'},catalog,endpoints,root)
    fixture=Fixture();m.execute_phase(root,'gate',transport=fixture);m.execute_phase(root,'smoke',transport=fixture)
    from decimal import Decimal
    monkeypatch.setattr(m,'_available',lambda *args:Decimal(0))
    result=m.execute_phase(root,'confirm',transport=fixture)
    from tracking_bench.common import read_json
    planned=sum(len(b['cases'])*2 for b in read_json(root/'confirmation-population.json'))
    assert result['status']=='STOPPED' and result['observed']==0 and result['planned']==planned>16
    assert m.audit_campaign(root)['status']=='PASS'


def test_confirmation_plan_to_block_binding(tmp_path):
    m=mod();catalog,endpoints=inputs();root=tmp_path/'c';m.freeze({'mode':'offline_fixture'},catalog,endpoints,root)
    fixture=Fixture();m.execute_phase(root,'gate',transport=fixture);m.execute_phase(root,'smoke',transport=fixture);m.execute_phase(root,'confirm',transport=fixture)
    from tracking_bench.common import read_json,file_hash
    pop=root/'confirmation-population.json';data=read_json(pop);data[0]['cases'].reverse();pop.write_text(json.dumps(data))
    frozen=root/'confirmation-freeze.json';data=read_json(frozen);data['population_hash']=file_hash(pop);frozen.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='block differs'):m.audit_campaign(root)
