// Style Guide — visual proof of design system
// Reference for all downstream component tickets (SCRUM-34 through SCRUM-38)

export default function StyleGuidePage() {
  return (
    <main className="max-w-3xl mx-auto p-4 py-8 space-y-12">
      <header className="text-center">
        <p className="text-xs uppercase tracking-widest" style={{ color: "var(--color-ink-muted)" }}>
          News To Me — Design System
        </p>
      </header>

      {/* ── Color Tokens ── */}
      <section>
        <h2 className="section-header">Color Tokens</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "paper", var: "--color-paper", desc: "Page background" },
            { label: "ink", var: "--color-ink", desc: "Primary text" },
            { label: "ink-muted", var: "--color-ink-muted", desc: "Secondary text" },
            { label: "rule", var: "--color-rule", desc: "Borders, dividers" },
            { label: "accent", var: "--color-accent", desc: "Section markers" },
            { label: "highlight", var: "--color-highlight", desc: "Highlighted bg" },
            { label: "positive", var: "--color-positive", desc: "Market up" },
            { label: "negative", var: "--color-negative", desc: "Market down" },
          ].map(({ label, var: token, desc }) => (
            <div key={token} className="space-y-1">
              <div
                className="h-12 w-full rounded border"
                style={{ backgroundColor: `var(${token})`, borderColor: "var(--color-rule)" }}
              />
              <p className="text-xs font-sans font-bold">{label}</p>
              <p className="text-xs" style={{ color: "var(--color-ink-muted)" }}>{desc}</p>
              <p className="text-xs font-mono" style={{ color: "var(--color-ink-muted)" }}>{token}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Typography Roles ── */}
      <section>
        <h2 className="section-header">Typography Roles</h2>
        <div className="space-y-6">
          <div>
            <p className="text-xs uppercase tracking-widest mb-1" style={{ color: "var(--color-ink-muted)" }}>Masthead</p>
            <p className="masthead">News To Me</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest mb-1" style={{ color: "var(--color-ink-muted)" }}>Section Header</p>
            <p className="section-header" style={{ fontSize: "0.875rem" }}>News</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest mb-1" style={{ color: "var(--color-ink-muted)" }}>Article Headline</p>
            <p className="article-headline">India&apos;s RBI keeps repo rate unchanged at 6.5% amid global uncertainty</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest mb-1" style={{ color: "var(--color-ink-muted)" }}>Article Body</p>
            <p className="article-body">
              The Reserve Bank of India&apos;s monetary policy committee voted 5-1 to hold the benchmark repurchase rate at 6.5% for the sixth consecutive meeting, citing persistent inflation pressures despite a slowdown in global growth.
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest mb-1" style={{ color: "var(--color-ink-muted)" }}>UI Chrome / Meta</p>
            <p className="text-xs" style={{ fontFamily: "var(--font-sans)", color: "var(--color-ink-muted)" }}>
              April 13, 2026 · Edition 42 · 4 min read
            </p>
          </div>
        </div>
      </section>

      {/* ── Spacing Scale ── */}
      <section>
        <h2 className="section-header">Spacing Scale</h2>
        <div className="space-y-3">
          {[
            { label: "section (24px)", value: "24px" },
            { label: "article (16px)", value: "16px" },
          ].map(({ label, value }) => (
            <div key={label} className="flex items-center gap-3">
              <div
                className="h-4 border-t border-dashed"
                style={{ width: value, borderColor: "var(--color-rule)" }}
              />
              <span className="text-xs" style={{ fontFamily: "var(--font-sans)", color: "var(--color-ink-muted)" }}>
                {label}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* ── Section Divider Treatment ── */}
      <section>
        <h2 className="section-header">Section Divider Treatment</h2>
        <div className="section-rule" />
        <p className="text-xs mt-2" style={{ color: "var(--color-ink-muted)", fontFamily: "var(--font-sans)" }}>
          1px solid rule below section header (--color-rule)
        </p>
      </section>

      {/* ── Article Card Anatomy ── */}
      <section>
        <h2 className="section-header">Article Card</h2>
        <div className="border-t border-b py-4 space-y-2" style={{ borderColor: "var(--color-rule)" }}>
          <p className="article-headline">Bangalore metro&apos;s Pink Line extension gets centre cabinet approval</p>
          <p className="article-body">
            The Union Cabinet has approved the extension of Bangalore Metro&apos;s Pink Line from Kempegowda to JP Nagar, adding 12 new stations across the city&apos;s southern corridor.
          </p>
          <details className="article-details">
            <summary className="text-xs cursor-pointer" style={{ color: "var(--color-accent)", fontFamily: "var(--font-sans)" }}>
              Read more
            </summary>
            <div className="mt-3 space-y-2 pt-3 border-t" style={{ borderColor: "var(--color-rule)" }}>
              <div>
                <p className="text-xs uppercase tracking-widest mb-1" style={{ color: "var(--color-ink-muted)", fontFamily: "var(--font-sans)" }}>Why it matters</p>
                <p className="article-body">The expansion will connect JP Nagar — one of the city&apos;s most densely populated residential areas — directly to the international airport via a single interchange.</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-widest mb-1" style={{ color: "var(--color-ink-muted)", fontFamily: "var(--font-sans)" }}>What to watch</p>
                <p className="article-body">Construction tender bids are expected by Q3 2026.</p>
              </div>
            </div>
          </details>
          <p className="text-xs" style={{ color: "var(--color-ink-muted)", fontFamily: "var(--font-sans)" }}>
            Source: <a href="#" style={{ color: "var(--color-accent)" }}>Deccan Herald</a>
          </p>
        </div>
      </section>

      {/* ── Breakpoints ── */}
      <section>
        <h2 className="section-header">Breakpoints</h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          {[
            { label: "Mobile", range: "< 768px", width: "100%" },
            { label: "Tablet", range: "768–1023px", width: "768px" },
            { label: "Desktop", range: "1024px+", width: "1024px" },
          ].map(({ label, range, width }) => (
            <div key={label} className="border rounded p-3" style={{ borderColor: "var(--color-rule)" }}>
              <p className="text-xs font-bold" style={{ fontFamily: "var(--font-sans)" }}>{label}</p>
              <p className="text-xs mt-1" style={{ color: "var(--color-ink-muted)", fontFamily: "var(--font-sans)" }}>{range}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Market Snapshot ── */}
      <section>
        <h2 className="section-header">Market Snapshot</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {[
            { name: "S&P 500", value: "5,234.18", change: "+0.42%", positive: true },
            { name: "NASDAQ", value: "16,428.82", change: "-0.13%", positive: false },
            { name: "NIFTY 50", value: "22,841.30", change: "+0.78%", positive: true },
            { name: "SENSEX", value: "75,412.07", change: "+0.55%", positive: true },
          ].map(({ name, value, change, positive }) => (
            <div key={name} className="border rounded p-2" style={{ borderColor: "var(--color-rule)" }}>
              <p className="text-xs" style={{ fontFamily: "var(--font-sans)", color: "var(--color-ink-muted)" }}>{name}</p>
              <p className="market-value" style={{ fontFamily: "var(--font-sans)" }}>{value}</p>
              <p className={`market-value ${positive ? "market-positive" : "market-negative"}`} style={{ fontFamily: "var(--font-sans)" }}>
                {change}
              </p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
