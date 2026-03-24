---
name: gitlab-commit-test-checklist
description: Analyze GitLab commits and changed source code in one or multiple repositories via MCP, then produce a risk-based QA testing checklist. Use when the user asks to review commits, understand code changes, assess impact, or prepare what to test after code changes.
---

# GitLab Commit Analysis -> QA Test Checklist

Use this skill to analyze commit-level changes and convert them into a practical QA checklist.

## When to use

- User asks to analyze a commit, several commits, a branch range, or MR-like change scope.
- User needs test focus after backend/frontend/config/DB/API changes.
- User wants one checklist across multiple repositories.

## Required MCP discipline

Before each MCP call, read the tool descriptor in:

- `mcps/user-GitLab_communication_server/tools/<tool>.json`

Use server:

- `user-GitLab communication server`

## Inputs to request or infer

Collect these first:

1. `project_id` or project path for each repository.
2. Scope of change:
   - one commit SHA, or
   - list of commit SHAs, or
   - compare range (`from` -> `to`), or
   - branch range.
3. Optional constraints:
   - environments/brands,
   - excluded files/patterns,
   - critical business flows to prioritize.

If project is unknown, find candidates with `search_repositories`.

## Workflow

### 1) Resolve repositories and change scope

For each repository:

- If needed: `search_repositories`.
- For commit list: `list_commits` (filter by branch/date/author).
- For single commit metadata: `get_commit`.

### 2) Collect diffs

Choose by scenario:

- Single commit -> `get_commit_diff` (`full_diff: true` when needed).
- Range/branches -> `get_branch_diffs` (`from`, `to`).
- Multiple commits -> loop through `get_commit_diff` for each SHA.

Use `excluded_file_patterns` in `get_branch_diffs` for noise reduction (for example: lock files, generated assets).

### 3) Read changed code context

For high-impact files (API contracts, validation, auth, payments, DB migrations, core business logic, feature flags):

- Fetch file content at target ref using `get_file_contents`.
- Optionally inspect repository layout with `get_repository_tree` to understand module boundaries.

### 4) Build impact map

For each changed area, map:

- **Surface**: UI / API / DB / integrations / config / infra.
- **Risk type**: regression, compatibility, data integrity, security, performance, observability.
- **Blast radius**: local module vs shared component vs cross-service.
- **Required test depth**: smoke / focused regression / full regression.

### 5) Produce QA checklist

Generate a concise, actionable checklist:

- Group by feature/module and risk.
- Include positive, negative, boundary, and rollback/error-path checks.
- Include integration checks for touched external systems.
- Include non-functional checks only when change indicates risk (performance/security/logging).

## Output format

Always return:

```markdown
# Commit Change Analysis

## Scope
- Repositories: [...]
- Compared changes: [...]
- Exclusions: [...]

## Key Technical Findings
- [Area]: [what changed] -> [risk]
- ...

## QA Testing Checklist
### 1) Smoke
- [ ] ...

### 2) Functional regression
- [ ] ...

### 3) API/contract validation
- [ ] ...

### 4) Data and migrations
- [ ] ...

### 5) Integrations
- [ ] ...

### 6) Non-functional (if applicable)
- [ ] Performance
- [ ] Security/permissions
- [ ] Logging/monitoring

## Test Data and Environments
- Data setup: ...
- Environments: ...

## Risks and Open Questions
- Risk: ...
- Question: ...
```

## Multi-repository rules

- Keep per-repo findings separate first, then create a merged checklist without duplicates.
- Mark cross-repo dependencies explicitly (for example: API provider changed in repo A, consumer in repo B).
- If repos are analyzed at different refs, warn about version skew.

## Quality rules for checklist items

Each checklist item must be:

- testable in one pass,
- specific about expected result,
- traceable to an observed code change.

Avoid vague items like "test everything around this".

## Fallback behavior

If diff is incomplete or inaccessible:

- state exactly what is missing,
- provide a provisional checklist based on available evidence,
- list the exact MCP calls still needed to finalize coverage.
