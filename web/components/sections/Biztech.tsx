import type { Biztech } from "@/lib/edition-types";

interface BiztechProps {
  biztech: Biztech;
}

// Deduplicate indices by name, preferring entries with value > 0
function uniqueIndices(
  indices: { name: string; value: number; change: number; change_percent: number }[]
) {
  const seen = new Map<string, typeof indices[0]>();
  for (const idx of indices) {
    if (
      !seen.has(idx.name) ||
      (idx.value > 0 && seen.get(idx.name)!.value === 0)
    ) {
      seen.set(idx.name, idx);
    }
  }
  return Array.from(seen.values()).filter((idx) => idx.value > 0);
}

export default function Biztech({ biztech }: BiztechProps) {
  const indices = uniqueIndices(biztech.market_snapshot.indices);

  return (
    <div className="space-y-6">
      {/* Market Ticker */}
      {indices.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {indices.map((idx) => {
            const isPositive = idx.change >= 0;
            const sign = isPositive ? "+" : "";
            return (
              <div
                key={idx.name}
                className="border rounded p-3"
                style={{ borderColor: "var(--color-rule)" }}
              >
                <p className="meta-text mb-1">{idx.name}</p>
                <p className="market-value font-semibold">
                  {idx.value.toLocaleString()}
                </p>
                <p
                  className={`market-value ${
                    isPositive ? "market-positive" : "market-negative"
                  }`}
                >
                  {sign}
                  {idx.change_percent.toFixed(2)}%
                </p>
              </div>
            );
          })}
        </div>
      )}

      {/* Article Cards */}
      {biztech.articles.map((article, i) => (
        <article key={i} className="mb-5 last:mb-0">
          <p className="article-headline">{article.headline}</p>
          <p className="article-body mt-2">{article.summary}</p>

          {article.market_impact && (
            <div
              className="mt-3 p-3 rounded"
              style={{ backgroundColor: "var(--color-highlight)" }}
            >
              <p className="meta-text font-semibold mb-1">Market Impact</p>
              <p className="article-body">{article.market_impact}</p>
            </div>
          )}

          {article.source_url && (
            <p className="meta-text mt-2">
              <a
                href={article.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
                style={{ color: "var(--color-ink-muted)" }}
              >
                Source
              </a>
            </p>
          )}
        </article>
      ))}
    </div>
  );
}
