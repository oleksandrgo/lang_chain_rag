# Component → Task Mapping

Use this mapping to generate Jira tasks from an Epic based on its **components**. Only create a task for a component that is present on the Epic.

All tasks inherit from the Epic:
- **Fix Version(s)** = Epic's fix version(s)
- **Project** = same project as the Epic
- **Epic Link** = Epic issue key (parent)

---

## 1. l10n_qa

**Meaning:** Hand off translations to the localization team.

| Field | Value |
|-------|--------|
| Issue Type | Task |
| Summary | `ES: L10N: {Epic Summary}` |
| Fix Version | Epic's fix version |
| Epic Link | Epic key (e.g. PROJ-123) |
| Assignee | oleksandr.golubishko@ringcentral.com |

---

## 2. dev_exn

**Meaning:** Implement the EXN component.

| Field | Value |
|-------|--------|
| Issue Type | Task |
| Summary | `Implement EXN component: {Epic Summary}` |
| Fix Version | Epic's fix version |
| Epic Link | Epic key |
| Assignee | To be assigned (or specify if known) |

---

## 3. dev_exr

**Meaning:** Implement the EXR component.

| Field | Value |
|-------|--------|
| Issue Type | Task |
| Summary | `Implement EXR component: {Epic Summary}` |
| Fix Version | Epic's fix version |
| Epic Link | Epic key |
| Assignee | To be assigned (or specify if known) |

---

## 4. qa_manual

**Meaning:** Run manual testing and review test artifacts (test cases, checklists, wiki).

| Field | Value |
|-------|--------|
| Issue Type | Task |
| Summary | `QA Manual: Test and review test artifacts (test cases/checklists/wiki): {Epic Summary}` |
| Fix Version | Epic's fix version |
| Epic Link | Epic key |
| Assignee | To be assigned (or specify if known) |

---

## 5. qa_automation

**Meaning:** Write or update automation test cases.

| Field | Value |
|-------|--------|
| Issue Type | Task |
| Summary | `QA Automation: Write or update automation cases: {Epic Summary}` |
| Fix Version | Epic's fix version |
| Epic Link | Epic key |
| Assignee | To be assigned (or specify if known) |

---

## Summary table (component → summary template)

| Component   | Summary template (English) |
|------------|-----------------------------|
| l10n_qa    | ES: L10N: {Epic Summary} |
| dev_exn    | Implement EXN component: {Epic Summary} |
| dev_exr    | Implement EXR component: {Epic Summary} |
| qa_manual  | QA Manual: Test and review test artifacts (test cases/checklists/wiki): {Epic Summary} |
| qa_automation | QA Automation: Write or update automation cases: {Epic Summary} |
