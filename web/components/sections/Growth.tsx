import type { GrowthSection } from "@/lib/edition-types";

interface GrowthProps {
  growth: GrowthSection;
}

function parseBody(body: string): string[] {
  return body.split(/\n\n/).filter((p) => p.trim().length > 0);
}

export default function Growth({ growth }: GrowthProps) {
  const paragraphs = parseBody(growth.body);

  return (
    <article>
      {/* Topic category tag */}
      <p className="tag-label mb-2">{growth.topic_category}</p>

      {/* Title */}
      <h3 className="article-headline mb-4">{growth.title}</h3>

      {/* Body paragraphs */}
      <div className="article-body space-y-3 mb-6">
        {paragraphs.map((para, i) => (
          <p key={i}>{para.trim()}</p>
        ))}
      </div>

      {/* Key Takeaways */}
      {growth.key_takeaways.length > 0 && (
        <div className="mb-5">
          <p className="font-sans text-xs font-bold uppercase tracking-wider mb-2" style={{ color: "var(--color-ink)" }}>
            Key Takeaways
          </p>
          <ul className="article-body space-y-1 pl-4 list-disc">
            {growth.key_takeaways.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Further Reading */}
      {growth.further_reading.length > 0 && (
        <div>
          <p className="meta-text font-bold uppercase tracking-wider mb-1">
            Further Reading
          </p>
          <ul className="space-y-1">
            {growth.further_reading.map((ref, i) => (
              <li key={i}>
                <a
                  href={ref.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="meta-text hover:underline"
                  style={{ color: "var(--color-accent)" }}
                >
                  {ref.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  );
}