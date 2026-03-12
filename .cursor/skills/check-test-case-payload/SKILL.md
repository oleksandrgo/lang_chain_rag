---
name: check-test-case-payload
description: Validates test case payload format and structure against the canonical JSON schema and HTML templates in test-case-payload-format.mdc. Use when checking output of docs-to-test-cases, validating draft file (drafts/test-cases-draft.json), or verifying a test case payload before sending to TestIT MCP.
---

# Check Test Case Payload Format

Validates that a test case (or draft file) conforms to the **payload format** defined in `.cursor/rules/test-case-payload-format.mdc`: JSON schema, HTML templates for Summary/Preconditions, steps shape, and relatedIssues format. Use after **docs-to-test-cases** generates a draft, or before calling TestIT MCP to create cases.

## When to Apply

- User asks to **check** or **validate** the output of **docs-to-test-cases** (e.g. the draft file).
- User wants to **validate payload format** or **check draft** before creating cases in TestIT.
- User references `drafts/test-cases-draft.json` or pastes a test case payload and asks for format validation.

## Input

- **Default**: Read `drafts/test-cases-draft.json` (check each item in `testCases`).
- **Alternative**: User provides a path to another JSON file, or pastes a single test case object or full draft object.

## Validation Rules (from test-case-payload-format.mdc)

Use the rule file as the single source of truth. Check the following.

### 1. JSON schema (top-level)

| Field | Required | Check |
|-------|----------|--------|
| summary | yes | String, HTML; see Summary template below |
| preconditions | yes | String, HTML; see Preconditions template below |
| priority | yes | Number (e.g. 1–3, 2 = normal) |
| executionType | yes | Number (e.g. 2 = Manual) |
| customValues | yes | Object with `ids` (array) and `createdValues` (array) |
| steps | yes | Non-empty array; each step has name, executionType, expectedResult |
| isForceUpdate | yes | Boolean (usually false) |
| behaviourGroups | yes | Array (often empty) |
| relatedIssues | yes | Non-empty array; see relatedIssues format below |

Draft file only: top-level must have `projectId`, `suiteId`, `testCases` (array). Each element in `testCases` may use camelCase or snake_case keys as per TestIT API (e.g. `customValues` vs `custom_values`); treat equivalents as the same for validation.

### 2. Summary HTML

Must contain the four green labels (exact or equivalent styling):

- `User Story:`
- `Product:`
- `Account type(/s):`
- `Brand:`

Labels use `color: rgb(102, 153, 102)` (or equivalent green). Content after each label may be empty in draft but labels must be present.

### 3. Preconditions HTML

Must contain:

- `Entry point(/s):` (green)
- `Entry point(/s) for AQA:` (blue: `rgb(7, 71, 166)`)
- `Note:` (blue)

### 4. Steps

Each step object must have:

- **name**: string (HTML, e.g. `<p>...</p>`)
- **executionType**: number (0)
- **expectedResult**: string (HTML)

### 5. relatedIssues

At least one item. Each item must have:

- **key**: string (e.g. PROJECT-123)
- **description**: string
- **type**: string (Task, Story, Bug, Epic, etc.)
- **iconUrl**: exactly `https://jira.ringcentral.com/secure/viewavatar?size=xsmall&avatarId=22485&avatarType=issuetype`

## Report Format

Return a concise report in this structure:

```markdown
# Test Case Payload Format Report

**Source:** [path or "pasted payload"]
**Cases checked:** [N]

## Draft file (if applicable)
- **projectId:** [present/missing/value]
- **suiteId:** [present/missing/value]

## Per-case results

### Case 1 [index or name]
- **JSON schema:** [✅ OK | ❌ Missing/invalid: list fields]
- **Summary HTML:** [✅ OK | ❌ Missing labels: list]
- **Preconditions HTML:** [✅ OK | ❌ Missing labels: list]
- **Steps:** [✅ OK | ❌ Invalid step(s): list]
- **relatedIssues:** [✅ OK | ❌ Missing/wrong: list]

### Case 2
...

---
**Overall:** [All cases valid | N issue(s) — fix before creating in TestIT.]
```

If a single case is validated, omit "Case 2" and use a single "Result" section.

## Workflow

1. **Obtain input**: Draft file path (default `drafts/test-cases-draft.json`), or user-provided path/paste.
2. **Load rule**: Read `.cursor/rules/test-case-payload-format.mdc` for exact schema and templates.
3. **For each test case** (in draft: each `testCases[]` item): run through the validation rules above.
4. **Output**: Fill the report format; list every missing or wrong field/label so the user (or docs-to-test-cases) can fix.

## Relation to Other Skills

- **docs-to-test-cases**: Produces the draft; run this skill on the draft to ensure payload format is correct.
- **validate-test-cases**: Validates *content* and structure (Summary/Preconditions/Steps/Keywords/Test Type, etc.) against `.cursor/rules/test-case-structure-guidelines.mdc`. Use both: this skill for format, validate-test-cases for content quality.
- **testit-plan-create**: Uses the same payload; a valid payload here is ready for `testit_create_case`.

## Reference

- Canonical schema and HTML templates: `.cursor/rules/test-case-payload-format.mdc`.
- Draft file structure: see docs-to-test-cases [reference.md](reference.md) and the same rule.
