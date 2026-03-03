# Forms & Input Components

21 components for data capture, user actions, and input manipulation.

---

### Button

- **Description**: Interactive element that triggers an action when clicked (submit, save, delete, navigate).
- **Primary use case**: Any action the user can take — the most fundamental interactive component.
- **When to use**:
  - Triggering form submission, API calls, or state changes
  - Primary, secondary, and tertiary actions on a page
  - Call-to-action (CTA) elements
- **When NOT to use**:
  - Navigating to another page (use Link)
  - Toggling a binary state (use Toggle)
- **Variants**: Primary (main CTA), Secondary (alternative), Tertiary/Ghost (low-emphasis), Danger (destructive), Icon-only
- **Accessibility**:
  - Use `<button>` element (not `<div>` or `<a>` styled as button)
  - Icon-only buttons need `aria-label`
  - Disabled state: prefer explaining why over disabling; if disabled, use `aria-disabled="true"`
  - Loading state: add Spinner and `aria-busy="true"`
- **Related**: Link, Button Group, Toggle

---

### Button Group

- **Description**: Wrapper that groups related buttons together visually and semantically.
- **Primary use case**: Actions that belong together (e.g., Save / Cancel, formatting toolbar).
- **When to use**:
  - Multiple related actions (align, format, zoom)
  - Split buttons (primary action + dropdown for alternatives)
  - Toolbar sections
- **When NOT to use**:
  - Unrelated actions (place separately)
  - View switching (use Segmented Control or Tabs)
- **Accessibility**:
  - Use `role="group"` with `aria-label` describing the group's purpose
  - Maintain logical tab order within the group
- **Related**: Button, Segmented Control, Stack

---

### Checkbox

- **Description**: Input allowing selection of zero or more options from a set, or toggling a single binary option.
- **Primary use case**: Multi-select from a list, or agreeing to terms / enabling a setting within a form.
- **When to use**:
  - Multiple selections allowed from a list
  - Single opt-in/opt-out within a form context
  - "Select all" patterns
- **When NOT to use**:
  - Single selection from mutually exclusive options (use Radio Button)
  - Instant on/off effect (use Toggle)
  - Large option sets (use multi-select Combobox)
- **Accessibility**:
  - Use `<input type="checkbox">` with associated `<label>`
  - Indeterminate state (partial selection): set via JavaScript `checkbox.indeterminate = true`
  - Group related checkboxes in `<fieldset>` with `<legend>`
- **Related**: Toggle, Radio Button, Select

---

### Color Picker

- **Description**: Specialized input for selecting a color value, typically with a visual palette and/or text input for hex/RGB values.
- **Primary use case**: Theme customization, design tools, branding settings.
- **When to use**:
  - User needs to choose an arbitrary color
  - Custom theme or branding configuration
- **When NOT to use**:
  - Choosing from a predefined set of colors (use Radio Button or Select with color swatches)
  - Non-visual settings
- **Accessibility**:
  - Provide text input alternative (hex/RGB) alongside visual picker
  - Label the input clearly ("Background color", not just "Color")
  - Ensure the selected color is communicated to screen readers
- **Related**: Text Input, Select, Slider

---

### Combobox

- **Description**: Text input combined with a dropdown list, allowing users to filter options by typing or select from the list.
- **Primary use case**: Selecting from large option sets where filtering by typing is essential.
- **When to use**:
  - 15+ options where users know what they're looking for
  - Options that can be filtered by text (city, country, user name)
  - Autocomplete / typeahead patterns
- **When NOT to use**:
  - ≤5 options (use Radio Button)
  - 6–15 options that are easy to scan (use Select)
  - Free-text input without predefined options (use Text Input)
- **Accessibility**:
  - Use `role="combobox"` on input, `role="listbox"` on options
  - `aria-expanded`, `aria-autocomplete`, `aria-activedescendant`
  - Arrow keys navigate options; Enter selects; Escape closes
- **Related**: Select, Search Input, Text Input

---

### Date Input

- **Description**: Multi-field text input for entering dates (day, month, year) via keyboard.
- **Primary use case**: Date entry where keyboard input is preferred over a visual calendar.
- **When to use**:
  - Known dates (birthdate, invoice date) where users type rather than browse
  - Accessibility-sensitive contexts where a visual calendar may be difficult
  - Date ranges with start and end fields
- **When NOT to use**:
  - Browsing available dates (use Datepicker)
  - Selecting relative dates ("last 7 days") — use Select or custom control
- **Accessibility**:
  - Label each field segment (day, month, year)
  - Validate input and provide clear error messages for invalid dates
  - Support common date formats (locale-aware)
- **Related**: Datepicker, Text Input

---

### Datepicker

- **Description**: Visual calendar overlay that allows users to select a date by browsing months and clicking a day.
- **Primary use case**: Selecting dates when browsing a calendar is more intuitive than typing.
- **When to use**:
  - Booking and scheduling (hotel check-in, appointment)
  - When the day-of-week context matters
  - Date range selection with visual feedback
- **When NOT to use**:
  - Known dates like birthdate (use Date Input — faster to type)
  - Dates far in the past or future (calendar browsing is slow)
