---
name: epic-to-tasks
description: Generates a list of Jira tasks from an Epic based on its components (l10n_qa, dev_exn, dev_exr, qa_manual, qa_automation). Use when the user wants to create tasks for an Epic, generate implementation tasks from Epic components, plan work breakdown from an Epic, or get task specs for localization, dev EXN/EXR, or QA manual/automation. Requires Epic issue key and MCP "user-atlassian" for Jira.
compatibility: Requires MCP server "user-atlassian" for jira_get_issue and jira_get_issue_fields. Task creation in Jira is done manually or via external tool; no jira_create_issue in MCP.
---

# Epic to Tasks — Component-Based Task List

Generates a **list of Jira tasks** to implement an Epic. Each task is derived from a **component** set on the Epic. Only components from the predefined set produce tasks; others are ignored.

## When to use

- User provides an **Epic issue key** (e.g. `PROJ-456`) and wants a list of tasks to implement it.
- User asks to "create tasks from Epic", "generate tasks by components", or "break down Epic into tasks".
- User wants task specs for: localization (l10n_qa), EXN/EXR development (dev_exn, dev_exr), manual QA (qa_manual), or automation QA (qa_automation).

## Supported components

| Component     | Meaning |
|-------------|---------|
| **l10n_qa** | Hand off translations to localization team |
| **dev_exn** | Implement EXN component |
| **dev_exr** | Implement EXR component |
| **qa_manual** | Manual testing and review of test artifacts (test cases, checklists, wiki) |
| **qa_automation** | Write or update automation test cases |

Task templates (Summary, Issue Type, default Assignee where defined) are in [references/component-tasks.md](references/component-tasks.md). Read that file when generating tasks.

## Rules for all tasks

- **Fix Version:** Every task must use the **Epic’s fix version(s)**. Do not invent or change fix version.
- **Project:** All tasks belong to the **same project** as the Epic.
- **Epic Link:** Each task must be linked to the Epic (parent Epic key).
- **Summaries:** Use **English only**. Replace `{Epic Summary}` in the template with the Epic’s summary text.

## Input

1. **Epic issue key** (required) — e.g. `PROJ-456`.
2. **Optional:** Override assignees for specific components (e.g. "assign qa_manual to X"); otherwise use defaults from the reference (l10n_qa has a default assignee; others "To be assigned").

## Process

1. **Fetch the Epic**  
   Call `jira_get_issue` with the Epic key. Then call `jira_get_issue_fields` with the same key (and `include_empty: true` if needed) to get **components** and **fix version** reliably.

2. **Extract from Epic**  
   - Summary (for `{Epic Summary}` in templates)  
   - Fix version(s)  
   - Project key  
   - List of component names (e.g. from `components` or equivalent field)

3. **Match components**  
   For each Epic component, check if it is one of: `l10n_qa`, `dev_exn`, `dev_exr`, `qa_manual`, `qa_automation`.  
   If yes, generate **one task** from [references/component-tasks.md](references/component-tasks.md).  
   Ignore any other components.

4. **Build task list**  
   For each matched component, fill in:
   - Issue Type = Task  
   - Summary = template with `{Epic Summary}` replaced by Epic summary  
   - Fix Version = Epic’s fix version  
   - Epic Link = Epic key  
   - Assignee = from reference or user override  

5. **Output**  
   Return the list in the report format below. If the user prefers a machine-readable form, also output a short JSON array of task specs (summary, fixVersion, epicKey, assignee, component).

## Output format

Use this structure every time:

```markdown
# Epic to Tasks — [Epic Key]

**Epic:** [key] — [Epic summary]
**Project:** [project key]
**Fix Version:** [Epic fix version(s)]

---

## Tasks to create

| # | Component     | Issue Type | Summary | Fix Version | Epic Link | Assignee |
|---|---------------|------------|---------|-------------|-----------|----------|
| 1 | l10n_qa       | Task       | ES: L10N: … | [from Epic] | [Epic key] | … |
| 2 | …             | …          | …       | …           | …         | …        |

---

**Instructions:** Create each row as a new Jira Task in project **[project key]**, with the given Summary, Fix Version, Epic Link, and Assignee. All text in English.
```

If the Epic has **no** supported components, say so clearly and do not output an empty table.

## MCP usage

- **jira_get_issue** — `issue_key`: Epic key.  
- **jira_get_issue_fields** — `issue_key`: Epic key; use to read `components`, `fixVersions`, `project` (or project key), and summary.  
- Tool schemas: read from `mcps/user-atlassian/tools/<tool_name>.json` before calling.

## Reference

- **Task templates (English):** [references/component-tasks.md](references/component-tasks.md)
