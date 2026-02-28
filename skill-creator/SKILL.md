---

> [!IMPORTANT]
> このスキルを使用する際は、まず最初に以下のコマンドを実行して使用状況を記録してください：
> `python C:/work/utility/skills-main/skills-main/usage_logger.py skill-creator`

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Composability

Claude can load multiple skills simultaneously. Design skills to work alongside others — avoid assumptions about being the only skill loaded. Use specific triggers in the description to prevent conflicts with other skills.

### Portability

Skills work across Claude.ai, Claude Code, and API. Avoid environment-specific assumptions unless documented in the `compatibility` frontmatter field. Create a skill once and it works across all surfaces, provided the environment supports any dependencies.

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that Claude reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

- **When to include**: For documentation that Claude should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Claude produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context

#### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxilary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (Unlimited because scripts can be executed without reading into context window)

#### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

Claude loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

**Pattern 2: Domain-specific organization**

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When a user asks about sales metrics, Claude only reads sales.md.

Similarly, for skills supporting multiple frameworks or variants, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, Claude only reads aws.md.

**Pattern 3: Conditional details**

Show basic content, link to advanced content:

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Claude reads REDLINING.md or OOXML.md only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Claude can see the full scope when previewing.

## Skill Creation Process

Skill creation involves these steps:

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (run init_skill.py)
4. Edit the skill (implement resources and write SKILL.md)
5. Package the skill (run package_skill.py)
6. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

### Step 1: Define Use Cases

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

Before writing any code, identify 2-3 concrete use cases. Define each using this structured format:

```yaml
Use Case: [Name]
Trigger: User says "[specific phrases]"
Steps:
  1. [What Claude does first]
  2. [What Claude does next]
  ...
Result: [Expected output]
```

**Identify the skill category** to guide design decisions:

1. **Document & Asset Creation** — Creating consistent, high-quality output (documents, presentations, code, designs). Key techniques: embedded style guides, template structures, quality checklists.
2. **Workflow Automation** — Multi-step processes with consistent methodology. Key techniques: step-by-step workflows with validation gates, iterative refinement loops.
3. **MCP Enhancement** — Workflow guidance on top of MCP tool access. Key techniques: coordinating multiple MCP calls, embedding domain expertise, providing context users would otherwise need to specify.

**Gather understanding through questions** (avoid asking too many at once):

- "What functionality should the skill support?"
- "Can you give examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

Conclude this step when use cases are clearly defined and the skill category is identified.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

### Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

When creating a new skill from scratch, always run the `init_skill.py` script. The script conveniently generates a new template skill directory that automatically includes everything a skill requires, making the skill creation process much more efficient and reliable.

Usage:

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script:

- Creates the skill directory at the specified path
- Generates a SKILL.md template with proper frontmatter and TODO placeholders
- Creates example resource directories: `scripts/`, `references/`, and `assets/`
- Adds example files in each directory that can be customized or deleted

After initialization, customize or remove the generated SKILL.md and example files as needed.

### Step 4: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Include information that would be beneficial and non-obvious to Claude. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Claude instance execute these tasks more effectively.

#### Learn Proven Design Patterns

Consult these helpful guides based on your skill's needs:

- **Workflow design**: See references/workflows.md for 6 workflow patterns (sequential, conditional, multi-MCP, iterative, context-aware, domain-specific) and MCP integration guidance
- **Output formats**: See references/output-patterns.md for template and example patterns
- **Testing methodology**: See references/testing-guide.md for triggering tests, functional tests, success criteria, and troubleshooting
- **Frontmatter options**: See references/frontmatter-reference.md for complete field documentation
- **Distribution and sharing**: See references/distribution.md for API usage, distribution methods, and positioning guidance

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

Added scripts must be tested by actually running them to ensure there are no bugs and that the output matches what is expected. If there are many similar scripts, only a representative sample needs to be tested to ensure confidence that they all work while balancing time to completion.

Any example files and directories not needed for the skill should be deleted. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.

#### Update SKILL.md

**Writing Guidelines:** Always use imperative/infinitive form.

##### Frontmatter

Write the YAML frontmatter. See references/frontmatter-reference.md for complete field documentation.

**Required fields:**

- `name`: Skill name in kebab-case (max 64 chars, must match folder name)
- `description`: Primary triggering mechanism. Structure as: `[What it does] + [When to use it] + [Key capabilities]`
  - Include all "when to use" information here — the body is only loaded after triggering
  - Include specific phrases users would say to trigger the skill
  - Mention relevant file types if applicable

**Good example:** `"Comprehensive document creation and editing with tracked changes and comments. Use when Claude needs to create, modify, or analyze .docx files, work with tracked changes, or add comments to documents."`

