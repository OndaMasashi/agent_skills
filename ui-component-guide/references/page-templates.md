# Page-Type Templates

10 common page types with recommended component compositions.

Each template provides:
- **Purpose**: What the page is for
- **Component zones**: Which components go where
- **Key patterns**: How components work together
- **Responsive notes**: Adaptation at different viewports

---

## 1. Dashboard

**Purpose**: At-a-glance overview of key metrics, recent activity, and quick actions.

| Zone | Components | Notes |
|---|---|---|
| Top bar | Header, Navigation, Search Input, Avatar | Persistent across pages |
| Summary row | Card (x3–6), Badge, Icon | Key metric cards |
| Main content | Table or List, Tabs, Pagination | Primary data view |
| Sidebar (optional) | Accordion, List, Badge | Filters or activity feed |
| Feedback layer | Toast, Skeleton, Empty State, Spinner | Loading and notification |

**Key patterns**:
- Card grid for KPI summary (3–4 across on desktop, stacked on mobile)
- Tabs to segment data views ("Overview", "Analytics", "Activity")
- Every data section must have a Skeleton loading state and an Empty State
- Badge on navigation items for notification counts
- Table for tabular data; List for activity feeds

**Responsive**:
- Desktop: Multi-column with sidebar
- Tablet: Collapse sidebar into Drawer
- Mobile: Stack vertically, summary cards scroll horizontally

---

## 2. Form Page

**Purpose**: Single-purpose data entry — registration, checkout, profile edit.

| Zone | Components | Notes |
|---|---|---|
| Header | Header, Breadcrumbs | Navigation context |
| Form container | Form, Fieldset, Label | Grouped fields |
| Input fields | Text Input, Textarea, Select, Combobox, Checkbox, Radio Button, Datepicker, File Upload, Toggle | As needed |
| Actions | Button, Button Group | Submit + Cancel |
| Feedback | Alert, Toast, Spinner | Validation and submission |

**Key patterns**:
- Group related fields in Fieldset with Legend (Address, Payment, Preferences)
- Label every input — never rely on placeholder alone
- Inline validation: show error below the specific field
- Form-level error: Alert at top summarizing issues with links to each field
- Disable submit button and show Spinner during submission
- Toast for success confirmation after redirect

**Responsive**:
- Desktop: 2-column layout for wide forms
- Mobile: Single column, full-width inputs

---

## 3. Settings Page

**Purpose**: Grouped preferences with toggles, selects, and save actions.

| Zone | Components | Notes |
|---|---|---|
| Navigation | Navigation or Tabs | Settings categories |
| Sections | Accordion or Card, Heading, Separator | Grouped settings |
| Controls | Toggle, Select, Radio Button, Checkbox, Text Input | Per-setting |
| Actions | Button | Save changes |
| Feedback | Toast, Alert | Confirmation and errors |

**Key patterns**:
- Navigation/Tabs for top-level categories (Account, Notifications, Privacy, Billing)
- Toggle for instant-effect settings; form submit for deferred changes
- If mixing instant (Toggle) and deferred (form fields), make the distinction visually clear
- Accordion for less-frequently used settings sections
- Show "Unsaved changes" Alert if user navigates away with pending changes

**Responsive**:
- Desktop: Side navigation + content area
- Mobile: Stacked navigation (or Tabs) above content

---

## 4. Landing Page

**Purpose**: Marketing page with strong visual impact, feature highlights, and call-to-action.

| Zone | Components | Notes |
|---|---|---|
| Top | Header, Navigation, Button (CTA) | Minimal navigation |
| Hero | Hero, Heading, Button | Primary message + CTA |
| Features | Card (grid), Icon, Heading | Feature showcase |
| Social proof | Quote, Avatar, Rating | Testimonials |
| Pricing | Card, Badge, Button, List | Plan comparison |
| Footer | Footer, Navigation, Link | Legal and secondary links |

**Key patterns**:
- Hero at top with single clear CTA
- Card grid for features (3 or 4 columns)
- Quote blocks with Avatar for testimonials
- Badge on pricing cards for "Popular" or "Best Value"
- Sticky CTA Button on mobile (bottom of viewport)

**Responsive**:
- Desktop: Multi-column sections
- Mobile: Full-width stacked sections, horizontal scroll for pricing cards

---

## 5. E-commerce Product Page

**Purpose**: Product details with images, pricing, variants, and purchase action.

| Zone | Components | Notes |
|---|---|---|
| Breadcrumbs | Breadcrumbs | Category hierarchy |
| Gallery | Carousel, Image | Product images |
| Details | Heading, Badge, Rating, List | Name, status, reviews, specs |
| Variants | Segmented Control, Radio Button, Select | Size, color, quantity |
| Actions | Button, Stepper | Add to cart, quantity |
| Description | Tabs or Accordion | Details, reviews, shipping |
| Related | Card (grid) | Related products |
| Feedback | Toast, Modal, Drawer | Cart confirmation |

