import { getEdition, formatEditionDate } from "@/lib/edition";
import { readingTime, readingTimeFromWords } from "@/lib/reading-time";
import Tldr from "@/components/sections/Tldr";
import News from "@/components/sections/News";
import Biztech from "@/components/sections/Biztech";
import Growth from "@/components/sections/Growth";
import Knowledge from "@/components/sections/Knowledge";
import Fun from "@/components/sections/Fun";

export default function HomePage() {
  const edition = getEdition();
  const formattedDate = formatEditionDate(edition.date);

  const newsWordCount = Object.values(edition.news)
    .flat()
    .reduce((sum, a) => sum + a.summary.split(/\s+/).length, 0);

  const biztechWordCount = edition.biztech.articles.reduce(
    (sum, a) => sum + a.summary.split(/\s+/).length, 0
  );

  const funWordCount = (
    edition.fun.riddle.question +
    edition.fun.logic_puzzle.question
  ).split(/\s+/).length;

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
            <Tldr items={edition.tldr} />
          </div>
        </section>

        {/* ── News (SCRUM-35) ── */}
        <section aria-labelledby="news-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="news-heading" className="section-header">News</h2>
            <span className="meta-text">{readingTimeFromWords(newsWordCount)}</span>
          </div>
          <div className="pb-section">
            <News articles={edition.news} />
          </div>
        </section>

        {/* ── Biz/Tech (SCRUM-36) ── */}
        <section aria-labelledby="biztech-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="biztech-heading" className="section-header">Biz &amp; Tech</h2>
            <span className="meta-text">{readingTimeFromWords(biztechWordCount)}</span>
          </div>
          <div className="pb-section">
            <Biztech biztech={edition.biztech} />
          </div>
        </section>

        {/* ── Growth (SCRUM-37) ── */}
        <section aria-labelledby="growth-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="growth-heading" className="section-header">Growth</h2>
            <span className="meta-text">{readingTime(edition.growth.body)}</span>
          </div>
          <div className="pb-section">
            <Growth growth={edition.growth} />
          </div>
        </section>

        {/* ── Knowledge (SCRUM-37) ── */}
        <section aria-labelledby="knowledge-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="knowledge-heading" className="section-header">Knowledge</h2>
            <span className="meta-text">{readingTime(edition.knowledge.body)}</span>
          </div>
          <div className="pb-section">
            <Knowledge knowledge={edition.knowledge} />
          </div>
        </section>

        {/* ── Fun (SCRUM-38) ── */}
        <section aria-labelledby="fun-heading">
          <div className="section-rule pt-6 pb-3 flex justify-between items-end">
            <h2 id="fun-heading" className="section-header">Fun</h2>
            <span className="meta-text">{readingTimeFromWords(funWordCount)}</span>
          </div>
          <div className="pb-section">
            <Fun fun={edition.fun} />
          </div>
        </section>

        {/* ── Footer ── */}
        <footer className="pt-6 mt-8 border-t" style={{ borderColor: "var(--color-rule)" }}>
          <div className="flex justify-between items-center">
            <p className="meta-text">
              Generated{" "}
              {new Date(edition.generated_at).toLocaleString("en-US", {
                dateStyle: "medium",
                timeStyle: "short",
              })}
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
