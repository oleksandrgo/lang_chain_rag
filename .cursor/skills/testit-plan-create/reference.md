# TestIT MCP Payload Format — Reference

This reference covers **TestIT-specific** usage. The canonical payload structure (JSON schema, HTML templates for Summary and Preconditions, steps format, relatedIssues format, example payload) is in the project rule:

**`.cursor/rules/test-case-payload-format.mdc`**

Use that rule when building the exact JSON shape and copy-paste HTML. Below: how to fill `customValues` and how to call the MCP.

---

## customValues and testit_get_fields

Values for `customValues.ids` (including **Keywords** and other custom fields) come from the list returned by the MCP tool **testit_get_fields**.

1. Before building the payload, call **testit_get_fields** with argument `project_id` — the ID of the project where the test case will be created.
2. In the response, each field has `id`, `name`, `typeId` and a **values** array. Each element in `values` has `id`, `name`, `fieldId`.
3. Find the required field (e.g. with `name: "Keywords"`) and its **values** array.
4. For the chosen keywords (and other fields if needed — Test type, Status, etc.) take the **id** from the `values` elements and pass them into **customValues.ids**.

The list of allowed Keywords and other custom values is thus defined by the project and is always up to date for the target project.

---

## Creating the test case via MCP

1. **Resolve parent (suite) ID**  
   Use `testit_get_project_tree` (project_id) or `testit_get_case` (parentId/ascendants) to get the suite `parent_id`. TestIT expects a **suite** ID, not the project root.

2. **Call** `testit_create_case` with server `user-testit`. Map the payload to tool arguments: **name**, **parent_id** (suite ID), **order**, **summary**, **preconditions**, **priority**, **steps**, **related_issues** (same as payload `relatedIssues`), **custom_values** (same as payload `customValues`). Check `mcps/user-testit/tools/testit_create_case.json` for required and optional parameters.

3. **Auth**  
   If TestIT returns 401, use `testit_login` (or ensure `TESTIT_USERNAME` / `TESTIT_PASSWORD` are set), then retry.
