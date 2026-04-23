import { getEdition, formatEditionDate } from "@/lib/edition";
import { readingTime } from "@/lib/reading-time";
import type { TldrItem, BiztechArticle, GrowthSection, KnowledgeSection, NewsSection } from "@/lib/edition-types";

// Deduplicate market indices by name, keeping the one with value > 0
function uniqueIndices(indices: { name: string; value: number; change: number; change_percent: number }[]) {
  const seen = new Map<string, typeof indices[0]>();
  for (const idx of indices) {
    if (!seen.has(idx.name) || (idx.value > 0 && seen.get(idx.name)!.value === 0)) {
      seen.set(idx.name, idx);
    }
  }
  return Array.from(seen.values()).filter((idx) => idx.value > 0);
}

export default function HomePage() {
  const edition = getEdition();
  const formattedDate = formatEditionDate(edition.date);

  const newsWordCount =
    Object.values(edition.news)
      .flat()
      .reduce((sum, a) => sum + a.summary.split(/\s+/).length, 0);

  const biztechWordCount = edition.biztech.articles.reduce(
    (sum, a) => sum + a.summary.split(/\s+/).length, 0
  );

  const funWordCount =
    (edition.fun.riddle.question + edition.fun.logic_puzzle.question).split(/\s+/).length;

  return (
    <div className="min-h-screen" style={{ backgroundColor: "var(--color-paper)" }}>
      {/* ── Masthead ── */}
      <header className="masthead-rule">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex items-baseline justify-between gap-4">
            <h1 className="masthead flex-1 text-center">News To Me</h1>
            <div className="meta-text text-right shrink-0">
              <p>{formattedDate}</p>
              <p>Edition {edition.edition_number}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 pb-16 space-y-0">

        {/* ── TLDR (SCRUM-34) ── */}
        <section aria-labelledby="tldr-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="tldr-heading" className="section-header">In Brief</h2>
            <span className="meta-text">{edition.tldr.length} stories</span>
          </div>
          <div className="pb-section">
            <TldrPlaceholder items={edition.tldr} />
          </div>
        </section>

        {/* ── News (SCRUM-35) ── */}
        <section aria-labelledby="news-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="news-heading" className="section-header">News</h2>
            <span className="meta-text">{readingTime(String(newsWordCount))}</span>
          </div>
          <div className="pb-section">
            <NewsPlaceholder articles={edition.news} />
          </div>
        </section>

        {/* ── Biz/Tech (SCRUM-36) ── */}
        <section aria-labelledby="biztech-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="biztech-heading" className="section-header">Biz &amp; Tech</h2>
            <span className="meta-text">{readingTime(String(biztechWordCount))}</span>
          </div>
          <div className="pb-section">
            <BiztechPlaceholder biztech={edition.biztech} />
          </div>
        </section>

        {/* ── Growth (SCRUM-37) ── */}
        <section aria-labelledby="growth-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="growth-heading" className="section-header">Growth</h2>
            <span className="meta-text">{readingTime(edition.growth.body)}</span>
          </div>
          <div className="pb-section">
            <GrowthPlaceholder growth={edition.growth} />
          </div>
        </section>

        {/* ── Knowledge (SCRUM-37) ── */}
        <section aria-labelledby="knowledge-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="knowledge-heading" className="section-header">Knowledge</h2>
            <span className="meta-text">{readingTime(edition.knowledge.body)}</span>
          </div>
          <div className="pb-section">
            <KnowledgePlaceholder knowledge={edition.knowledge} />
          </div>
        </section>

        {/* ── Fun (SCRUM-38) ── */}
        <section aria-labelledby="fun-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="fun-heading" className="section-header">Fun</h2>
            <span className="meta-text">{readingTime(String(funWordCount))}</span>
          </div>
          <div className="pb-section">
            <FunPlaceholder />
          </div>
        </section>

        {/* ── Footer ── */}
        <footer className="pt-6 mt-8 border-t" style={{ borderColor: "var(--color-rule)" }}>
          <div className="flex justify-between items-center">
            <p className="meta-text">
              Generated {new Date(edition.generated_at).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" })}
            </p>
            <p className="meta-text">
              {edition.pipeline_stats.articles_fetched.toLocaleString()} articles
            </p>
          </div>
          <p className="meta-text mt-2">Generated by News To Me pipeline</p>
        </footer>

      </main>
    </div>
  );
}

// ── Placeholder components (replaced by SCRUM-34 through SCRUM-38) ──

function TldrPlaceholder({ items }: { items: TldrItem[] }) {
  return (
    <div className="space-y-3">
      {items.slice(0, 3).map((item, i) => (
        <div key={i} className="border-l-2 pl-3" style={{ borderColor: "var(--color-accent)" }}>
          <p className="tag-label">{item.region?.toUpperCase()}</p>
          <p className="article-headline">{item.headline}</p>
          <p className="article-body mt-1">{item.summary}</p>
        </div>
      ))}
    </div>
  );
}

function NewsPlaceholder({ articles }: { articles: NewsSection }) {
  const regions = ["bangalore", "karnataka", "india", "us", "world"] as const;
  return (
    <div className="space-y-6">
      {regions.map((region) =>
        articles[region]?.length ? (
          <div key={region}>
            <p className="subregion-header mb-3 pb-2 border-b" style={{ borderColor: "var(--color-rule)" }}>
              {region.charAt(0).toUpperCase() + region.slice(1)}
            </p>
            {articles[region].slice(0, 3).map((art, i) => (
              <div key={i} className="mb-5">
                <p className="article-headline">{art.headline}</p>
                <p className="article-body mt-1">{art.summary}</p>
              </div>
            ))}
          </div>
        ) : null
      )}
    </div>
  );
}

function BiztechPlaceholder({ biztech }: { biztech: { market_snapshot: { indices: { name: string; value: number; change: number; change_percent: number }[] }; articles: BiztechArticle[] } }) {
  const validIndices = uniqueIndices(biztech.market_snapshot.indices);
  return (
    <div className="space-y-4">
      {validIndices.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {validIndices.map((idx) => (
            <div key={idx.name} className="border rounded p-2" style={{ borderColor: "var(--color-rule)" }}>
              <p className="meta-text">{idx.name}</p>
              <p className="market-value">{idx.value.toLocaleString()}</p>
              <p className={`market-value ${idx.change >= 0 ? "market-positive" : "market-negative"}`}>
                {idx.change >= 0 ? "+" : ""}{idx.change_percent.toFixed(2)}%
              </p>
            </div>
          ))}
        </div>
      )}
      {biztech.articles.slice(0, 3).map((art, i) => (
        <div key={i} className="mb-5">
          <p className="article-headline">{art.headline}</p>
          <p className="article-body mt-1">{art.summary}</p>
        </div>
      ))}
    </div>
  );
}

function GrowthPlaceholder({ growth }: { growth: GrowthSection }) {
  return (
    <div>
      <p className="tag-label">{growth.topic_category}</p>
      <p className="article-headline">{growth.title}</p>
      <p className="article-body mt-2">{growth.body.slice(0, 200)}...</p>
    </div>
  );
}

function KnowledgePlaceholder({ knowledge }: { knowledge: KnowledgeSection }) {
  return (
    <div>
      <p className="tag-label">{knowledge.category}</p>
      <p className="article-headline">{knowledge.title}</p>
      <p className="article-body mt-2">{knowledge.body.slice(0, 200)}...</p>
    </div>
  );
}

function FunPlaceholder() {
  return (
    <p className="meta-text">Puzzle, sudoku, chess &amp; riddles — coming in SCRUM-38.</p>
  );
}
