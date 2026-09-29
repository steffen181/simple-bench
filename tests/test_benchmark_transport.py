"""Unknown billing must stay reserved; model requests must contain no oracle."""
import json
import threading
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from tracking_bench.budget import Budget
from tracking_bench.openrouter import OpenRouter, request_for, validate_response, ceiling_for

MODEL = dict(id='vendor/model', context_length=1000,
             supported_parameters=['max_tokens', 'temperature', 'seed', 'reasoning'],
             pricing=dict(prompt='0.000001', completion='0.000002', request='0'))


@pytest.fixture
def endpoint():
    received = []
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            received.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(dict(id='r1', model='vendor/model', provider='P',
                choices=[dict(finish_reason='stop', message=dict(content='Ben'))],
                usage=dict(cost=0.001, prompt_tokens=20, completion_tokens=1))).encode())
        def log_message(self, *args):
            pass
    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}', received
    server.shutdown()
    thread.join()


def test_real_serialization_without_gold(endpoint):
    url, received = endpoint
    request = request_for(dict(prompt='Who holds the key?', gold='Ben', oracle_trace=['secret']), MODEL, 64, dict(temperature=0))
    response = OpenRouter(api_key='test-key', base_url=url).complete(request)
    normalized = validate_response(response)
    assert normalized['text'] == 'Ben' and normalized['cost'] == '0.001'
    assert len(received) == 1
    assert set(received[0]) == {'model', 'messages', 'max_tokens', 'temperature', 'provider', 'stream'}
    assert received[0]['provider']['require_parameters'] is True
    assert received[0]['provider']['allow_fallbacks'] is False
    assert received[0]['messages'] == [dict(role='user', content='Who holds the key?')]
    assert 'secret' not in json.dumps(received)
    assert ceiling_for(MODEL, 64) == Decimal('0.001128')
    assert received[0]['provider']['max_price'] == dict(prompt=1.0, completion=2.0, request=0.0)


def test_unsupported_parameters_and_credentials():
    with pytest.raises(ValueError, match='unsupported'):
        request_for(dict(prompt='x'), MODEL, 64, dict(top_k=4))
    with pytest.raises(ValueError):
        request_for(dict(prompt='x'), MODEL, 64, dict(api_key='forbidden'))
    with pytest.raises(ValueError):
        OpenRouter(api_key='key', base_url='http://example.org')


def raw(body, status=200):
    return dict(http_status=status, body=json.dumps(body))


@pytest.mark.parametrize('body,status', [
    ({'error': {'message': 'bad'}}, 'api_error'),
    ({'choices': [{'finish_reason': 'length', 'message': {'content': 'Ben'}}]}, 'length'),
    ({'choices': [{'finish_reason': 'stop', 'message': {'content': None, 'refusal': 'no'}}]}, 'refusal'),
    ({'choices': [{'finish_reason': 'tool_calls', 'message': {'content': ''}}]}, 'unsupported_finish'),
    ({'choices': []}, 'malformed'),
    ({'choices': [{'finish_reason': 'stop', 'message': {'content': None}}]}, 'malformed'),
])
def test_response_states(body, status):
    assert validate_response(raw(body))['status'] == status
    assert validate_response(raw(body))['cost'] is None


def test_http_error_timeout_and_malformed_are_observations():
    assert validate_response(raw({}, 429))['status'] == 'http_error'
    assert validate_response(dict(http_status=None, error='TimeoutError'))['status'] == 'transport_error'
    assert validate_response(dict(http_status=200, body='not-json'))['status'] == 'malformed'


def test_shared_budget_unknown_charge_and_duplicate_attempt(tmp_path):
    path = tmp_path / 'budget.json'
    one, two = Budget(path, '100'), Budget(path, '100')
    one.reserve('a', '60')
    with pytest.raises(ValueError, match='budget'):
        two.reserve('b', '41')
    with pytest.raises(ValueError, match='duplicate'):
        two.reserve('a', '1')
    one.settle('a', '10')
    two.reserve('b', '90')
    with pytest.raises(ValueError):
        one.reserve('c', '.01')
    assert one.snapshot()['spent'] == '10'
    assert one.snapshot()['reserved'] == '90'
    with pytest.raises(ValueError):
        one.settle('a', '10')
    with pytest.raises(ValueError):
        Budget(path, '101').snapshot()


def test_cost_over_bound_records_spend_and_blocks_future_requests(tmp_path):
    ledger = Budget(tmp_path / 'budget.json', '100')
    ledger.reserve('a', '1')
    with pytest.raises(ValueError, match='ceiling'):
        ledger.settle('a', '2')
    assert ledger.snapshot()['spent'] == '2'
    assert ledger.snapshot()['halted'] is True
    with pytest.raises(ValueError):
        ledger.reserve('b', '1')


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '-1'])
def test_invalid_money_rejected(tmp_path, value):
    with pytest.raises(ValueError):
        Budget(tmp_path / 'budget.json', value)


def test_concurrent_reservations_cannot_overspend(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    path = tmp_path / 'budget.json'
    def reserve(i):
        try:
            Budget(path).reserve(str(i), '60')
            return True
        except ValueError:
            return False
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(pool.map(reserve, range(4))) == 1
    assert Budget(path).snapshot()['reserved'] == '60'


def test_http_failure_redacts_key_and_does_not_retry():
    seen = []
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            seen.append(1)
            self.send_response(429)
            self.end_headers()
            self.wfile.write(b'{"error":"echo-secret-token"}')
        def log_message(self, *args):
            pass
    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        response = OpenRouter(api_key='echo-secret-token', base_url=f'http://127.0.0.1:{server.server_port}').complete({})
        assert 'echo-secret-token' not in json.dumps(response)
        assert validate_response(response)['status'] == 'http_error'
        assert seen == [1]
    finally:
        server.shutdown()
        thread.join()


def test_missing_prices_cannot_be_treated_as_free():
    with pytest.raises(ValueError, match='price'):
        ceiling_for(dict(MODEL, pricing={}), 8)


def test_live_and_fixture_ledgers_cannot_mix(tmp_path):
    path = tmp_path / 'budget.json'
    Budget(path, mode='offline_fixture').reserve('fixture', '1')
    with pytest.raises(ValueError, match='mode'):
        Budget(path, mode='live').reserve('live', '1')




def test_optional_request_price_does_not_hide_extra_costs():
    price = dict(prompt='0.000001', completion='0.000002')
    assert ceiling_for(dict(MODEL, pricing=dict(price, request='.01')), 64) == Decimal('.011128')
    for extra in [dict(surcharge='.1'), dict(input_cache_write='.0000025'),
                  dict(overrides=[{'prompt': '.01'}])]:
        with pytest.raises(ValueError):
            ceiling_for(dict(MODEL, pricing=dict(price, **extra)), 64)
