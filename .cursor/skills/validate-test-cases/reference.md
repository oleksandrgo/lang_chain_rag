# Test Case Structure — Reference

Validation criteria and allowed keyword lists are defined in **`.cursor/rules/test-case-structure-guidelines.mdc`**. This skill checks a test case against those criteria and returns a structured validation report.

For the expected payload structure (draft/TestIT JSON and HTML templates), see `.cursor/rules/test-case-payload-format.mdc`.

---

## Sections to check (reminder)

| Section | Required |
|--------|----------|
| Summary | User Story, Product, Brand, Account type(s) — all mandatory |
| Preconditions | Entry points required; Note optional |
| Steps | At least one; active voice; no vague statements |
| Keywords | Min. one product type, one brand, one platform (Web/Mobile) |
| Test Type | One of: end2end, BDD, Integration, UI_Automation |
| Attachments | If SAF in preconditions → .json required |
| Linked Requirements / Related Issues | At least one linked |

Details, full keyword lists, and examples: `.cursor/rules/test-case-structure-guidelines.mdc`.
