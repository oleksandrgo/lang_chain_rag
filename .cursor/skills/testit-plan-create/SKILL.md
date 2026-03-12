---
name: testit-plan-create
description: Create planned test cases in TestIT via MCP and format them in the project's JSON payload format. Use when the user asks to create test cases in TestIT, plan test cases for TestIT, format test cases for the TestIT MCP server, or parse documentation into the TestIT API payload structure (summary/preconditions HTML, steps, relatedIssues, customValues). Always use this skill when creating or scheduling test cases through TestIT MCP or when the target format includes summary with User Story/Product/Brand/Account type, preconditions with Entry points, steps with name/expectedResult, and relatedIssues.
---

# TestIT: Planned Test Cases — Create & Format for MCP

This skill creates test cases in TestIT via MCP and ensures payloads match the project's JSON format (HTML summary/preconditions, steps, relatedIssues) expected by the TestIT MCP server.

## When to use

- Create or plan test cases in TestIT via MCP.
- Parse specs, user stories, or docs into the TestIT JSON payload format.
- Format an existing test case description into the exact structure required by the MCP server (summary, preconditions, steps, relatedIssues, etc.).

## Workflow

### 1. Build the payload in project format

Always build the test case in the **exact JSON structure** used by the TestIT MCP server. Full schema and HTML templates: see `.cursor/rules/test-case-payload-format.mdc`.

Required top-level fields:

- **summary** — HTML string with sections: User Story, Product, Account type(s), Brand (see reference for template).
- **preconditions** — HTML string with: Entry point(s), Entry point(s) for AQA, Note (see reference).
- **priority** — number (e.g. 2).
- **executionType** — number (e.g. 2 = Manual).
- **steps** — array of `{ "name": "<p>...</p>", "executionType": 0, "expectedResult": "<p>...</p>" }`.
- **relatedIssues** — array of `{ "key", "description", "type", "iconUrl" }` (at least one).
- **customValues** — `{ "ids": [...], "createdValues": [] }` (e.g. keyword/workflow IDs from project).
- **behaviourGroups** — array (often empty).
- **isForceUpdate** — boolean (default false).

Use the HTML snippets from `.cursor/rules/test-case-payload-format.mdc` so Summary and Preconditions match existing TestIT styling (green labels, structure).

### 2. Create the test case in TestIT via MCP

1. **Resolve parent (suite) ID**  
   Use `testit_get_project_tree` (project_id) or `testit_get_case` (parentId/ascendants) to get the suite `parent_id`. TestIT expects a **suite** ID, not the project root.

2. **Call MCP**  
   Use `call_mcp_tool` with server `user-testit`, tool `testit_create_case`, and map the JSON payload to the tool arguments:

   - **name** — short title (e.g. from User Story or first step).
   - **parent_id** — suite ID from step 1.
   - **order** — integer (e.g. 0 or next order in suite).
   - **user_story** — plain text or HTML for Summary "User Story" (tool may wrap in template).
   - **product** — from Summary "Product".
   - **brand** — from Summary "Brand".
   - **account_type** — from Summary "Account type(s)".
   - **entry_points** — from Preconditions "Entry point(s)".
   - **entry_points_aqa** — from Preconditions "Entry point(s) for AQA".
   - **priority** — same as payload (e.g. 2).
   - **steps** — same structure as in payload (array of objects with name, executionType, expectedResult).
   - **related_issues** — same as payload `relatedIssues` (key, description, type, iconUrl).
   - **custom_values** — same as payload `customValues` if the tool supports it.

3. **Check tool schema**  
   Before calling, read `mcps/user-testit/tools/testit_create_case.json` to confirm required and optional parameters and types.

4. **Auth**  
   If TestIT returns 401, use `testit_login` (or ensure `TESTIT_USERNAME` / `TESTIT_PASSWORD` are set), then retry.

### 3. Return both payload and result

- **Payload**: Output the full JSON payload (as built in step 1) so it can be used for API/MCP or documentation.
- **Result**: Summarize the result of `testit_create_case` (e.g. created case ID, or error message).

## Alignment with project rules

- Follow **test-case-structure-guidelines**: Summary (User Story, Product, Brand, Account type), Preconditions (Entry points, Note), Steps (active voice), at least one Related Issue, allowed Keywords and Test Type.
- For validation of structure and keywords, use the **validate-test-cases** skill on the payload (summary/preconditions/steps as text) before or after creating.

## Reference

- **Payload schema and HTML templates**: `.cursor/rules/test-case-payload-format.mdc` — exact JSON shape and copy-paste HTML for Summary and Preconditions.
- **TestIT MCP and testit_get_fields**: [reference.md](reference.md) (this file).
- **MCP tool descriptor**: `mcps/user-testit/tools/testit_create_case.json`.
- **Test case structure and keywords**: `.cursor/rules/test-case-structure-guidelines.mdc`.
