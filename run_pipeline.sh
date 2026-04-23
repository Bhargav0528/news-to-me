#!/usr/bin/env python3
"""Run full pipeline assembly with LLM generation."""
import os, sys, json, time

os.environ.setdefault('LLM_PROVIDER', 'openrouter')
os.environ.setdefault('OPENROUTER_API_KEY', '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')
os.environ.setdefault('OPENROUTER_MODEL', 'minimax/minimax-m2.7')
os.environ.setdefault('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')

sys.path.insert(0, os.getcwd())

print("Starting assembly...", flush=True)
t0 = time.time()
from pipeline.generators.assembler import EditionAssembler
assembler = EditionAssembler()
edition = assembler.assemble()
elapsed = time.time() - t0

print(f"Total: {elapsed:.1f}s", flush=True)
print("Sections: " + str(list(edition.keys())), flush=True)
for region, articles in edition.get("news", {}).items():
    print(f"  {region}: {len(articles)} articles", flush=True)
print("TLDR: " + str(len(edition.get("tldr", []))), flush=True)
print("Growth: " + edition.get("growth", {}).get("title", "MISSING")[:80], flush=True)
print("Knowledge: " + edition.get("knowledge", {}).get("title", "MISSING")[:80], flush=True)
print("Fun keys: " + str(list(edition.get("fun", {}).keys())), flush=True)
print("Sudoku rows: " + str(len(edition.get("fun", {}).get("sudoku", {}).get("grid", []))), flush=True)
print("Chess: " + edition.get("fun", {}).get("chess", {}).get("best_move", "MISSING"), flush=True)
print("ALL DONE", flush=True)