- **Accessibility**:
  - Calendar grid uses `role="grid"` with arrow key navigation
  - Selected date announced with `aria-selected="true"`
  - Provide keyboard shortcut to jump months/years
  - Include a text input fallback for keyboard-only users
- **Related**: Date Input, Modal, Popover

---

### Fieldset

- **Description**: Semantic wrapper that groups related form fields with a legend/title.
- **Primary use case**: Organizing forms into logical sections (address, payment, preferences).
- **When to use**:
  - Grouping related radio buttons or checkboxes
  - Sectioning long forms into labeled areas
  - Multi-field inputs (address: street, city, zip)
- **When NOT to use**:
  - Single input fields
  - Non-form content grouping (use Card or section headings)
- **Accessibility**:
  - Use `<fieldset>` with `<legend>` — screen readers announce the legend for each field inside
  - Nest fieldsets sparingly (avoid more than 2 levels)
- **Related**: Form, Label, Checkbox, Radio Button

---

### File Upload

- **Description**: Input control that allows users to select files from their device for upload.
- **Primary use case**: Uploading documents, images, or data files.
- **When to use**:
  - Document submission (resumes, reports, invoices)
  - Image/media upload (profile photo, gallery)
  - Data import (CSV, Excel)
- **When NOT to use**:
  - Capturing photos in real-time (use camera API)
  - Text content that can be pasted (use Textarea)
- **Accessibility**:
  - Use `<input type="file">` with clear label
  - Show accepted file types and size limits before upload
  - Provide upload progress feedback (Progress Bar or percentage)
  - Announce upload completion to screen readers
- **Related**: Button, Progress Bar, File

---

### Form

- **Description**: Container element that groups input controls for structured data submission.
- **Primary use case**: Any multi-field data entry (registration, checkout, settings).
- **When to use**:
  - Collecting structured user input (name, email, password)
  - Multi-step data entry flows
  - Any submit-to-server interaction
- **When NOT to use**:
  - Single instant-effect controls (use Toggle or Button directly)
  - Display-only content
- **Accessibility**:
  - Use `<form>` element with clear submit button
  - Associate all errors with their fields via `aria-describedby`
  - Show form-level error summary at the top using Alert
  - Support form submission via Enter key
- **Related**: Fieldset, Label, Button, Alert

---

### Label

- **Description**: Text label associated with a form input, identifying what information the field expects.
- **Primary use case**: Every form input must have a label.
- **When to use**:
  - Always — every Text Input, Select, Checkbox, etc. needs a Label
  - Above or beside the input field
- **When NOT to use**:
  - Decorative text that isn't associated with an input
  - As a heading for a form section (use `<legend>` inside Fieldset)
- **Accessibility**:
  - Use `<label for="inputId">` to explicitly associate with the input
  - Never rely on placeholder text as the only label
  - Include required field indicator and helper text as needed
- **Related**: Text Input, Fieldset, Form

---

### Radio Button

- **Description**: Input allowing selection of exactly one option from a mutually exclusive set.
- **Primary use case**: Choosing one option from a small, visible set.
- **When to use**:
  - 2–5 mutually exclusive options
  - All options should be visible simultaneously
  - Users need to compare options before choosing
- **When NOT to use**:
  - More than 5 options (use Select or Combobox)
  - Multiple selections allowed (use Checkbox)
  - Binary toggle (use Toggle or single Checkbox)
- **Accessibility**:
  - Group in `<fieldset>` with `<legend>` describing the choice
  - Arrow keys navigate between options within the group
  - One option should be pre-selected (avoid "no selection" state)
- **Related**: Select, Checkbox, Segmented Control, Toggle

---

### Rich Text Editor

- **Description**: WYSIWYG content editor that allows users to create formatted text with headings, bold, italic, lists, links, and embedded media.
- **Primary use case**: Content authoring where formatting control is needed (blog posts, comments, documentation).
- **When to use**:
  - User-generated content requiring formatting
  - CMS content editing
  - Email composition
- **When NOT to use**:
  - Simple text input (use Textarea)
  - Code editing (use code editor component)
  - Short single-line values (use Text Input)
- **Accessibility**:
  - Toolbar buttons need proper `aria-label` and `aria-pressed` states
  - Keyboard shortcuts for formatting (Ctrl+B for bold, etc.)
  - Provide Markdown or plain-text fallback
- **Related**: Textarea, Text Input

---

### Search Input

- **Description**: Text input specifically designed for search queries, typically with a search icon and clear button.
- **Primary use case**: Site-wide or section-specific content search.
- **When to use**:
  - Global search in Header
  - Filtering within a data table or list
  - Command palette / quick navigation
- **When NOT to use**:
  - Filtering a small set of options (use Select or Segmented Control)
  - Navigating to a known URL (use Navigation)
- **Accessibility**:
  - Use `<input type="search">` or `role="searchbox"`
  - Wrap in `<form role="search">` with `aria-label`
  - Provide a visible submit button (not just Enter key)
  - Clear button needs `aria-label="Clear search"`
- **Related**: Combobox, Text Input, Navigation

---

### Segmented Control

