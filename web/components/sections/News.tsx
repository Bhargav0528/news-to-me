import type { Article, NewsSection } from "@/lib/edition-types";

function ArticleCard({ article, index }: { article: Article; index: number }) {
  return (
    <article className="mb-5 last:mb-0">
      <h4 className="article-headline mb-1">
        {index + 1}. {article.headline}
      </h4>

      <p className="article-body mb-2">{article.summary}</p>

      <details className="article-details">
        <summary
          className="meta-text cursor-pointer"
          style={{ color: "var(--color-accent)" }}
        >
          Read more
        </summary>

        <div className="mt-3 space-y-3 border-l-2 pl-4" style={{ borderColor: "var(--color-rule)" }}>
          {article.why_it_matters && (
            <div>
              <p className="meta-text font-semibold mb-0.5" style={{ color: "var(--color-ink)" }}>
                Why it matters
              </p>
              <p className="article-body">{article.why_it_matters}</p>
            </div>
          )}
          {article.what_to_watch && (
            <div>
              <p className="meta-text font-semibold mb-0.5" style={{ color: "var(--color-ink)" }}>
                What to watch
              </p>
              <p className="article-body">{article.what_to_watch}</p>
            </div>
          )}
          {article.public_reactions && (
            <div>
              <p className="meta-text font-semibold mb-0.5" style={{ color: "var(--color-ink)" }}>
                Public reactions
              </p>
              <p className="article-body">{article.public_reactions}</p>
            </div>
          )}
          {article.context && (
            <div>
              <p className="meta-text font-semibold mb-0.5" style={{ color: "var(--color-ink)" }}>
                Context
              </p>
              <p className="article-body">{article.context}</p>
            </div>
          )}
        </div>

        {article.source_url && (
          <p className="meta-text mt-3">
            <a
              href={article.source_url}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "var(--color-accent)" }}
            >
              Source ↗
            </a>
          </p>
        )}
      </details>
    </article>
  );
}

function Subregion({ label, articles }: { label: string; articles: Article[] }) {
  if (!articles || articles.length === 0) return null;
  return (
    <div className="mb-8 last:mb-0">
      <span className="subregion-header">{label}</span>
      <div className="subregion-header-rule" />
      {articles.slice(0, 5).map((article, i) => (
        <ArticleCard key={i} article={article} index={i} />
      ))}
    </div>
  );
}

interface NewsProps {
  articles: NewsSection;
}

export default function News({ articles }: NewsProps) {
  return (
    <section aria-label="News">
      <Subregion label="Bangalore" articles={articles.bangalore} />
      <Subregion label="Karnataka" articles={articles.karnataka} />
      <Subregion label="India" articles={articles.india} />
      <Subregion label="US" articles={articles.us} />
      <Subregion label="World" articles={articles.world} />
    </section>
  );
}
