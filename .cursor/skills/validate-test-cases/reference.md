# Test Case Structure — Reference

Criteria and keyword lists for validation. Used by the validate-test-cases skill.

For the expected payload structure (draft/TestIT JSON and HTML templates), see `.cursor/rules/test-case-payload-format.mdc`.

---

## Required Sections

| Section | Required | Notes |
|--------|----------|--------|
| Summary | Yes | All sub-fields mandatory |
| Preconditions | Yes | Entry points required; Note optional |
| Steps | Yes | At least one step |
| Keywords | Yes | Min. one per group (see below) |
| Test Type | Yes | One of: end2end, BDD, Integration, UI_Automation |
| Attachments | Conditional | Required if SAF account creation in preconditions |
| Linked Requirements / Related Issues | Yes | At least one requirement or related issue linked (в TestIT — секция Related Issues) |

---

## Summary — Mandatory Fields

- **User Story**: list of tasks/stories that influenced the test case.
- **Product**: list of products covered.
- **Brand**: list of brands this test applies to.
- **Account type(s)**: type(s) of account required for the test.

All four must be present and filled.

---

## Preconditions

- **Entry points**: required — steps to bring the system to the initial state.
- **Note**: optional — additional context or setup.

---

## Steps

- At least **one step** required.
- Use **active voice** and precise verbs: `Click`, `Enter`, `Select`, `Upload`, `Open`, `Check`, `Complete`.
- Instructions must be **clear and unambiguous**; any person should be able to follow without extra clarification.
- **Avoid vague statements**, e.g.:
  - ❌ "Verify that everything works"
  - ❌ "Ensure the page is correct"
- **Prefer concrete**, e.g.:
  - ✅ "Verify that the username is displayed in the top-right corner of the page."

---

## Keywords — Allowed Values

**At least one** keyword from **each** group must be present. Do **not** use "automated" or "automatable" as keywords (there is a dedicated field for that).

### Product type (at least one)

- RC Office  
- RC Fax  
- RC Meetings(Freyja)

### Brands (at least one)

- All brands  
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

### Platform type (exactly one of)

- Web  
- Mobile  

---

## Test Type — Allowed Values

Exactly one of:

- `end2end`
- `BDD`
- `Integration`
- `UI_Automation`

---

## Attachments

- If preconditions mention **SAF account creation**, appropriate **.json** files must be attached.
- Otherwise: no mandatory attachments; report "Attachments are present (if applicable)" when not required.

---

## Linked Requirements / Related Issues

- The test case **must** be linked to **at least one** requirement or related issue.
- In TestIT: use the **Related Issues** section (Key, Type, Description) to link requirements or issues.
- If none: verdict "❌ No linked requirements or related issues found".
