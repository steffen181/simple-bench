"""Immutable continuation segments; HTTP429 retries never replace model answers."""
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import fcntl
import time

from .common import digest, read_json
from .run import prepare, run, verify, _load_plan
from .openrouter import OpenRouter


@contextmanager
def process_lock(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('series locked by another process') from None
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


class LimitedOpenRouter(OpenRouter):
    """Exactly two shared process slots for calls using this campaign transport."""
    def __init__(self, *args, slot_directory, **kwargs):
        super().__init__(*args, **kwargs)
        self.slot_directory = Path(slot_directory)
        self.slot_directory.mkdir(parents=True, exist_ok=True)

    def complete(self, request):
        while True:
            for index in range(2):
                with (self.slot_directory / f'{index}.lock').open('a') as handle:
                    try:
                        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        continue
                    try:
                        return super().complete(request)
                    finally:
                        fcntl.flock(handle, fcntl.LOCK_UN)
            time.sleep(.1)


def prepare_series(corpus, config, catalog, root):
    if len(config['models']) != 1 or len(config['max_tokens']) != 1:
        raise ValueError('series requires exactly one model and token budget')
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    prepare(corpus, config, catalog, root / 'base')
    (root / 'segments').mkdir()


def collect_series(root):
    root = Path(root).resolve()
    _, corpus, config, catalog, _ = _load_plan(root / 'base')
    cases = {c['id']: c for c in corpus['cases']}
    attempts, settled, summaries = [], {}, []
    segments = sorted((root / 'segments').iterdir())
    for number, segment in enumerate(segments):
        if segment.name != f'{number:06d}' or not (segment / 'seal.json').is_file():
            raise ValueError('nonsequential or unsealed segment; manual reconciliation required')
        verify(segment)
        _, subset, cfg, cat, schedule = _load_plan(segment)
        if cfg != config or cat != catalog:
            raise ValueError('series contract changed')
        expected = [c for c in corpus['cases'] if c['id'] not in settled][:128]
        if subset['cases'] != expected:
            raise ValueError('segment selection differs from unresolved prefix')
        summary = read_json(segment / 'summary.json')
        summaries.append(summary)
        for i, item in enumerate(schedule[:summary['observed']]):
            receipt = read_json(segment / 'receipts' / f'{i:06d}.json')
            raw = read_json(segment / 'responses' / f'{i:06d}.json')
            attempt = dict(case_id=item['case_id'], segment=str(segment), index=i, receipt=receipt, raw=raw)
            attempts.append(attempt)
            if receipt['response']['status'] in ('stop', 'length', 'refusal') and receipt['response']['cost'] is not None:
                if item['case_id'] in settled:
                    raise ValueError('duplicate settled case')
                settled[item['case_id']] = attempt
    return dict(corpus=corpus, config=config, catalog=catalog, attempts=attempts, settled=settled,
                summaries=summaries, segment_count=len(segments))


def _delay(raw, retry):
    delay = 30 * 2 ** (retry - 1)
    value = raw.get('retry_after')
    if value:
        try:
            delay = max(delay, float(value))
        except (ValueError, TypeError):
            try:
                delay = max(delay, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError, OverflowError):
                pass
    return delay


def continue_series(root, transport, sleep=time.sleep):
    root = Path(root).resolve()
    with process_lock(root / 'controller.lock'):
        _load_plan(root / 'base', executing=True)
        while True:
            state = collect_series(root)
            remaining = [c for c in state['corpus']['cases'] if c['id'] not in state['settled']]
            if state['summaries'] and state['summaries'][-1]['status'] != 'COMPLETE':
                last_summary = state['summaries'][-1]
                last = state['attempts'][-1] if last_summary['observed'] else None
                if (not last or last['raw'].get('http_status') != 429
                        or last_summary['reason'] not in ('unknown_cost', 'http_error')):
                    return dict(status='STOPPED', reason=last_summary['reason'], settled=len(state['settled']))
                count = sum(a['case_id'] == last['case_id'] for a in state['attempts'])
                if count > 3:
                    return dict(status='STOPPED', reason='retry_limit', settled=len(state['settled']))
                sleep(_delay(last['raw'], count))
            if not remaining:
                return dict(status='COMPLETE', settled=len(state['settled']))
            subset = dict(state['corpus'], cases=remaining[:128])
            subset['hash'] = digest({k: v for k, v in subset.items() if k != 'hash'})
            segment = root / 'segments' / f"{state['segment_count']:06d}"
            prepare(subset, state['config'], state['catalog'], segment)
            run(segment, transport)
