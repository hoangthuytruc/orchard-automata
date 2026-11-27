# Run flow: rounds, briefs, findings, acceptance

Used by `run` and by the coordinator role (`$ORCHARD/roles/coordinator.md`). The approved plan file is the contract.
The rules of a run (one writer per file, walls between author and reviewer, tiers, isolation levels, when a run ends
early) are in `$ORCHARD/docs/workflow-model.md`; this file is the procedure that applies them. The project's guides
and profile override anything here.

This file is the only home of the package brief (section 2) and the implementer's return (section 3);
`$ORCHARD/roles/implementer.md` points here.

Contents: 1 Before the first round · 2 Package brief · 3 Implementer return · 4 Shared tree or working copies ·
5 Review · 6 Findings · 7 The loop · 8 Real-backend check · 9 Test report · 10 Acceptance

## 1. Before the first round

Each step is a check with an observable result. A failed check ends the run early, with the reason in one line and
nothing changed; the run never waits mid-way for an answer.

1. **Profile.** `python3 -I $ORCHARD/scripts/profile_check.py check .orchard/profile.md`. Exit 2: a required key is
   missing; end early and name it. Exit 3: a source file changed; discover only those keys again, and end early for
   the developer to confirm any value that now differs.
2. **Plan status.** Only `Status: approved <date>` starts the work; anything else ends the run with one line saying
   what is missing. Then `python3 -I $ORCHARD/scripts/plan_seal.py check <plan>`: exit 1 means the plan was edited
   after approval (the changed sections are named), and the run ends early for the developer to approve the new text
   or restore the old; exit 2 means the plan was approved without a seal, which the run says once and the report
   lists as a gap.
3. **Base branch.** The plan header names the base branch, confirmed at approval; the run does not ask again.
   `git merge-base --is-ancestor <base> HEAD` must succeed, or the run ends early.
4. **Lock.** `python3 -I $ORCHARD/scripts/lock_check.py snapshot <plans_dir>/<name>.lock.json <locked_globs>`, with the
   globs of the plan's section 8 (by default the profile's `locked_globs`), each glob in single quotes so the shell
   expands none of them.
5. **Starting state.** `python3 -I $ORCHARD/scripts/evidence.py state` and `git status --short`, recorded in the
   evidence file, so the report can say what was there before.
6. **Run log.** `python3 -I $ORCHARD/scripts/runlog.py start --workflow <workflow> --skill run --task <name>
   --isolation <level>`; keep the RUN_ID for the events in section 7.

## 2. Package brief

One implementer per work package, started by the coordinator on the tier the plan gives the package. The brief is
the agent's whole world: it does not see the conversation, any memory, or another package's work, so the brief
carries everything it needs and nothing else. Write it as a file in `<plans_dir>/<name>/` and hand the implementer
that file.

```markdown
# Brief: package <n>, <package name> (round <r>)

Root: <repository root>. Plan: <path to the plan file>. Tier: <strong | light>, because <the plan's reason>.

## Your rows of the plan (quoted, not summarised)
<the package row of section 7>
<the scenario rows of section 5 this package proves>
<the design-change rows of section 3 it builds>

## Files you own
<paths or globs>
Edit no other file. If you need one, stop and say which, and why.

## Locked
<globs>. Never edit these.

## Procedure
Follow $ORCHARD/skills/implement/SKILL.md. In short: for each scenario row, write the test bound to it first, at the
cheapest kind that can observe it ($ORCHARD/references/test-strategy.md); run it and see it fail for the right
reason, recorded with `--files <the test file>`; after that the test file is not edited (a wrong test is a reason
to stop and say "test defect"); write the least code that passes; remove what your change made unused; review your diff against
$ORCHARD/references/review-checklist.md part C. The bar is $ORCHARD/references/standards.md.

## Commands
Build: <build>. Tests, scoped to this package: <test.unit with its scope>; <test.behaviour, in-process only>.
Lint: <lint>. Generate before a new file is seen: <generate, or none>.
Evidence file for red runs: <reports_dir>/<name>/evidence.jsonl ($ORCHARD/references/run-flow.md, section 3).
Run no other test command. Never start a test run through the UI or against a real backend: the verifier does that
once per run.

## Stop and report, do not reach
- You need a file you do not own, or a locked file.
- The plan is wrong or impossible as written: say what and why; do not work around it.
- Three loops of the same failing test without convergence.
- The change would touch something the plan did not name: a public interface, a fixture, text a person sees, stored
  data, a call to the backend, a dependency, a build setting or a CI step.

## Fix round only
Findings to fix (quoted from the review, with type, severity, path:line and evidence):
<findings>
Each fix starts with a test that fails because of the finding.
Earlier failures of this package (only for a step up to strong): <both failures, with their output>

## Never
Commit, push, branch, stage for commit, or mention an AI or a tool in code, comments or text.

## Return
Exactly the format in $ORCHARD/references/run-flow.md, section 3.
```

