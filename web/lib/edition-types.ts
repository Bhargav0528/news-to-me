// Edition JSON types — derived from data/edition.json (source of truth)
// NOTE: These types must stay in sync with what Becky's pipeline writes.

export interface Article {
  headline: string;
  summary: string;
  why_it_matters: string;
  what_to_watch: string;
  public_reactions: string;
  context: string;
  source_url: string;
}

export interface MarketIndex {
  name: string;
  value: number;
  change: number;
  change_percent: number;
}

export interface MarketSnapshot {
  indices: MarketIndex[];
}

export interface BiztechArticle {
  headline: string;
  summary: string;
  market_impact: string;
  source_url: string;
}

export interface Biztech {
  market_snapshot: MarketSnapshot;
  articles: BiztechArticle[];
}

export interface GrowthSection {
  title: string;
  body: string;
  key_takeaways: string[];
  further_reading: { title: string; url: string }[];
  topic_category: string;
}

export interface KnowledgeSection {
  title: string;
  body: string;
  category: string;
  surprising_fact: string;
  everyday_connection: string;
}

export interface LogicPuzzle {
  question: string;
  hint: string;
  answer: string;
}

export interface Riddle {
  question: string;
  answer: string;
}

export type SudokuGrid = number[][];

export interface ChessPosition {
  fen: string;
  description: string;
  best_move: string;
  explanation: string;
}

export interface FunSection {
  logic_puzzle: LogicPuzzle;
  riddle: Riddle;
  sudoku: { grid: SudokuGrid; solution: SudokuGrid };
  chess: ChessPosition;
  previous_day_answers: Record<string, string>;
}

export interface TldrItem {
  headline: string;
  summary: string;
  region: string;
  category: string;
}

export interface NewsSection {
  bangalore: Article[];
  karnataka: Article[];
  india: Article[];
  us: Article[];
  world: Article[];
}

export interface PipelineStats {
  articles_fetched: number;
  full_text_success_rate: number;
  total_time_seconds: number;
  token_usage: Record<string, number>;
}

export interface Edition {
  date: string;
  edition_number: number;
  generated_at: string;
  pipeline_stats: PipelineStats;
  tldr: TldrItem[];
  news: NewsSection;
  biztech: Biztech;
  growth: GrowthSection;
  knowledge: KnowledgeSection;
  fun: FunSection;
}
