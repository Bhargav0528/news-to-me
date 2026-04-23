#!/usr/bin/env python3
"""Test LLM generation - write output to file."""
import os, sys, time

os.environ.setdefault('LLM_PROVIDER', 'openrouter')
os.environ.setdefault('OPENROUTER_API_KEY', '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')
os.environ.setdefault('OPENROUTER_MODEL', 'minimax/minimax-m2.7')
os.environ.setdefault('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')

sys.path.insert(0, os.getcwd())
log = open('/tmp/llm_test_log.txt', 'w')

def log_print(msg):
    log.write(msg + '\n')
    log.flush()

log_print('Starting...')

t0 = time.time()
from pipeline.generators.engine import build_adapter, ModelConfig
adapter = build_adapter(ModelConfig())
log_print(f'Adapter built in {time.time()-t0:.1f}s')

log_print('Test 1: simple generation')
t0 = time.time()
r = adapter.generate_json('Return valid JSON only.', 'Return JSON with x=1')
log_print(f'  Result: {r} in {time.time()-t0:.1f}s')

log_print('Test 2: growth section')
from pipeline.generators.feature_sections import generate_growth_section
t0 = time.time()
g = generate_growth_section()
log_print(f'  Title: {g.get("title","MISSING")[:80]} in {time.time()-t0:.1f}s')

log_print('Test 3: knowledge section')
from pipeline.generators.feature_sections import generate_knowledge_section
t0 = time.time()
k = generate_knowledge_section()
log_print(f'  Title: {k.get("title","MISSING")[:80]} in {time.time()-t0:.1f}s')

log_print('Test 4: fun section')
from pipeline.generators.feature_sections import generate_fun_section
t0 = time.time()
f = generate_fun_section()
log_print(f'  Puzzle: {f.get("logic_puzzle",{}).get("question","MISSING")[:60]} in {time.time()-t0:.1f}s')
log_print(f'  Sudoku: {len(f.get("sudoku",{}).get("grid",[]))} rows')
log_print(f'  Chess: {f.get("chess",{}).get("best_move","MISSING")}')

log_print('ALL DONE in total ' + str(time.time() - t0) + 's')
log.close()