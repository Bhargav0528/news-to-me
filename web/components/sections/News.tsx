import { Article, NewsSection } from "@/lib/edition-types";

interface ArticleCardProps {
  article: Article;
  index: number;
}

/** Truncate summary to ~120 chars, ending at a word boundary */
function truncate(text: string, maxChars = 120): string {
  if (text.length <= maxChars) return text;
  const truncated = text.slice(0, maxChars);
  const lastSpace = truncated.lastIndexOf(" ");
  return lastSpace > 80 ? truncated.slice(0, lastSpace) + "…" : truncated + "…";
}

function ArticleCard({ article, index }: ArticleCardProps) {
  return (
    <article className="mb-5 last:mb-0">
      {/* Headline */}
      <h4 className="article-headline mb-1">
        {index + 1}. {article.headline}
      </h4>

      {/* Summary — always visible, truncated */}
      <p className="article-body mb-2">{truncate(article.summary)}</p>

      {/* Expandable full card */}
      <details className="article-details">
        <summary className="meta-text text-accent hover:text-ink transition-colors cursor-pointer">
          Read more
        </summary>

        <div className="mt-3 space-y-3 border-l-2 border-rule pl-4">
          {article.why_it_matters && (
            <div>
              <p className="meta-text font-semibold text-ink mb-0.5">Why it matters</p>
              <p className="article-body">{article.why_it_matters}</p>
            </div>
          )}
          {article.what_to_watch && (
            <div>
              <p className="meta-text font-semibold text-ink mb-0.5">What to watch</p>
              <p className="article-body">{article.what_to_watch}</p>
            </div>
          )}
          {article.public_reactions && (
            <div>
              <p className="meta-text font-semibold text-ink mb-0.5">Public reactions</p>
              <p className="article-body">{article.public_reactions}</p>
            </div>
          )}
          {article.context && (
            <div>
              <p className="meta-text font-semibold text-ink mb-0.5">Context</p>
              <p className="article-body">{article.context}</p>
            </div>
          )}
        </div>

        {/* Source */}
        {article.source_url && (
          <p className="meta-text mt-3">
            <a
              href={article.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-ink underline underline-offset-2"
            >
              Source ↗
            </a>
          </p>
        )}
      </details>
    </article>
  );
}

interface SubregionProps {
  label: string;
  articles: Article[];
}

function Subregion({ label, articles }: SubregionProps) {
  if (!articles || articles.length === 0) return null;
  return (
    <div className="mb-8 last:mb-0">
      <span className="subregion-header">{label}</span>
      <div className="subregion-header-rule" />
      <div>
        {articles.slice(0, 5).map((article, i) => (
          <ArticleCard key={i} article={article} index={i} />
        ))}
      </div>
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
