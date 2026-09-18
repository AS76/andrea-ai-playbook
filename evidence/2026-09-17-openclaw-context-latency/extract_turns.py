#!/usr/bin/env python3
"""Finite, read-only extraction of persisted Cleo model turns. No network or service calls."""
import csv
import datetime as dt
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

START = dt.datetime(2026, 9, 15, 16, 14, 20, tzinfo=dt.timezone.utc)
END = dt.datetime(2026, 9, 17, 16, 14, 20, tzinfo=dt.timezone.utc)
DB = Path('/root/.openclaw/agents/cleo/agent/openclaw-agent.sqlite')
OUT = Path(__file__).resolve().parent
MS = lambda t: int(t.timestamp() * 1000)
ISO = lambda n: dt.datetime.fromtimestamp(n / 1000, dt.timezone.utc).isoformat(timespec='milliseconds')
ANON = lambda s: hashlib.sha256(s.encode()).hexdigest()[:12]

def main():
    db = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    windows = {r['session_id']: r for r in db.execute('SELECT session_id, session_key, created_at, updated_at, channel FROM session_windows')}
    runs = defaultdict(list)
    for r in db.execute('SELECT session_id, seq, event_json, created_at FROM trajectory_runtime_events WHERE created_at >= ? AND created_at < ? ORDER BY session_id, created_at', (MS(START)-86400000, MS(END))):
        e = json.loads(r['event_json']); typ = e.get('type'); rid = e.get('runId')
        if not rid or typ not in ('session.started', 'session.ended', 'context.compiled', 'model.completed', 'tool.call'):
            continue
        if not runs[r['session_id']] or runs[r['session_id']][-1]['id'] != rid:
            runs[r['session_id']].append({'id': rid, 'start': None, 'end': None, 'system_chars': None, 'tool_calls': 0, 'compactions': None, 'errors': False, 'context_seq': None})
        x = runs[r['session_id']][-1]; d = e.get('data') or {}
        if typ == 'session.started': x['start'] = r['created_at']
        elif typ == 'session.ended': x['end'] = r['created_at']; x['errors'] = d.get('status') not in ('completed', 'success', None)
        elif typ == 'context.compiled':
            sp = d.get('systemPrompt'); x['system_chars'] = sp.get('originalChars') if isinstance(sp, dict) else len(sp) if isinstance(sp, str) else None
            x['context_seq'] = r['seq']
        elif typ == 'tool.call': x['tool_calls'] += 1
        elif typ == 'model.completed': x['compactions'] = d.get('compactionCount')
    fields = ['timestamp_utc','timestamp_europe_rome','session_anon','session_kind','transcript_seq','run_anon','provider','requested_model','response_model','input_tokens_reported','cache_read_tokens','cache_write_tokens','prompt_tokens_derived','uncached_input_tokens_derived','output_tokens','total_tokens_reported','recorded_cost_usd','request_payload_bytes','provider_latency_ms','first_response_ms','model_turn_interval_upper_bound_ms','run_total_duration_ms','assistant_tool_call_count','run_tool_call_count','memory_retrieval_tool_count','run_compaction_count','run_error','failover_model_changed_in_run','system_prompt_chars_run','bootstrap_context_chars_report','tool_schema_chars_report','skill_metadata_chars_report','conversation_chars','retrieved_memory_chars','hook_runtime_context_chars_report','context_report_source','source_event_seq']
    summary = {'window_start_utc': START.isoformat(), 'window_end_utc': END.isoformat(), 'turns': 0, 'sessions': 0, 'by_session_kind': Counter(), 'by_response_model': Counter(), 'prompt_tokens_sum': 0, 'input_tokens_reported_sum': 0, 'cache_read_sum': 0, 'cache_write_sum': 0, 'output_tokens_sum': 0, 'cost_sum_usd': 0.0, 'prompt_token_values': [], 'session_turns': Counter(), 'session_prompt_tokens': Counter(), 'report_rows': 0, 'run_count': 0, 'run_durations_ms': [], 'tool_calls': 0, 'memory_tool_calls': 0, 'compaction_runs': 0, 'target': {}}
    rows = []
    prev_at = {}; prev_model = {}; session_set = set(); run_set = set()
    for r in db.execute('SELECT session_id, seq, event_json, created_at FROM transcript_events WHERE created_at >= ? AND created_at < ? ORDER BY session_id, seq', (MS(START), MS(END))):
        e = json.loads(r['event_json'])
        if e.get('type') != 'message': continue
        m = e.get('message') or {}; sid = r['session_id']; at = r['created_at']; role = m.get('role')
        if role != 'assistant' or not isinstance(m.get('usage'), dict):
            prev_at[sid] = at
            continue
        usage = m['usage']; w = windows.get(sid); key = (w['session_key'] if w else '') or ''
        kind = 'telegram_dm' if ':telegram:direct:' in key and ':heartbeat' not in key else 'heartbeat' if ':heartbeat' in key else 'other'
        run = next((x for x in reversed(runs.get(sid, [])) if x['start'] is not None and x['start'] <= at and (x['end'] is None or at <= x['end'] + 2000)), None)
        rid = run['id'] if run else None
        report = None
        # Only the last persisted report for a session survives. Match its generation to this run.
        if w:
            pass
        session_set.add(sid)
        if rid: run_set.add((sid, rid))
        content = m.get('content') or []
        tool_names = [v.get('name') for v in content if isinstance(v, dict) and v.get('type') in ('toolCall', 'tool_use')]
        memcount = sum(1 for v in content if isinstance(v, dict) and v.get('type') in ('toolCall', 'tool_use') and any(s in str((v.get('arguments') or {}).get('id') if v.get('name') == 'tool_call' else v.get('name')).lower() for s in ('memory_search','memory_get','clawmem','vault_search','memory_retrieve')))
        inp = usage.get('input'); cr = usage.get('cacheRead'); cw = usage.get('cacheWrite'); out = usage.get('output')
        prompt = sum(v for v in (inp, cr, cw) if isinstance(v, (int,float))) if any(isinstance(v,(int,float)) for v in (inp,cr,cw)) else None
        model = m.get('responseModel') or ''
        changed = bool(rid and (sid,rid) in prev_model and prev_model[(sid,rid)] != model)
        if rid: prev_model[(sid,rid)] = model
        cost = (usage.get('cost') or {}).get('total')
        row = {'timestamp_utc': ISO(at), 'timestamp_europe_rome': dt.datetime.fromtimestamp(at/1000,dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=2))).isoformat(timespec='milliseconds'), 'session_anon': ANON(sid), 'session_kind': kind, 'transcript_seq': r['seq'], 'run_anon': ANON(rid) if rid else 'UNKNOWN', 'provider': m.get('provider') or 'UNKNOWN', 'requested_model': m.get('model') or 'UNKNOWN', 'response_model': model or 'UNKNOWN', 'input_tokens_reported': inp, 'cache_read_tokens': cr, 'cache_write_tokens': cw, 'prompt_tokens_derived': prompt, 'uncached_input_tokens_derived': inp, 'output_tokens': out, 'total_tokens_reported': usage.get('totalTokens'), 'recorded_cost_usd': cost, 'request_payload_bytes': 'UNKNOWN', 'provider_latency_ms': 'UNKNOWN', 'first_response_ms': 'UNKNOWN', 'model_turn_interval_upper_bound_ms': at - prev_at[sid] if sid in prev_at else '', 'run_total_duration_ms': (run['end']-run['start']) if run and run['end'] and run['start'] else '', 'assistant_tool_call_count': len(tool_names), 'run_tool_call_count': run['tool_calls'] if run else '', 'memory_retrieval_tool_count': memcount, 'run_compaction_count': run['compactions'] if run else '', 'run_error': run['errors'] if run else 'UNKNOWN', 'failover_model_changed_in_run': changed, 'system_prompt_chars_run': run['system_chars'] if run else '', 'bootstrap_context_chars_report': '', 'tool_schema_chars_report': '', 'skill_metadata_chars_report': '', 'conversation_chars': 'UNKNOWN', 'retrieved_memory_chars': 'UNKNOWN', 'hook_runtime_context_chars_report': '', 'context_report_source': '', 'source_event_seq': r['seq']}
        rows.append(row); prev_at[sid] = at
        summary['turns'] += 1; summary['by_session_kind'][kind] += 1; summary['by_response_model'][model or 'UNKNOWN'] += 1
        summary['session_turns'][ANON(sid)] += 1; summary['session_prompt_tokens'][ANON(sid)] += prompt or 0
        for k,v in [('prompt_tokens_sum',prompt),('input_tokens_reported_sum',inp),('cache_read_sum',cr),('cache_write_sum',cw),('output_tokens_sum',out)]: summary[k] += v or 0
        summary['cost_sum_usd'] += cost or 0; summary['tool_calls'] += len(tool_names); summary['memory_tool_calls'] += memcount
        if prompt is not None: summary['prompt_token_values'].append(prompt)
        if kind == 'telegram_dm' and 1789632116000 <= at <= 1789632219000:
            summary['target'][str(r['seq'])] = {'timestamp_utc': ISO(at), 'prompt_tokens': prompt, 'response_model': model, 'cost_usd': cost, 'tool_calls': len(tool_names)}
    # Persisted latest system-prompt report is added only to rows in its exact run.
    for sid in session_set:
        raw = db.execute('SELECT entry_json FROM session_nodes WHERE current_session_id=?', (sid,)).fetchone()
        if not raw: continue
        try: ent = json.loads(raw[0]); rep = ent.get('systemPromptReport') or {}
        except Exception: continue
        gen = rep.get('generatedAt'); target_run = next((x for x in runs.get(sid,[]) if gen and x['start'] and abs(x['start']-gen)<10000),None)
        if not target_run: continue
        for row in rows:
            if row['session_anon'] != ANON(sid) or row['run_anon'] != ANON(target_run['id']): continue
            row['bootstrap_context_chars_report'] = (rep.get('systemPrompt') or {}).get('projectContextChars','')
            row['tool_schema_chars_report'] = (rep.get('tools') or {}).get('schemaChars','')
            row['skill_metadata_chars_report'] = (rep.get('skills') or {}).get('promptChars','')
            row['hook_runtime_context_chars_report'] = (rep.get('currentTurn') or {}).get('runtimeContextChars','')
            row['context_report_source'] = rep.get('source','')
            summary['report_rows'] += 1
    with (OUT/'openclaw-turn-metrics-48h.csv').open('w', newline='') as f:
        wr=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');wr.writeheader();wr.writerows(sorted(rows, key=lambda row: (row['timestamp_utc'], row['session_anon'], row['transcript_seq'])))
    summary['sessions'] = len(session_set);summary['run_count']=len(run_set)
    summary['by_session_kind']=dict(summary['by_session_kind']);summary['by_response_model']=dict(summary['by_response_model']);summary['session_turns']=dict(summary['session_turns']);summary['session_prompt_tokens']=dict(summary['session_prompt_tokens'])
    p=sorted(summary.pop('prompt_token_values'))
    summary['prompt_tokens_median']=p[len(p)//2] if p else None;summary['prompt_tokens_p90']=p[int(.9*(len(p)-1))] if p else None;summary['prompt_tokens_max']=p[-1] if p else None
    (OUT/'analysis-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('session_turns','session_prompt_tokens','target')},indent=2))

if __name__ == '__main__': main()
