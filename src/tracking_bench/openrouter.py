"""Small OpenRouter adapter: explicit parameters, no SDK defaults or retries."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from .budget import money

PARAMETERS = {'temperature', 'seed', 'reasoning', 'reasoning_effort', 'top_p'}


def _prices(model):
    pricing = model['pricing']
    if not {'prompt', 'completion'} <= pricing.keys():
        raise ValueError('missing price components')
    # Additional nonzero charge categories cannot be bounded by this text runner.
    for key, value in pricing.items():
        if key not in ('prompt', 'completion', 'request') and money(value) != 0:
            raise ValueError(f'unsupported price component: {key}')
    # An omitted optional request price is NOT a claim that every route is free.
    # We explicitly require max_price.request=0 in request_for, admitting only
    # routes without a per-request surcharge. Token prices remain mandatory.
    return {key: money(pricing.get(key, '0')) for key in ('prompt', 'completion', 'request')}



def _text_prices(model):
    """Bound plain text without tools, including every known tier/cache rate."""
    base = model['pricing']
    if not {'prompt', 'completion'} <= base.keys():
        raise ValueError('missing price components')
    tiers = base.get('overrides', [])
    if not isinstance(tiers, list):
        raise ValueError('invalid price overrides')
    prices = dict(prompt=money(0), completion=money(0), request=money(0), input_bound=money(0))
    cache = {'input_cache_read', 'input_cache_write', 'input_cache_write_1h'}
    conditions = {'min_prompt_tokens', 'max_prompt_tokens', 'utc_days', 'utc_start', 'utc_end'}
    for tier in [base, *tiers]:
        if not isinstance(tier, dict):
            raise ValueError('invalid price tier')
        for key, value in tier.items():
            if key == 'overrides' and tier is base:
                continue
            if key in conditions and tier is not base:
                continue  # Maximize all tiers regardless of activation condition.
            amount = money(value)
            if key in ('prompt', 'completion', 'request'):
                prices[key] = max(prices[key], amount)
            elif key in cache:
                prices['input_bound'] = max(prices['input_bound'], amount)
            elif key != 'web_search' and amount:
                raise ValueError(f'unsupported text price component: {key}')
            # web_search is unreachable: request_for has no tools/plugins/URLs.
    prices['input_bound'] = max(prices['input_bound'], prices['prompt'])
    return prices


def _policy_prices(model, price_policy):
    if price_policy is None:
        return _prices(model)
    if price_policy != 'text-v2':
        raise ValueError('unknown price policy')
    return _text_prices(model)


def _off_parameters(model, params):
    if (model.get('reasoning') or {}).get('mandatory'):
        raise ValueError('mandatory reasoning cannot be disabled')
    if any(key in params for key in ('reasoning', 'reasoning_effort')):
        raise ValueError('reasoning policy conflicts with explicit reasoning parameters')
    if 'reasoning' in model['supported_parameters']:
        return dict(params, reasoning={'enabled': False})
    if model.get('reasoning'):
        raise ValueError('reasoning cannot be disabled through this adapter')
    return params


def reasoning_evidence(raw):
    data = json.loads(raw['body'])
    message = data['choices'][0]['message']
    usage = data.get('usage')
    usage = usage if isinstance(usage, dict) else {}
    details = usage.get('completion_tokens_details') or {}
    tokens = details.get('reasoning_tokens') if isinstance(details, dict) else None
    if any(message.get(k) for k in ('reasoning', 'reasoning_content', 'reasoning_details')):
        return 'reasoning_enabled'
    if type(tokens) is int and tokens > 0:
        return 'reasoning_enabled'
    if type(tokens) is not int or tokens != 0:
        return 'reasoning_unverified'
    return 'off_verified'

def ceiling_for(model, max_tokens, price_policy=None):
    context = model['context_length']
    if type(context) is not int or context <= 0 or type(max_tokens) is not int or not 0 < max_tokens <= context:
        raise ValueError('invalid context/max_tokens')
    top_limit = (model.get('top_provider') or {}).get('max_completion_tokens')
    if top_limit is not None and max_tokens > top_limit:
        raise ValueError('max_tokens exceeds catalog completion limit')
    prices = _policy_prices(model, price_policy)
    return prices.get('input_bound', prices['prompt']) * context + prices['completion'] * max_tokens + prices['request']


def request_for(public, model, max_tokens, params=None, provider=None, price_policy=None, reasoning_policy=None):
    params = {} if params is None else params
    if reasoning_policy is not None:
        if reasoning_policy != 'off':
            raise ValueError('unknown reasoning policy')
        params = _off_parameters(model, params)
    if set(params) - PARAMETERS:
        raise ValueError('unsupported request parameter')
    if (set(params) | {'max_tokens'}) - set(model['supported_parameters']):
        raise ValueError('unsupported model parameters')
    ceiling_for(model, max_tokens, price_policy)
    prices = _policy_prices(model, price_policy)
    routing = dict(require_parameters=True, allow_fallbacks=False,
                   max_price={k: float(v * (1000000 if k in ('prompt', 'completion') else 1)) for k, v in prices.items() if k != 'input_bound'})
    if provider:
        routing['only'] = [provider]
    extra = {}
    if 'stop_sequences' in public:
        stops = public['stop_sequences']
        if ('stop' not in model['supported_parameters'] or not isinstance(stops, list)
                or not 1 <= len(stops) <= 4 or any(not isinstance(s, str) or not s for s in stops)
                or len(set(stops)) != len(stops)):
            raise ValueError('invalid or unsupported stop sequences')
        extra['stop'] = stops
    return dict(model=model['id'], messages=[dict(role='user', content=public['prompt'])],
                max_tokens=max_tokens, stream=False, provider=routing, **params, **extra)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward bearer credentials to a redirected host.


class OpenRouter:
    def __init__(self, api_key=None, base_url='https://openrouter.ai/api/v1', timeout=120):
        self.key = api_key if api_key is not None else os.environ.get('OPENROUTER_API_KEY')
        parsed = urllib.parse.urlsplit(base_url)
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('invalid API URL')
        if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1', 'localhost', '::1')):
            raise ValueError('HTTPS required outside loopback tests')
        self.base_url, self.timeout = base_url.rstrip('/'), timeout
        self.opener = urllib.request.build_opener(_NoRedirect)

    def _request(self, path, payload=None):
        if payload is not None and not self.key:
            raise ValueError('OPENROUTER_API_KEY is not configured')
        headers = {'Content-Type': 'application/json'}
        if self.key:
            headers['Authorization'] = 'Bearer ' + self.key
        req = urllib.request.Request(self.base_url + path, data=json.dumps(payload, allow_nan=False).encode() if payload is not None else None, headers=headers)
        retry_after = None
        try:
            with self.opener.open(req, timeout=self.timeout) as response:
                status, body = response.status, response.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as exc:
            status, body = exc.code, exc.read().decode('utf-8', errors='replace')
            retry_after = exc.headers.get('Retry-After') if exc.headers else None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return dict(http_status=None, error=type(exc).__name__)
        if self.key:
            body = body.replace(self.key, '[REDACTED]')
        result = dict(http_status=status, body=body)
        if retry_after:
            result['retry_after'] = retry_after.replace(self.key, '[REDACTED]') if self.key else retry_after
        return result

    def catalog(self):
        response = self._request('/models')
        if response['http_status'] != 200:
            raise ValueError('catalog request failed')
        data = json.loads(response['body'])
        if not isinstance(data.get('data'), list):
            raise ValueError('invalid catalog')
        return data

    def complete(self, request):
        return self._request('/chat/completions', request)


def validate_response(raw):
    result = dict(status='malformed', text='', cost=None, usage=None, model=None,
                  provider=None, request_id=None, system_fingerprint=None, finish_reason=None)
    if raw.get('http_status') is None:
        return dict(result, status='transport_error')
    try:
        data = json.loads(raw.get('body', ''))
    except (ValueError, TypeError):
        return dict(result, status='http_error' if raw['http_status'] != 200 else 'malformed')
    if not isinstance(data, dict):
        return result
    usage = data.get('usage')
    if isinstance(usage, dict) and usage.get('cost') is not None:
        try:
            result['cost'] = str(money(usage['cost']))
        except ValueError:
            pass
    result.update(usage=usage, model=data.get('model'), provider=data.get('provider'),
                  request_id=data.get('id'), system_fingerprint=data.get('system_fingerprint'))
    if raw['http_status'] != 200:
        return dict(result, status='http_error')
    if 'error' in data:
        return dict(result, status='api_error')
    choices = data.get('choices')
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        return result
    choice = choices[0]
    message = choice.get('message')
    result['finish_reason'] = finish = choice.get('finish_reason')
    if not isinstance(message, dict):
        return result
    if message.get('refusal') or finish == 'content_filter':
        return dict(result, status='refusal')
    if finish not in ('stop', 'length'):
        return dict(result, status='unsupported_finish')
    content = message.get('content')
    if content is None and finish == 'length':
        content = ''  # Reasoning exhausted the output budget; no visible answer.
    if not isinstance(content, str):
        return result
    return dict(result, status=finish, text=content)
