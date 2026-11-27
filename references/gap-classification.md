# Gap classification

Used by `verify` and `handoff` whenever an integration test or a real-backend call disagrees with the plan: a
status code, a reply shape, an error body, an ordering, a value the plan expected. A gap is not fixed by changing
the plan, the scenario or the test to match what was seen. It is classified, given an owner and a severity, and
recorded in the test report's "Real-backend checks" table, column "Gap class and owner"
(`$ORCHARD/templates/test-report.md`).

## Classes

Pick exactly one class per gap. When two seem to fit, record the evidence for both and ask the owner in the report;
do not guess.

| Class | How it shows | Owner | What happens next |
| --- | --- | --- | --- |
| App defect | The backend answers as the plan and the fixtures say; the app handles it wrongly | The app: this run | A finding, back to Implement in a fix round when a round is left; the fix starts with a test that fails because of it. With no round left, the verdict is "blocked" |
| Backend defect or missing build | The backend answers against its own documented contract, or the endpoint or field is not built yet in the test environment | The backend team | Listed for the developer with a drafted message to that team. The app gets no workaround and no client copy of a server rule |
| Contract ambiguity | The plan, the spec or the design does not pin the behaviour, and the backend's answer is one valid reading | Product or design | An open question in the report. The scenario is not changed until the owner decides |
| Fixture drift | The backend answers correctly and the app is right, but a fixture no longer matches the real reply | The app: this run | The fixture is updated from the recorded reply (never edited by hand to pass), in a fix round; the tests that use it run again |
| Environment or data | The test environment is down, blocked, slow, misconfigured, or holds data that makes the call meaningless | QA or the backend team | Recorded as "not verified" with the reason; the call is not repeated. The check is listed under "Not run" |

## Severity

By the effect on the person using the app, if the gap reached them:

| Severity | Effect |
| --- | --- |
| High | They cannot finish the journey, lose data, or see wrong data |
| Medium | They finish, but only with a workaround, a retry or a degraded state |
| Low | Cosmetic, or on a path few people take |

An app defect or fixture drift that becomes a finding is labelled with the review checklist's labels
(`$ORCHARD/references/review-checklist.md`, part D); the gap severity above is what the report shows the developer.

## Rules

- Record the evidence under the four real-backend rules (`$ORCHARD/references/test-strategy.md`, section 5):
  request shape, status, reply shape; no tokens or personal data.
- Each gap has one owner. The developer sends any message; a skill only drafts it.
- A gap owned outside the app is not fixed in the app. It is listed for the developer with what it blocks; a
  required check it leaves failing makes the verdict "Blocked" (`$ORCHARD/references/run-flow.md`, section 7).
