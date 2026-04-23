#!/usr/bin/env python3
import json, os, sys, time

os.environ.setdefault("LLM_PROVIDER", "openrouter")
os.environ.setdefault("OPENROUTER_API_KEY", "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")
os.environ.setdefault("OPENROUTER_MODEL", "minimax/minimax-m2.7")
os.environ.setdefault("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

print("PATH check:", sys.path[:3])
sys.path.insert(0, os.getcwd())

print("Importing engine...")
t0 = time.time()
from pipeline.generators.engine import build_adapter, ModelConfig
print(f"Engine imported in {time.time()-t0:.1f}s")

print("Building adapter...")
t0 = time.time()
adapter = build_adapter(ModelConfig())
print(f"Adapter built in {time.time()-t0:.1f}s")

print("Testing simple generate...")
t0 = time.time()
r = adapter.generate_json("Return valid JSON only.", "Return JSON with x=1")
print(f"Generated in {time.time()-t0:.1f}s: {r}")

print("Importing feature_sections...")
t0 = time.time()
from pipeline.generators.feature_sections import generate_growth_section
print(f"feature_sections imported in {time.time()-t0:.1f}s")

print("Generating growth...")
t0 = time.time()
growth = generate_growth_section()
print(f"Growth generated in {time.time()-t0:.1f}s")
print(f"  title: {growth.get('title', 'MISSING')[:80]}")
print(f"  body: {len(growth.get('body', ''))} chars")
print(f"  topic: {growth.get('topic_category', 'MISSING')}")

print("ALL DONE")