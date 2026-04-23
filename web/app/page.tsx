import { getEdition, formatEditionDate } from "@/lib/edition";
import { readingTime } from "@/lib/reading-time";
import type { Article, TldrItem, BiztechArticle, GrowthSection, KnowledgeSection, NewsSection } from "@/lib/edition-types";

// Sections are built in Wave 4 (SCRUM-34 through SCRUM-38).
// This shell only provides the masthead, section wrappers, and dividers.

export default async function HomePage() {
  const edition = getEdition();
  const formattedDate = formatEditionDate(edition.date);

  return (
    <div className="min-h-screen" style={{ backgroundColor: "var(--color-paper)" }}>
      {/* ── Masthead ── */}
      <header className="masthead-rule">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex items-baseline justify-between gap-4">
            <h1 className="masthead flex-1 text-center">News To Me</h1>
            <div className="text-xs text-right shrink-0" style={{ fontFamily: "var(--font-sans)", color: "var(--color-ink-muted)" }}>
              <p>{formattedDate}</p>
              <p>Edition {edition.edition_number}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 pb-16 space-y-0">

        {/* ── TLDR (SCRUM-34) ── */}
        <section aria-labelledby="tldr-heading">
          <div className="section-rule pt-6 pb-3">
            <h2 id="tldr-heading" className="section-header">In Brief</h2>
          </div>
          <div className="pb-section">
            <TldrPlaceholder items={edition.tldr} />
          </div>
        </section>

        {/* ── News (SCRUM-35) ── */}
        <section aria-labelledby="news-heading">
          <div className="section-rule pt-6 pb-3">
            <h2 id="news-heading" className="section-header">News</h2>
          </div>
          <div className="pb-section">
            <NewsPlaceholder articles={edition.news} />
          </div>
        </section>

        {/* ── Biz/Tech (SCRUM-36) ── */}
        <section aria-labelledby="biztech-heading">
          <div className="section-rule pt-6 pb-3">
            <h2 id="biztech-heading" className="section-header">Biz & Tech</h2>
          </div>
          <div className="pb-section">
            <BiztechPlaceholder biztech={edition.biztech} />
          </div>
        </section>

        {/* ── Growth (SCRUM-37) ── */}
        <section aria-labelledby="growth-heading">
          <div className="section-rule pt-6 pb-3">
            <h2 id="growth-heading" className="section-header">Growth</h2>
          </div>
          <div className="pb-section">
            <GrowthPlaceholder growth={edition.growth} />
          </div>
        </section>

        {/* ── Knowledge (SCRUM-37) ── */}
        <section aria-labelledby="knowledge-heading">
          <div className="section-rule pt-6 pb-3">
            <h2 id="knowledge-heading" className="section-header">Knowledge</h2>
          </div>
          <div className="pb-section">
            <KnowledgePlaceholder knowledge={edition.knowledge} />
          </div>
        </section>

        {/* ── Fun (SCRUM-38) ── */}
        <section aria-labelledby="fun-heading">
          <div className="section-rule pt-6 pb-3">
            <h2 id="fun-heading" className="section-header">Fun</h2>
          </div>
          <div className="pb-section">
            <FunPlaceholder />
          </div>
        </section>

        {/* ── Footer ── */}
        <footer className="pt-6 mt-8 border-t" style={{ borderColor: "var(--color-rule)" }}>
          <div className="flex justify-between items-center">
            <p className="text-xs" style={{ fontFamily: "var(--font-sans)", color: "var(--color-ink-muted)" }}>
              Generated {new Date(edition.generated_at).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" })}
            </p>
            <p className="text-xs" style={{ fontFamily: "var(--font-sans)", color: "var(--color-ink-muted)" }}>
              {edition.pipeline_stats.articles_fetched.toLocaleString()} articles · {readingTime(edition.growth.body).replace(" min read", " min")}
            </p>
          </div>
        </footer>

      </main>
    </div>
  );
}

// ── Placeholder components (replaced by SCRUM-34 through SCRUM-38) ──

function TldrPlaceholder({ items }: { items: TldrItem[] }) {
  return (
    <div className="space-y-3">
      {items.slice(0, 2).map((item, i) => (
        <div key={i} className="border-l-2 pl-3" style={{ borderColor: "var(--color-accent)" }}>
          <p className="text-xs uppercase tracking-wider mb-1" style={{ fontFamily: "var(--font-sans)", color: "var(--color-accent)" }}>
            {item.region?.toUpperCase()}
          </p>
          <p className="article-headline text-base">{item.headline}</p>
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
            <p className="text-xs uppercase tracking-widest mb-2" style={{ fontFamily: "var(--font-sans)", color: "var(--color-ink-muted)" }}>
              {region.charAt(0).toUpperCase() + region.slice(1)}
            </p>
            {articles[region].slice(0, 2).map((art, i) => (
              <div key={i} className="mb-4">
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
  const { indices } = biztech.market_snapshot;
  return (
    <div className="space-y-4">
      {indices.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {indices.map((idx) => (
            <div key={idx.name} className="border rounded p-2" style={{ borderColor: "var(--color-rule)" }}>
              <p className="text-xs" style={{ fontFamily: "var(--font-sans)", color: "var(--color-ink-muted)" }}>{idx.name}</p>
              <p className="market-value" style={{ fontFamily: "var(--font-sans)" }}>{idx.value.toLocaleString()}</p>
              <p className={`market-value ${idx.change >= 0 ? "market-positive" : "market-negative"}`} style={{ fontFamily: "var(--font-sans)" }}>
                {idx.change >= 0 ? "+" : ""}{idx.change_percent}%
              </p>
            </div>
          ))}
        </div>
      )}
      {biztech.articles.slice(0, 2).map((art, i) => (
        <div key={i}>
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
      <p className="text-xs uppercase tracking-widest mb-2" style={{ fontFamily: "var(--font-sans)", color: "var(--color-accent)" }}>
        {growth.topic_category}
      </p>
      <p className="article-headline">{growth.title}</p>
      <p className="article-body mt-2">{growth.body.slice(0, 200)}...</p>
    </div>
  );
}

function KnowledgePlaceholder({ knowledge }: { knowledge: KnowledgeSection }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-widest mb-2" style={{ fontFamily: "var(--font-sans)", color: "var(--color-accent)" }}>
        {knowledge.category}
      </p>
      <p className="article-headline">{knowledge.title}</p>
      <p className="article-body mt-2">{knowledge.body.slice(0, 200)}...</p>
    </div>
  );
}

function FunPlaceholder() {
  return (
    <div className="text-sm" style={{ color: "var(--color-ink-muted)", fontFamily: "var(--font-sans)" }}>
      Puzzle, sudoku, chess & riddles — coming in SCRUM-38.
    </div>
  );
}
