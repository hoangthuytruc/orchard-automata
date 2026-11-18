# Feature development

## Trigger

A feature or bug-fix request for an Apple-platform project.

## Inputs

- Request and acceptance criteria
- Repository and target platform
- Xcode project or workspace, scheme, and test destination
- Relevant architecture and project instructions

## States

| State | Agent action | Exit evidence |
| --- | --- | --- |
| Intake | Confirm scope; inspect project instructions and affected code | Written acceptance criteria and known constraints |
| Plan | Identify change, dependencies, and verification route | Short implementation plan |
| Implement | Make focused code and resource changes | Diff covering acceptance criteria |
| Verify | Run relevant build and tests; inspect failures | Commands, destinations, and results recorded |
| Review | Check behavior, regressions, accessibility, and project conventions | Findings resolved or documented |
| Ready | Summarize change and remaining limits | Reviewable handoff with evidence |

## Transitions

- `Intake → Plan` when request and affected target are clear.
- `Plan → Implement` when approach and verification route are defined.
- `Implement → Verify` when change covers acceptance criteria.
- `Verify → Implement` when build or tests fail because of the change.
- `Verify → Review` when relevant checks pass, or blocked checks are documented with reason.
- `Review → Plan` when findings change scope or design.
- `Review → Implement` when findings need code changes.
- `Review → Ready` when findings are resolved and handoff is complete.

## Apple-specific verification

Select checks from project context: Xcode build for intended scheme and destination, unit or UI tests, simulator behavior, accessibility, signing, and entitlements. Record exact checks run. Do not claim checks that were not run.

## Handoff

Before merging, distributing through TestFlight, or submitting to App Store Connect, present the completed change and verification evidence for the responsible person's decision.
