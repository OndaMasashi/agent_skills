# Distribution and Sharing

Guide for distributing skills across different surfaces.

## Distribution Methods

### Individual Users

1. Download the skill folder
2. Zip the folder (if needed)
3. Upload to Claude.ai via Settings > Capabilities > Skills
4. Or place in Claude Code skills directory

### Organization-Level

- Admins can deploy skills workspace-wide
- Automatic updates and centralized management

## Using Skills via API

For programmatic use cases — building applications, agents, or automated workflows.

Key capabilities:

- `/v1/skills` endpoint for listing and managing skills
- Add skills to Messages API requests via the `container.skills` parameter
- Version control and management through the Claude Console
- Works with the Claude Agent SDK for building custom agents

**Note:** Skills in the API require the Code Execution Tool beta.

### When to Use API vs. Claude.ai

| Use Case | Best Surface |
| --- | --- |
| End users interacting with skills directly | Claude.ai / Claude Code |
| Manual testing and iteration | Claude.ai / Claude Code |
| Individual, ad-hoc workflows | Claude.ai / Claude Code |
| Applications using skills programmatically | API |
| Production deployments at scale | API |
| Automated pipelines and agent systems | API |

## GitHub Distribution

1. **Host on GitHub** — Public repo, clear README (repo-level, not inside skill folder), example usage with screenshots
2. **Document in your MCP repo** — Link to skills from MCP docs, explain why using both together is valuable
3. **Create an installation guide:**

```markdown
## Installing the [Your Service] skill

1. Download the skill:
   - Clone repo: `git clone https://github.com/yourcompany/skills`
   - Or download ZIP from Releases

2. Install in Claude:
   - Open Claude.ai > Settings > Skills
   - Click "Upload skill"
   - Select the skill folder (zipped)

3. Enable and test:
   - Toggle on the [Your Service] skill
   - Ask Claude: "Set up a new project in [Your Service]"
```

## Positioning Your Skill

Focus on outcomes, not features:

**Good:** "The ProjectHub skill enables teams to set up complete project workspaces in seconds — including pages, databases, and templates — instead of spending 30 minutes on manual setup."

**Bad:** "The ProjectHub skill is a folder containing YAML frontmatter and Markdown instructions that calls our MCP server tools."

Highlight the MCP + skills story: "Our MCP server gives Claude access to your Linear projects. Our skills teach Claude your team's sprint planning workflow. Together, they enable AI-powered project management."

## Reference Links

- [Skills API Quickstart](https://docs.anthropic.com/en/docs/build-with-claude/skills)
- [Agent Skills open standard](https://github.com/anthropics/agent-skills)
- [Partner Skills Directory](https://claude.ai/skills) — Asana, Atlassian, Canva, Figma, Sentry, Zapier, etc.
- [Example Skills repository](https://github.com/anthropics/skills)