**Bad example:** `"Helps with documents."` (Too vague — no trigger context, no capabilities)

**Negative triggers** — when the skill might be confused with similar skills, add exclusions:
`"...Do NOT use for plain text files or CSV processing."`

**Optional fields:**

- `license`: License reference (e.g., `MIT`, `Apache-2.0`)
- `compatibility`: Environment requirements, 1-500 chars (e.g., `"Requires Python 3.9+"`)
- `allowed-tools`: Restrict which tools Claude may use with this skill
- `metadata`: Object with `author`, `version`, `mcp-server`, `category`, `tags`, etc.

##### Body

Write instructions for using the skill and its bundled resources. Recommended body structure:

1. **Instructions** - Core procedures and workflows (the main content)
2. **Examples** - Input/output pairs or usage scenarios showing desired style and quality
3. **Troubleshooting** - Common issues and solutions (if applicable)

Put critical instructions at the top. Use `## Important` or `## Critical` headers for must-follow rules. For critical validations, prefer bundling scripts over relying on language instructions — code is deterministic; language interpretation is not.

### Step 5: Packaging a Skill

Once development of the skill is complete, it must be packaged into a distributable .skill file that gets shared with the user. The packaging process automatically validates the skill first to ensure it meets all requirements:

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory specification:

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

The packaging script will:

1. **Validate** the skill automatically, checking:

   - YAML frontmatter format and required fields
   - Skill naming conventions and directory structure
   - Description completeness and quality
   - File organization and resource references

2. **Package** the skill if validation passes, creating a .skill file named after the skill (e.g., `my-skill.skill`) that includes all files and maintains the proper directory structure for distribution. The .skill file is a zip file with a .skill extension.

If validation fails, the script will report the errors and exit without creating a package. Fix any validation errors and run the packaging command again.

### Quick Validation Checklist

Before you start:

- [ ] 2-3 concrete use cases defined (Use Case / Trigger / Steps / Result)
- [ ] Skill category identified (Document & Asset Creation, Workflow Automation, or MCP Enhancement)
- [ ] Tools identified (built-in or MCP)
- [ ] Folder structure planned

During development:

- [ ] Folder named in kebab-case, SKILL.md exists (exact spelling)
- [ ] YAML frontmatter has `---` delimiters
- [ ] Description follows `[What it does] + [When to use it] + [Key capabilities]` structure
- [ ] Negative triggers included if risk of over-triggering
- [ ] No XML tags (< >) in frontmatter
- [ ] Instructions are clear and actionable
- [ ] Error handling included
- [ ] Examples provided
- [ ] SKILL.md body under 500 lines
- [ ] References split out for content beyond essential procedures and clearly linked

Before packaging:

- [ ] All scripts tested and functional
- [ ] Frontmatter passes validation (run package_skill.py)
- [ ] No TODO placeholders remaining
- [ ] Example files from init_skill.py removed or replaced
- [ ] Tested triggering on obvious tasks
- [ ] Tested triggering on paraphrased requests
- [ ] Verified doesn't trigger on unrelated topics

After first use:

- [ ] Skill triggers on intended inputs
- [ ] Skill does NOT trigger on unrelated inputs
- [ ] Output quality meets expectations
- [ ] Iterate on description and instructions based on feedback
- [ ] Update version in metadata

### Step 6: Test and Iterate

After creating the skill, test it systematically before distributing. See references/testing-guide.md for the complete testing methodology, including success criteria definitions.

**Pro Tip: Iterate on a single task before expanding.** The most effective approach is to iterate on a single challenging task until Claude succeeds, then extract the winning approach into the skill. This leverages Claude's in-context learning and provides faster signal than broad testing. Once the foundation works, expand to multiple test cases for coverage.

**Testing dimensions:**

1. **Triggering tests**: Verify the skill activates for intended inputs and does NOT activate for unrelated inputs.
   - Should trigger: "Create a PDF report" / Should NOT trigger: "What is a PDF?"
2. **Functional tests**: Verify output quality using Given/When/Then format.
   - Given [specific input], When [user request], Then [expected output]
3. **Performance check**: Compare results with and without the skill. The skill should reduce back-and-forth messages, avoid failed tool calls, and produce consistent results.

**Iteration signals:**

- **Undertriggering** (skill does not activate when it should): Broaden description keywords, add trigger phrases
- **Overtriggering** (skill activates for unrelated queries): Add negative triggers (`Do NOT use for...`), make description more specific
- **Poor execution** (output quality is low): Add examples or scripts, check reference files are loaded, move critical instructions to top of SKILL.md

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again
