"""Process-safe shared USD ledger. Uncertain attempts retain their reservation."""
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
import fcntl
import os
from pathlib import Path
import tempfile

from .common import canonical, read_json


def money(value):
    try:
        value = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError('invalid money') from exc
    if not value.is_finite() or value < 0:
        raise ValueError('invalid money')
    return value


class Budget:
    def __init__(self, path, limit='100', mode='live'):
        if mode not in ('live', 'offline_fixture'):
            raise ValueError('unknown budget mode')
        self.mode = mode
        self.path = Path(path).resolve()
        self.limit = money(limit)
        if not 0 < self.limit <= 100:
            raise ValueError('authorized budget must be >0 and <=100 USD')
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _locked(self):
        with self.path.with_suffix(self.path.suffix + '.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            data = read_json(self.path) if self.path.exists() else dict(schema='benchmark-budget-v1', limit=str(self.limit), attempts={}, halted=False, mode=self.mode)
            if money(data['limit']) != self.limit or data['schema'] != 'benchmark-budget-v1':
                raise ValueError('budget limit/schema mismatch')
            if data['mode'] != self.mode:
                raise ValueError('budget mode mismatch')
            yield data

    def _save(self, data):
        fd, name = tempfile.mkstemp(dir=self.path.parent, prefix='.budget-')
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(canonical(data) + b'\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.path)
            directory = os.open(self.path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    @staticmethod
    def _totals(data):
        spent = sum((money(a['cost']) for a in data['attempts'].values() if a['cost'] is not None), Decimal(0))
        reserved = sum((money(a['ceiling']) for a in data['attempts'].values() if a['cost'] is None), Decimal(0))
        return spent, reserved

    def snapshot(self):
        with self._locked() as data:
            spent, reserved = self._totals(data)
            return dict(data, spent=str(spent), reserved=str(reserved), remaining=str(self.limit - spent - reserved))

    def reserve(self, attempt_id, ceiling, limits=None):
        ceiling = money(ceiling)
        with self._locked() as data:
            if attempt_id in data['attempts']:
                raise ValueError('duplicate attempt')
            spent, reserved = self._totals(data)
            if data['halted'] or spent + reserved + ceiling > self.limit:
                raise ValueError('budget exhausted or halted')
            if limits:
                registered = data.setdefault('limits', {})
                for scope, limit in limits.items():
                    limit = money(limit)
                    if not isinstance(scope, str) or not scope or not 0 < limit <= self.limit:
                        raise ValueError('invalid spending scope')
                    if scope in registered and money(registered[scope]) != limit:
                        raise ValueError('scope limit mismatch')
                    scoped = {'attempts': {k: a for k, a in data['attempts'].items() if scope in a.get('scopes', [])}}
                    scope_spent, scope_reserved = self._totals(scoped)
                    if scope_spent + scope_reserved + ceiling > limit:
                        raise ValueError('scope budget exhausted')
                    registered[scope] = str(limit)
            data['attempts'][attempt_id] = dict(ceiling=str(ceiling), cost=None)
            if limits:
                data['attempts'][attempt_id]['scopes'] = list(limits)
            self._save(data)

    def settle(self, attempt_id, cost):
        cost = money(cost)
        with self._locked() as data:
            attempt = data['attempts'][attempt_id]
            if attempt['cost'] is not None:
                raise ValueError('attempt already settled')
            attempt['cost'] = str(cost)
            exceeded = cost > money(attempt['ceiling'])
            data['halted'] |= exceeded
            self._save(data)
        if exceeded:
            raise ValueError('provider cost exceeded reserved ceiling; ledger halted')
