---
name: ui-component-guide
description: >
  Select and combine the right UI components for web application features and pages.
  Use when asked "which component should I use", "what components does a dashboard need",
  "propose a UI", "component recommendations", "UIコンポーネントを提案", "画面構成を考えて",
  or when building/modifying web UI and needing component selection guidance.
  Covers 60 standard web UI components across 5 categories with page-type templates
  and selection workflows.
  Do NOT use for design system generation (colors, typography, style) — use ui-ux-pro-max.
  Do NOT use for code compliance auditing — use web-design-guidelines.
  Do NOT use for creative aesthetic direction — use frontend-design.
---
# UI Component Guide

Select the right UI components and combine them into effective page layouts for web applications.

## Component Categories Overview

| Category | Count | Components |
|---|---|---|
| **Navigation & Structure** | 8 | Breadcrumbs, Header, Footer, Navigation, Tabs, Pagination, Skip Link, Tree View |
| **Layout** | 6 | Card, Carousel, Drawer, Hero, Stack, Separator |
| **Forms & Input** | 21 | Button, Button Group, Checkbox, Color Picker, Combobox, Date Input, Datepicker, Fieldset, File Upload, Form, Label, Radio Button, Rich Text Editor, Search Input, Segmented Control, Select, Slider, Stepper, Text Input, Textarea, Toggle |
| **Data Display** | 14 | Accordion, Avatar, Badge, File, Heading, Icon, Image, Link, List, Quote, Rating, Table, Video, Visually Hidden |
| **Feedback & Status** | 11 | Alert, Dropdown Menu, Empty State, Modal, Popover, Progress Bar, Progress Indicator, Skeleton, Spinner, Toast, Tooltip |

Detailed component specs: see `references/components-*.md`

## Component Selection Workflow

### Step 1: Classify the Request

| Request Type | Action |
|---|---|
| **Page composition** ("build a settings page") | Go to Step 2a |
| **Feature component** ("how to show upload progress") | Go to Step 2b |
| **Component comparison** ("Modal vs Drawer") | Go to Step 2c |

### Step 2a: Page Composition

1. Identify the page type from the user's description.
2. Read `references/page-templates.md` for the matching template.
3. Present the recommended component list organized by page zone (header, main content, sidebar, feedback).
4. Adapt the template to user-specific requirements.

Available templates: Dashboard, Form Page, Settings Page, Landing Page, E-commerce Product Page, Data Table Page, Onboarding Flow, Profile Page, Search Results Page, Error/404 Page.

### Step 2b: Feature Component Selection

Identify the user action or data type, then select:

**Choosing one from many?**
- ≤5 options → Radio Button
- 6–15 options → Select
- >15 or filterable → Combobox

**Choosing multiple?**
- Checkbox group or Multi-select

**Binary toggle?**
- Instant effect → Toggle
- Deferred (form submit) → Checkbox

**Entering text?**
- Single line → Text Input
- Multi-line → Textarea
- Formatted → Rich Text Editor

**Picking a date?**
- Keyboard-friendly → Date Input
- Visual calendar → Datepicker

**Showing status?**
- Static label → Badge
- Determinate progress → Progress Bar
- Indeterminate → Spinner
- Content placeholder → Skeleton

**Revealing content?**
- In-page expand/collapse → Accordion
- Interrupting dialog → Modal
- Side panel → Drawer
- Contextual (click) → Popover
- Brief hint (hover) → Tooltip

**Confirming action?**
- Destructive/important → Modal
- Success notification → Toast
- Inline warning → Alert

Read the relevant `references/components-*.md` for the matched component's full specification.

### Step 2c: Component Comparison

1. Read the reference files for both components.
2. Present a comparison table: purpose, interaction model, content capacity, accessibility, mobile behavior.
3. Recommend based on the user's context.

### Step 3: Cross-Cutting Concerns

After selecting components, apply these checks. See `references/cross-cutting.md` for details.

- **Responsive behavior**: How does each component adapt at mobile / tablet / desktop?
- **Loading states**: Skeleton for initial load, Spinner for actions, Progress Bar for determinate operations.
- **Empty states**: Every list, table, and data display needs an Empty State component.
- **Error states**: Every form input needs inline error; every async action needs failure feedback.
- **Accessibility**: Keyboard navigation path, ARIA roles, focus management for overlays.

### Step 4: Compose and Validate

1. List all selected components with their roles on the page.
2. Verify no redundant components (e.g., both Tabs and Segmented Control for the same purpose).
3. Check interaction flow: does the user's path through components make sense?
4. Confirm feedback coverage: every user action has a visible response.

## Quick Decision Trees

### How to show a list of items

- Scannable, few fields per item → **List**
- Rich content with actions → **Card** (in grid/stack)
- Many columns, sortable/filterable → **Table**
- Hierarchical/nested → **Tree View**
- Long list, paged → add **Pagination**

### How to collect user input

- Single value, short → **Text Input**
- Single value, long → **Textarea**
- Formatted text → **Rich Text Editor**
- Selection from list → **Select** / **Combobox** / **Radio Button** (see Step 2b)
- File → **File Upload**
- Date → **Date Input** / **Datepicker**
- Number in range → **Slider** (approximate) / **Stepper** (precise)
- Color → **Color Picker**
- Group of related inputs → **Fieldset** with **Label** on each

### How to notify the user

- Non-blocking success/info → **Toast**
- Important inline message → **Alert**
- Requires user decision → **Modal**
- Contextual help → **Tooltip** (hover) / **Popover** (click, richer content)

## Composability with Other Skills

This skill selects WHICH components to use. For the next steps:

- **Styling and design system** (colors, typography, spacing) → use `ui-ux-pro-max`
- **Compliance auditing** → use `web-design-guidelines`
- **Creative implementation** → use `frontend-design`
