"""Exact colored-graph identities for large tracking episodes (separate v2 schema)."""
from .common import digest


def solve(episode):
    initial=episode['initial'];n=len(initial)
    if not 2<=n<=64 or any(type(x) is not int for x in initial) or sorted(initial)!=list(range(n)):
        raise ValueError('initial ownership must be a bijection for 2..64 entities')
    q=episode['query'];task=episode['task']
    if type(q) is not int or q not in range(n) or task not in ('swap','handoff'):
        raise ValueError('invalid query/task')
    if len(episode['events'])>128:raise ValueError('too many events')
    holdings=[set() for _ in range(n)]
    for obj,owner in enumerate(initial):holdings[owner].add(obj)
    for e in episode['events']:
        a,b=e['source'],e['target']
        if any(type(x) is not int or x not in range(n) for x in (a,b)) or a==b:raise ValueError('invalid participants')
        if task=='swap' and e['kind']=='swap':holdings[a],holdings[b]=holdings[b],holdings[a]
        elif task=='handoff' and e['kind']=='give':
            obj=e['object']
            if type(obj) is not int or obj not in range(n) or obj not in holdings[a]:raise ValueError('invalid object/giver')
            holdings[a].remove(obj);holdings[b].add(obj)
        else:raise ValueError('incompatible event')
    return next(p for p,objects in enumerate(holdings) if q in objects)


def canonical_id(episode):
    solve(episode)
    try:from igraph import Graph
    except ImportError as exc:raise ValueError('Install tracking-bench[campaign] for the v2 generator') from exc
    n=len(episode['initial']);colors=[0]*n+[2 if i==episode['query'] else 1 for i in range(n)]
    edges=[(owner,n+obj) for obj,owner in enumerate(episode['initial'])]
    for index,e in enumerate(episode['events']):
        ev=len(colors);colors.append(100+index)
        if e['kind']=='swap':edges.extend([(ev,e['source']),(ev,e['target'])])
        else:
            for color,target in [(10,e['source']),(11,e['target']),(12,n+e['object'])]:
                role=len(colors);colors.append(color);edges.extend([(ev,role),(role,target)])
    graph=Graph(n=len(colors),edges=edges);graph.vs['color']=colors
    normalized=graph.permute_vertices(graph.canonical_permutation(color=colors))
    return digest(dict(schema='ownership-bliss-v2',task=episode['task'] if episode['events'] else 'initial',
        colors=normalized.vs['color'],edges=sorted(tuple(sorted(edge)) for edge in normalized.get_edgelist())))