A plan with one package, or a package the plan gives to the main session, may be built by the main session itself;
the run is then logged at the Shared level.

## 3. Implementer return

The implementer's last message is this, and nothing else. It is a claim, not evidence: the coordinator runs the
checks itself (section 7) and never copies a result from a return into the report.

**Red runs are recorded.** Each new test is run before its code exists through `python3 -I
$ORCHARD/scripts/evidence.py record <evidence file> --check <its kind's command key> --selection red-<Type.method>
-- <scoped test command>`, and must exit non-zero on its assertion. "Seen failing first with" quotes that record's
failure line. The red run names its test files with `--files <test file>...`, placed before the `--`, so the
record keeps their content hash. A bug-fix regression test written by `debug` is covered by debug's own record.

**A test is not edited after its red run.** `evidence.py held <evidence file>` lists every test file whose content
differs from the latest red run that named it. The coordinator runs it before `Implement → Verify` and before the
report; `verdict.py` reads the same thing, and a file it lists keeps the verdict at "Not ready". Two ways out, and
no third: the test is seen failing again in its new form and recorded as a new red run (before its code exists, or
with the claim broken on purpose and restored), or the implementer stops and returns "test defect" with the
evidence, and the coordinator decides. A fix round that adds a test to a file records that test's red run with the
same `--files`, which holds the file again. What the hash cannot see, an earlier test in that file edited in the
same step, is read by the review of fixes (section 5). Before
`Implement → Verify`, the coordinator checks that each test in the table has a `red-<test>` record with a non-zero
exit in the evidence file (`evidence.py table` shows it as "before the code"). A test without one is reported as
not seen failing first; the return's claim is not copied.

```markdown
## Package <n>: <name> — <done | stopped>

Files changed:
- <path> (<added | modified | deleted>)

Tests added or changed:
| Test | Scenario | Kind | Seen failing first with |
| --- | --- | --- | --- |
| <Type.method> | <id or N1> | <unit · behaviour · visual · integration> | <the failure message before the code existed> |

Commands run:
| Command | Exit | Last lines |
| --- | --- | --- |

Tests changed after their red run: <test, why, and the new red record; or "none">

Not run, and why: <checks this package could not run, or "none">

Plan problems: <anything in the plan that proved wrong, unclear or incomplete, with evidence; or "none">

Stopped because: <only when stopped: the file needed, the loops used up, the plan problem, or a test defect; with
evidence>
```

## 4. Shared tree or working copies

The plan names the arrangement; the coordinator may change it when the work turns out different, and says so in the
report.

| Shared working tree | A working copy each |
| --- | --- |
| a few small packages, clearly separate files | large or long packages, or files that sit close together |
| the file split is the only protection | a wrong split shows as a conflict, not as lost work |

