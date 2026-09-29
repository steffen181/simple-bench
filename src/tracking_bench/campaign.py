"""Predeclared structural selections; never inspect model responses."""
from collections import defaultdict
from .common import digest
from .corpus import build_corpus, validate_corpus


def _first_families(rows, n, dimensions):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row['stratum'].get(d) for d in dimensions)].append(row)
    selected = []
    for key in sorted(groups, key=str):
        group = groups[key]
        ids = sorted({r['scenario_id'] for r in group})[:n]
        selected.extend(r for r in group if r['scenario_id'] in ids)
    return selected


def select_corpora(root):
    full = build_corpus(root)
    suites = {s: [c for c in full['cases'] if c['suite'] == s] for s in full['suites']}
    discovery = _first_families(suites['discovery'], 2, ['k_total', 'query'])
    answer = [c for c in suites['answer_budget'] if c['stratum']['condition'] != 'copy-context-free']
    copies = [c for c in suites['answer_budget'] if c['stratum']['condition'] == 'copy-context-free']
    rep = _first_families(suites['repetition'], 1, ['task', 'k_total'])
    structures = [c for c in suites['swap_structures'] if c['stratum']['alias_set'] == 1
                  and c['stratum']['legacy_name_group'] == 1 and c['stratum']['rotation'] == 0]
    wording = _first_families(suites['swap_wording'], 2, [])
    tokenizer = _first_families(suites['tokenizer'], 1, ['k_total'])
    comparison = discovery + _first_families(answer, 4, ['task','k_total']) + copies + rep + structures + wording + tokenizer
    pilot = _first_families([c for c in suites['discovery'] if c['stratum']['k_total'] in [0,1,2,8,32,64,128]], 1, ['k_total'])
    pilot += _first_families(answer, 1, ['task','k_total'])
    pilot += _first_families([c for c in rep if c['stratum']['task']=='swap' and c['stratum']['k_total']==2],1,[])
    pilot += [c for c in structures if c['stratum']['word']=='single' and c['stratum']['query']==0]
    pilot += _first_families([c for c in wording if c['stratum']['condition']=='ownership-bare'],1,[])
    pilot += sorted(copies, key=lambda c:c['id'])[:1]
    result = {}
    for name, rows in [('pilot',pilot),('qwen_full',suites['answer_budget']),('comparison',comparison)]:
        assert len({c['id'] for c in rows}) == len(rows)
        corpus = dict(full, cases=sorted(rows,key=lambda c:c['id']), selection=dict(protocol='no-reasoning-20260925', phase=name))
        corpus['hash'] = digest({k:v for k,v in corpus.items() if k!='hash'})
        validate_corpus(corpus)
        result[name] = corpus
    return result
