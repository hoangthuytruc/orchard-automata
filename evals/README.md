# Evals

One case per skill, plus dry runs of the `feature-development`, `bug-fix` and `review-only` workflows, all on the
sample project `sample/Ledger`. Each case runs the same prompt with the skill set and without it, and grades both
arms. The harness is `claude plugin eval`, started by `adapters/claude-code/eval.sh`. These cases are the proof in
`docs/skill-set-plan.md` sections 11 and 13: a change to core is accepted only when its case passes on the sample.

## What passes

- **The gate is the case's own graders.** A case passes when every run with the skill set passes all of its
  graders. A grader for a new rule is written so that it fails without the rule and passes with it.
- **The with/without delta is a signal, never a gate.** It is printed beside each case. A negative delta is read,
  not scored: the arm without skills may improvise around a blocked command, which the skill set forbids.
- **An environment that blocks the build is "not run (environment)", not failed.** When a run with the skill set
  fails and its final message or graded files show the build or test command stopped by the sandbox, the case is
  reported as not run. It proves nothing either way and is run again where the build works. The detection is a
  pattern over the harness's grader evidence (`ENV_BLOCK_PATTERN` in `eval.sh` overrides it), so a case it marks is
  read before it is trusted.

`eval.sh` prints this summary after the harness's own output and saves it as `summary.txt` beside the results. It
exits 0 when no case failed, 1 when one failed or none ran.

## Cases

| Case | Skill | What it checks |
| --- | --- | --- |
| `adopt-ledger` | adopt | Draft profile from discovery; each value has a hashed file source or is `missing`; status draft |
| `plan-led7` | plan | Plan for LED-7: requirements with quotes, conflicts settled by the source ranking or asked, scenario bases, the 140-character rule as a team decision, twelve impact perspectives, the 409 contract, packages with tiers, locks. Absorbs the source's ticket impact case |
| `plan-draft-ledger` | plan | Drafting mode: scenarios from scratch for a feature with none; legacy-only and unsourced behaviour left out or put to the owner |
| `plan-recheck-ledger` | plan | Re-check mode: a basis per existing scenario, removals, team decisions, the spec clause with no scenario |
| `implement-refund-balance` | implement | Refund sign and empty-store crash fixed test-first, no new force unwrap |
| `test-deterministic-store` | test | Sleep removed, time injected, empty, refund and month-boundary tests |
| `verify-ledger` | verify | Evidence by script with the change state; lock check finds the edited register and stops the move on; what did not run |
| `debug-ledger-latest-crash` | debug | Reproduction, cause, experiment, one failing regression test; production code unchanged |
| `review-ledger-package` | review | Separate reviewer; seeded defects found with file:line, type, severity, fix; project rule LR-1 cited |
| `debt-ledger-report` | debt | Ranked report with impact, likelihood, effort, evidence and first step; nothing fixed |
| `handoff-ledger` | handoff | Verdict computed by `verdict.py` and quoted first; stale unit-test evidence not used as proof; open finding to the developer; no separate acceptance-criteria table; draft pull-request body carrying the verdict and the top part, with no tool credit |
| `update-docs-led` | update-docs | Only delivered scenarios written, new id, binding instead of a pending tag, register rows, gate check run, plan documented |
| `run-led-refund` | run | `feature-development` dry run: approved plan to test report without asking; implementer and reviewer agents; evidence, lock check and run log by script |
| `retro-ledger` | retro | Proposal only for the signal repeated across runs; single events set aside; no baseline under five runs; nothing edited |
| `workflow-bug-fix-refund` | run, debug | `bug-fix` dry run: reproduction, compact plan on TS_LED_002, fix, separate review, test failing before and passing after |
| `workflow-review-only` | review | `review-only` dry run on an uncommitted diff: seeded diff defects found, no build or test run, nothing edited |

Not ported from the source suite: the architecture-decision case (its skill was merged into `plan`, and decision
records now live only in the plan), and the ticket impact case as a separate case (its graders moved into
`plan-led7`).

## Format

A case is a folder with:

