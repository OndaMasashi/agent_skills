# Feedback & Status Components

11 components for system-to-user communication, progress indication, and contextual information.

---

### Alert

- **Description**: Prominent inline message that communicates important information, warnings, errors, or success states to the user.
- **Primary use case**: Persistent, contextual feedback that stays visible until the user addresses it or the condition changes.
- **When to use**:
  - Form validation error summary at the top of a form
  - System-wide announcements (maintenance, deprecation)
  - Inline warnings or success messages after an action
  - Page-level status information
- **When NOT to use**:
  - Transient notifications (use Toast)
  - Interrupting the user for a decision (use Modal)
  - Contextual help on hover (use Tooltip)
- **Variants**: Info (neutral), Success (positive), Warning (caution), Error/Danger (critical)
- **Accessibility**:
  - Use `role="alert"` for urgent messages (errors) — triggers immediate screen reader announcement
  - Use `role="status"` for non-urgent messages (info, success)
  - Do not use `role="alert"` on page load — only for dynamic content changes
  - Include a dismiss button with `aria-label="Dismiss"` if closable
- **Related**: Toast, Modal, Badge, Empty State

---

### Dropdown Menu

- **Description**: Overlay list of actions or navigation options that appears when triggered by a button click.
- **Primary use case**: Presenting secondary actions without cluttering the primary UI.
- **When to use**:
  - "More actions" menus (edit, delete, share, duplicate)
  - User account menus (profile, settings, logout)
  - Context menus (right-click alternatives)
  - Compact navigation for secondary links
- **When NOT to use**:
  - Selecting a form value (use Select or Combobox)
  - Primary navigation (use Navigation)
  - Complex content or forms (use Drawer or Popover)
- **Accessibility**:
  - Trigger: `aria-haspopup="true"`, `aria-expanded`
  - Menu: `role="menu"` with `role="menuitem"` children
  - Arrow keys navigate items; Enter/Space activates; Escape closes
  - Focus returns to trigger on close
  - Separator between groups: `role="separator"`
- **Related**: Select, Popover, Navigation, Button

---

### Empty State

- **Description**: Placeholder content shown when a list, table, or data area has no items to display.
- **Primary use case**: Guiding users when there's no data — providing context and a path forward.
- **When to use**:
  - First-time use ("No projects yet — create your first project")
  - Empty search results ("No results found — try a different query")
  - Empty filtered views ("No items match your filters")
  - Error states that prevent data loading
- **When NOT to use**:
  - Loading states (use Skeleton or Spinner)
  - Temporary gaps in data (use Skeleton)
- **Content pattern**: Illustration/icon + Explanatory headline + Description + Primary action (CTA button)
- **Accessibility**:
  - Ensure the empty state text is in the DOM (not just a background image)
  - CTA button must be keyboard accessible
  - Distinguish between "no data" and "error" states clearly
- **Related**: Skeleton, Alert, Card, List, Table

---

### Modal

- **Description**: Overlay dialog that appears above the page content, dimming the background and requiring user interaction before returning to the main interface.
- **Primary use case**: Capturing focused user attention for critical actions, confirmations, or self-contained tasks.
- **When to use**:
  - Destructive action confirmations ("Delete this item?")
  - Short forms that don't warrant a new page (create, rename, share)
  - Critical information requiring acknowledgment
  - Media previews (image lightbox)
- **When NOT to use**:
  - Non-critical information (use Toast or Alert)
  - Complex multi-step workflows (use a dedicated page or Drawer)
  - Frequent/repeated actions (modal fatigue — use inline editing)
  - Mobile: full-screen modals should be considered as separate pages
- **Accessibility**:
  - Trap focus inside the modal while open
  - `role="dialog"` with `aria-modal="true"` and `aria-labelledby` (title)
  - Close on Escape key press
  - Restore focus to the trigger element on close
  - Provide visible close button (X) and Cancel action
  - Background content must be `aria-hidden="true"` and `inert`
- **Related**: Drawer, Alert, Popover, Toast

---

### Popover

- **Description**: Small overlay panel triggered by a click, containing richer content than a tooltip (text, links, forms, or interactive elements).
- **Primary use case**: Contextual information or quick actions that don't warrant a Modal or Drawer.
- **When to use**:
  - Rich contextual help with links or actions
  - Quick edit forms (rename, change status)
  - Filter panels on compact layouts
  - User profile cards on hover/click
- **When NOT to use**:
  - Simple text hints (use Tooltip)
  - Full forms or complex content (use Modal or Drawer)
  - Critical confirmations (use Modal)
- **Accessibility**:
  - Trigger: `aria-haspopup="dialog"`, `aria-expanded`
  - Content: `role="dialog"` with `aria-label`
  - Close on Escape; optionally close on click outside
  - Focus moves into popover on open; returns to trigger on close
- **Related**: Tooltip, Modal, Drawer, Dropdown Menu

---

### Progress Bar

- **Description**: Horizontal bar that fills to indicate the completion percentage of an operation.
- **Primary use case**: Showing determinate progress — when the system knows how much work remains.
- **When to use**:
  - File uploads with known size
  - Multi-step processes (step 3 of 5)
  - Download progress
  - Profile completion percentage