A working copy (for example a git worktree) starts from the last commit, without the uncommitted work in the main
tree, and may need the project's setup first (`generate`). When a package is done, bring its diff into the main tree
uncommitted: in the working copy `git add -A -N . && git diff HEAD --binary > <plans_dir>/<name>/<package>.patch`,
then in the main tree `git apply --3way <patch>`. A conflict means the split was wrong: the run ends early with both
sides in the report; the split is the developer's to change in the plan.

Packages with no dependency between them run side by side, up to `workers`; the others run in order. Two test runs
never share one simulator (`device_policy`).

## 5. Review

**Full review**, after round 1, and again only when section 7 calls for it: the reviewer role
(`$ORCHARD/roles/reviewer.md`), a separate read-only agent on the strong tier. It receives the repository root, the
target "working tree", the plan file path and the project's review rules. It is not given the implementers' briefs,
returns or reasoning. It judges the change against the plan with `$ORCHARD/references/review-checklist.md` and
returns general comments and inline findings in that file's output format (part E).

**Review of fixes**, after each fix round: the same role on the light tier, given only the findings that were fixed
and the diff since the last review. It answers per finding: fixed, not fixed, or fixed and broke something (a new
finding). It also accounts for every hunk of that diff: the finding the hunk fixes, or "fixes no finding" with what
it changes. A hunk that fixes no finding was not asked for; it is judged as new work by the line review of the
checklist, and when more than a few lines are in that state the coordinator calls a second full review (section 7,
step 5). A hunk in a test file that changes a test no finding names is always reported.

The reviewer never fixes. The agent that fixes a finding is not the one that raised it.

## 6. Findings

The labels and what blocks are in `$ORCHARD/references/review-checklist.md`, part D. In a run:

- **What blocks** (a Blocker or a Risk, anything at High or Medium) opens a fix round. Each fix starts with a test
  that fails because of the finding.
- **What does not block** (a NOTE, Low, NIT) is not fixed in the run. It goes to the developer in the test report,
  "What I need from you", with a recommendation; the developer decides at acceptance.
- **Open questions** from the general review go to the developer in the test report. One that must block is also an
  inline finding.
- **A fix's tier** comes from its finding, as a package's does (`$ORCHARD/docs/workflow-model.md`, "Tiers").
- A once-per-run check that fails is handled like a blocking finding (section 7, step 6).
- Each finding is logged: `runlog.py event <RUN_ID> finding --round <r> --note "<type> <severity> <rule>"`.

## 7. The loop

1. **Round 1.** The implementers work, side by side where the plan allows; their changes are brought into one tree.
2. **Verify**, cheapest first, each check through `python3 -I $ORCHARD/scripts/evidence.py record <evidence file>
   --check <kind> --selection <scope> -- <command>`: static analysis (`lint`, the knowledge base check), the affected
   unit tests, the affected in-process behaviour tests, then `lock_check.py verify <snapshot>`. A failure stops the
   sequence (`$ORCHARD/references/test-strategy.md`, section 9). A failing check after round 1 is a blocking result
   for the review to see, not a reason to rerun.
3. **Full review** (section 5).
4. **Fix round** when anything blocks: one implementer per package with a blocking finding, each with a fix brief
   (section 2); then the affected checks, the lock check, and a review of fixes.
5. **Repeat** 4 until nothing blocks. A second full review is needed only when a fix round changed more than its
   findings asked for, or a review of fixes raised new findings.