**Key patterns**:
- Carousel for product images with thumbnail navigation
- Segmented Control or Radio Button for size/color (visual swatches)
- Stepper for quantity selection
- Tabs for product details / reviews / shipping info
- Toast or Drawer for "Added to cart" confirmation
- Badge for sale price, stock status, or shipping tags

**Responsive**:
- Desktop: 2-column (gallery left, details right)
- Mobile: Stacked — gallery → details → tabs → related

---

## 6. Data Table Page

**Purpose**: Filterable, sortable, paginated tabular data with bulk actions.

| Zone | Components | Notes |
|---|---|---|
| Header | Heading, Button, Search Input | Title + create action + search |
| Filters | Select, Combobox, Datepicker, Segmented Control, Button | Filter controls |
| Table | Table, Checkbox, Badge, Link, Dropdown Menu | Data with row actions |
| Pagination | Pagination, Select (page size) | Navigation |
| Bulk actions | Button Group, Alert | Selected row actions |
| Feedback | Skeleton, Empty State, Toast, Modal | States |

**Key patterns**:
- Search Input and filter controls above the table
- Table with sortable column headers (click to sort)
- Checkbox column for bulk selection with "Select all" header
- Dropdown Menu per row for actions (Edit, Delete, Duplicate)
- Pagination below with page size selector
- Skeleton rows during loading; Empty State when no results
- Modal for delete confirmation

**Responsive**:
- Desktop: Full table with all columns
- Tablet: Hide less important columns, add horizontal scroll
- Mobile: Switch to Card/List view or responsive table pattern

---

## 7. Onboarding Flow

**Purpose**: Multi-step wizard guiding new users through initial setup.

| Zone | Components | Notes |
|---|---|---|
| Progress | Progress Indicator | Step position |
| Content | Heading, Image or Icon, Form elements | Step content |
| Navigation | Button Group | Back / Next / Skip |
| Feedback | Alert, Toast | Validation |

**Key patterns**:
- Progress Indicator at top showing current step and total
- 3–7 steps maximum (break longer flows into sections)
- "Back" button always available (except step 1)
- "Skip" option for non-essential steps
- Validate each step before allowing "Next"
- Final step: summary of choices with "Complete" CTA
- Toast for success; redirect to main app on completion

**Responsive**:
- Desktop: Centered content area with generous whitespace
- Mobile: Full-width steps, progress indicator may simplify to "Step 2 of 5" text

---

## 8. Profile Page

**Purpose**: Display user information with edit capability.

| Zone | Components | Notes |
|---|---|---|
| Header | Avatar, Heading, Badge, Button | Photo, name, role, edit |
| Info sections | List, Heading, Separator, Link | Contact, bio, activity |
| Edit mode | Form, Text Input, Textarea, File Upload, Button | Inline or modal editing |
| Activity | List, Tabs, Pagination | Recent activity, posts |
| Feedback | Toast, Skeleton | Save confirmation, loading |

**Key patterns**:
- Large Avatar with edit overlay (camera icon) for photo change
- View/Edit toggle: either inline editing or Modal/Drawer for edit form
- Tabs for activity sections (Posts, Comments, Likes)
- Badge for role/status (Admin, Verified, Premium)
- Skeleton while profile data loads

**Responsive**:
- Desktop: 2-column (sidebar with avatar + info, main with activity)
- Mobile: Stacked — avatar → info → tabs → activity

---

## 9. Search Results Page

**Purpose**: Display filtered results with search controls and refinement options.

| Zone | Components | Notes |
|---|---|---|
| Search bar | Search Input, Button | Query input |
| Filters | Accordion, Checkbox, Radio Button, Slider, Select, Button | Refinement |
| Results info | Heading, Badge, Segmented Control | Count, sort, view toggle |
| Results | List or Card (grid), Image, Badge, Link | Result items |
| Pagination | Pagination | Page navigation |
| Feedback | Skeleton, Empty State, Spinner | Loading and no results |

**Key patterns**:
- Search Input persistent at top
- Filter sidebar with Accordion sections (Category, Price, Rating, etc.)
- Segmented Control for List/Grid view toggle
- Badge for result count and active filter tags
- Skeleton matching result card shape during loading
- Empty State with suggestions when no results found

**Responsive**:
- Desktop: Sidebar filters + results grid
- Tablet: Collapsible filter Drawer
- Mobile: Filter button → full-screen Drawer, single-column results

---

## 10. Error / 404 Page

**Purpose**: Inform user of an error and provide recovery paths.

| Zone | Components | Notes |
|---|---|---|
| Content | Empty State, Heading, Image or Icon | Error message |
| Actions | Button, Link | Recovery options |
| Navigation | Navigation, Search Input, Header | Persistent wayfinding |

**Key patterns**:
- Large, friendly illustration or icon (not technical jargon)
- Clear heading explaining what happened ("Page not found", "Something went wrong")
- Brief description with possible causes
- Primary action: "Go to home page" Button
- Secondary actions: Search Input, Link to help/support, Link to previous page
- Maintain Header/Navigation so users aren't stranded

**Responsive**:
- Same structure across all viewports
- Center content vertically and horizontally
