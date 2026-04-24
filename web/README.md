# News To Me — Frontend

Personal daily digital newspaper built with Next.js 16 + App Router + Tailwind CSS v4.

## Commands

```bash
# Development
npm run dev

# Production build (static export for Vercel)
npm run build

# Type checking
npm run type-check
```

## Architecture

- **Framework:** Next.js 16.2.4 with App Router
- **Styling:** Tailwind CSS v4 via `@theme` CSS tokens (no tailwind.config.ts)
- **Output:** Static export (`output: 'export'`) — no server runtime
- **Data:** Pipeline writes `edition.json` → `web/public/data/edition.json` → imported at build time by server components
- **TypeScript:** strict mode

## Section Order (PRD order)

1. TLDR
2. News (Bangalore → Karnataka → India → US → World)
3. Biz/Tech (market snapshot first)
4. Growth
5. Knowledge
6. Fun
