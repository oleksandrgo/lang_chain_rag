---
name: docs-to-test-cases
description: Generates test cases from documentation (specs, requirements, user stories) following the project's required structure (Summary, Preconditions, Steps, Keywords, Test Type, Attachments, Linked Requirements / Related Issues). Use when the user asks to create test cases from docs, convert documentation to test cases, or generate test cases from a spec/requirements.
---

# Generate Test Cases from Documentation

Creates one or more test cases from provided documentation (spec, requirements, user story, Confluence page, etc.) so that each case matches the project structure and can pass validation.

## When to Apply

- User asks to **create test cases from documentation**, **generate test cases from spec**, or **convert docs to test cases**.
- User provides or references documentation and wants test cases in the project format.
- User wants test cases that comply with `.cursor/rules/test-case-structure-guidelines.mdc`.

## Workflow

1. **Obtain the documentation**  
   From user message, attached file, or referenced URL/path. If unclear, ask for the doc or path.

2. **Extract test scenarios**  
   Identify distinct scenarios, flows, or acceptance criteria that deserve a separate test case. One scenario = one test case (or split into several if a flow is long).

3. **For each scenario, generate a full test case** using the structure in [reference.md](reference.md):
   - **Summary**: User Story, Product, Brand, Account type(s) — infer from doc or ask if missing.
   - **Preconditions**: Entry points (required); Note (optional). If doc mentions SAF account creation, plan for Attachments.
   - **Steps**: At least one; active voice, precise verbs; no vague statements.
   - **Keywords**: At least one product type, one brand, one platform (Web/Mobile); never "automated"/"automatable".
   - **Test Type**: Exactly one of `end2end`, `BDD`, `Integration`, `UI_Automation`.
   - **Attachments**: Required if preconditions include SAF account creation (.json).
   - **Linked Requirements / Related Issues**: At least one (requirement or issue; в TestIT — секция "Related Issues", Key / Type / Description).

4. **Write to draft file**  
   - **4a.** Write the generated test cases to the **draft file** `drafts/test-cases-draft.json` in the workspace. Create the `drafts/` directory if it does not exist. Use the **JSON** structure from `.cursor/rules/test-case-payload-format.mdc` (and Draft file section in [reference.md](reference.md) for draft wrapper: projectId, suiteId, testCases). Each item in testCases: summary/preconditions as HTML from the rule, steps, custom_values, related_issues. Obtain keyword IDs via `testit_get_fields(project_id)` when building the draft so that `custom_values.ids` is already filled.
   - **4b.** Tell the user the path and: "You can edit this file. When ready, say 'Create these test cases in TestIT' or 'Create in TestIT from draft' to create them from this file."

5. **Create in TestIT from draft** (on user request)  
   When the user asks to create test cases from the draft file:
   - Read the draft file (default: `drafts/test-cases-draft.json`).
   - Use `projectId` and `suiteId` from the file (or ask the user if missing). For each item in `testCases`: the object is already in the shape expected by `testit_create_case` — set `parent_id` from `suiteId`, `order` from index (or from the draft). Call `testit_create_case` via MCP for each case (see **testit-plan-create** skill for tool usage and schema).
   - Optionally run **validate-test-cases** on each case before creation.

6. **Optional validation**  
   Suggest: "Should I validate these test cases?" and run the **validate-test-cases** skill if the user agrees. Can be done before or after editing the draft, or before creating in TestIT.

## Rules for Generated Content

- **Summary**: All four sub-fields mandatory. If the doc does not state Product/Brand/Account type, infer reasonable defaults and mention in a note (e.g. "Brand/Product inferred from context; adjust if needed").
- **Steps**: Use verbs like Click, Enter, Select, Upload, Open, Check, Complete. Avoid "Verify that everything works"; use concrete checks (e.g. "Verify that the username is displayed in the top-right corner").
- **Keywords**: Use only allowed values from [reference.md](reference.md). Include at least one from Product type, one Brand, one Platform (Web or Mobile).
- **Test Type**: Choose the most appropriate; if unclear, prefer `end2end` and note it.

## Reference

Full structure, mandatory fields, and allowed keywords: [reference.md](reference.md).  
**JSON payload shape and HTML templates** (summary, preconditions, steps, relatedIssues): `.cursor/rules/test-case-payload-format.mdc`.  
Draft file path and draft wrapper (projectId, suiteId, testCases): [reference.md](reference.md) (Draft file section).  
Project rules summary: `.cursor/rules/test-case-structure-guidelines.mdc`.  
To validate generated cases: use the **validate-test-cases** skill.  
To create cases in TestIT from the draft: follow step 5 above and use **testit-plan-create** (`.cursor/skills/testit-plan-create/reference.md`) for MCP usage.
