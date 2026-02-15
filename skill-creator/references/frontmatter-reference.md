# YAML Frontmatter Reference

Complete reference for all SKILL.md frontmatter fields.

## Required Fields

### name (string)
- Hyphen-case only: lowercase letters, digits, and hyphens
- Must match the skill folder name
- Max 64 characters
- Cannot start/end with hyphen or contain consecutive hyphens
- Cannot include "claude" or "anthropic" (reserved)

### description (string)
- Max 1024 characters
- Cannot contain XML angle brackets (< or >)
- Structure: `[What it does] + [When to use it] + [Key capabilities]`

**Good example:**
```yaml
description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. Use when Claude needs to fill PDF forms, extract data from PDFs, merge or split PDF files, or generate PDF reports programmatically.
```

**Bad example:**
```yaml
description: Helps with PDFs.
```
(Too vague — no trigger context, no capabilities listed)

**With negative triggers:**
```yaml
description: Advanced data analysis for CSV files. Use for statistical modeling, regression, clustering. Do NOT use for simple data exploration (use data-viz skill instead).
```

## Optional Fields

### license (string)
- License reference for open-source distribution
- Common values: `MIT`, `Apache-2.0`, or `Complete terms in LICENSE.txt`

### compatibility (string, 1-500 chars)
- Environment requirements for the skill
- Examples:
  - `"Requires Python 3.9+ and pypdf library"`
  - `"Intended for Claude Code. Requires network access for API calls."`

### allowed-tools (string or list)
- Restricts which tools Claude may use when this skill is active
- Example:
  ```yaml
  allowed-tools: "Bash(python:*) Bash(npm:*) WebFetch"
  ```
- This is a restriction, not a grant — limits Claude's tool access to only listed tools

### metadata (object)
- Custom key-value pairs for additional information
- Suggested fields:
  ```yaml
  metadata:
    author: team-name
    version: '1.0.0'
    mcp-server: server-name
    category: productivity
    tags: [project-management, automation]
    documentation: https://docs.example.com
    support: support@example.com
  ```

## Security Notes

**Forbidden in frontmatter:**
- XML angle brackets (< >) — frontmatter appears in Claude's system prompt; malicious content could inject instructions
- Skills named with "claude" or "anthropic" prefix (reserved by Anthropic)

**Best practices:**
- Never include secrets, API keys, or credentials in frontmatter
- Keep description factual and specific — avoid manipulative language
