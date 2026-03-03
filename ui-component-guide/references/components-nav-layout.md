# Navigation & Structure + Layout Components

14 components for wayfinding, page structure, and content spatial arrangement.

---

## Navigation & Structure (8)

### Breadcrumbs

- **Description**: Horizontal trail showing the user's location within a site hierarchy.
- **Primary use case**: Multi-level navigation where users need to orient themselves and backtrack.
- **When to use**:
  - Site has 3+ levels of hierarchy
  - Users frequently navigate between levels
  - Page titles alone are insufficient for orientation
- **When NOT to use**:
  - Flat site structure (1–2 levels)
  - Single-page applications with no hierarchy
  - As a replacement for primary navigation
- **Accessibility**:
  - Wrap in `<nav aria-label="Breadcrumb">`
  - Use `<ol>` for ordered list semantics
  - Mark current page with `aria-current="page"`
  - Separators are decorative — use CSS or `aria-hidden="true"`
- **Related**: Navigation, Tabs

---

### Header

- **Description**: Top-of-page region containing site branding, primary navigation, and global actions (search, user menu).
- **Primary use case**: Persistent site-wide navigation and identity.
- **When to use**:
  - Every page of a multi-page application
  - As the primary container for Navigation, Search Input, Avatar
- **When NOT to use**:
  - Full-screen immersive experiences (games, media players)
  - Embedded widgets or iframes
- **Accessibility**:
  - Use `<header>` landmark element
  - Include a skip link as the first focusable element inside
  - Ensure all interactive elements are keyboard accessible
- **Related**: Footer, Navigation, Skip Link

---

### Footer

- **Description**: Bottom-of-page region containing secondary navigation, legal links, contact information, and social links.
- **Primary use case**: Site-wide secondary information and utility links.
- **When to use**:
  - Every page of a public-facing website
  - To provide copyright, privacy policy, terms of service links
- **When NOT to use**:
  - Single-screen apps where all content fits in viewport
  - Modal or overlay contexts
- **Accessibility**:
  - Use `<footer>` landmark element
  - Ensure links have descriptive text (not "click here")
- **Related**: Header, Navigation

---

### Navigation

- **Description**: Container for a set of links that help users move between pages or sections of an application.
- **Primary use case**: Primary wayfinding — the main menu of the application.
- **When to use**:
  - As the main menu in Header (horizontal) or sidebar (vertical)
  - Secondary navigation within a section
- **When NOT to use**:
  - Switching between views of the same data (use Tabs or Segmented Control)
  - Actions that don't navigate (use Button or Dropdown Menu)
- **Accessibility**:
  - Use `<nav aria-label="Main navigation">`
  - Mark current page with `aria-current="page"`
  - On mobile, hamburger menu must have `aria-expanded` and `aria-controls`
- **Related**: Breadcrumbs, Tabs, Header, Drawer

---

### Tabs

- **Description**: Horizontal set of selectable labels that switch between related panels of content within the same context.
- **Primary use case**: Organizing related content into parallel views without page navigation.
- **When to use**:
  - 2–7 peer-level content sections
  - Users need to compare or switch between views quickly
  - Content is at the same level of hierarchy
- **When NOT to use**:
  - Sequential steps (use Progress Indicator / Stepper)
  - More than 7 options (use Navigation or Select)
  - If all content should be visible at once (use Accordion or sections)
- **Accessibility**:
  - Use `role="tablist"`, `role="tab"`, `role="tabpanel"`
  - Arrow keys move between tabs; Tab key moves into the panel
  - `aria-selected="true"` on active tab
  - `aria-controls` links tab to its panel
- **Related**: Segmented Control, Navigation, Accordion

---

### Pagination

- **Description**: Controls for navigating between pages of a dataset or content list.
- **Primary use case**: Breaking large datasets into manageable pages.
- **When to use**:
  - Datasets with 20+ items
  - Users need to jump to specific pages
  - SEO requires distinct page URLs
- **When NOT to use**:
  - Short lists that fit on one page
  - Infinite scroll is preferred (social feeds, timelines)
  - Real-time data that changes frequently
- **Accessibility**:
  - Wrap in `<nav aria-label="Pagination">`
  - Current page marked with `aria-current="page"`
  - Disabled buttons use `aria-disabled="true"`, not `disabled` attribute
- **Related**: Table, List, Search Input

---

### Skip Link

- **Description**: Hidden link that becomes visible on keyboard focus, allowing users to skip directly to main content.
- **Primary use case**: Keyboard and screen reader users bypassing repetitive navigation.
- **When to use**:
  - Every page with a Header or Navigation
  - First focusable element in the DOM
- **When NOT to use**:
  - Pages with no repetitive content to skip
- **Accessibility**:
  - Must be the very first focusable element
  - Visually hidden until focused (use CSS, not `display:none`)
  - Target must have `id` and be focusable (`tabindex="-1"` if not natively focusable)
- **Related**: Header, Navigation

---

### Tree View

