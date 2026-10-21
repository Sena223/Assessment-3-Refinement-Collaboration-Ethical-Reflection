#!/usr/bin/env python3
"""Turn run logs into a readable Markdown file (for Appendix B / C). Each run is labelled with platform, date and context.

python3 logs_to_markdown.py <results.csv> <logs dir> > outputs.md
Runs appear in the order of the results CSV.
"""
import csv, json, os, sys

rows = list(csv.DictReader(open(sys.argv[1])))
print('# Full workflow outputs\n')
for r in rows:
    d = json.load(open(os.path.join(sys.argv[2], r['log_file'])))
    rec = (d[0] if isinstance(d, list) else d)['record']
    lab, run, fin, gate = rec['label'], rec['run'], rec['final'], rec['gate']
    print(f"## {run['case_id']} · {run['variant']} · repeat {run['repeat']}\n")
    print(f"- **Platform:** {lab['platform']} · screener `{lab['screening_model']}` · reviewer `{lab['reviewer_model']}`" + (f" · embeddings `{lab['embedding_model']}`" if lab.get('embedding_model') else ''))
    print(f"- **Generated:** {lab['generated_at']} · n8n execution {lab['execution_id']} · {lab['workflow']}")
    print(f"- **Context:** {lab['context']} · job `{run['job_file']}` · resume `{run['resume_file']}`")
    print(f"- **Route:** **{gate['route']}** (scores alone imply {gate['base_outcome']}) · attempts: {rec['attempts']}")
    if gate['reasons']:
        print('- **Reasons for the route:**')
        for x in gate['reasons']: print('  - ' + x.replace('\n', ' '))
    print(f"- **Job-ad check:** excluded {[x['id'] for x in rec['job_check']['excluded']] or 'none'}; to confirm {[x['id'] for x in rec['job_check']['review']] or 'none'}")
    print(f"- **Privacy step:** redaction {'on' if rec['redaction']['applied'] else 'off'} {rec['redaction']['fields'] or ''}; policy triggers {rec.get('policy_triggers') or 'none'}; injection suspected: {rec['injection_suspected']}\n")
    print('**Attempts (agentic trace)**\n')
    for h in rec['history']:
        searches = '; '.join(f"{t['tool']}(\"{t['query'][:70]}\") → {', '.join(t['chunk_ids']) or 'no chunks'}" for t in h['tool_calls']) or 'no searches'
        print(f"- Attempt {h['attempt']}: {searches}")
        if h['automated_issues']: print('  - Automated checks: ' + '; '.join(f"{i['code']} ({i['detail'][:90]})" for i in h['automated_issues']))
        print(f"  - Reviewer: **{h['reviewer']['verdict']}**" + (f": {h['reviewer']['critique'][:400]}" if h['reviewer'].get('critique') else ''))
    out = rec['history'][-1]['output']
    print('\n**Final screening output**\n')
    print('| Criterion | Score | Evidence quote | Rationale | KB refs |\n|---|---|---|---|---|')
    for k in out.get('criteria', []):
        q = str(k.get('evidence_quote', '')).replace('\n', ' / ').replace('|', '/')
        print(f"| {k.get('id')} | {k.get('score')} | {q} | {str(k.get('rationale','')).replace('|','/')} | {', '.join(k.get('kb_refs') or []) or '–'} |")
    if fin.get('flags'):
        print('\nFlags: ' + '; '.join(f"{f.get('type')}: {f.get('detail')}" + (f" ({', '.join(f.get('kb_refs') or [])})" if f.get('kb_refs') else '') for f in fin['flags']))
    print(f"\nRecommendation: {fin.get('overall_recommendation')} · confidence {fin.get('confidence')}\n\nSummary: {fin.get('summary')}\n\n---\n")
