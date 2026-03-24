# Reference: Risk -> Test Focus Matrix

Use this matrix to translate code changes into test focus quickly.

## Change type mapping

- **API request/response model changed**
  - Validate backward compatibility.
  - Validate required/optional fields.
  - Validate error codes and messages.
  - Validate consumer-side parsing.

- **Business rules/validation changed**
  - Positive scenario with valid data.
  - Negative scenarios for each validation branch.
  - Boundary values and locale-specific formatting.

- **DB migration/data access changed**
  - Migration up/down in staging-like environment.
  - Data integrity before/after migration.
  - Index/query performance on representative data.

- **Auth/roles/permissions changed**
  - Access allowed for expected roles.
  - Access denied for unauthorized roles.
  - Token/session edge cases (expired/invalid/revoked).

- **Feature flags/config changed**
  - Behavior with flag ON and OFF.
  - Default value behavior for missing config.
  - Safe fallback when config service unavailable.

- **Integration/client SDK changed**
  - Contract checks with external service sandbox/mock.
  - Retry/timeout behavior.
  - Idempotency where applicable.

- **UI flow changed**
  - Main user path smoke.
  - Validation and inline errors.
  - Browser/resolution/device matrix if impact is UI-visible.

## Minimal evidence package in report

For each major checklist block include:

1. Changed file(s) or module.
2. Why this is a risk.
3. What test confirms safety.

## Example of strong checklist item

- [ ] `POST /orders`: sending payload without `customerId` returns `400` with validation code `ORD-VAL-001`; no order is persisted.

## Example of weak checklist item

- [ ] Check order creation works.
