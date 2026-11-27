# What a test may assert, and when a test set is finished

Date: 2026-11-27. The test strategy gained sections 16 ("What a test may assert") and 17 ("A finished test set"),
adapted from an MIT-licensed testing skill (`THIRD_PARTY_NOTICES.md`). Before, the strategy said which kind of test
to write and how to make it deterministic, but not where an expected value may come from, and it had no rule for
when to stop.

## Changed

| File | Change |
| --- | --- |
| `references/test-strategy.md` | Sections 16 and 17; section 13 step 5 says the branch list is where to look, not a quota |
| `references/review-checklist.md` | Section 10: two questions that point to sections 16 and 17 |
| `references/standards.md` | An expectation changes only when its source changed |
| `skills/test/SKILL.md` | Write mode names each case's source and the failure it catches; the Close report lists them |
| `docs/terms.md` | Change detector; undecided behaviour |
| `THIRD_PARTY_NOTICES.md` | The source, what was taken and not taken, its licence |

Not taken: the source's rule against test doubles for a project's own modules (section 3 keeps fakes behind
protocols at layer boundaries), and its guidance on guards, which is a coding rule.

## Applied to the sample

One agent followed `skills/test/SKILL.md` in write mode on a copy of `sample/Ledger` with the note rule added
(`add_note_rule` in `evals/fixtures/scaffold-lib.sh`), outside this repository. Request: "add tests for the balance
in TransactionStore and for NoteRule". Not an eval run: one run, read by hand, no grader.

| Expected of the new rules | Seen |
| --- | --- |
| Each test names the source of its expected value | Yes: scenario ids TS_LED_001, 002 and 006 with the spec clause, per test |
| No expected value is read from the code | Yes: the note tests write 140 from the scenario; `NoteRule.maxLength` is not referenced in the test file (checked with `grep`) |
| Each case names the failure only it catches | Yes: 140 catches `<` for `<=`; 6 catches `==`; 141 catches a rule that refuses nothing |
| Each case was seen to fail | Yes: three mutations of the rule and one of the balance, each restored; the refund test fails on the seeded defect S3 ("1400" is not equal to "600") |
| The existing test is extended before a new one is added | Yes: `testAddIncreasesBalance` became the two-purchase case of TS_LED_001 |
| A changed expectation names its reason | Yes: 500 became 1250, with the scenario's values as the reason; the `sleep(1)` was replaced by a seam |
| Cases that catch nothing new are not written | Yes: "empty store" and "139 characters" are listed as considered and not written, each with the case that already catches the failure |
| A rule with no source is named for the owner, not tested | Yes: trimming before counting, what a character is, an empty note, a balance below zero, "at once" |
| The skill changes no behaviour | Yes: `git status` shows the two test files and one internal seam; the defect is left for `debug` or `implement` |

Observation: the 140-character limit has no spec or design basis (seeded D3), yet it was tested, because the
scenario TS_LED_006 is in the knowledge base and an approved scenario is a valid source. Finding that the scenario
itself has no basis is the work of a re-check in `plan` and of "Against the sources" in `review`, not of `test`.

## Not verified

- No eval run, and no grader for these rules yet.
- One run in write mode. The audit and flaky modes, a configuration value, and an existing test that turns red
  because a requirement changed were not tried.
- The review side (section 10's new questions) was not run on a test diff.
