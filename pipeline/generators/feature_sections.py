"""Feature section generation helpers for growth, knowledge, and fun."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.generators.engine import build_adapter, ModelConfig
from pipeline.utils.validation import strip_markdown


def _load_prompt(path: Path) -> str:
    """Load a prompt template file."""
    return path.read_text().strip()


PROMPT_DIR = Path(__file__).resolve().parents[2] / 'pipeline' / 'generators' / 'prompts'


def _growth_fallback() -> dict[str, Any]:
    """Fallback when LLM fails for growth section."""
    import datetime
    categories = ["finance", "career", "relationships", "health", "tax", "communication"]
    day_idx = datetime.date.today().day % len(categories)
    return {
        "title": f"Money habits to build before your next big life change",
        "body": f"Whether you're planning a major purchase, a wedding, or simply want more breathing room in your monthly budget, the habits you build now will determine how smoothly things go.\n\nStart with tracking where every rupee goes — not to judge yourself, but to see patterns you didn't notice. Most people are surprised to find small, consistent leaks that add up to something significant.\n\nThen, before building savings, pay down any high-interest debt. A guaranteed 15-20% return by eliminating debt is better than most investment returns you'll get.\n\nOnce debt is managed, build a simple buffer: one month of essentials. It changes how you sleep.\n\nFinally, automate what you can. Whatever gets deducted before you see it is the easiest savings you'll ever do.",
        "key_takeaways": [
            "Track spending for 30 days before deciding where to cut — data beats guesswork",
            "Pay off high-interest debt before building savings — guaranteed returns win",
            "Automate savings the day you get paid — what you don't see, you don't miss"
        ],
        "further_reading": [
            {"title": "The psychology of money", "url": "https://www.goodreads.com/book/show/5908.The_Psychology_of_Money"}
        ],
        "topic_category": categories[day_idx],
    }


def generate_growth_section(adapter=None) -> dict[str, Any]:
    """Build the growth section via LLM generation."""
    adapter = adapter or build_adapter(ModelConfig())
    prompt = _load_prompt(PROMPT_DIR / 'growth.txt')
    categories = ["finance", "career", "relationships", "health", "tax", "communication"]
    import datetime
    day_idx = datetime.date.today().day % len(categories)
    topic_hint = f"Topic category for today: {categories[day_idx]}."

    user = f"""{topic_hint}

Articles from today's edition:
{json.dumps(_get_recent_article_context())}

Return JSON with:
- title: string, engaging title
- body: plain text (NO markdown), 400-600 words, practical and actionable
- key_takeaways: list of 3 specific takeaways, plain text only
- further_reading: list of 2-3 resources with title and url fields
- topic_category: string
"""
    try:
        result = adapter.generate_json(prompt, user)
        if "key_takeaways" in result and len(result["key_takeaways"]) > 3:
            result["key_takeaways"] = result["key_takeaways"][:3]
        # Sanitize markdown from all text fields
        result["body"] = strip_markdown(result.get("body", ""))
        result["key_takeaways"] = [strip_markdown(k) for k in result.get("key_takeaways", [])]
        return result
    except Exception as exc:
        import logging
        logging.warning(f"Growth section LLM failed ({exc}), using fallback")
        return _growth_fallback()


def _knowledge_fallback() -> dict[str, Any]:
    """Fallback when LLM fails for knowledge section."""
    return {
        "title": "The origin of zero: nothing became everything",
        "body": "Zero seems obvious now. But for most of human history, mathematicians didn't have it. The number zero as we understand it — representing the absence of quantity — was a genuinely radical idea, and it emerged in different places independently.\n\nThe Babylonians used a placeholder for empty columns in their base-60 number system, but they never treated it as a real number. The ancient Greeks debated the concept of 'nothing' philosophically but wouldn't put it in equations.\n\nThe first recorded use of zero as a number — with arithmetic rules — comes from Indian mathematicians around the 5th century CE. Brahmagupta wrote down formal rules for how zero interacts with addition, subtraction, and multiplication. Without zero, negative numbers don't work cleanly. Without negative numbers, algebra gets much harder.\n\nThis spread westward through Arabic mathematicians who preserved and extended Indian work. The word 'algebra' comes from Arabic. Without this transmission, the entire trajectory of science and engineering would look very different.",
        "category": "history",
        "surprising_fact": "Ancient Roman numerals have no zero — and the Roman Empire managed just fine without it for centuries. But their merchants had to use abacuses for any serious calculation.",
        "everyday_connection": "Every time you see a '0' on your phone, check your balance, or encounter any decimal system, you're using a concept that took thousands of years to invent.",
    }


def generate_knowledge_section(adapter=None) -> dict[str, Any]:
    """Build the knowledge section via LLM generation."""
    adapter = adapter or build_adapter(ModelConfig())
    prompt = _load_prompt(PROMPT_DIR / 'knowledge.txt')

    user = f"""Today's top articles:
{json.dumps(_get_recent_article_context())}

