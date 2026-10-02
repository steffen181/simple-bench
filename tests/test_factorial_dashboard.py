import json


def test_export_keeps_full_axes_unknowns_and_strips_raw_fields(tmp_path):
    from tracking_bench.factorial_dashboard import export
    data=dict(schema='factorial-results-v1',cells=[dict(phase='develop',task='swap',model='openai/gpt-6-luna',seed='all',n=7,k=16,relevant_updates=8,d=8,accuracy_all_planned=None,observed=0,planned=6)],raw={'api_key':'DO_NOT_EXPORT'},api_key='DO_NOT_EXPORT',limitations=['Unknown is not zero'])
    export(data,tmp_path/'out')
    public=json.loads((tmp_path/'out/results.json').read_text())
    assert 'raw' not in public and 'DO_NOT_EXPORT' not in (tmp_path/'out/index.html').read_text()
    assert public['cells'][0]['d']==8 and public['cells'][0]['accuracy_all_planned'] is None
    assert 'N × R' in (tmp_path/'out/index.html').read_text()
    assert (tmp_path/'out/results.csv').exists() and (tmp_path/'out/SHA256SUMS').exists()


def test_incomplete_heatmap_value_is_unknown_not_wrong(tmp_path):
    from tracking_bench.factorial_dashboard import export
    data=dict(cells=[dict(phase='develop',task='swap',model='openai/gpt-6-luna',seed='all',n=7,k=16,relevant_updates=8,d=8,correct=1,observed=1,planned=6,accuracy_all_planned=1/6)],limitations=[])
    export(data,tmp_path/'out')
    cell=json.loads((tmp_path/'out/results.json').read_text())['cells'][0]
    assert cell['display_accuracy'] is None
    assert cell['correct']==1 and cell['observed']==1 and cell['planned']==6
