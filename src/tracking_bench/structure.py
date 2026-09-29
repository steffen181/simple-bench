"""Independent possession-set oracle and exact renaming-invariant identities.

Initial possession must be bijective. Canonicalization costs (n-1)! * events;
2..8 entities are supported. Equal final answers are NOT equal structures.
"""
from collections import defaultdict
from itertools import permutations
from .common import digest


def solve(episode):
    initial = episode['initial']
    n = len(initial)
    if (not 2 <= n <= 8 or any(type(i) is not int for i in initial)
            or sorted(initial) != list(range(n))):
        raise ValueError('initial ownership must be a bijection for 2..8 entities')
    query = episode['query']
    if type(query) is not int or query not in range(n):
        raise ValueError('invalid query')
    task = episode['task']
    if task not in ('swap','handoff'):
        raise ValueError('unsupported task')
    possessions = [set() for _ in range(n)]
    for obj, owner in enumerate(initial):
        possessions[owner].add(obj)
    for event in episode['events']:
        a, b = event['source'], event['target']
        if any(type(p) is not int or p not in range(n) for p in (a,b)) or a == b:
            raise ValueError('invalid event participants')
        if event['kind'] == 'swap' and task == 'swap':
            possessions[a], possessions[b] = possessions[b], possessions[a]
        elif event['kind'] == 'give' and task == 'handoff':
            obj = event['object']
            if type(obj) is not int or obj not in range(n) or obj not in possessions[a]:
                raise ValueError('invalid object or giver')
            possessions[a].remove(obj)
            possessions[b].add(obj)
        else:
            raise ValueError('event kind incompatible with task')
    return next(owner for owner, objects in enumerate(possessions) if query in objects)


def canonical_structure(episode):
    solve(episode)  # Reject invalid paths before deriving an identity.
    n, query = len(episode['initial']), episode['query']
    others = [obj for obj in range(n) if obj != query]
    paths = []
    for labels in permutations(range(1,n)):
        objects = dict(zip(others,labels))
        objects[query] = 0
        people = {owner: objects[obj] for obj,owner in enumerate(episode['initial'])}
        path = []
        for event in episode['events']:
            a,b = people[event['source']],people[event['target']]
            if event['kind'] == 'swap':
                path.append(('swap',min(a,b),max(a,b),-1))
            else:
                path.append(('give',a,b,objects[event['object']]))
        paths.append(tuple(path))
    return digest(dict(version='ownership-canonical-v1',entities=n,
                       task=episode['task'] if episode['events'] else 'initial',events=min(paths)))


def structure_audit(cases):
    groups = defaultdict(list)
    cache = {}
    identities = []
    for case in cases:
        if 'structure' not in case:
            raise ValueError('missing structure; source cannot be declared disjoint')
        key = digest(case['structure'])
        if key not in cache:
            cache[key] = canonical_structure(case['structure'])
        identity = cache[key]
        identities.append(identity)
        groups[case['stratum']['task'],case['stratum']['k_total']].append(identity)
    return dict(cases=len(identities),canonical_structures=len(set(identities)),
                groups=[dict(task=t,k_total=k,cases=len(v),canonical_structures=len(set(v)))
                        for (t,k),v in sorted(groups.items())],
                coverage='Supplied structured cases only; not an all-archive contamination audit.')
