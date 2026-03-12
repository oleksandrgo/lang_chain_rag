# Test Case Structure for Generation

Full test case structure and allowed keywords are in **`.cursor/rules/test-case-structure-guidelines.mdc`**. Use that rule when generating each section and when choosing keywords. Below: only what is specific to this skill — Output Template (markdown) and Draft file (JSON).

---

## Output Template (markdown)

```markdown
## Test Case: [Short title]

**Summary**
- **User Story:** [from doc]
- **Product:** [product(s)]
- **Brand:** [brand(s)]
- **Account type(s):** [type(s)]

**Preconditions**
- **Entry points:** [steps to initial state]
- **Note:** [optional]

**Steps**
1. [Action in active voice.]
2. [Action.]
3. [Expected result / verification.]

**Keywords**
- [Product type], [Brand], [Platform]

**Test Type:** [end2end | BDD | Integration | UI_Automation]

**Attachments:** [None | .json for SAF if applicable]

**Linked Requirements / Related Issues:** [requirement ID, issue key or doc reference; в TestIT — заполнить секцию Related Issues]
```

---

## Draft file (JSON)

Generated test cases are written to an editable draft file in **JSON format**. The structure is the **same as the payload** sent to TestIT when creating the test case (`testit_create_case`), so you can edit and then create without conversion.

- **Path**: `drafts/test-cases-draft.json` in the workspace. Create the `drafts/` folder if it does not exist.
- **When generating the draft**: call `testit_get_fields(project_id)` to get keyword IDs and fill `custom_values.ids` in each case. Set `projectId` and `suiteId` (target suite for creation). Summary and preconditions must be HTML — use the templates in `.cursor/rules/test-case-payload-format.mdc`.
- **When creating in TestIT**: read the draft; for each item in `testCases`, pass it to `testit_create_case` with `parent_id` = `suiteId` and `order` = index (or value from draft).

**Structure of the draft file:** top level has `projectId`, `suiteId`, and `testCases` (array). Each element in `testCases` has the same shape as one test case payload: `name`, `summary`, `preconditions`, `priority`, `execution_type`, `steps`, `custom_values`, `related_issues`, `is_force_update`, `behaviour_groups`. For the exact JSON shape of one test case and the HTML for `summary`/`preconditions`, see **`.cursor/rules/test-case-payload-format.mdc`**.

Minimal example (full schema and HTML templates in the rule):

```json
{
  "projectId": 1343,
  "suiteId": 817806,
  "testCases": [
    {
      "name": "Short title for the case",
      "summary": "<p>...HTML from rule template...</p>",
      "preconditions": "<p>...HTML from rule template...</p>",
      "priority": 2,
      "execution_type": 2,
      "steps": [{ "name": "<p>Step 1</p>", "expectedResult": "<p>Expected 1</p>", "executionType": 0 }],
      "custom_values": { "ids": [], "createdValues": [] },
      "related_issues": [{ "key": "PROJ-123", "description": "Title", "type": "Task", "iconUrl": "https://jira.ringcentral.com/secure/viewavatar?size=xsmall&avatarId=22485&avatarType=issuetype" }],
      "is_force_update": false,
      "behaviour_groups": []
    }
  ]
}
```

- **custom_values.ids**: IDs from `testit_get_fields(project_id)` (e.g. Keywords field `values[].id`). Fill when generating the draft.
- **related_issues**: Always use the fixed `iconUrl` (see rule). At least one item required.
- **summary** / **preconditions**: HTML strings; use the templates from `.cursor/rules/test-case-payload-format.mdc`.

---

To validate generated cases, use the **validate-test-cases** skill.
