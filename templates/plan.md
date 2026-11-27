# Plan: <name>
Status: draft
<!-- Statuses, in order: draft → approved <date> → executed → accepted <date> → documented <date>.
     `plan` sets draft and approved (approved only on the developer's word); `run` sets executed and accepted
     (accepted only on the developer's word); `update-docs` sets documented. A re-check has no run: `plan` moves it
     approved → accepted on the developer's word. -->
Workflow: <feature-development | bug-fix> · Isolation: <Shared | Standard | Strict> (<reason if raised>) · Base branch: <branch>

<!-- Top part: for the developer. One screen, plain words, read in two minutes. No paths, type or test names.
     If a line would not change what the developer decides, it belongs in the working detail. -->

## In short
<Two or three sentences: what will be built, for whom, and the one decision that shapes it.>

## What changes for the person using the app
- <behaviour, in their words>

## How it will be built
- <Approach: one line per part of the change, three or four at most>
- Rejected: <the option not taken, and why, in one line>
- Risk: <what it costs or risks, in one line>

## Scenarios
<n> added, <n> changed, <n> removed. In plain words:
- Added: <title> (required by <spec name or design screen>)
- Changed: <title>: <what is different>
- Removed: <title>: <why>
Kept by team decision, for you to confirm: <title>, or none.

## What I need from you
1. <question>. I recommend <option>, because <one line>. Blocks: <what>.
Or: nothing; the plan is ready to approve.

## How the work is split
<n> packages, <side by side | in order>, on <tiers>; <shared tree | a working copy each>. Up to three rounds,
with a full review after the first. The scenario files stay locked until acceptance.

## Not covered
- <what this plan leaves out, and where it belongs>

---

# Working detail (for the agents)
Sources: <ticket keys and versions · spec pages and versions · design file and version · code at <commit>>

## 1. Scope
| This change owns | Out of scope → who owns it |
| --- | --- |

## 2. Requirements
<!-- Every rule, flow step, state, limit, error and exit the sources state: one line each, with its quote.
     This list is the coverage proof; a count of scenarios is not. -->
| # | Requirement | Source and version | Quote | Scenario, or reason for none |
| --- | --- | --- | --- | --- |

## 3. Design change
| Area | Today (path:line) | After | Why |
| --- | --- | --- | --- |
State owner, dependency direction, isolation per new type, side-effect boundaries, test seams, migration slices.
A cross-team contract (API shape, error codes, analytics, copy keys) is written here.

## 4. Impact
<!-- references/impact-checklist.md: every perspective answered; "none, because …" is a valid answer. -->
| Perspective | Impact | Owner |
| --- | --- | --- |

## 5. Scenario changes
<!-- Change: one of the values listed in references/scenario-gate.md ("Where a re-check's results go"),
     Keep included. A kept scenario that gains a test, the usual bug fix, is Keep, with the new test in Test.
     Basis: Spec, Design, Spec + Design, or Team decision (confirmed, with who and date). Provisional ids N1, N2…
     Kind: unit, visual, behaviour, integration, or manual. Oracle: say it when not a plain example
     (property, snapshot, compatibility, person). -->
| Change | Scenario | Steps | Basis | Evidence | Kind | Oracle | Test |
| --- | --- | --- | --- | --- | --- | --- | --- |

### Pending or blocked scenarios the change touches
<!-- Not scenario changes: the coverage check stops reading section 5 at this heading. A scenario that this change
     resolves also has its row in the table above. -->
| Scenario | Tag today | Test that will resolve it, or reason it stays |
| --- | --- | --- |

## 6. Open questions
| # | Question | Options | Recommended | Blocks | Answer (who, date) |
| --- | --- | --- | --- | --- | --- |

## 7. Work packages
| # | Package | Files it owns | Tier and reason | Depends on | Done when |
| --- | --- | --- | --- | --- | --- |
Tree: <shared | a working copy each>, because <one line>.

## 8. Rounds and locks
Rounds: at most three. Full review on strong after round 1; review of fixes after each fix round.
Locked: <globs from the profile's `locked_globs`>.
Real-backend checks: <hypothesis, environment, data to clean up> or none.
Integration tests: <the endpoints the change touches, to run them on> or none.

## Result (written by run)
| Scenario | Delivered | Test | Note |
| --- | --- | --- | --- |
Not delivered, and why: …

## Change note (written by update-docs)

---

<!-- Compact plan (bug-fix only). Use when an approved scenario already states the expected behaviour. Valid only
while the fix stays in one package and changes no public interface, fixture, text a person sees, stored data or
backend call. If any of those must change, stop and write the full plan.

A compact plan is this file with one part replaced, nothing else:
- Kept: the header lines (title, Status, Workflow line with isolation and base branch).
- Kept, shortened: the top part for the developer. "In short", "What changes for the person using the app" and
  "What I need from you" always; the others in a line each, or left out when they would say nothing.
- Kept: the "Working detail" heading and its Sources line.
- Replaced: sections 1–8, by the "Compact plan" section below. Its locks are the profile's `locked_globs`.
- Kept, empty until later: "Result" and "Change note".
`gate_check.py --coverage` recognises the "## Compact plan" heading and checks every row: a scenario id, a
reproduction, a cause at path:line, owned files, a tier with its reason, and a proof.

## Compact plan
| Scenario id | Reproduction | Cause (path:line) | Files the fix owns | Tier and reason | Proof |
| --- | --- | --- | --- | --- | --- |
Proof = the failing regression test from `debug`, made to pass.
-->
