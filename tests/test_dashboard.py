import importlib,json
from test_frontier_campaign import inputs,Fixture


def test_static_dashboard_sanitizes_and_keeps_unknown_distinct(tmp_path):
    from tracking_bench.frontier_campaign import freeze,execute_phase
    from tracking_bench.frontier_analysis import analyze_campaign
    catalog,eps=inputs();freeze({'mode':'offline_fixture'},catalog,eps,tmp_path/'c');execute_phase(tmp_path/'c','gate',transport=Fixture())
    result=analyze_campaign(tmp_path/'c');result['secret']='DO_NOT_EXPORT';result['models'][0]['provider']='</script><script>alert(1)</script>'
    d=importlib.import_module('tracking_bench.dashboard');d.export(result,tmp_path/'dashboard')
    text=(tmp_path/'dashboard/index.html').read_text()
    assert 'DO_NOT_EXPORT' not in text and '</script><script>alert(1)</script>' not in text
    assert 'https://cdn.' not in text and 'native_acc_norm' in text
    assert (tmp_path/'dashboard/results.csv').exists()
    saved=json.loads((tmp_path/'dashboard/results.json').read_text());assert saved['native_acc_norm'] is None
    assert 'offline_fixture' in text and '—' in text
