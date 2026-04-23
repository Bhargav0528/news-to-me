import { TldrItem } from "@/lib/edition-types";

interface TldrProps {
  items: TldrItem[];
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
            {/* Number + Region + Headline */}
            <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1 mb-2">
              <span
                className="text-xs font-sans font-bold tabular-nums"
                style={{ color: "var(--color-ink-muted)" }}
              >
                {index + 1}.
              </span>
              <span className="tag-label">{item.region.toUpperCase()}</span>
              <h3 className="article-headline">{item.headline}</h3>
            </div>

            {/* Summary (always visible) */}
            <p className="article-body">{item.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