- **Description**: Hierarchical display of nested items, where parent nodes can be expanded or collapsed to show/hide children.
- **Primary use case**: File browsers, category navigation, organizational structures.
- **When to use**:
  - Data has parent-child relationships with multiple nesting levels
  - Users need to explore and navigate hierarchical structures
- **When NOT to use**:
  - Flat lists with no hierarchy (use List)
  - Only 2 levels of nesting (use Accordion)
  - Primary navigation (use Navigation)
- **Accessibility**:
  - Use `role="tree"`, `role="treeitem"`, `role="group"`
  - Arrow keys: Up/Down between items, Left/Right to collapse/expand
  - `aria-expanded` on expandable items
  - `aria-selected` for selectable items
- **Related**: Accordion, List, Navigation

---

## Layout (6)

### Card

- **Description**: Container for a single, self-contained entity of content (article, product, contact, task).
- **Primary use case**: Presenting collections of items in grid or stack layouts.
- **When to use**:
  - Displaying entities with mixed content types (image + text + action)
  - Grid or masonry layouts
  - Content that can be individually acted upon
- **When NOT to use**:
  - Tabular data with many columns (use Table)
  - Simple text-only lists (use List)
  - Full-width content sections (use Hero or plain sections)
- **Accessibility**:
  - If entire card is clickable, use a single `<a>` or `<button>` and avoid nested interactive elements
  - Maintain heading hierarchy within cards
  - Ensure sufficient color contrast for card borders/shadows
- **Related**: List, Table, Hero

---

### Carousel

- **Description**: Multi-slide container that displays one or a few items at a time, with controls to cycle through content.
- **Primary use case**: Showcasing featured content, image galleries, testimonials.
- **When to use**:
  - Highlighting a curated set of items (3–8)
  - Image or media galleries
  - Space-constrained areas where content must rotate
- **When NOT to use**:
  - Critical content (users often miss slides beyond the first)
  - Large datasets (use Pagination or infinite scroll)
  - If all items are equally important (use Card grid)
- **Accessibility**:
  - Pause auto-rotation when user interacts or hovers
  - Provide visible Previous/Next buttons
  - Use `aria-roledescription="carousel"` and `aria-label` for slides
  - Ensure keyboard users can navigate all slides
- **Related**: Card, Tabs, Image

---

### Drawer

- **Description**: Panel that slides in from the edge of the screen (typically left or right), overlaying or pushing main content.
- **Primary use case**: Secondary content, filters, or navigation that don't warrant a full page.
- **When to use**:
  - Mobile navigation menus
  - Filter panels on data-heavy pages
  - Detail views that shouldn't replace the current context
  - Shopping carts or quick-edit panels
- **When NOT to use**:
  - Content requiring user's immediate decision (use Modal)
  - Brief information (use Popover or Tooltip)
  - Primary page content
- **Accessibility**:
  - Trap focus inside while open
  - Provide a close button as the first or last focusable element
  - `aria-modal="true"` and `role="dialog"`
  - Restore focus to trigger element on close
  - `Escape` key closes the drawer
- **Related**: Modal, Popover, Navigation

---

### Hero

- **Description**: Large, prominent banner section at the top of a page, typically containing a headline, description, CTA, and background image or illustration.
- **Primary use case**: Landing pages and marketing sections that need strong visual impact.
- **When to use**:
  - Landing pages and home pages
  - Feature announcement sections
  - Campaign or promotional pages
- **When NOT to use**:
  - Interior pages of applications (dashboards, settings)
  - Data-heavy pages where space is at a premium
  - Every page (dilutes impact)
- **Accessibility**:
  - Background images must not contain essential text (use real text overlay)
  - Ensure sufficient contrast between text and background
  - CTA button must be keyboard accessible and clearly labeled
- **Related**: Card, Image, Button

---

### Stack

- **Description**: Layout utility that applies consistent spacing (margin/gap) between its child elements, either vertically or horizontally.
- **Primary use case**: Maintaining uniform spacing between components without manual margin management.
- **When to use**:
  - Vertical stacking of form fields, cards, or sections
  - Horizontal rows of buttons or icons
  - Any layout needing consistent spacing between siblings
- **When NOT to use**:
  - Complex grid layouts (use CSS Grid directly)
  - Single elements with no siblings
- **Accessibility**:
  - No specific ARIA requirements (layout-only component)
  - Ensure child elements maintain logical DOM order
- **Related**: Separator, Fieldset, Button Group

---

### Separator

- **Description**: Visual divider line (horizontal or vertical) between sections or groups of content.
- **Primary use case**: Visually grouping or separating related content areas.
- **When to use**:
  - Between distinct sections in a list or form
  - Inside dropdown menus to group actions
  - Between navigation groups
- **When NOT to use**:
  - Between every single item (overuse reduces effectiveness)
  - When spacing alone provides sufficient separation
- **Accessibility**:
  - Decorative separators: `role="none"` or `aria-hidden="true"`
  - Semantic separators: `<hr>` or `role="separator"`
  - If vertical and interactive (resizable panes): add `aria-orientation="vertical"` and keyboard support
- **Related**: Stack, List, Dropdown Menu
