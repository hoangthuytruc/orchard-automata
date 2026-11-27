# Review rules: <project>

<!--
Copy to .orchard/review-rules.md. The reviewer reads it after the core checklist (references/review-checklist.md).
Project rules win over core when they disagree (docs/boundaries.md). Write only what is true for this project;
a rule true for every iOS project belongs in core.
Each rule: an id, the rule in one line, how to see a breach, and the severity a breach gets.
-->

| Id | Rule | How a breach shows | Severity |
| --- | --- | --- | --- |
| PR-1 | <rule> | <grep pattern, file, or what to read> | <Blocker / Risk / High / Medium / Low / NIT> |

## Project smells for the mechanical scan

- <pattern>: <why it is a candidate here>

## Architecture

- Layers: <names and allowed dependency direction>
- State: <pattern for screens and models>
- Navigation: <pattern>
- Dependency injection: <pattern>

## Tests

- Element lookup in UI tests: <accessibility identifiers only; how exceptions are marked>
- Test doubles: <where fixtures and fakes live>
