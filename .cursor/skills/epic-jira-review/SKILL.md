---
name: epic-jira-review
description: Reviews Jira tickets (especially Epics) against the required epic structure (Background, Requirement, Brands, Links, Rollout Dates, Acceptance Criteria), checks wording and contradictions, and produces errors per section plus questions for the product owner. Use when the user asks to review a Jira ticket or Epic, check epic structure, validate an epic before development, or review a ticket against epic guidelines. Supports optional Confluence pages and related Jira issues via Atlassian MCP.
compatibility: Requires MCP server "user-atlassian" for Jira/Confluence. Epic structure is defined in .cursor/rules/epic-structure-guidelines.mdc — load it when applying this skill.
---

# Epic Jira Ticket Review

Reviews a Jira ticket (typically an Epic) against the project's **Epic Structure Guidelines**, checks clarity and consistency, and outputs **errors per section** plus **questions for the product owner**.

## When to Apply

- User asks to **review**, **check**, or **validate** a Jira ticket or Epic.
- User wants to ensure an Epic is ready for the development team (structure + quality).
- User provides a Jira issue key and optionally Confluence page IDs/links or related ticket keys for context.

## Required Structure (Checklist)

Use the structure from [.cursor/rules/epic-structure-guidelines.mdc](.cursor/rules/epic-structure-guidelines.mdc); if that file is not in context, use [references/epic-structure.md](references/epic-structure.md). Summary of the six required sections:

| # | Section | What to verify |
|---|--------|----------------|
| 1 | **Background** | Business/technical context; explains *why* — purpose, impact, dependencies. |
| 2 | **Requirement** | Clear description of *what* to implement; system behavior, logic, user interaction. |
| 3 | **List of Brands to Be Rolled Out** | "All brands" or a list of brands; "All brands" is sufficient — a list like RC US, RC UK is not required. |
| 4 | **Links** | Figma, docs, API specs, related Jira/Confluence. |
| 5 | **Rollout Dates** | A single rollout-to-prod date is sufficient; Start/End and phases are optional. |
| 6 | **Acceptance Criteria** | Bullet checklist; each item testable and clearly written. |

## Input

1. **Jira ticket**  
   - Prefer **issue key** (e.g. `PROJ-123`) so you can fetch it via MCP: `jira_get_issue` (server: `user-atlassian`).  
   - If the user pastes ticket content instead, use that text.

2. **Optional — Confluence pages**  
   - User may pass Confluence page IDs or (title + space key).  
   - Fetch via MCP: `confluence_get_page` (server: `user-atlassian`) with `page_id`, or `title` + `space_key`.  
   - Use this content to check alignment (e.g. requirements vs spec) and to spot contradictions.

3. **Optional — Related Jira tickets**  
   - User may pass other issue keys, or you can use `jira_get_linked_issues` for the main ticket.  
   - Fetch each with `jira_get_issue` and use for context, scope boundaries, and consistency.

**MCP usage:** Before calling any tool, read the tool descriptor from `mcps/user-atlassian/tools/<tool_name>.json` to ensure correct arguments.

## Review Process

1. **Obtain ticket content**  
   If an issue key is given, call `jira_get_issue`. If Confluence page IDs or other issue keys are given, fetch them with the appropriate MCP tools.

2. **Load Epic Structure Guidelines**  
   Read `.cursor/rules/epic-structure-guidelines.mdc` and use it as the authoritative checklist.

3. **Per-section review**  
   For each of the six sections:
   - **Presence:** Is the section present and not empty?
   - **Quality:** Does it match the guideline (e.g. Background explains *why*, Requirement describes *what*, AC items are testable)?
   - **Consistency:** If Confluence or related tickets were provided, check for alignment and contradictions.

4. **Overall quality and consistency**  
   - Wording: clear, unambiguous, no vague or conflicting statements.  
   - Internal contradictions: e.g. dates vs phases, brands vs scope.  
   - Consistency with linked Confluence/Jira content when available.

5. **Build two outputs**  
   - **Errors:** One list per section (and one for “Overall”) with concrete, actionable issues.  
   - **Questions for the product owner:** Open points that need clarification or detail before development.

## Report Format (Output)

Always return the result in this structure.

```markdown
# Epic Jira Review Report

**Ticket:** [issue key or "Pasted content"]
**Reviewed at:** [date/time if relevant]

---

## Errors by Section

### 1. Background
- [ ] [Error 1 if any]
- [ ] [Error 2 if any]
- Or: No errors.

### 2. Requirement
- [ ] …

### 3. List of Brands to Be Rolled Out
- [ ] …

### 4. Links
- [ ] …

### 5. Rollout Dates
- [ ] …

### 6. Acceptance Criteria
- [ ] …

### Overall (wording, consistency, contradictions)
- [ ] …

---

## Questions for the Product Owner

1. [Question 1 — e.g. missing detail, ambiguity, or contradiction]
2. [Question 2]
…

---

**Summary:** [One short sentence: e.g. "Ready for dev" / "Needs revision — see errors and PO questions above."]
```

## Rules

- **Errors** must be specific. Do **not** treat as errors: "All brands" in Brands (no need to list RC US, RC UK, etc.); a single rollout date in Rollout Dates (one date = when deployed to prod is sufficient).
- **Questions for PO** should focus on gaps, ambiguities, or conflicts that block clear implementation; avoid restating the same point as both an error and a question.
- If Confluence or related tickets were used, briefly note in the report that they were considered (e.g. "Compared with Confluence page X and linked ticket Y").
- If the user did not provide an issue key and only pasted text, say so and perform the review on the pasted content only; you can still suggest fetching the ticket by key for links/Confluence next time.

## Reference

- **Primary:** [.cursor/rules/epic-structure-guidelines.mdc](.cursor/rules/epic-structure-guidelines.mdc) — read when applying this skill.
- **Fallback:** [references/epic-structure.md](references/epic-structure.md) — same six sections in short form if the rule file is not available.
