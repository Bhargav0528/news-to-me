import { TldrItem } from "@/lib/edition-types";

interface TldrProps {
  items: TldrItem[];
}

function RegionTag({ region }: { region: string }) {
  const label = region.toUpperCase();
  return (
    <span className="tag-label border-l-2 border-accent pl-1.5 mr-2">
      {label}
    </span>
  );
}

export default function Tldr({ items }: TldrProps) {
  return (
    <section aria-label="In Brief">
      <div className="space-y-4">
        {items.map((item, index) => (
          <article
            key={index}
            className="border-l-2 border-accent pl-4 py-1"
          >
            {/* Number + Region + Headline row */}
            <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1 mb-1">
              <span className="font-sans text-sm font-bold text-ink-muted tabular-nums">
                {index + 1}.
              </span>
              <RegionTag region={item.region} />
              <h3 className="article-headline flex-1">{item.headline}</h3>
            </div>

            {/* Summary (always visible) */}
            <p className="article-body pl-0">{item.summary}</p>

            {/* Expandable full summary */}
            <details className="article-details mt-2">
              <summary className="meta-text text-accent hover:text-ink transition-colors">
                Read more
              </summary>
              <div className="mt-2 pl-0">
                <p className="article-body">{item.summary}</p>
              </div>
            </details>
          </article>
        ))}
      </div>
    </section>
  );
}
