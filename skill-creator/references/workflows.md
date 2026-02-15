# Workflow Patterns

Use these patterns when designing skill workflows. Most skills combine multiple patterns.

## Choosing Your Approach

- **Problem-first**: User describes an outcome ("I need to set up a project workspace") → the skill orchestrates the right tool calls in the right sequence.
- **Tool-first**: User has access to tools ("I have Notion MCP connected") → the skill teaches Claude the optimal workflows and best practices.

Most skills lean one direction. Knowing which framing fits helps choose the right pattern.

## Pattern 1: Sequential Workflows

For tasks that require steps in a specific order. Give Claude an overview of the process towards the beginning of SKILL.md:

```markdown
Filling a PDF form involves these steps:

1. Analyze the form (run analyze_form.py)
2. Create field mapping (edit fields.json)
3. Validate mapping (run validate_fields.py)
4. Fill the form (run fill_form.py)
5. Verify output (run verify_output.py)
```

Key techniques: explicit step ordering, dependencies between steps, validation at each stage, rollback instructions for failures.

## Pattern 2: Conditional Workflows

For tasks with branching logic, guide Claude through decision points:

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

## Pattern 3: Multi-MCP Coordination

For workflows that span multiple services or MCP servers:

```markdown
## Design-to-Development Handoff

### Phase 1: Design Export (Figma MCP)
1. Export design assets from Figma
2. Generate design specifications

### Phase 2: Asset Storage (Drive MCP)
1. Create project folder in Drive
2. Upload all assets, generate shareable links

### Phase 3: Task Creation (Linear MCP)
1. Create development tasks with asset links
2. Assign to engineering team

### Phase 4: Notification (Slack MCP)
1. Post handoff summary to #engineering
```

Key techniques: clear phase separation, data passing between MCPs, validation before moving to next phase, centralized error handling.

## Pattern 4: Iterative Refinement

For tasks where output quality improves with iteration:

```markdown
## Report Generation

### Initial Draft
1. Fetch data via MCP
2. Generate first draft report

### Quality Check
1. Run validation script: scripts/check_report.py
2. Identify issues (missing sections, formatting, data errors)

### Refinement Loop
1. Address each identified issue
2. Regenerate affected sections
3. Re-validate
4. Repeat until quality threshold met

### Finalization
1. Apply final formatting and save
```

Key techniques: explicit quality criteria, validation scripts, know when to stop iterating.

## Pattern 5: Context-Aware Tool Selection

For skills where the same outcome requires different tools depending on context:

```markdown
## Smart File Storage

### Decision Tree
1. Check file type and size
2. Determine best storage location:
   - Large files (>10MB): Use cloud storage MCP
   - Collaborative docs: Use Notion/Docs MCP
   - Code files: Use GitHub MCP
   - Temporary files: Use local storage

### Execute Storage
- Call appropriate MCP tool based on decision
- Apply service-specific metadata

### Provide Context to User
- Explain why that storage was chosen
```

Key techniques: clear decision criteria, fallback options, transparency about choices.

## Pattern 6: Domain-Specific Intelligence

For skills that encode expert knowledge beyond tool access:

```markdown
## Payment Processing with Compliance

### Before Processing (Compliance Check)
1. Fetch transaction details via MCP
2. Apply compliance rules:
   - Check sanctions lists
   - Verify jurisdiction allowances
   - Assess risk level
3. Document compliance decision

### Processing
IF compliance passed:
   - Process transaction via payment MCP
ELSE:
   - Flag for review, create compliance case

### Audit Trail
- Log all compliance checks and decisions
```

Key techniques: domain expertise embedded in logic, compliance before action, comprehensive documentation.

## Skills + MCP Integration

MCP provides tools (raw capabilities); skills provide recipes (intelligent workflows).

When building a skill that leverages MCP:

1. Document required MCP servers in the `compatibility` frontmatter field
2. List MCP tools in `allowed-tools` if restricting access
3. Provide workflow guidance for combining multiple MCP operations
4. Include fallback instructions when MCP server is unavailable
5. Add error handling for common MCP issues (connection failures, auth errors)
