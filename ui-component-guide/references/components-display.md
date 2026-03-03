# Data Display Components

14 components for presenting information to users.

---

### Accordion

- **Description**: Vertical stack of interactive headings that toggle the display of associated content panels. Each section can be expanded or collapsed independently.
- **Primary use case**: Presenting content in a compact, scannable format where users selectively reveal details.
- **When to use**:
  - FAQ pages
  - Settings or configuration sections
  - Long-form content that users explore selectively
  - Reducing vertical scroll on mobile
- **When NOT to use**:
  - Essential content that all users need to see (hidden by default)
  - Only 1–2 sections (use plain sections with headings)
  - Content users need to compare across sections (use Tabs or visible sections)
- **Accessibility**:
  - **Button-based**: Use `<button>` with `aria-expanded` and `aria-controls`
  - **Details/Summary**: Native HTML approach, works without JavaScript
  - Icon indicators (chevron, +/−) must have `aria-hidden="true"`
  - Heading level of triggers should fit the page's heading hierarchy
- **Related**: Tabs, Tree View, Drawer

---

### Avatar

- **Description**: Circular or rounded image representing a user, team, or entity — with fallback to initials or generic icon.
- **Primary use case**: Identifying users in lists, comments, headers, and conversation threads.
- **When to use**:
  - User profiles and account menus
  - Comment threads and chat messages
  - Team member lists and assignments
  - Activity feeds
- **When NOT to use**:
  - Product images (use Image or Card)
  - Decorative icons (use Icon)
- **Accessibility**:
  - `alt` text: user's name if informative, empty `alt=""` if decorative alongside text name
  - Initials fallback must have `aria-label` with full name
  - Status indicator (online/offline) needs screen reader text
- **Related**: Image, Icon, Badge

---

### Badge

- **Description**: Small label attached to an element indicating status, count, or metadata (e.g., "New", "3", "Beta").
- **Primary use case**: Drawing attention to status changes, counts, or categories without interrupting workflow.
- **When to use**:
  - Notification counts on navigation items
  - Status labels (Active, Pending, Archived)
  - Category or tag indicators
  - Version or feature labels (Beta, Pro)
- **When NOT to use**:
  - Long text content (use Alert or Toast)
  - Interactive status changes (use Button or Toggle)
  - Primary information display
- **Accessibility**:
  - Use `aria-label` or visually hidden text for screen readers ("3 unread notifications")
  - Color must not be the only indicator — include text or icon
  - Dynamic count changes should use `aria-live="polite"`
- **Related**: Alert, Icon, Avatar

---

### File

- **Description**: Visual representation of a file (document, image, spreadsheet) showing file name, type icon, size, and optional actions.
- **Primary use case**: Displaying uploaded or attached files in lists or detail views.
- **When to use**:
  - File attachment lists in forms or messages
  - Document management interfaces
  - Download sections
- **When NOT to use**:
  - File selection for upload (use File Upload)
  - Image previews (use Image)
- **Accessibility**:
  - File type communicated via icon and text (not icon alone)
  - Download/remove actions need clear labels
  - File size and type in accessible text
- **Related**: File Upload, Image, Link, List

---

### Heading

- **Description**: Section title element (`h1`–`h6`) that structures page content hierarchically.
- **Primary use case**: Organizing page content into scannable sections with a logical hierarchy.
- **When to use**:
  - Every content section needs a heading
  - Use `h1` for the page title (one per page)
  - Use `h2`–`h6` in descending order for subsections
- **When NOT to use**:
  - Styling text to look big (use CSS, not heading elements)
  - Labels for form fields (use Label)
- **Accessibility**:
  - Heading levels must be sequential — never skip levels (h1 → h3)
  - Screen reader users navigate by heading structure
  - One `<h1>` per page
- **Related**: Label, Separator

---

### Icon

- **Description**: Small visual symbol that represents an action, status, category, or object.
- **Primary use case**: Enhancing recognition and scannability of UI elements alongside text.
- **When to use**:
  - Alongside button labels for recognition (save icon + "Save")
  - Status indicators (check, warning, error)
  - Navigation items
  - File type indicators
- **When NOT to use**:
  - As the sole means of communication (always pair with text or tooltip)
  - Decorative purposes that add no meaning
  - Complex illustrations (use Image)
- **Accessibility**:
  - Decorative icons: `aria-hidden="true"` and `focusable="false"`
  - Meaningful icons (standalone): `aria-label` or `<title>` in SVG
  - Icon buttons: the button itself needs `aria-label`, not the icon
- **Related**: Button, Badge, Image, Avatar

---

### Image

- **Description**: Element for embedding raster or vector images with appropriate sizing, loading, and fallback behavior.
- **Primary use case**: Displaying photos, illustrations, diagrams, and visual content.
- **When to use**:
  - Product photos, hero images, article illustrations
  - User-uploaded content
  - Diagrams and charts
- **When NOT to use**:
  - Small UI symbols (use Icon)
  - User avatars (use Avatar)
  - Background decoration (use CSS background-image)
- **Accessibility**:
  - Informative images: descriptive `alt` text
  - Decorative images: `alt=""`
  - Complex images (charts, diagrams): provide text alternative nearby or `aria-describedby`
  - Use `loading="lazy"` for below-the-fold images
- **Related**: Avatar, Icon, Carousel, Card

