---
name: validate-test-cases
description: Validates test cases against the required structure (Summary, Preconditions, Steps, Keywords, Test Type, Attachments, Linked Requirements / Related Issues) and returns a structured validation report. Use when the user asks to validate, review, or check a test case; when reviewing test cases from TestIT or docs; or when verifying test case structure and completeness.
---

# Validate Test Cases

Validates a test case against the project's Test Case Structure and returns a structured **Agent Report** with a verdict for each section.

## When to Apply

- User asks to **validate**, **review**, or **check** a test case.
- User pastes or shares a test case and wants a compliance check.
- User works with test cases in TestIT, Confluence, or other docs and needs a structure review.

## Validation Process

1. **Obtain the test case**  
   From user message, attached file, or referenced artifact (e.g. TestIT). If data is incomplete, ask for the full test case or link.

2. **Check each section** against the criteria in `.cursor/rules/test-case-structure-guidelines.mdc`:
   - Summary (User Story, Product, Brand, Account type(s) — all mandatory)
   - Preconditions (Entry points required; Note optional)
   - Steps (at least one; active voice, precise verbs; no vague statements)
   - Keywords (at least one product type, one brand, one platform: Web or Mobile; no "automated"/"automatable")
   - Test Type (exactly one of: `end2end`, `BDD`, `Integration`, `UI_Automation`)
   - Attachments (if SAF account creation in preconditions → .json files required)
   - Linked Requirements / Related Issues (at least one linked; в TestIT — секция Related Issues)

3. **Build the report** using the format below. For each section assign exactly one verdict and add a short comment where needed.

## Report Format (Output)

Return the validation result in this structure. Use the exact headings and verdicts.

```markdown
# Test Case Validation Report

## Summary
**Verdict:** [✅ Ready | ✏️ Minor revision needed | ❌ Major revision needed]
**Comment:** [Short description of what is missing or incorrect, or "No changes needed."]

## Preconditions
**Verdict:** [✅ Ready | ✏️ Minor revision needed | ❌ Major revision needed]
**Comment:** [Explanation or "No changes needed."]

## Steps
**Verdict:** [✅ Ready | ✏️ Minor revision needed | ❌ Major revision needed]
**Comment:** [What to improve or "No changes needed."]

## Keywords
**Verdict:** [✅ All required keywords are present | ❌ Missing: [list missing groups or keywords]]
**Comment:** [If missing: product type / brand / platform. Do not suggest "automated" or "automatable."]

## Test Type
**Verdict:** [✅ Test type is correctly set to '[value]' | ❌ Test type is missing | ❌ Test type is incorrect (allowed: end2end, BDD, Integration, UI_Automation)]
**Comment:** [If wrong/missing: what to set.]

## Attachments
**Verdict:** [✅ Attachments are present (if applicable) | ❌ Missing required attachments]
**Comment:** [If SAF in preconditions and no .json: "Attach .json for SAF account creation." Otherwise brief note.]

## Linked Requirements / Related Issues
**Verdict:** [✅ Requirement(s) or related issue(s) linked | ❌ No linked requirements or related issues found]
**Comment:** [Brief note if none linked; в TestIT — заполнить Related Issues.]

---
**Overall:** [Ready for submit | Revision needed — see comments above.]
```

## Verdict Rules

- **✅ Ready** — Section is complete and meets the criteria.
- **✏️ Minor revision needed** — Small gaps (e.g. one optional field, wording improvements).
- **❌ Major revision needed** — Mandatory field missing, wrong format, or critical gap.

For **Keywords**, either return "✅ All required keywords are present" or list what is missing (e.g. "Missing: product type, platform"). Do not suggest keywords "automated" or "automatable".

## Reference

Full checklist, keyword lists, and examples: `.cursor/rules/test-case-structure-guidelines.mdc`. This file (reference.md): validation process and report format.
