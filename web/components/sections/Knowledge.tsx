import type { KnowledgeSection } from "@/lib/edition-types";

interface KnowledgeProps {
  knowledge: KnowledgeSection;
}

function parseBody(body: string): string[] {
  return body.split(/\n\n/).filter((p) => p.trim().length > 0);
}

export default function Knowledge({ knowledge }: KnowledgeProps) {
  const paragraphs = parseBody(knowledge.body);

  return (
    <article>
      {/* Category tag */}
      <p className="tag-label mb-2">{knowledge.category}</p>

      {/* Title */}
      <h3 className="article-headline mb-4">{knowledge.title}</h3>

      {/* Body paragraphs */}
      <div className="article-body space-y-3 mb-5">
        {paragraphs.map((para, i) => (
          <p key={i}>{para.trim()}</p>
        ))}
      </div>

      {/* Surprising Fact — highlighted callout */}
      {knowledge.surprising_fact && (
        <div
          className="p-3 mb-4 rounded"
          style={{ backgroundColor: "var(--color-highlight)" }}
        >
          <p className="font-sans text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "var(--color-ink)" }}>
            Surprising Fact
          </p>
          <p className="article-body">{knowledge.surprising_fact}</p>
        </div>
      )}

      {/* Everyday Connection — muted border-left callout */}
      {knowledge.everyday_connection && (
        <div
          className="pl-3"
          style={{ borderLeft: "3px solid var(--color-accent)" }}
        >
          <p className="font-sans text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "var(--color-ink)" }}>
            Everyday Connection
          </p>
          <p className="article-body">{knowledge.everyday_connection}</p>
        </div>
      )}
    </article>
  );
}