- **When NOT to use**:
  - Unknown duration (use Spinner)
  - Page-level loading (use Skeleton)
  - Step-by-step process navigation (use Progress Indicator)
- **Accessibility**:
  - Use `<progress>` element or `role="progressbar"`
  - `aria-valuemin="0"`, `aria-valuemax="100"`, `aria-valuenow="[current]"`
  - `aria-label` describing what's progressing ("Uploading file")
  - For screen readers: announce milestones (25%, 50%, 75%, 100%) with `aria-live`
- **Related**: Spinner, Skeleton, Progress Indicator

---

### Progress Indicator

- **Description**: Visual representation of the user's position within a multi-step process (stepper/wizard).
- **Primary use case**: Multi-step forms and workflows where users need to know their position and remaining steps.
- **When to use**:
  - Checkout flows (Cart → Shipping → Payment → Confirmation)
  - Onboarding wizards
  - Multi-step form submissions
  - Setup/configuration processes
- **When NOT to use**:
  - Single-step processes
  - Non-linear processes where steps can be completed in any order
  - Simple progress of a background task (use Progress Bar)
- **Accessibility**:
  - Use `<ol>` with `<li>` for each step (ordered, semantic)
  - Current step: `aria-current="step"`
  - Completed steps: visually distinct and clickable for navigation back
  - Announce step changes to screen readers
- **Related**: Progress Bar, Tabs, Breadcrumbs

---

### Skeleton

- **Description**: Low-fidelity placeholder that mirrors the shape of content that is loading, shown before the real content appears.
- **Primary use case**: Perceived performance improvement — showing the user that content is coming rather than a blank screen.
- **When to use**:
  - Initial page load or section load
  - Before Card grids, List items, or Table rows populate
  - Image placeholders while images download
  - Text block placeholders
- **When NOT to use**:
  - User-initiated actions (use Spinner on the button)
  - Very fast loads (<200ms) — skeleton flicker is worse than no skeleton
  - Error states (use Empty State or Alert)
- **Accessibility**:
  - Use `aria-busy="true"` on the container while loading
  - Remove `aria-busy` and announce content when loaded
  - Skeleton shapes should match the actual content layout
  - Ensure skeleton animations respect `prefers-reduced-motion`
- **Related**: Spinner, Progress Bar, Empty State

---

### Spinner

- **Description**: Animated indicator (typically circular) showing that a background process is in progress with unknown duration.
- **Primary use case**: Indeterminate loading — when the system cannot predict how long an action will take.
- **When to use**:
  - Button loading state (inline spinner replacing or beside the label)
  - Small content area loading
  - API calls with unknown response time
  - Transitional states between views
- **When NOT to use**:
  - Page-level initial load (use Skeleton)
  - Known-duration processes (use Progress Bar)
  - Long waits >5 seconds (add context text or Progress Bar)
- **Accessibility**:
  - Use `role="status"` with visually hidden text ("Loading...")
  - `aria-busy="true"` on the area being updated
  - Ensure animation respects `prefers-reduced-motion`
- **Related**: Skeleton, Progress Bar, Button

---

### Toast

- **Description**: Transient notification that appears temporarily (typically 3–8 seconds) and auto-dismisses, usually at the edge of the viewport.
- **Primary use case**: Non-blocking confirmation of user actions ("Saved", "Copied to clipboard", "Email sent").
- **When to use**:
  - Success confirmations for background actions
  - Non-critical informational messages
  - Undo opportunities ("Item deleted — Undo")
- **When NOT to use**:
  - Errors requiring user action (use Alert or Modal)
  - Critical information the user must not miss
  - Persistent messages (use Alert)
  - Complex content with multiple actions
- **Accessibility**:
  - Use `role="status"` or `aria-live="polite"` (not `role="alert"` which is too aggressive)
  - Toast queue: show one at a time or stack with limit
  - Ensure dismiss button and any action buttons are keyboard accessible
  - Auto-dismiss timer should pause on hover/focus
  - Provide sufficient display time (minimum 5 seconds)
- **Related**: Alert, Modal, Badge, Snackbar

---

### Tooltip

- **Description**: Small text popup that appears on hover or keyboard focus, providing a brief description or label for an element.
- **Primary use case**: Supplementary information that clarifies an element's purpose without cluttering the UI.
- **When to use**:
  - Icon-only buttons or actions that need text explanation
  - Abbreviations or technical terms
  - Truncated text (show full text on hover)
  - Data visualization point details
- **When NOT to use**:
  - Rich content with links or actions (use Popover)
  - Essential information the user must see (use Label or inline text)
  - Mobile interfaces (no hover available — use Popover with tap)
  - Form validation errors (use inline error text)
- **Accessibility**:
  - Use `aria-describedby` pointing to the tooltip content
  - Tooltip must appear on both hover AND keyboard focus
  - Must persist long enough to be read (don't dismiss on mouse move within tooltip area)
  - `role="tooltip"` on the tooltip element
  - `Escape` key dismisses the tooltip
- **Related**: Popover, Label, Badge, Visually Hidden