---

### Link

- **Description**: Inline text element that navigates the user to another page, section, or resource when clicked.
- **Primary use case**: In-content navigation to related pages or resources.
- **When to use**:
  - Inline text references to other pages
  - "Read more" / "Learn more" actions
  - Breadcrumb and navigation items
  - External resource references
- **When NOT to use**:
  - Triggering actions (form submit, delete, toggle) — use Button
  - Primary navigation when Navigation component is more appropriate
- **Accessibility**:
  - Use `<a href>` element (not `<span>` with click handler)
  - Link text must be descriptive — avoid "click here" or "read more" alone
  - External links: indicate with icon and `aria-label` ("opens in new tab")
  - `target="_blank"` must include `rel="noopener noreferrer"`
- **Related**: Button, Navigation, Breadcrumbs

---

### List

- **Description**: Vertical display of related items in a scannable single-column format.
- **Primary use case**: Displaying collections of similar items (messages, tasks, contacts, settings).
- **When to use**:
  - Items with 1–3 pieces of information each
  - Vertically scannable content
  - Activity feeds, notification lists, menu items
- **When NOT to use**:
  - Items with many data fields (use Table)
  - Rich visual content per item (use Card grid)
  - Hierarchical nested data (use Tree View)
- **Accessibility**:
  - Use `<ul>` for unordered items, `<ol>` for ordered/sequential items
  - Screen readers announce list length ("list, 5 items")
  - Interactive list items: ensure each has a clear interactive target
- **Related**: Table, Card, Tree View, Pagination

---

### Quote

- **Description**: Styled block for displaying quotations with attribution.
- **Primary use case**: Highlighting testimonials, citations, or referenced text.
- **When to use**:
  - Customer testimonials
  - Article citations and pull quotes
  - Expert endorsements on landing pages
- **When NOT to use**:
  - Code blocks (use `<pre><code>`)
  - Alert messages (use Alert)
  - Emphasis of your own content (use bold or callout)
- **Accessibility**:
  - Use `<blockquote>` for block quotes, `<q>` for inline quotes
  - Include `cite` attribute or visible attribution
  - Ensure contrast and readability of quoted text
- **Related**: Card, Alert, Heading

---

### Rating

- **Description**: Display and/or input of a rating value, typically shown as stars (1–5).
- **Primary use case**: Product reviews, feedback collection, satisfaction surveys.
- **When to use**:
  - Product or service ratings
  - User feedback forms
  - Skill or difficulty level indication
- **When NOT to use**:
  - Complex scoring systems (use Slider or Text Input)
  - Binary like/dislike (use Button or Toggle)
- **Accessibility**:
  - Read-only: use `aria-label` ("Rating: 4 out of 5 stars")
  - Input mode: use radio button group semantics
  - Do not rely on star color alone — include numeric value
- **Related**: Slider, Icon, Badge

---

### Table

- **Description**: Grid of rows and columns for displaying structured, tabular data with optional sorting, filtering, and pagination.
- **Primary use case**: Comparing multiple items across many attributes.
- **When to use**:
  - Data with 4+ comparable attributes per item
  - Users need to sort, filter, or search data
  - Financial data, reports, logs, inventories
- **When NOT to use**:
  - Simple lists with 1–3 fields (use List)
  - Visual content (use Card grid)
  - Mobile-first layouts where horizontal scrolling is unacceptable
- **Accessibility**:
  - Use `<table>`, `<thead>`, `<tbody>`, `<th>`, `<td>`
  - `<th scope="col">` for column headers, `<th scope="row">` for row headers
  - `<caption>` or `aria-label` for table purpose
  - Sortable columns: `aria-sort="ascending|descending|none"` on `<th>`
  - For responsive: consider cards on mobile rather than horizontal scroll
- **Related**: List, Pagination, Card, Accordion

---

### Video

- **Description**: Embedded video player with playback controls, captions, and optional poster image.
- **Primary use case**: Displaying instructional, promotional, or user-generated video content.
- **When to use**:
  - Product demos, tutorials, and walkthroughs
  - Marketing and landing page hero sections
  - Embedded third-party video (YouTube, Vimeo)
- **When NOT to use**:
  - Background ambience (use CSS background-video, muted and autoplaying)
  - Audio-only content (use audio player)
  - GIF-like short loops (use animated image)
- **Accessibility**:
  - Provide captions/subtitles (`<track kind="captions">`)
  - Never autoplay with sound
  - Keyboard-accessible player controls
  - Provide text transcript as alternative
- **Related**: Image, Carousel, Card

---

### Visually Hidden

- **Description**: Utility that hides content visually while keeping it accessible to screen readers and assistive technology.
- **Primary use case**: Providing additional context to screen reader users that would be redundant or cluttering for sighted users.
- **When to use**:
  - Icon-only buttons that need a text label for screen readers
  - "Skip to content" link text
  - Additional context for form errors or status changes
  - Table cell context that's visually obvious but not programmatically clear
- **When NOT to use**:
  - Hiding content from all users (use `display: none` or `hidden`)
  - SEO keyword stuffing
- **Accessibility**:
  - Use CSS clip/position technique (not `display:none` or `visibility:hidden`)
  - Content remains in the accessibility tree and is announced by screen readers
- **Related**: Skip Link, Icon, Label
