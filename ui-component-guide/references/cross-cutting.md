# Cross-Cutting Concerns

Design considerations that apply across all component selections.

---

## Responsive Adaptation Patterns

| Pattern | Components Affected | Approach |
|---|---|---|
| Stack on mobile | Card grid, Button Group | Switch from row to column at breakpoint |
| Collapse to Drawer | Navigation, Sidebar, Filters | Replace persistent panel with hamburger + Drawer |
| Full-screen overlay | Modal, Datepicker, Select | Expand to full viewport on mobile |
| Horizontal scroll | Tabs, Table, Carousel | Allow horizontal scroll with scroll indicators |
| Hide secondary | Breadcrumbs, Pagination, Table columns | Truncate or hide at small viewports |
| Simplify | Progress Indicator, Rating | Reduce to text ("Step 2/5", "4.5/5") on mobile |

**Breakpoint guidance** (common):
- Mobile: < 640px — single column, stacked layout
- Tablet: 640–1024px — 2 columns, collapsible sidebar
- Desktop: > 1024px — full layout with sidebar, multi-column grids

---

## Loading State Matrix

| User Action | Component | Pattern |
|---|---|---|
| Page initial load | Skeleton | Mirror layout shape of expected content |
| Section data fetch | Skeleton | Match Card/List/Table row shapes |
| Button action | Button (disabled + Spinner) | Inline spinner, disable button |
| Form submission | Button (disabled + Spinner) + form disable | Prevent double submit |
| Data fetch (known duration) | Progress Bar | Show percentage |
| Data fetch (unknown duration) | Spinner | Centered in content area |
| Image load | Skeleton → Image | Maintain aspect ratio placeholder |
| Lazy-loaded content | Skeleton (below fold) | Appear as user scrolls |

**Rules**:
- Always show something — never leave a blank area during load
- Skeleton for structural content (cards, lists, text blocks)
- Spinner for small, focused actions (button press, inline update)
- Progress Bar only when you know the total
- Respect `prefers-reduced-motion` — reduce or stop animation

---

## Empty State Guidelines

Every data display area must handle the empty case.

| Scenario | Heading | Description | CTA |
|---|---|---|---|
| First-time use | "No [items] yet" | Brief explanation of what this area shows | "Create your first [item]" |
| No search results | "No results found" | Suggest broadening search or checking spelling | "Clear search" or "Try a different query" |
| No filter matches | "No [items] match" | List active filters | "Clear filters" |
| Error loading | "Couldn't load [items]" | Brief error context | "Try again" |
| Permission denied | "You don't have access" | Explain what's needed | "Request access" or "Contact admin" |

**Design rules**:
- Include a friendly illustration or icon — but don't make it the primary focus
- Keep text concise: headline + 1-sentence description + CTA
- CTA button should be a primary action that resolves the empty state
- Never show an empty table/list with just column headers and no rows

---

## Error State Guidelines

### Inline Field Errors (Form Validation)

- Show error message directly below the field
- Use red/danger color + error icon
- Connect error to field via `aria-describedby`
- Show on blur (field loses focus) or on submit
- Clear error when user corrects the value

### Form-Level Errors

- Alert component at the top of the form
- Summarize all errors with links to each invalid field
- "2 errors found: [Name is required](#), [Email is invalid](#)"
- Use `role="alert"` so screen readers announce immediately

### Async Operation Errors

| Severity | Component | Behavior |
|---|---|---|
| Recoverable | Toast | "Failed to save. Try again." with retry action |
| Partial failure | Alert (inline) | "3 of 5 items updated. 2 failed." with details |
| Critical failure | Modal | "Connection lost. Your changes may not be saved." |
| Network error | Full-page Empty State | "Unable to connect" + retry button |

### Error Recovery Patterns

- Always provide a way to retry or recover
- Preserve user input on error (don't clear the form)
- For destructive actions: require confirmation Modal before executing
- Log errors for debugging but show user-friendly messages

---

## Accessibility Checklist for Component Composition

### Focus Management

- **Focus order**: Follows visual order (top-to-bottom, left-to-right)
- **Focus trapping**: Modal and Drawer must trap focus while open
- **Focus restoration**: Return focus to trigger element when overlay closes
- **Skip navigation**: Include Skip Link as the first focusable element

### ARIA Landmarks

Use landmarks to structure the page for screen reader navigation:

| Landmark | Element | Usage |
|---|---|---|
| `banner` | `<header>` | Site-wide header (once per page) |
| `navigation` | `<nav>` | Navigation groups (multiple allowed, label each) |
| `main` | `<main>` | Primary page content (once per page) |
| `complementary` | `<aside>` | Sidebar content |
| `contentinfo` | `<footer>` | Site-wide footer (once per page) |
| `search` | `<form role="search">` | Search functionality |

### Keyboard Navigation

- All interactive elements reachable via Tab key
- Arrow keys within composite widgets (Tabs, Menu, Radio Group, Tree)
- Escape closes overlays (Modal, Drawer, Popover, Tooltip, Dropdown)
- Enter/Space activates buttons and links
- Document all custom keyboard shortcuts

### Dynamic Content

- Status messages: `aria-live="polite"` (Toast, Badge count updates)
- Urgent messages: `aria-live="assertive"` or `role="alert"` (form errors)
- Loading regions: `aria-busy="true"` while loading, remove when done
- Expanded/collapsed: `aria-expanded` on triggers (Accordion, Drawer, Dropdown)

### Color and Contrast

- Text: minimum 4.5:1 contrast ratio (WCAG AA)
- Large text (18px+): minimum 3:1 contrast ratio
- Interactive boundaries: minimum 3:1 against adjacent colors
- Never use color as the only indicator — always pair with text, icon, or pattern
- Test with color blindness simulators

### Motion and Animation

- Respect `prefers-reduced-motion` media query
- Provide alternative for motion-dependent information (Carousel, Spinner, Progress)
- Auto-playing content must have pause/stop controls
- Avoid flashing content (≤3 flashes per second)
