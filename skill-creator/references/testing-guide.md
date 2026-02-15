# Testing and Iteration Guide

Effective skill testing covers three areas: triggering, functionality, and performance.

## 1. Triggering Tests

Verify the skill activates for intended inputs and does NOT activate for unrelated inputs.

**Test template:**

| Input | Should Trigger? | Result |
|-------|----------------|--------|
| "Help me set up a new ProjectHub workspace" | Yes | |
| "I need to create a project in ProjectHub" | Yes | |
| "Initialize a ProjectHub project for Q4 planning" | Yes | |
| "What's the weather in San Francisco?" | No | |
| "Help me write Python code" | No | |
| "Create a spreadsheet" | No (unless skill handles sheets) | |

Run 10-20 test queries. Track how many trigger automatically vs. require explicit invocation. Target: 90%+ trigger rate on relevant queries.

## 2. Functional Tests

Verify the skill produces correct outputs using Given/When/Then format:

```
Test: Create project with 5 tasks
Given: Project name "Q4 Planning", 5 task descriptions
When: Skill executes workflow
Then:
  - Project created with correct name
  - 5 tasks created with correct properties
  - All tasks linked to project
  - No errors during execution
```

Test cases to cover:
- Valid outputs generated for common inputs
- Error handling works for invalid inputs
- Edge cases (empty input, large input, special characters)

## 3. Performance Comparison

Compare the same task with and without the skill enabled:

```
Without skill:
- User provides instructions each time
- Multiple back-and-forth messages needed
- Inconsistent results across sessions

With skill:
- Automatic workflow execution
- Minimal clarifying questions
- Consistent results across sessions
```

Metrics to track: tool calls, total tokens consumed, number of user corrections needed.

## Troubleshooting

### Skill Doesn't Trigger (Undertriggering)

**Signals:** Skill does not activate when expected, users must manually invoke it.

**Solutions:**
- Add more trigger phrases and keywords to the description field
- Include alternative phrasings users might say
- Mention relevant file types if applicable
- **Debug:** Ask Claude "When would you use the [skill name] skill?" — adjust based on the response

### Skill Triggers Too Often (Overtriggering)

**Signals:** Skill loads for unrelated queries, users disable it.

**Solutions:**
- Add negative triggers: `Do NOT use for simple data exploration (use data-viz skill instead).`
- Make description more specific: `Processes PDF legal documents` instead of `Processes documents`
- Clarify scope: `Use specifically for online payment workflows, not for general financial queries.`

### Instructions Not Followed

**Signals:** Skill triggers but Claude does not follow the instructions.

**Common causes and fixes:**
1. **Instructions too verbose** — Keep concise, use bullet points. Move detailed reference to separate files.
2. **Critical instructions buried** — Put important instructions at the top. Use `## Important` or `## Critical` headers.
3. **Ambiguous language** — Replace vague instructions with specific ones:
   - Bad: `Make sure to validate things properly`
   - Good: `CRITICAL: Before calling create_project, verify: project name is non-empty, at least one team member assigned, start date is not in the past`
4. **Model skipping steps** — For critical validations, bundle a script that performs checks programmatically rather than relying on language instructions. Code is deterministic; language interpretation is not.

### Large Context Issues

**Signals:** Skill seems slow or responses degraded.

**Solutions:**
- Move detailed docs from SKILL.md to `references/` and link to them
- Keep SKILL.md under 500 lines / 5,000 words
- If many skills enabled simultaneously (20-50+), consider selective enablement

### MCP Connection Issues

**Signals:** Skill loads but MCP tool calls fail.

**Checklist:**
1. Verify MCP server is connected and running
2. Check authentication (API keys valid, permissions/scopes correct)
3. Test MCP independently without the skill: "Use [Service] MCP to fetch my projects"
4. Verify skill references correct MCP tool names (case-sensitive)
