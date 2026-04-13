from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import importlib.util, sys

spec = importlib.util.spec_from_file_location('llm_abstraction', '/home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me/poc/scrum-8-llm-quality/llm_abstraction.py')
module = importlib.util.module_from_spec(spec)
sys.modules['llm_abstraction'] = module
spec.loader.exec_module(module)
build_adapter = module.build_adapter
ModelConfig = module.ModelConfig

BASE = Path('/home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me/poc/scrum-17-prompt-quality')
RAW = BASE / 'raw_outputs'
RAW.mkdir(parents=True, exist_ok=True)

GROWTH_TOPICS = [
    'building an emergency fund',
    'salary negotiation',
    'managing family finances across US and India',
]
KNOWLEDGE_TOPICS = ['history', 'science', 'economics']
FUN_TOPICS = ['set-1', 'set-2', 'set-3']

GROWTH_PROMPT = '''You are writing the Growth section for a morning newspaper for a reader balancing life between the US and India. Return JSON only with schema:
{
  "section": "Growth",
  "title": string,
  "hook": string,
  "advice": [string],
  "resources": [{"label": string, "url": string}],
  "why_it_matters": string
}
Rules:
- Be practical, specific, and culturally aware.
- Avoid generic motivational fluff.
- advice must have exactly 4 items.
- resources must have exactly 2 items and should look like real links.
- why_it_matters should be 1 to 2 sentences.
- Output valid parseable JSON only.
'''

KNOWLEDGE_PROMPT = '''You are writing the Knowledge section for a morning newspaper. Return JSON only with schema:
{
  "section": "Knowledge",
  "title": string,
  "surprising_fact": string,
  "explanation": string,
  "takeaways": [string]
}
Rules:
- Make it engaging, not textbook-dry.
- surprising_fact should feel memorable.
- explanation should be 2 short paragraphs worth of content in one string.
- takeaways must have exactly 3 items.
- Output valid parseable JSON only.
'''

FUN_PROMPT = '''You are writing the Fun and Puzzles section for a morning newspaper. Return JSON only with schema:
{
  "section": "Fun",
  "riddle": {"question": string, "answer": string},
  "logic_puzzle": {"question": string, "answer": string},
  "sudoku": {"grid": [[int,int,int,int,int,int,int,int,int],[int,int,int,int,int,int,int,int,int],[int,int,int,int,int,int,int,int,int],[int,int,int,int,int,int,int,int,int],[int,int,int,int,int,int,int,int,int],[int,int,int,int,int,int,int,int,int],[int,int,int,int,int,int,int,int,int],[int,int,int,int,int,int,int,int,int],[int,int,int,int,int,int,int,int,int]]},
  "chess_puzzle": {"fen": string, "task": string}
}
Rules:
- Sudoku grid uses 0 for blanks.
- Try to make the sudoku valid and solvable.
- Chess FEN should try to be legal.
- Logic puzzle should have a clear single answer.
- Output valid parseable JSON only.
'''


def run_one(adapter: Any, system_prompt: str, user_content: str, out_path: Path) -> dict[str, Any]:
    result = adapter.generate_json(system_prompt, user_content)
    out_path.write_text(json.dumps(result, indent=2))
    return result


def main() -> None:
    adapter = build_adapter(ModelConfig())
    manifest = {"growth": [], "knowledge": [], "fun": []}

    for i, topic in enumerate(GROWTH_TOPICS, start=1):
        out = RAW / f'growth-{i}.json'
        run_one(adapter, GROWTH_PROMPT, f'Topic: {topic}', out)
        manifest['growth'].append(str(out))

    for i, topic in enumerate(KNOWLEDGE_TOPICS, start=1):
        out = RAW / f'knowledge-{i}.json'
        run_one(adapter, KNOWLEDGE_PROMPT, f'Category: {topic}', out)
        manifest['knowledge'].append(str(out))

    for i, topic in enumerate(FUN_TOPICS, start=1):
        out = RAW / f'fun-{i}.json'
        run_one(adapter, FUN_PROMPT, f'Puzzle set id: {topic}', out)
        manifest['fun'].append(str(out))

    (BASE / 'manifest.json').write_text(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