- `prompt.md`: frontmatter (`name`, `description`, `tags`, `runs`, `max_turns`, `timeout_seconds`,
  `allowed_tools`, `expected_outcome`) and the prompt. A prompt names the skill by its bare name ("use the plan
  skill"); it never names a seeded defect or points to `SEEDED.md`.
- `case.yaml`: `context.scaffold_script: scaffold.sh`. The script must sit inside the case folder.
- `scaffold.sh`: builds the workspace in the current directory. It sources `fixtures/scaffold-lib.sh`, which copies
  `sample/Ledger` with its `.orchard/` folder (found from the case folder, symlinks resolved), makes the profile's
  `knowledge_base_check` runnable from the workspace, and makes one git commit so the lock, evidence and diff
  scripts work. Shared fixtures (plans, a review, a test report, a run log) live in `fixtures/`.
- `graders/*.md`: one grader per file. Types: `llm` (a rubric; `focus: {source: file, path: …}` or the final
  message), `regex` (`target: last_message` or a file), `tool_used` (`tool`, `input_match`, `min`, `max`,
  `arm: with-only`), `file_exists`.

## Shared guards

Every case carries these, with identical text, so a guard means the same thing everywhere. Edit them all together.

| Grader | Checks |
| --- | --- |
| `no-commit` | No `git commit`, `push`, `tag`, `merge`, new branch, or pull-request command |
| `no-gate-edit`, `no-gate-write` | No Edit or Write under `docs/features/` (the scenario files). Absent only in `update-docs-led` |
| `honest-report` | The final message reports each command with what actually happened, and claims no commit |
| `tests-ran` | `swift test` was run. Only where the skill runs tests: implement, test, verify, debug, run, bug-fix |
| `skill-fired` | The Skill tool was called with the skill, `with-only` |

`skill-fired` and the reviewer graders are specific to the Claude Code adapter: the plugin exposes skills as
`orchard:<name>`, so `input_match` accepts `orchard:<name>` or the bare name, and the reviewer is the subagent
`orchard-reviewer`. Another tool's harness needs its own form of these graders.

## Running

```bash
adapters/claude-code/eval.sh smoke                 # one run per case, both arms
adapters/claude-code/eval.sh full                  # three runs per case
adapters/claude-code/eval.sh case 'plan-*'
```

Per-developer settings, never written into a case:

- **Judge.** The judge for `llm` graders is `JUDGE_MODEL` in `eval.sh`; unset, the harness default is used. Use the
  strong tier: a light judge has failed reports that met every rubric line.
- **Run log.** `run-led-refund` and `workflow-bug-fix-refund` call `scripts/runlog.py`, which writes to
  `$ORCHARD_RUNLOG`, else to the developer's own `~/.orchard/runlog.jsonl`. Export `ORCHARD_RUNLOG` to a scratch
  file before an eval run, or the eval runs join the real log.

Results land in `evals/results/<timestamp>-<mode>/` (`report.html`, `aggregate-result.json`); keep them out of git.

## Limits of the harness

Learned on the source suite; they still hold.

- An `llm` grader with `focus: files` shows the judge only the created paths, and `focus: trace` shows raw JSON
  lines. Content is judged through a file at a path the prompt fixes, or through the final message.
- Judges are noisy on long files. Where a fact can be matched, a `regex` grader carries it (for example
  `Status:\s*executed`, `file:…#<hex>`, `first!` still present).
- Inside the eval sandbox, `git` and SwiftPM's own sandbox may be blocked. Runs then fall back to `swiftc` plus
  `xctest`, and `honest-report` accepts a truthfully reported substitute. Do not tell a run to use
  `swift test --disable-sandbox`: both arms hung until the timeout. With `git` blocked, `scripts/evidence.py`
  cannot compute the change state; the case still grades that the script was called.
- Test-first order, and whether an agent read a file before writing, are not graded: the trace is not judgeable.
- A file edited through Bash (`sed -i`, a redirect) escapes the `no-*-edit` graders, which see only the Edit and
  Write tools. The `regex` and `llm` graders on the file contents catch the result where it matters.
- One run per case is a smoke signal. Use `full` before trusting a delta between the arms; the delta stays a
  signal even then.

## Seeded defects

`SEEDED.md` lists every seeded defect with file and line, and which cases find it. It is for graders and for the
run log's `seeded_missed` count; a prompt never points to it. A change to `sample/Ledger` must update it, and the
scaffolds must still build: run each `scaffold.sh` in an empty folder and `swift build --build-tests` there.