Return JSON with:
- title: string, engaging title
- body: plain text (NO markdown), 300-500 words, conversational tone
- category: one of history, science, geography, math, literature, economics, philosophy
- surprising_fact: string, one fact that surprises people, plain text only
- everyday_connection: string, how this connects to daily life, plain text only
"""
    try:
        result = adapter.generate_json(prompt, user)
        result["body"] = strip_markdown(result.get("body", ""))
        result["surprising_fact"] = strip_markdown(result.get("surprising_fact", ""))
        result["everyday_connection"] = strip_markdown(result.get("everyday_connection", ""))
        return result
    except Exception as exc:
        import logging
        logging.warning(f"Knowledge section LLM failed ({exc}), using fallback")
        return _knowledge_fallback()


def _chess_fallback() -> dict[str, str]:
    """Return a hardcoded chess puzzle when Lichess API is unavailable."""
    return {
        "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
        "description": "White to move. Classic scholar's mate setup — can you finish it in one?",
        "best_move": "Bxf7#",
        "explanation": "1. Bxf7# is checkmate: the bishop sacrifices on f7, delivering checkmate. The black king cannot capture the bishop (queen on e8 blocks), cannot move to any safe square, and no other piece can block or capture it.",
    }


def _fun_fallback(sudoku_grid, sudoku_solution, chess_puzzle) -> dict[str, Any]:
    """Fallback when LLM fails for fun section."""
    return {
        "logic_puzzle": {
            "question": "Four people need to cross a bridge at night. They have one flashlight. At most two people can cross at a time, and whoever crosses must carry the flashlight. Person A takes 1 minute, B takes 2 minutes, C takes 5 minutes, D takes 10 minutes. When two cross together, they go at the slower person's pace. What's the fastest time to get all four across?",
            "hint": "Think about who should be paired together, and who should NOT be paired together.",
            "answer": "17 minutes. Send A and B across (2 min), A returns (1 min). Send C and D across (10 min), B returns (2 min). Send A and B across again (2 min). Total: 2+1+10+2+2 = 17 minutes."
        },
        "riddle": {
            "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?",
            "answer": "An echo."
        },
        "sudoku": {"grid": sudoku_grid, "solution": sudoku_solution},
        "chess": chess_puzzle,
        "previous_day_answers": {},
    }


def generate_fun_section(adapter=None) -> dict[str, Any]:
    """Build the fun section via LLM generation."""
    adapter = adapter or build_adapter(ModelConfig())
    prompt_template = _load_prompt(PROMPT_DIR / 'fun.txt')
    import datetime
    prompt = prompt_template.format(date=datetime.date.today().isoformat())

    # Build sudoku using py-sudoku (not LLM)
    sudoku_grid, sudoku_solution = _generate_sudoku()

    # Get chess puzzle from Lichess API (not LLM)
    chess_puzzle = _get_chess_puzzle()

    user = f"""Return JSON with:
- logic_puzzle: {{"question": string, "hint": string, "answer": string}}
  Medium difficulty, 3-5 minute solve, exactly one solution
- riddle: {{"question": string, "answer": string}}
  Short, clever, satisfying answer
- sudoku: use {json.dumps({"grid": sudoku_grid, "solution": sudoku_solution})}
- chess: use {json.dumps(chess_puzzle)}
- previous_day_answers: {{}}

Do NOT generate sudoku or chess yourself. Use the provided data.
"""
    try:
        result = adapter.generate_json(prompt, user)
        result["sudoku"] = {"grid": sudoku_grid, "solution": sudoku_solution}
        result["chess"] = chess_puzzle
        result["previous_day_answers"] = {}
        return result
    except Exception as exc:
        import logging
        logging.warning(f"Fun section LLM failed ({exc}), using fallback")
        return _fun_fallback(sudoku_grid, sudoku_solution, chess_puzzle)


def _get_recent_article_context() -> list[dict[str, str]]:
    """Fetch recent article titles and summaries for LLM context."""
    from pathlib import Path
    import sqlite3
    db_path = Path('data/news_to_me.db')
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT title, excerpt, full_text, region
        FROM raw_articles
        ORDER BY COALESCE(published_date, '') DESC
        LIMIT 10
        """
    ).fetchall()
    conn.close()
    articles = []
    for r in rows:
        text = ' '.join(((r['full_text'] or r['excerpt'] or '')).split())
        articles.append({
            "title": r['title'],
            "summary": text[:3000],
            "region": r['region'],
        })
    return articles