6. **Once-per-run checks**, after the last edit: visual tests, behaviour tests through the UI, integration tests on
   the endpoints the plan names, each only when the profile enables it, and the design comparison for every frame in
   scope (`$ORCHARD/references/test-strategy.md`, section 6). If one fails and a round is left, it opens a fix round:
   the fix starts from the failing check, is reviewed, and the affected checks run again. If no round is left, the run
   goes to Ready with the verdict "Blocked" and the failure in the report.
   Every loop of a package that ends failing, and every required check that still fails at the end of a round, is
   logged with its cause: `runlog.py event <RUN_ID> loop_failed --cause <cause> --round <r> --note "<package or
   check>"`. The coordinator sets the cause from the evidence, not from the return's own words: `plan_gap` (the
   plan was wrong, unclear or incomplete: a "Plan problems" entry the code confirms), `executor` (the plan was right
   and the work was not), `test_defect` (the test was wrong), `flaky` (it passes and fails on the same code),
   `environment` (simulator, device, backend or tool), `blocked` (a file not owned, a lock, a missing answer). When
   the evidence does not decide between two, it logs the one that is cheaper to rule out next and says so in the
   note.
7. **At most three rounds** in all. A package that fails two loops on its tier runs its third on strong, with both
   failures in its brief (`runlog.py event <RUN_ID> step_up`); after that it is not tried again. Review rounds that
   run out do not stop the run: the remaining findings go into the report.
8. **Before the report:** `evidence.py held <evidence file>` and `plan_seal.py check <plan>` (sections 3 and 1);
   then `evidence.py stale <evidence file>`; a stale result is run again, or reused only where
   `affected_map` shows the later edits did not touch it, or reported as not verified. For each scenario not
   delivered, its code and tests are removed and the plan's "Result" says why.

**Ending early.** The run ends early, reports both sides and stops, only when going on would mean guessing: sources
conflict with no rule to settle them, a locked file would have to change, the plan is wrong, a required profile key
is missing, or working copies conflict. Log it: `runlog.py event <RUN_ID> ended_early --note "<reason>"`.

Other run log events, recorded when they happen, never estimated afterwards: `tier`, `loop_failed`, `first_try_fail`, `flaky`,
`wait` (on a device or the backend), `send_back`. Tokens and time per role come from the tool where it reports them;
otherwise "not available".

## 8. Real-backend check

When the server's behaviour is not sure (a status code, an error body, an ordering, a field the spec does not pin),
test the hypothesis against the real backend instead of guessing.

- The four rules for any call to the real backend are in `$ORCHARD/references/test-strategy.md`, section 5: test
  environments only, one targeted call, clean up, record shapes and never secrets.
- Run it with the project's integration command scoped to the question, or one request, through `evidence.py record
  --check integration`.
- Record the hypothesis, the environment, the request shape, the status, the reply shape, and whether the data was
  cleaned up, for the test report's "Real-backend checks" table.
- A reply that contradicts the plan is a gap: classify it with `$ORCHARD/references/gap-classification.md`. It is
  never a reason to change the plan, a scenario or a test quietly.

## 9. Test report

`handoff` writes the report from `$ORCHARD/templates/test-report.md` to
`<reports_dir>/<YYYY-MM-DD>-<name>-test-report.md`, from the evidence file, the findings and the plan only. At the
Strict level a separate report writer does it (`$ORCHARD/roles/report-writer.md`). The verdict is the one
`$ORCHARD/scripts/verdict.py` prints from the evidence file, the plan and the latest review, quoted as it is.

Then the coordinator updates the plan file: fills "Result", lists what was not delivered and why, and sets the
status to `executed`. Log the end: `runlog.py finish <RUN_ID> --outcome <green | red | blocked | ended_early>
--findings <n>`.

## 10. Acceptance

- The developer reads the report and accepts, or sends back. Nothing is published: no commit, push, branch or pull
  request.
- A fix the developer asks for is one more fix round, starting with a failing test, followed by the affected checks
  and a review of fixes; the report is then updated. Log `runlog.py event <RUN_ID> send_back --note "<their words>"`.
- The status becomes `accepted <date>` only on the developer's words. Then `update-docs` writes the delivered
  scenarios into the knowledge base (`$ORCHARD/references/scenario-register.md`, section 1).
- Once the quality of the work is known, rate it: `runlog.py rate <RUN_ID> --accepted <n> --rejected <n>
  --rework-minutes <n> --verify-minutes <n>`.
