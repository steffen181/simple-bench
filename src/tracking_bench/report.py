"""Descriptive results with explicit coverage and semantic (person) pairing."""
from collections import defaultdict
import csv
import io
from itertools import combinations
from pathlib import Path

from .budget import money
from .common import canonical, digest, read_json, write_new
from .run import verify

DIMENSIONS = ('entities', 'task', 'condition', 'k_total', 'k_target', 'relevant_updates', 'word',
              'template', 'variant', 'repetition', 'legacy_name_group')


def _records(out):
    corpus = read_json(out / 'corpus.json')
    cases = {c['id']: c for c in corpus['cases']}
    schedule = read_json(out / 'schedule.json')
    for index, item in enumerate(schedule):
        receipt = out / 'receipts' / f'{index:06d}.json'
        yield item, cases[item['case_id']], read_json(receipt) if receipt.exists() else None



def _contrasts(records):
    episodes = defaultdict(list)
    for item, case, receipt in records:
        s = case['stratum']
        # Only names/labels are two encodings of the same question; ownership and
        # answer-cued copy/lookup controls remain separate semantic contrasts.
        condition = 'answer_encoding' if s['condition'] in ('names', 'labels') else s['condition']
        episode = [case['suite'], case['scenario_id'], condition, s.get('alias_set'), s.get('legacy_name_group')]
        if case['suite'] == 'swap_structures':
            episode[1] = [s['word'], s['query'], s['rotation']]
        key = digest([item['model'], item['max_tokens'], episode])
        variant = {k: s.get(k) for k in ('condition', 'variant', 'repetition', 'orientation')}
        episodes[key].append((item, case, variant, receipt))
    contrasts = {}
    for entries in episodes.values():
        entries = sorted(entries, key=lambda row: canonical(row[2]))
        for left, right in combinations(entries, 2):
            item, case, a, ra = left
            _, _, b, rb = right
            if a == b:
                continue
            dimensions = dict(model=item['model'], max_tokens=item['max_tokens'], suite=case['suite'],
                              task=case['stratum']['task'], k_total=case['stratum']['k_total'],
                              entities=case['stratum'].get('entities'), relevant_updates=case['stratum'].get('relevant_updates'),
                              word=case['stratum'].get('word'), legacy_name_group=case['stratum'].get('legacy_name_group'),
                              left=a, right=b)
            key = digest(dimensions)
            if key not in contrasts:
                contrasts[key] = dict(**dimensions, planned_pairs=0, observed_pairs=0,
                                      valid_pairs=0, person_agree=0, both_correct=0,
                                      left_only_correct=0, right_only_correct=0)
            group = contrasts[key]
            group['planned_pairs'] += 1
            if ra is None or rb is None:
                continue
            group['observed_pairs'] += 1
            x, y = ra['score'], rb['score']
            if x['person'] is not None and y['person'] is not None:
                group['valid_pairs'] += 1
                group['person_agree'] += x['person'] == y['person']
            if x['correct'] is not None and y['correct'] is not None:
                group['both_correct'] += x['correct'] and y['correct']
                group['left_only_correct'] += x['correct'] and not y['correct']
                group['right_only_correct'] += y['correct'] and not x['correct']
    return list(contrasts.values())


def analyze(out):
    out = Path(out)
    verified = verify(out)
    summary = read_json(out / 'summary.json')
    corpus = read_json(out / 'corpus.json')
    groups, pairs = {}, defaultdict(list)
    actual_models, providers = set(), set()
    for item, case, receipt in _records(out):
        key = dict(model=item['model'], max_tokens=item['max_tokens'], suite=case['suite'],
                   **{k: case['stratum'][k] for k in DIMENSIONS if k in case['stratum']})
        group_id = digest(key)
        if group_id not in groups:
            groups[group_id] = dict(**key, planned=0, observed=0, scored=0, correct=0, strict_correct=0,
                                   first_correct=0, accepted=0, truncated=0, refusal=0, technical_errors=0,
                                   cost_usd='0', unknown_cost=0, elapsed_seconds=0., families=set(),
                                   chance_sum=0., pairs_total=0, pairs_valid=0, pairs_agree=0)
        group = groups[group_id]
        group['planned'] += 1
        group['families'].add(case['family_id'])
        group['chance_sum'] += 1 / len(case['candidates'])
        if receipt is None:
            continue
        group['observed'] += 1
        group['elapsed_seconds'] += receipt['elapsed_seconds']
        response, score = receipt['response'], receipt['score']
        actual_models.add(str(response['model'] or 'UNKNOWN'))
        providers.add(str(response['provider'] or 'UNKNOWN'))
        if response['cost'] is None:
            group['unknown_cost'] += 1
        else:
            group['cost_usd'] = str(money(group['cost_usd']) + money(response['cost']))
        if score['correct'] is not None:
            group['scored'] += 1
            for field in ('correct', 'strict_correct', 'first_correct'):
                group[field] += int(score[field])
        group['accepted'] += score['status'] == 'accepted'
        group['truncated'] += score['status'] == 'truncated'
        group['refusal'] += score['status'] == 'refusal'
        group['technical_errors'] += response['status'] not in ('stop', 'length', 'refusal')
        pairs[(group_id, case['pair_id'])].append(score['person'])
    for (group_id, _), persons in pairs.items():
        for a, b in combinations(persons, 2):
            group = groups[group_id]
            group['pairs_total'] += 1
            if a is not None and b is not None:
                group['pairs_valid'] += 1
                group['pairs_agree'] += a == b
    for group in groups.values():
        group['families'] = len(group['families'])
        group['accuracy_scored'] = group['correct'] / group['scored'] if group['scored'] else None
        group['coverage'] = group['observed'] / group['planned']
        group['uniform_guess_accuracy'] = group.pop('chance_sum') / group['planned']
    return dict(schema='benchmark-report-v1', execution_kind=summary['execution_kind'],
                status=summary['status'], reason=summary['reason'], **{k: verified[k] for k in ('observed', 'planned', 'manifest_hash')},
                corpus_hash=corpus['hash'], returned_models=sorted(actual_models), returned_providers=sorted(providers),
                groups=list(groups.values()), contrasts=_contrasts(_records(out)), limitations=corpus['limitations'] + [
                    'Descriptive discovery results; no independence assumption or significance claim.',
                    'Accuracy denominator excludes technical failures/refusals; coverage and counts accompany it.',
                    'Model/provider IDs are API claims; weights, tokenizer and native chat template are not verified.',
                    'COMPLETE denotes technical execution only. Fixture scores are not model evidence.'])


