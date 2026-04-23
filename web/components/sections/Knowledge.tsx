import type { KnowledgeSection } from "@/lib/edition-types";

interface KnowledgeProps {
  knowledge: KnowledgeSection;
}

function parseBody(body: string): string[] {
  return body.split(/\n\n/).filter((p) => p.trim().length > 0);
}

/** Render **bold** markdown as <strong>, plain text as <span> */
function renderInlineMarkdown(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    const match = part.match(/^\*\*(.+)\*\*$/);
    if (match) return <strong key={i}>{match[1]}</strong>;
    return <span key={i}>{part}</span>;
  });
}

export default function Knowledge({ knowledge }: KnowledgeProps) {
  const paragraphs = parseBody(knowledge.body);

  return (
    <article>
      <p className="tag-label mb-2">{knowledge.category}</p>

      <h3 className="article-headline mb-4">{knowledge.title}</h3>

      <div className="article-body space-y-3 mb-5">
        {paragraphs.map((para, i) => (
          <p key={i}>{renderInlineMarkdown(para.trim())}</p>
        ))}
      </div>

      {knowledge.surprising_fact && (
        <div
          className="p-3 mb-4 rounded"
          style={{ backgroundColor: "var(--color-highlight)" }}
        >
          <p className="meta-text font-bold uppercase tracking-wider mb-1" style={{ color: "var(--color-ink)" }}>
            Surprising Fact
          </p>
          <p className="article-body">{renderInlineMarkdown(knowledge.surprising_fact)}</p>
        </div>
      )}

      {knowledge.everyday_connection && (
        <div
          className="pl-3"
          style={{ borderLeft: "3px solid var(--color-accent)" }}
        >
          <p className="meta-text font-bold uppercase tracking-wider mb-1" style={{ color: "var(--color-ink)" }}>
            Everyday Connection
          </p>
          <p className="article-body">{renderInlineMarkdown(knowledge.everyday_connection)}</p>
        </div>
      )}
    </article>
  );
}
