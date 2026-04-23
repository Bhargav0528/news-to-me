import type { FunSection } from "@/lib/edition-types";

// ── Chess FEN Parser ──────────────────────────────────────────────

type Piece = string;

function parseFen(fen: string): Piece[][] {
  const rank0 = fen.split(" ")[0];
  const rows = rank0.split("/");
  const board: Piece[][] = [];

  for (const row of rows) {
    const boardRow: Piece[] = [];
    for (const ch of row) {
      if (/\d/.test(ch)) {
        for (let i = 0; i < parseInt(ch); i++) boardRow.push("");
      } else {
        boardRow.push(ch);
      }
    }
    board.push(boardRow);
  }
  return board;
}

// ── Chess piece symbols ────────────────────────────────────────────

const PIECE_SYMBOLS: Record<string, string> = {
  K: "♔", Q: "♕", R: "♖", B: "♗", N: "♘", P: "♙",
  k: "♚", q: "♛", r: "♜", b: "♝", n: "♞", p: "♟",
};

// ── Chess board renderer ──────────────────────────────────────────

function ChessSquare({ piece, isLight }: { piece: Piece; isLight: boolean }) {
  const bg = isLight ? "#f0d9b5" : "#b58863";
  const symbol = piece ? PIECE_SYMBOLS[piece] : "";
  const isWhitePiece = piece && piece === piece.toUpperCase();
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
        color: isWhitePiece ? "#fff" : "#1a1a1a",
        fontWeight: 700,
      }}
    >
      {symbol}
    </div>
  );
}

// ── Sudoku renderer ──────────────────────────────────────────────

function SudokuCell({ value, isGiven }: { value: number; isGiven: boolean }) {
  return (
    <div
      className="sudoku-cell"
      style={{ fontWeight: isGiven ? 700 : 400 }}
    >
      {value === 0 ? "" : value}
    </div>
  );
}

// ── Sub-section header ────────────────────────────────────────────

function SubsectionHeader({ label }: { label: string }) {
  return (
    <div className="fun-subsection-header">
      <span className="fun-subsection-label">{label}</span>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────

interface FunProps {
  fun: FunSection;
}

export default function Fun({ fun }: FunProps) {
  const { logic_puzzle, riddle, sudoku, chess, previous_day_answers } = fun;
  const board = parseFen(chess.fen);
  const hasAnswers = Object.keys(previous_day_answers).length > 0;

  return (
    <div className="space-y-6">

      {/* ── Logic Puzzle ── */}
      <div>
        <SubsectionHeader label="Logic Puzzle" />
        <pre className="logic-puzzle-text">{logic_puzzle.question}</pre>
        <details className="article-details logic-puzzle-hint mt-2">
          <summary className="meta-text cursor-pointer">Hint</summary>
          <p className="article-body mt-2">{logic_puzzle.hint}</p>
        </details>
        <details className="article-details logic-puzzle-answer mt-2">
          <summary className="meta-text cursor-pointer">Answer</summary>
          <p className="article-body mt-2">{logic_puzzle.answer}</p>
        </details>
      </div>

      {/* ── Riddle ── */}
      <div>
        <SubsectionHeader label="Riddle" />
        <p className="riddle-question">{riddle.question}</p>
        <details className="article-details mt-2">
          <summary className="meta-text cursor-pointer">Reveal answer</summary>
          <p className="article-body mt-2">{riddle.answer}</p>
        </details>
      </div>

      {/* ── Sudoku ── */}
      <div>
        <SubsectionHeader label="Sudoku" />
        <div className="sudoku-wrapper">
          <div className="sudoku-grid">
            {sudoku.grid.map((row, rowIdx) =>
              row.map((cell, colIdx) => (
                <SudokuCell
                  key={`${rowIdx}-${colIdx}`}
                  value={cell}
                  isGiven={cell !== 0}
                />
              ))
            )}
          </div>
        </div>
      </div>

      {/* ── Chess ── */}
      <div>
        <SubsectionHeader label="Chess" />
        <p className="article-body mb-3">{chess.description}</p>
        <div className="chess-grid-wrapper">
          <div className="chess-grid">
            {board.map((row, rowIdx) =>
              row.map((piece, colIdx) => (
                <ChessSquare
                  key={`${rowIdx}-${colIdx}`}
                  piece={piece}
                  isLight={(rowIdx + colIdx) % 2 === 0}
                />
              ))
            )}
          </div>
        </div>
        <details className="article-details mt-3">
          <summary className="meta-text cursor-pointer">Best move + explanation</summary>
          <p className="article-headline mt-2">{chess.best_move}</p>
          <p className="article-body mt-1">{chess.explanation}</p>
        </details>
      </div>

      {/* ── Yesterday&apos;s Answers ── */}
      {hasAnswers && (
        <div>
          <SubsectionHeader label="Yesterday's Answers" />
          <div className="space-y-1">
            {Object.entries(previous_day_answers).map(([key, answer]) => (
              <p key={key} className="meta-text">
                <span className="font-semibold capitalize">
                  {key.replace(/_/g, " ")}:{" "}
                </span>
                {answer}
              </p>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
