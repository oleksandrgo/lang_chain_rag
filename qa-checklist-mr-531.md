# Commit Change Analysis

## Scope
- **Repository:** `es/express-setup-renaissance` (project_id `12396`)
- **MR:** [531](https://git.ringcentral.com/es/express-setup-renaissance/-/merge_requests/531)
- **Code scope:** `GWA-23079 | ES: Development Rena: Add new FTUE type for quick onboarding of setup rocket`
- **Related Epic (requirements):** `GWA-23076` (Quick Onboarding routing + activation contract)
- **Confluence spec:** [ES: Sample account for visual FTUE](https://wiki.ringcentral.com/spaces/OdessaTeam/pages/1027415054/ES+Sample+account+for+visual+FTUE)
- **Target branch:** `release_26.1`
- **Source commit:** `4f0592a7bc38ee5fc0e69c0d84f22ee83082e841`
- **Changed files:** 2

## Key Technical Findings
- FTUE mapping changed in `UPSService`:
  - removed `single_visual_ftue`
  - removed `multi_visual_ftue`
  - added `quick_onboarding` (only for `licenseqty === 1`)
  - all other cases -> `disabled`
- This aligns with Epic `GWA-23076` acceptance criteria (legacy FTUE values must not be used; `quick_onboarding` only for 1 DL).
- Preference update flow remains:
  1. `GET /restapi/v1.0/account/~/extension/~/custom-preferences?ids=ftue_type` (read `Etag`)
  2. `PATCH /restapi/v1.0/account/~/extension/~/custom-preferences` with `If-Match`
  3. one retry on failed patch
- Exception handling still swallows errors (`catch (Exception $e) {}`), which can hide runtime failures.
- Unit tests expanded significantly and now verify:
  - request payload
  - headers (`If-Match`)
  - retry behavior
  - exception swallow path

## QA Testing Checklist

### 1) Smoke
- [ ] `op=confirmAccount`: Admin + RingEX(Office) + non-Webinar + non-Air + `licenseqty=1` -> `ftue_type=quick_onboarding`.
- [ ] Non-admin user -> no FTUE preference write call.
- [ ] Admin + Office + `licenseqty=3` -> `ftue_type=disabled` and Quick Onboarding is not shown.

### 2) Functional Regression
- [ ] Webinar flow -> always `disabled`.
- [ ] Air flow -> always `disabled`.
- [ ] Non-office plans -> always `disabled`.
- [ ] Excluded funnels (`s-dev-web-rc-self-us-8.0`, `s-dev-m-rc-self-us-8.0`) -> `disabled`.
- [ ] Boundary checks for `licenseqty`: `null`, `0`, `1`, `2`, `5`, `6`, empty string.
- [ ] Confirm no activation-time writes with legacy values: `single_visual_ftue` and `multi_visual_ftue`.
- [ ] For non-1 DL accounts, verify fallback requirement from Epic: not routed to Quick Onboarding, not set to `quick_onboarding`.

### 3) API / Contract Validation
- [ ] Verify GET call happens before PATCH when update is expected.
- [ ] Verify PATCH payload:
  - `records[0].id = ftue_type`
  - `records[0].value = quick_onboarding | disabled`
- [ ] Verify `If-Match` header is set from returned `Etag`.
- [ ] Simulate first PATCH failure and verify single retry with refreshed `Etag`.
- [ ] Validate end-to-end activation contract from Epic: Nova sends additional parameter for qualified 1 DL account, Rena applies `quick_onboarding`.

### 4) Data and Migrations
- [ ] Confirm no DB migration/schema changes.
- [ ] Validate tolerance of legacy values (`single_visual_ftue`, `multi_visual_ftue`) in downstream consumers.

### 5) Integrations
- [ ] Validate custom-preferences API integration in normal `confirmAccount` flow.
- [ ] Validate behavior on API failures/timeouts.
- [ ] Ensure failures are observable in monitoring/logging.
- [ ] Cross-service integration check: routing decision in Nova (1 DL) is consistent with FTUE value set by Rena.

### 6) Non-Functional (If Applicable)
- [ ] Performance: no extra calls in success path.
- [ ] Security/permissions: write path executes only for admin conditions.
- [ ] Logging/monitoring: retry/failure scenarios are traceable.

## Test Data and Environments
- **Data setup:**
  - user roles: admin / non-admin
  - product: RingEX(Office) / non-office
  - flags: webinar / air
  - `licenseqty`: `null`, `0`, `1`, `2`, `3`, `5`, `6`, empty
  - `funnelId`: normal + excluded values
  - signup/activation scenarios: ecommerce + sales agent (per Confluence)
- **Environment:**
  - staging/release aligned with `release_26.1`
  - access to API request logs/proxy for request verification (`GET` + `PATCH`)
  - ability to observe Nova -> Rena activation parameter handoff

## Risks and Open Questions
- **Risk:** Behavior for `licenseqty` 2..5 changed from `multi_visual_ftue` to `disabled`.
- **Risk:** Swallowed exceptions can mask real failures.
- **Question:** Is retirement of `multi_visual_ftue` coordinated with all consumers/analytics?
- **Question:** Should failed retries emit explicit logs/metrics?
- **Question:** Is additional parameter from Nova mandatory for setting `quick_onboarding`, or is `licenseqty` alone authoritative in all activation paths?
