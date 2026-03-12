# Check Test Case Payload — Reference

Quick checklist and draft-file specifics. Full schema and HTML: `.cursor/rules/test-case-payload-format.mdc`.

---

## Validation checklist (per case)

- [ ] **Top-level**: summary, preconditions, priority, executionType, customValues, steps, isForceUpdate, behaviourGroups, relatedIssues present and correct types.
- [ ] **customValues**: `ids` (array), `createdValues` (array).
- [ ] **summary HTML**: Labels "User Story:", "Product:", "Account type(/s):", "Brand:" present (green styling).
- [ ] **preconditions HTML**: "Entry point(/s):", "Entry point(/s) for AQA:", "Note:" present.
- [ ] **steps**: Array length ≥ 1; each step has `name`, `executionType` (0), `expectedResult` (HTML).
- [ ] **relatedIssues**: Length ≥ 1; each item has `key`, `description`, `type`, `iconUrl` = `https://jira.ringcentral.com/secure/viewavatar?size=xsmall&avatarId=22485&avatarType=issuetype`.

---

## Draft file (`drafts/test-cases-draft.json`)

- Top-level: `projectId`, `suiteId`, `testCases` (array).
- TestIT API may use snake_case in responses; draft or MCP may use camelCase. Treat as equivalent: `custom_values` ↔ `customValues`, `related_issues` ↔ `relatedIssues`, `execution_type` ↔ `executionType`, `is_force_update` ↔ `isForceUpdate`, `behaviour_groups` ↔ `behaviourGroups`.
- Validate every object in `testCases[]` with the same rules as a single payload.

---

## When to run

1. After **docs-to-test-cases** has written the draft — run this skill on the draft.
2. After manual edits to the draft — re-run before "Create in TestIT".
3. On any pasted test case JSON — to verify format before sending to MCP.