def _generate_sudoku() -> tuple[list[list[int]], list[list[int]]]:
    """Generate a valid sudoku puzzle and solution using py-sudoku, seeded by today's date."""
    import datetime
    try:
        from sudoku import Sudoku
        seed = int(datetime.date.today().strftime("%Y%m%d"))
        board = Sudoku(3, puzzle=0.5, seed=seed).board
        solver = Sudoku(3)
        solution = solver.solve(board)
        grid = [[int(c) if c else 0 for c in row] for row in board]
        sol_grid = [[int(c) if c else 0 for c in row] for row in solution.board]
        return grid, sol_grid
    except Exception:
        # Fallback: date-derived hardcoded puzzle as last resort
        import datetime, random
        day_val = int(datetime.date.today().strftime("%Y%m%d")) % 3
        solutions = [
            [[5,3,4,6,7,8,9,1,2],[6,7,2,1,9,5,3,4,8],[1,9,8,3,4,2,5,6,7],[8,5,9,7,6,1,4,2,3],[4,2,6,8,5,3,7,9,1],[7,1,3,9,2,4,8,5,6],[9,6,1,5,3,7,2,8,4],[2,8,7,4,1,9,6,3,5],[3,4,5,2,8,6,1,7,9]],
            [[1,2,3,4,5,6,7,8,9],[4,5,6,7,8,9,1,2,3],[7,8,9,1,2,3,4,5,6],[2,3,4,5,6,7,8,9,1],[5,6,7,8,9,1,2,3,4],[8,9,1,2,3,4,5,6,7],[3,4,5,6,7,8,9,1,2],[6,7,8,9,1,2,3,4,5],[9,1,2,3,4,5,6,7,8]],
            [[9,8,7,6,5,4,3,2,1],[6,5,4,3,2,1,9,8,7],[3,2,1,9,8,7,6,5,4],[8,9,2,1,7,3,4,5,6],[1,7,3,2,4,5,6,9,8],[5,4,6,8,9,2,7,1,3],[2,3,5,7,1,6,8,4,9],[7,6,8,4,3,9,1,5,2],[4,1,9,5,6,8,2,3,7]],
        ]
        solution = solutions[day_val]
        puzzle = [row[:] for row in solution]
        random.seed(int(datetime.date.today().strftime("%Y%m%d")))
        blanks = 0
        while blanks < 40:
            r, c = random.randint(0, 8), random.randint(0, 8)
            if puzzle[r][c] != 0:
                puzzle[r][c] = 0
                blanks += 1
        return puzzle, solution


def _get_chess_puzzle() -> dict[str, str]:
    """Fetch today's puzzle from Lichess daily puzzle API, with local fallback."""
    import requests, logging
    try:
        resp = requests.get("https://lichess.org/api/puzzle/daily", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        puzzle_fen = data.get("puzzle", {}).get("fen")
        solution_moves = data.get("puzzle", {}).get("solution", [])
        best_move_uci = solution_moves[0] if solution_moves else None
        if not puzzle_fen or not best_move_uci:
            raise ValueError("Missing FEN or solution in Lichess response")
        import chess
        board = chess.Board(puzzle_fen)
        move = chess.Move.from_uci(best_move_uci)
        best_move_san = board.san(move) if move in board.legal_moves else best_move_uci
        rating = data.get("puzzle", {}).get("rating", 0)
        themes = data.get("puzzle", {}).get("themes", [])
        # Infer color from FEN (e.g. "w" = white to move)
        fen_color = puzzle_fen.split()[1] if len(puzzle_fen.split()) > 1 else "w"
        color = "Black" if fen_color == "b" else "White"
        desc = f"{color} to move."
        if rating:
            desc += f" Rating: {rating}."
        if themes:
            desc += f" Themes: {', '.join(themes[:4])}."
        # Build explanation
        piece = board.piece_at(move.from_square)
        captured = board.piece_at(move.to_square)
        board.push(move)
        result = "checkmate" if board.is_checkmate() else "check" if board.is_check() else "capture" if captured else "good move"
        explanation = f"{piece.symbol().upper()} plays {best_move_san} — {result}."
        return {"fen": puzzle_fen, "description": desc, "best_move": best_move_san, "explanation": explanation}
    except Exception as exc:
        logging.warning(f"Lichess puzzle fetch failed ({exc}), using fallback")
        return _chess_fallback()


# Expose for direct testing
if __name__ == "__main__":
    import sys
    try:
        result = generate_growth_section()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)