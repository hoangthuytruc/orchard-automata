# Review against the product sources

Date: 2026-11-27. The review checklist gained "Against the sources" in part A: the reviewer reads the spec, the
design and the ticket itself and compares the scenarios and their tests with them. Before, review checked the code
against the plan only, so a scenario that misread its source passed.

## Changed

| File | Change |
| --- | --- |
| `references/review-checklist.md` | Part A, "Against the sources"; a "Sources" line under Verification in the output format |
| `roles/reviewer.md` | Step 2 reads the product sources through the profile and names what it could not open |
| `skills/review/SKILL.md` | Contract and general steps name the product sources |
| `references/scenario-gate.md` | Header says the reviewer reads sections 1 and 2 and settles nothing |
| `evals/workflow-review-only/graders/sources-checked.md` | New grader |

The profile's "Read by" column is unchanged on purpose: `review` still runs when a source key is missing, and
names that source as not checked.

## Applied to the sample

One separate reviewer, started with the one-line prompt of the `review` skill, on the `workflow-review-only`
scaffold (a copy of `sample/Ledger` with the uncommitted daily-limit change), outside this repository. Not an
eval run: one run, read by hand, no grader.

| Expected of the new check | Seen in the review |
| --- | --- |
| Names the sources it read, with version or status | Yes: spec v3 clause 3, ticket criteria 2 to 5 and the backend comment, design frame 210:31 from both design notes, scenarios TS_LED_003 and TS_LED_004; the legacy spec named as superseded |
| Names what it could not check | Yes: "the rendered frame, only text notes exist in the repository" |
| Compares the change with a quoted clause | Yes: Blocker on `DailyLimit.swift:16`, "409 and `code: DAILY_LIMIT`" against `status >= 400` (seeded R1) |
| Finds a scenario that contradicts its source | Yes: TS_LED_004 against spec v3 clause 3 (seeded D1), under "Outside the diff", with the reason the spec wins in words |
| Finds what the sources require and the change lacks | Yes: the "Contact support" button of frame 210:31 and TS_LED_003, as an open question |
| Does not settle a conflict no rule settles | Yes: "Resets at midnight" against "Resets at 00:00" against the server's time (seeded D6) is an open question |
| Changes nothing | Yes: `git status` after the review shows only the scaffold's two files |

The review also reported the other seeded defects of the diff (R2 to R5) and D8.

## Not verified

- No eval run: the new grader has not run, and the with-and-without difference is not measured.
- One run on one change. A review with a plan, and a pull-request target with an external spec or design tool, were
  not tried.
- The screenshot-against-frame comparison had nothing to compare: the change has no evidence file.
