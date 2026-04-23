#!/usr/bin/env python3
"""Run each generator step by step with hard timeouts."""
import os, sys, time, json

os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'
os.environ['OPENROUTER_MODEL'] = 'minimax/minimax-m2.7'
os.environ['OPENROUTER_BASE_URL'] = 'https://openrouter.ai/api/v1'
sys.path.insert(0, os.getcwd())

log = open('/tmp/step_log.txt', 'w', buffering=1)
def L(msg):
    log.write(msg + '\n'); log.flush()
    print(msg, flush=True)

t0_total = time.time()

L("Building adapter...")
from pipeline.generators.engine import build_adapter, ModelConfig
adapter = build_adapter(ModelConfig())

L("1/7: Growth")
t1 = time.time()
from pipeline.generators.feature_sections import generate_growth_section
g = generate_growth_section()
L(f"  Done in {time.time()-t1:.1f}s | {g.get('title','MISSING')[:70]}")

L("2/7: Knowledge")
t1 = time.time()
from pipeline.generators.feature_sections import generate_knowledge_section
k = generate_knowledge_section()
L(f"  Done in {time.time()-t1:.1f}s | {k.get('title','MISSING')[:70]}")

L("3/7: Fun")
t1 = time.time()
from pipeline.generators.feature_sections import generate_fun_section
f = generate_fun_section()
L(f"  Done in {time.time()-t1:.1f}s | puzzle={f.get('logic_puzzle',{}).get('question','MISSING')[:50]}")
L(f"  Sudoku: {len(f.get('sudoku',{}).get('grid',[]))} rows | Chess: {f.get('chess',{}).get('best_move','MISSING')}")

L("4/7: News")
t1 = time.time()
from pipeline.generators.assembler import _prefetch_news_rows
from pipeline.generators.news import generate_news_sections
news_rows = _prefetch_news_rows('data/news_to_me.db')
ns = generate_news_sections(news_rows, adapter)
L(f"  Done in {time.time()-t1:.1f}s")
for region, arts in ns.items():
    L(f"    {region}: {len(arts)} articles")

L("5/7: TLDR")
t1 = time.time()
from pipeline.generators.tldr import generate_tldr
t = generate_tldr(ns, adapter)
L(f"  Done in {time.time()-t1:.1f}s | {len(t)} items")

L("6/7: BizTech")
t1 = time.time()
from pipeline.generators.assembler import _prefetch_biztech_rows
from pipeline.generators.biztech import generate_biztech
biztech_rows, indices = _prefetch_biztech_rows('data/news_to_me.db')
b = generate_biztech(biztech_rows, indices, adapter)
L(f"  Done in {time.time()-t1:.1f}s | {len(b.get('articles',[]))} articles")

L("7/7: Full assembly")
t1 = time.time()
from pipeline.generators.assembler import EditionAssembler
assembler = EditionAssembler()
edition = assembler.assemble()
L(f"  Done in {time.time()-t1:.1f}s")
L(f"  Sections: {list(edition.keys())}")
L(f"  News regions: {list(edition.get('news',{}).keys())}")
L(f"  Growth title: {edition.get('growth',{}).get('title','MISSING')[:80]}")

L(f"ALL DONE in total {time.time()-t0_total:.1f}s")
log.close()