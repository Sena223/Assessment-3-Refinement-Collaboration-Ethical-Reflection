#!/usr/bin/env python3
"""Summarise a bias-test results CSV (from run_batch.py) into a readable Markdown table.

python3 summarise_bias.py batches/results_bias_tests.csv > bias_summary.md

For each variant: per-criterion scores across repeats, total score (mean, SD, range), routes, attempts
and flags. Differences between paired variants are compared against the run-to-run variation of the
baseline, so acceptable variation can be told apart from a systematic difference (Week 11; rubric C2).
"""
import csv, statistics as st, sys, collections

rows = list(csv.DictReader(open(sys.argv[1])))
by = collections.OrderedDict()
for r in rows:
    by.setdefault((r['case_id'], r['variant']), []).append(r)

def scores(r):
    return {kv.split('=')[0]: int(kv.split('=')[1]) for kv in r['scores'].split() if '=' in kv}

print(f"# Bias test summary\n\nSource: `{sys.argv[1].split('/')[-1]}` · {len(rows)} runs · platform: {rows[0]['platform']} · "
      f"screener {rows[0]['screening_model']} · reviewer {rows[0]['reviewer_model']} · retrieval: {rows[0]['retrieval_effective']} · "
      f"redaction: {'on' if rows[0]['redaction'] == 'True' else 'off'} · generated {min(r['generated_at'] for r in rows)[:10]}\n")
crit = sorted({k for r in rows for k in scores(r)}, key=lambda k: (k[0] != 'E', k))
print('## Per variant\n')
print('| Case | Variant | n | ' + ' | '.join(crit) + ' | Total mean (SD) | Total range | Routes | Attempts | Flags |')
print('|' + '---|' * (len(crit) + 8))
stats = {}
for (case, var), rs in by.items():
    sc = [scores(r) for r in rs]
    tot = [sum(s.values()) for s in sc]
    stats[(case, var)] = tot
    cols = [' '.join(str(s.get(k, '–')) for s in sc) for k in crit]
    routes = collections.Counter(r['route'] for r in rs)
    flags = collections.Counter(f.strip() for r in rs for f in r['flags'].split('|') if f.strip())
    sd = st.stdev(tot) if len(tot) > 1 else 0
    print(f"| {case} | {var} | {len(rs)} | " + ' | '.join(cols) +
          f" | {st.mean(tot):.1f} ({sd:.2f}) | {min(tot)}–{max(tot)} | " + ', '.join(f'{k}×{v}' for k, v in routes.items()) +
          f" | {' '.join(r['attempts'] for r in rs)} | " + (', '.join(f'{k}×{v}' for k, v in flags.items()) or '–') + ' |')
print('\nCriterion cells list the score from each repeat in run order. Execution IDs and log files are in the results CSV.\n')
keys = list(by)
if len(keys) >= 2:
    print('## Paired comparisons\n')
    base = stats[keys[0]]; base_sd = st.stdev(base) if len(base) > 1 else 0
    for a, b in [(keys[0], keys[1])] + ([(keys[3], keys[2])] if len(keys) >= 4 else []):
        d = st.mean(stats[b]) - st.mean(stats[a])
        print(f"- **{b[1]} vs {a[1]}:** mean total {st.mean(stats[b]):.1f} vs {st.mean(stats[a]):.1f} (difference {d:+.1f}); "
              f"baseline run-to-run SD {base_sd:.2f}. Routes: {dict(collections.Counter(r['route'] for r in by[b]))} vs {dict(collections.Counter(r['route'] for r in by[a]))}.")
    print('\nA difference that is small relative to the baseline SD, with matching routes, is consistent with ordinary run-to-run variation; '
          'a difference that is large relative to it, or a change in route, needs explaining.')
