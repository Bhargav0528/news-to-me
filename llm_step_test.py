#!/usr/bin/env python3
import os, sys, time, json

os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'
os.environ['OPENROUTER_MODEL'] = 'minimax/minimax-m2.7'
os.environ['OPENROUTER_BASE_URL'] = 'https://openrouter.ai/api/v1'
sys.path.insert(0, os.getcwd())

# Force unbuffered
import sys
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

log = open('/tmp/llm_log.txt', 'w', buffering=1)
def L(msg):
    log.write(msg + '\n')
    log.flush()

L('BEGIN')
t0 = time.time()

from pipeline.generators.engine import build_adapter, ModelConfig
L('engine imported')
adapter = build_adapter(ModelConfig())
L('adapter built')

L('1: simple generate')
r = adapter.generate_json('Return valid JSON only.', 'Return JSON with x=1')
L(f'result={r}')

L('2: growth')
from pipeline.generators.feature_sections import generate_growth_section
g = generate_growth_section()
L(f'growth title={g.get("title","MISSING")[:80]}')

L('3: knowledge')
from pipeline.generators.feature_sections import generate_knowledge_section
k = generate_knowledge_section()
L(f'knowledge title={k.get("title","MISSING")[:80]}')

L('4: fun')
from pipeline.generators.feature_sections import generate_fun_section
f = generate_fun_section()
L(f'fun puzzle={f.get("logic_puzzle",{}).get("question","MISSING")[:60]}')
L(f'sudoku rows={len(f.get("sudoku",{}).get("grid",[]))}')
L(f'chess={f.get("chess",{}).get("best_move","MISSING")}')

L('5: news sections')
from pipeline.generators.news import generate_news_sections
import sqlite3
conn = sqlite3.connect('data/news_to_me.db')
conn.row_factory = sqlite3.Row
ns = generate_news_sections(conn, adapter)
L(f'news regions: {list(ns.keys())}')

L('6: tldr')
from pipeline.generators.tldr import generate_tldr
t = generate_tldr(ns, adapter)
L(f'tldr count={len(t)}')

L('7: biztech')
from pipeline.generators.biztech import generate_biztech
b = generate_biztech(conn, adapter)
L(f'biztech articles={len(b.get("articles",[]))}')
conn.close()

elapsed = time.time() - t0
L(f'DONE total={elapsed:.1f}s')
log.close()