- **Description**: Set of 2–5 buttons that act as a toggle between mutually exclusive views or modes.
- **Primary use case**: Switching between different views of the same data (list/grid, day/week/month).
- **When to use**:
  - 2–5 options that switch the display mode
  - Compact alternative to Tabs when space is limited
  - Toolbar view toggles
- **When NOT to use**:
  - Form input (use Radio Button)
  - Navigation between pages (use Tabs or Navigation)
  - Many options (use Select or Tabs)
- **Accessibility**:
  - Use `role="radiogroup"` with `role="radio"` on each segment
  - Arrow keys navigate between segments
  - `aria-checked="true"` on selected segment
- **Related**: Tabs, Radio Button, Button Group

---

### Select

- **Description**: Dropdown control that reveals a list of options, from which the user selects one.
- **Primary use case**: Single selection from a moderate list where options don't need to be visible simultaneously.
- **When to use**:
  - 6–15 options
  - Options are straightforward and don't require comparison
  - Space is limited (compact form layouts)
- **When NOT to use**:
  - ≤5 options (use Radio Button — all visible)
  - >15 options (use Combobox — filterable)
  - Multiple selections (use Checkbox group or multi-select)
- **Accessibility**:
  - Native `<select>` is most accessible; custom selects need full keyboard support
  - Custom: `role="listbox"` with `role="option"`, arrow keys, type-ahead
  - `aria-expanded` on trigger, `aria-selected` on chosen option
- **Related**: Combobox, Radio Button, Dropdown Menu

---

### Slider

- **Description**: Input that allows users to select a value (or range) by dragging a handle along a track.
- **Primary use case**: Selecting an approximate value within a continuous range.
- **When to use**:
  - Volume, brightness, or opacity controls
  - Price range filters
  - Values where precision isn't critical
- **When NOT to use**:
  - Precise numeric input (use Stepper or Text Input)
  - Very large ranges with meaningful specific values
  - Mobile forms (small touch targets)
- **Accessibility**:
  - Use `<input type="range">` or `role="slider"`
  - `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, `aria-valuetext`
  - Arrow keys adjust value; support larger increments with Page Up/Down
- **Related**: Stepper, Text Input, Progress Bar

---

### Stepper

- **Description**: Numeric input with increment (+) and decrement (−) buttons for precise value adjustment.
- **Primary use case**: Selecting a precise numeric value (quantity, count, number of items).
- **When to use**:
  - Quantity selection (e-commerce cart)
  - Small numeric ranges (1–10)
  - Values that increment in fixed steps
- **When NOT to use**:
  - Large value ranges (use Slider or Text Input)
  - Approximate values (use Slider)
  - Non-numeric input
- **Accessibility**:
  - Use `role="spinbutton"` with `aria-valuemin`, `aria-valuemax`, `aria-valuenow`
  - Up/Down arrow keys to increment/decrement
  - +/− buttons need `aria-label` ("Increase quantity", "Decrease quantity")
- **Related**: Slider, Text Input

---

### Text Input

- **Description**: Single-line text field for short-form data entry.
- **Primary use case**: Any short text value — name, email, URL, phone number.
- **When to use**:
  - Single-line text values
  - Email, password, URL, phone, search queries
  - Numeric values that may include formatting (phone numbers, credit cards)
- **When NOT to use**:
  - Multi-line text (use Textarea)
  - Selecting from predefined options (use Select, Combobox, or Radio Button)
  - File paths (use File Upload)
- **Accessibility**:
  - Always pair with Label via `for`/`id`
  - Use appropriate `type` attribute (email, tel, url, password)
  - Use `aria-describedby` for helper text and error messages
  - `autocomplete` attribute for autofill support
- **Related**: Textarea, Label, Combobox, Search Input

---

### Textarea

- **Description**: Multi-line text field for longer-form content input.
- **Primary use case**: Comments, descriptions, messages, and notes.
- **When to use**:
  - Multi-line free text (comments, feedback, bio)
  - Content that may be a few sentences to a few paragraphs
- **When NOT to use**:
  - Single-line values (use Text Input)
  - Formatted content (use Rich Text Editor)
  - Code editing (use dedicated code editor)
- **Accessibility**:
  - Always pair with Label
  - Set sensible default `rows` to indicate expected length
  - Use `aria-describedby` for character count and helper text
  - Allow resize (don't disable `resize` CSS property without reason)
- **Related**: Text Input, Rich Text Editor

---

### Toggle

- **Description**: Switch control that immediately activates or deactivates a setting (on/off).
- **Primary use case**: Settings that take effect immediately without a form submit.
- **When to use**:
  - Instant-effect on/off settings (dark mode, notifications, airplane mode)
  - Feature flags visible to users
  - Preferences that apply immediately
- **When NOT to use**:
  - Form fields that require explicit submission (use Checkbox)
  - Choosing from options (use Radio Button or Select)
  - Actions (use Button)
- **Accessibility**:
  - Use `role="switch"` with `aria-checked`
  - Label must clearly describe the ON state ("Enable notifications")
  - Announce state change to screen readers
  - Provide visual on/off text labels, not just color
- **Related**: Checkbox, Radio Button, Button
