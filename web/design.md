# News To Me — Design System

## Visual Direction

**Source of truth:** Deccan Herald-inspired traditional newspaper feel
**Vibe:** Calm, scannable, authoritative — traditional broadsheet treatment

## Typography

| Role | Font | Size |
|------|------|------|
| Masthead | Georgia, serif | 48px |
| Section headers | Georgia, serif | 24px bold |
| Article headlines | Georgia, serif | 18px bold |
| Article body | Georgia, serif | 14px |
| UI chrome | system-ui | 12px |

## Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--color-paper` | `#faf8f4` | Page background (warm off-white) |
| `--color-ink` | `#1a1a1a` | Primary text (near-black) |
| `--color-ink-muted` | `#555555` | Secondary text |
| `--color-rule` | `#cccccc` | Horizontal rules, borders |
| `--color-accent` | `#c41e3a` | Accent red (section markers, flags) |
| `--color-highlight` | `#fff3cd` | Highlighted text background |

## Spacing System

- Section padding: `24px` vertical
- Article spacing: `16px` between articles
- Grid gap: `1px` (hairline for newspaper column rules)

## Component Treatments

### Masthead
- Centered, Georgia serif, uppercase, letter-spaced
- Double-rule border above and below
- Date + edition number right-aligned

### Section Headers
- All-caps, small, letter-spaced
- Left border accent in `--color-accent`
- Hairline rule below

### Article Card
- Headline in Georgia bold
- Summary in Georgia regular
- Source URL as small muted link
- Expandable via `<details>` / `<summary>`

### Market Snapshot
- Inline table, monospace numerals
- Color-coded change (red negative, green positive)

## Responsive Strategy

| Breakpoint | Range | Layout |
|-----------|-------|--------|
| Mobile | < 768px | Single column, full-width sections |
| Tablet | 768–1023px | Constrained to max-width |
| Desktop | 1024px+ | max-width 1024px, centered |

- No horizontal scroll ever
- Main column: max-width 1024px, centered with auto margins

## No Images in V1

Images are explicitly out of scope per PRD. Text only.
