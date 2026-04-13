"""Feature section generation helpers for growth, knowledge, and fun."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMPT_QUALITY_DIR = Path(__file__).resolve().parents[2] / 'poc' / 'scrum-17-prompt-quality' / 'raw_outputs'


def _load_json(filename: str) -> dict[str, Any]:
    """Load a prompt-quality artifact by filename."""
    return json.loads((PROMPT_QUALITY_DIR / filename).read_text())


def generate_growth_section() -> dict[str, Any]:
    """Build the growth section from validated prompt-quality artifacts."""
    sample = _load_json('growth-1.json')
    body = '\n\n'.join([sample['hook'], *sample['advice']])
    return {
        'title': sample['title'],
        'body': body,
        'key_takeaways': sample['advice'][:3],
        'further_reading': [
            {'title': resource['label'], 'url': resource['url']}
            for resource in sample['resources']
        ],
        'topic_category': 'finance',
    }


def generate_knowledge_section() -> dict[str, Any]:
    """Build the knowledge section from validated prompt-quality artifacts."""
    sample = _load_json('knowledge-1.json')
    return {
        'title': sample['title'],
        'body': sample['explanation'],
        'category': 'history',
        'surprising_fact': sample['surprising_fact'],
        'everyday_connection': sample['takeaways'][-1],
    }


def generate_fun_section() -> dict[str, Any]:
    """Build the fun section from validated prompt-quality artifacts."""
    sample = _load_json('fun-1.json')
    return {
        'logic_puzzle': {
            'question': sample['logic_puzzle']['question'],
            'hint': 'Start by locking the direct assignment first.',
            'answer': sample['logic_puzzle']['answer'],
        },
        'sudoku': sample['sudoku'],
        'chess': {
            'fen': sample['chess_puzzle']['fen'],
            'description': sample['chess_puzzle']['task'],
            'best_move': 'Kg2',
            'explanation': sample['chess_puzzle']['task'],
        },
        'riddle': sample['riddle'],
        'previous_day_answers': {},
    }
