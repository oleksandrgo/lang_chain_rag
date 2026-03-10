# Epic Structure (Reference)

Required structure for Epics in Jira. Source: `.cursor/rules/epic-structure-guidelines.mdc`.

## 1. Background
- Business and technical context.
- Explains **why** this task is needed — purpose, impact, dependencies.

## 2. Requirement
- Clear description of **what** needs to be implemented.
- System behavior, logic, expected user interaction.

## 3. List of Brands to Be Rolled Out
- "All brands" (all supported brands) or a specific list. "All brands" is sufficient — a list like RC US, RC UK is not required.

## 4. Links
- Figma mockups, technical documentation, API specs.
- Related Jira tickets or Confluence pages.

## 5. Rollout Dates
- A single rollout-to-prod date is sufficient. Start/End and phases are optional.

## 6. Acceptance Criteria
- Bullet-point checklist; conditions for completion.
- Each point testable and clearly written.

**Example AC:**
- [ ] User can access the new field on both mobile and desktop
- [ ] Input is validated against backend constraints
- [ ] Analytics event is triggered and tracked correctly
