import type { FunSection } from "@/lib/edition-types";

// ── Chess FEN Parser ──────────────────────────────────────────────

type Piece = string; // 'K' | 'Q' | 'R' | 'B' | 'N' | 'P' | 'k' | 'q' | 'r' | 'b' | 'n' | 'p' | ''

function parseFen(fen: string): Piece[][] {
  // FEN format: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
  // We only need rank 0 (the board position before any moves)
  const rank0 = fen.split(" ")[0];
  const rows = rank0.split("/");
  const board: Piece[][] = [];

  for (const row of rows) {
    const boardRow: Piece[] = [];
    for (const ch of row) {
      if (/\d/.test(ch)) {
        // Empty squares: repeat that many times
        for (let i = 0; i < parseInt(ch); i++) boardRow.push("");
      } else {
        boardRow.push(ch);
      }
    }
    board.push(boardRow);
  }
  return board;
}

// ── Chess Piece display ──────────────────────────────────────────

const PIECE_SYMBOLS: Record<string, string> = {
  K: "♔", Q: "♕", R: "♖", B: "♗", N: "♘", P: "♙",
  k: "♚", q: "♛", r: "♜", b: "♝", n: "♞", p: "♟",
};

function ChessSquare({ piece, isLight }: { piece: Piece; isLight: boolean }) {
  const bg = isLight ? "#f0d9b5" : "#b58863";
  const symbol = piece ? PIECE_SYMBOLS[piece] : "";
  const isWhite = piece && piece === piece.toUpperCase();
  return (
    <div
      style={{
        backgroundColor: bg,
        width: "100%",
        aspectRatio: "1",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "clamp(1.25rem, 3vw, 2rem)",
        color: isWhite ? "#fff" : "#1a1a1a",
        fontWeight: 700,
      }}
    >
      {symbol}
    </div>
  );
}

// ── Sudoku ───────────────────────────────────────────────────────

const BOX_STARTS = [0, 3, 6];
const BOX_ENDS   = [3, 6, 9];

function SudokuCell({ value, given }: { value: number; given: boolean }) {
  return (
    <div
      className="sudoku-cell"
      style={{ fontWeight: given ? 700 : 400 }}
    >
      {value === 0 ? "" : value}
    </div>
  );
}

// Determine if a cell is at a 3×3 box boundary (for thick borders)
function isBoxEdge(index: number, dimension: "row" | "col"): boolean {
  const pos = dimension === "row" ? index : index;
  return pos === 3 || pos === 6;
}

// ── Section sub-header ────────────────────────────────────────────

function SubsectionHeader({ label }: { label: string }) {
  return (
    <div className="fun-subsection-header">
      <span className="fun-subsection-label">{label}</span>
    </div>
  );
}

// ── Main Fun Component ───────────────────────────────────────────

interface FunProps {
  fun: FunSection;
}

export default function Fun({ fun }: FunProps) {
  const { logic_puzzle, riddle, sudoku, chess, previous_day_answers } = fun;

  // Chess board
  const board = parseFen(chess.fen);

  return (
    <div className="space-y-6">

      {/* ── Logic Puzzle ────────────────────────────────────────── */}
      <div>
        <SubsectionHeader label="Logic Puzzle" />
        <div className="logic-puzzle-question">
          <pre className="logic-puzzle-text">{logic_puzzle.question}</pre>
        </div>
        <details className="article-details logic-puzzle-hint">
          <summary className="meta-text">💡 Hint</summary>
          <p className="article-body mt-2">{logic_puzzle.hint}</p>
        </details>
        <details className="article-details logic-puzzle-answer">
          <summary className="meta-text">✅ Answer</summary>
          <p className="article-body mt-2">{logic_puzzle.answer}</p>
        </details>
      </div>

      {/* ── Riddle ───────────────────────────────────────────────── */}
      <div>
        <SubsectionHeader label="Riddle" />
        <p className="article-headline riddle-question">{riddle.question}</p>
        <details className="article-details mt-2">
          <summary className="meta-text">Reveal answer</summary>
          <p className="article-body mt-2">{riddle.answer}</p>
        </details>
      </div>

      {/* ── Sudoku ──────────────────────────────────────────────── */}
      <div>
        <SubsectionHeader label="Sudoku" />
        <div className="sudoku-wrapper">
          <div className="sudoku-grid">
            {sudoku.grid.map((row, rowIdx) =>
              row.map((cell, colIdx) => {
                const isGiven = cell !== 0;
                return (
                  <SudokuCell
                    key={`${rowIdx}-${colIdx}`}
                    value={cell}
                    given={isGiven}
                  />
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* ── Chess ───────────────────────────────────────────────── */}
      <div>
        <SubsectionHeader label="Chess" />
        <p className="article-body mb-3">{chess.description}</p>
        <div className="chess-grid-wrapper">
          <div className="chess-grid">
            {board.map((row, rowIdx) =>
              row.map((piece, colIdx) => {
                const isLight = (rowIdx + colIdx) % 2 === 0;
                return (
                  <ChessSquare
                    key={`${rowIdx}-${colIdx}`}
                    piece={piece}
                    isLight={isLight}
                  />
                );
              })
            )}
          </div>
        </div>
        <details className="article-details mt-3">
          <summary className="meta-text">Best move + explanation</summary>
          <p className="article-headline mt-2">{chess.best_move}</p>
          <p className="article-body mt-1">{chess.explanation}</p>
        </details>
      </div>

      {/* ── Yesterday's Answers ──────────────────────────────────── */}
      {Object.keys(previous_day_answers).length > 0 && (
        <div>
          <SubsectionHeader label="Yesterday&apos;s Answers" />
          <div className="space-y-1">
            {Object.entries(previous_day_answers).map(([key, answer]) => (
              <p key={key} className="meta-text">
                <span className="font-semibold capitalize">{key.replace(/_/g, " ")}: </span>
                {answer}
              </p>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
