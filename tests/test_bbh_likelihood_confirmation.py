import importlib
import math
import pytest

def m():return importlib.import_module('tracking_bench.bbh_likelihood_confirmation')

def test_native_decision_uses_full_character_normalization():
    r=m().native_result(3,'(B)',[-4.,-2.,-3.])
    assert r['prediction']=='(B)' and r['normalized_loglikelihoods']==[-4/3,-2/3,-1.]
    for values in ([-1.],[-1.,float('nan'),-2.],[-1.,float('inf'),-2.]):
        with pytest.raises(ValueError):m().native_result(3,'(B)',values)

def test_every_case_has_native_measurement_and_reference_no_cot():
    cases=[dict(id='g',origin='generated'),dict(id='a',origin='anchor'),dict(id='c',origin='control'),dict(id='r',origin='reference')]
    rr=m().requests(cases)
    assert [r['case_id'] for r in rr if r['condition']==m().PRIMARY]==['g','a','c','r']
    assert len(rr)==13 and sum(r['case_id']=='r' for r in rr)==1

def test_full_candidates_use_harness_pair_encoding_and_reject_truncation():
    class LM:
        max_length=10
        def _encode_pair(self,context,answer):
            assert context=='Q\nA:' and answer in [' (A)',' (B)',' (C)']
            return [1,2],[3,4,5]
    rows=m().token_requests(LM(),'Q\nA:',3)
    assert len(rows)==3 and rows[1]['answer']==' (B)' and rows[1]['answer_ids']==[3,4,5]
    lm=LM();lm.max_length=4
    with pytest.raises(ValueError):m().token_requests(lm,'Q\nA:',3)

def test_native_audit_does_not_gate_on_accuracy_and_rejects_missing():
    mod=m();case=dict(id='x',n=3,target='(C)',origin='control')
    row=dict(case_id='x',condition=mod.PRIMARY,loglikelihoods=[-1.,-2.,-3.],result=mod.native_result(3,'(C)',[-1.,-2.,-3.]),native_acc_norm=0.)
    assert mod.audit_rows([case],[dict(case_id='x',condition=mod.PRIMARY)],[row])==1
    with pytest.raises(ValueError):mod.audit_rows([case],[dict(case_id='x',condition=mod.PRIMARY)],[])
    with pytest.raises(ValueError):mod.audit_rows([case],[dict(case_id='x',condition=mod.PRIMARY)],[dict(row,native_acc_norm=1.)])


def test_reference_population_is_exact_original_and_secondary_excluded(monkeypatch):
    mod=m();original=[dict(input='original question',target='(B)',n=3,source_index=0)]
    monkeypatch.setattr(mod.fresh,'make_phase',lambda *args:[])
    assert mod.make_phase(original,set(),[17],1,'development')==[]
    result=mod.make_phase(original,set(),[23],1,'confirmation')
    assert len(result)==1 and result[0]['input']==original[0]['input'] and result[0]['target']=='(B)'
    assert result[0]['origin']=='reference' and mod.requests(result)==[dict(case_id=result[0]['id'],condition=mod.PRIMARY)]


def test_dependency_seal_covers_inherited_encoder_and_sampler(tmp_path):
    for name in ['models/huggingface.py','models/utils.py','api/model.py','api/task.py','api/samplers.py']:
        p=tmp_path/name;p.parent.mkdir(exist_ok=True);p.write_text('# pinned source\n')
    files=m().harness_sources(tmp_path/'models/huggingface.py')
    assert {str(p.relative_to(tmp_path)) for p in files}=={'models/huggingface.py','models/utils.py','api/model.py','api/task.py','api/samplers.py'}