def compare(paths):
    reports = [analyze(path) for path in paths]
    if len(reports) < 2:
        raise ValueError('comparison requires at least two runs')
    if len({r['corpus_hash'] for r in reports}) != 1:
        raise ValueError('comparison requires identical corpus')
    if len({r['execution_kind'] for r in reports}) != 1:
        raise ValueError('cannot compare fixture and live results')
    configs = [read_json(Path(p) / 'config.json') for p in paths]
    if any(c['max_tokens'] != configs[0]['max_tokens'] for c in configs):
        raise ValueError('comparison requires identical token budgets')
    observations, contracts = {}, {}
    for path, config in zip(paths, configs):
        for model in config['models']:
            key = str(path) + ':' + model['id']
            # Parameters remain visible; unequal reasoning/temp contracts cannot be
            # silently interpreted as a model-only controlled comparison.
            contracts[key] = model.get('parameters', {})
            observations[key] = {}
        for item, case, receipt in _records(Path(path)):
            observations[str(path) + ':' + item['model']][(item['case_id'], item['max_tokens'])] = (case, receipt)
    comparisons = []
    for (a, left), (b, right) in combinations(observations.items(), 2):
        groups = {}
        for key in left.keys() & right.keys():
            case, ra = left[key]
            _, rb = right[key]
            if not ra or not rb or ra['score']['correct'] is None or rb['score']['correct'] is None:
                continue
            dimensions = dict(suite=case['suite'], max_tokens=key[1],
                              **{k: case['stratum'][k] for k in DIMENSIONS if k in case['stratum']})
            group_id = digest(dimensions)
            if group_id not in groups:
                groups[group_id] = dict(**dimensions, paired_scored=0, both_correct=0,
                                        left_only_correct=0, right_only_correct=0, neither_correct=0)
            group = groups[group_id]
            x, y = ra['score']['correct'], rb['score']['correct']
            group['paired_scored'] += 1
            group['both_correct' if x and y else 'left_only_correct' if x else 'right_only_correct' if y else 'neither_correct'] += 1
        comparisons.append(dict(left=a, right=b, equal_parameters=contracts[a] == contracts[b], groups=list(groups.values())))
    return dict(schema='benchmark-comparison-v1', corpus_hash=reports[0]['corpus_hash'], reports=reports,
                paired_case_budget_count=len(read_json(Path(paths[0]) / 'corpus.json')['cases']) * len(configs[0]['max_tokens']),
                comparisons=comparisons, contracts=contracts)


def export_report(report, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    write_new(out / 'report.json', report)
    if 'groups' not in report:
        (out / 'REPORT.md').write_text('# Paired benchmark comparison\n\nSee report.json for suite-level paired counts and explicit parameter contracts.\n', encoding='utf-8')
        return
    groups = report['groups']
    columns = list(dict.fromkeys(k for group in groups for k in group))
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns)
    writer.writeheader()
    writer.writerows(groups)
    (out / 'groups.csv').write_text(buffer.getvalue(), encoding='utf-8')
    lines = ['# Functional API benchmark', '', f"Execution: **{report['execution_kind']} / {report['status']}**. Coverage: {report['observed']}/{report['planned']}.",
             '', 'Fixture results test infrastructure only.' if report['execution_kind'] == 'offline_fixture' else 'Descriptive discovery results; no independent holdout.',
             '', '| Model | Suite | Budget | Condition | k | Observed/planned | Correct/scored | Truncated |',
             '|---|---|---:|---|---:|---:|---:|---:|']
    for g in groups:
        lines.append(f"| {g['model']} | {g['suite']} | {g['max_tokens']} | {g.get('condition')} | {g.get('k_total')} | {g['observed']}/{g['planned']} | {g['correct']}/{g['scored']} | {g['truncated']} |")
    lines += ['', '## Limits', ''] + ['- ' + text for text in report['limitations']]
    (out / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
