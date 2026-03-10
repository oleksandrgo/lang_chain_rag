# Test Case Structure for Generation

Use this when generating test cases from documentation. Generated cases must include all sections below and use only allowed keywords so they pass **validate-test-cases**.

---

## Required Sections (all mandatory unless marked conditional)

| Section | Required | Notes |
|--------|----------|--------|
| Summary | Yes | All sub-fields mandatory |
| Preconditions | Yes | Entry points required; Note optional |
| Steps | Yes | At least one step |
| Keywords | Yes | Min. one per group (see lists below) |
| Test Type | Yes | One of: end2end, BDD, Integration, UI_Automation |
| Attachments | If SAF in preconditions | .json for SAF account creation |
| Linked Requirements / Related Issues | Yes | At least one requirement or related issue (в TestIT — Related Issues) |

---

## Summary — Mandatory Fields

- **User Story**: tasks/stories the test case covers (from doc).
- **Product**: product(s) covered.
- **Brand**: brand(s) this test applies to.
- **Account type(s)**: account type(s) needed for the test.

All four must be present.

---

## Preconditions

- **Entry points**: required — steps to reach initial state.
- **Note**: optional — extra context or setup.  
If SAF account creation is in preconditions → add **Attachments** with .json.

---

## Steps

- At least one step. Use **active voice** and precise verbs: Click, Enter, Select, Upload, Open, Check, Complete.
- Be concrete: e.g. "Verify that the username is displayed in the top-right corner" — not "Verify that everything works."

---

## Keywords — Allowed Values

Use **at least one** from **each** group. Do **not** use "automated" or "automatable."

### Product type (at least one)

- RC Office  
- RC Fax  
- RC Meetings(Freyja)

### Brand (at least one)

- ES_Charter_SMB  
- ES_Charter_Enterprise  
- ES_Sunrise  
- ES_Frontier  
- ES_Telekom  
- ES_Unify_Office(DT-Atos)  
- ES_Versatel  
- ES_Eastlink  
- ES_MCM  
- ES_Ecotel  
- ES_Mercury  
- ES_Verizon  
- ES_Vodafone  
- ES_FedRAMP  
- ES_Rainbow  
- ES_AT&T_UB  
- ES_AVAYA  
- ES_AU  
- ES_BT  
- ES_EU  
- ES_UK  
- ES_US  
- ES_CA  
- ES_AT&T  
- ES_Telus  
- RC brands  

### Platform (exactly one)

- Web  
- Mobile  

---

## Linked Requirements / Related Issues

- At least one requirement or related issue must be linked to the test case.
- In TestIT: fill the **Related Issues** section (Key, Type, Description).
- In generated text: specify requirement ID, issue key, or doc reference.

---

## Test Type — Allowed Values

Exactly one of:

- `end2end`
- `BDD`
- `Integration`
- `UI_Automation`

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

For full validation criteria, see `.cursor/skills/validate-test-cases/reference.md`.
