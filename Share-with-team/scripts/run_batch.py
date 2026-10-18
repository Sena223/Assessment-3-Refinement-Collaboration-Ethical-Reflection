#!/usr/bin/env python3
"""Run a batch of screening cases through the A3 n8n workflow and summarise the results.

Usage:
    python3 run_batch.py batches/example_batch.csv

Each CSV row is one test case. `repeats` runs the same row several times (use 5 for bias tests
and the run-to-run baseline). For every run the workflow writes a full JSON log (platform, models,
date, execution ID, every attempt, retrieved chunks, route). This script then writes
results_<batch>.csv with one line per run, for Appendix B (test cases) and Appendix C (bias tests).

Requirements: n8n installed and on PATH (or set N8N_BIN to its folder), both A3 workflows
imported, the tool workflow published, and the data folder in place (see README.md).
"""
import csv, json, os, subprocess, sys, time, glob

DATA_DIR = os.environ.get('A3_DATA_DIR', os.path.expanduser('~/.n8n-files/a3'))
WORKFLOW_ID = os.environ.get('A3_WORKFLOW_ID', 'A3ResumeScreen01')
N8N_BIN = os.environ.get('N8N_BIN', '')
CONFIG = os.path.join(DATA_DIR, 'config', 'run-config.json')
LOGS = os.path.join(DATA_DIR, 'logs')
FIELDS = ['run_label', 'case_id', 'variant', 'job_file', 'resume_file', 'retrieval_mode', 'redact_identifiers', 'max_attempts', 'top_k']


def env():
    e = dict(os.environ)
    if N8N_BIN:
        e['PATH'] = N8N_BIN + os.pathsep + e['PATH']
    e.setdefault('N8N_RUNNERS_BROKER_PORT', '5689')   # avoids clashing with an open n8n editor
    return e


def run_once(cfg):
    with open(CONFIG, 'w') as f:
        json.dump(cfg, f, indent=2)
    before = set(glob.glob(os.path.join(LOGS, '*.json')))
    t0 = time.time()
    p = subprocess.run(['n8n', 'execute', '--id', WORKFLOW_ID, '--rawOutput'],
                       capture_output=True, text=True, env=env(), timeout=1200)
    secs = round(time.time() - t0)
    new = sorted(set(glob.glob(os.path.join(LOGS, '*.json'))) - before, key=os.path.getmtime)
    if not new:
        tail = (p.stdout + p.stderr)[-1500:]
        return None, secs, tail
    with open(new[-1]) as f:
        d = json.load(f)
    rec = (d[0] if isinstance(d, list) else d).get('record', d)
    return (rec, new[-1]), secs, ''


def summarise(rec, path, secs):
    final, gate, run = rec['final'], rec['gate'], rec['run']
    hist = rec.get('history', [])
    calls = [t for h in hist for t in h.get('tool_calls', [])]
    row = {
        'execution_id': rec['label']['execution_id'], 'generated_at': rec['label']['generated_at'],
        'platform': rec['label']['platform'], 'screening_model': rec['label']['screening_model'],
        'reviewer_model': rec['label']['reviewer_model'], 'retrieval_effective': run.get('retrieval_effective'),
        'redaction': run.get('redact_identifiers'), 'case_id': run.get('case_id'), 'variant': run.get('variant'),
        'repeat': run.get('repeat'), 'attempts': rec.get('attempts'), 'route': gate.get('route'),
        'base_outcome': gate.get('base_outcome'), 'confidence': final.get('confidence'),
        'agent_recommendation': final.get('overall_recommendation'),
        'scores': ' '.join(f"{s['id']}={s['score']}" for s in final.get('scores', [])),
        'total_score': sum(s['score'] for s in final.get('scores', []) if isinstance(s.get('score'), int)),
        'flags': ' | '.join(f"{f.get('type')}" for f in final.get('flags', [])),
        'searches': len(calls), 'tools_used': ' '.join(sorted({t['tool'] for t in calls})),
        'chunks_retrieved': ' '.join(sorted({c for t in calls for c in t.get('chunk_ids', [])})),
        'reviewer_verdicts': ' '.join(h['reviewer']['verdict'] for h in hist),
        'route_reasons': ' || '.join(gate.get('reasons', []))[:1500],
        'seconds': secs, 'log_file': os.path.basename(path),
    }
    return row


def main(batch_csv):
    with open(batch_csv, newline='') as f:
        rows = [r for r in csv.DictReader(f) if any(v.strip() for v in r.values())]
    out_path = os.path.join(os.path.dirname(os.path.abspath(batch_csv)),
                            'results_' + os.path.splitext(os.path.basename(batch_csv))[0] + '.csv')
    results, failures = [], []
    total = sum(int(r.get('repeats') or 1) for r in rows)
    n = 0
    for r in rows:
        for rep in range(1, int(r.get('repeats') or 1) + 1):
            n += 1
            cfg = {k: r[k] for k in FIELDS if r.get(k, '').strip() != ''}
            cfg['repeat'] = rep
            cfg['redact_identifiers'] = str(cfg.get('redact_identifiers', 'true')).lower() != 'false'
            cfg['max_attempts'] = int(cfg.get('max_attempts', 3))
            cfg['top_k'] = int(cfg.get('top_k', 4))
            print(f"[{n}/{total}] {cfg.get('case_id')} {cfg.get('variant')} repeat {rep} ...", end=' ', flush=True)
            res, secs, err = run_once(cfg)
            if not res:
                print(f'FAILED ({secs}s)')
                failures.append({'case': cfg.get('case_id'), 'variant': cfg.get('variant'), 'repeat': rep, 'error': err})
                continue
            row = summarise(res[0], res[1], secs)
            results.append(row)
            print(f"{row['route']}  scores {row['scores']}  ({secs}s, exec {row['execution_id']})")
            with open(out_path, 'w', newline='') as f:   # rewrite after every run so nothing is lost
                w = csv.DictWriter(f, fieldnames=list(row.keys()))
                w.writeheader(); w.writerows(results)
    print(f'\n{len(results)} runs written to {out_path}')
    if failures:
        print(f'{len(failures)} failed runs:')
        for x in failures:
            print(' -', x['case'], x['variant'], x['repeat'], x['error'][-300:].replace('\n', ' '))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
