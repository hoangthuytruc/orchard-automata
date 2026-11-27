# Boundaries

Each layer has one kind of source, one artifact and one writer. The chain a person can follow is: scenario id → work package → test → evidence row → acceptance.

| Layer | Answers | Sources allowed | Artifact | Agent may | Agent never |
| --- | --- | --- | --- | --- | --- |
| Product | What and why | Spec, design, recorded product decision | Scenarios with a basis | Draft, list conflicts and open questions | Invent behaviour; use code or a lone ticket as basis (unless the profile ranks a ticket as a basis); write to the knowledge base before acceptance |
| Technical | How | Standards, project architecture rules | Plan: packages, owned files, locks, verification route | Propose the split and the design | Change scope; add a dependency, build setting or CI step without asking |
| Code | The change | The approved plan | Uncommitted diff | Edit files its package owns | Edit another package's file or a locked file; commit |
| Test | Proof | Scenario ids, test strategy | Tests and the test report | Add and strengthen tests | Weaken, skip or delete a test; edit scenario files |
| Evidence | What ran and what it showed | Test and command records, network logs, screenshots and screen recordings of the running product, code references, file hashes, all from this run on the final change | The evidence file and the report that links every claim to its evidence ([what counts](principles.md#what-counts-as-evidence)); what could not be captured is named with its reason | Capture, record and quote | Summarise from memory; pair a near match as proof; claim a behaviour done with no evidence |
| Decision | Go or no go | All of the above | Status change, commit, pull request, merge, release | Present | Decide |

**Locked files.** From approval to acceptance, the files of the profile's `locked_globs` are locked and verified by hash (`scripts/lock_check.py`): by default the knowledge base and the check configuration a run must not touch (the default list is in [`templates/project-profile.md`](../templates/project-profile.md)). Only `update-docs` writes the knowledge base, and only after acceptance.

**Git.** No skill commits, pushes, creates a branch or tag, or opens, approves or merges a pull request. Those belong to the Decision layer.

## Conflicts

A conflict is two statements that cannot both hold for the same behaviour or the same file, each from something the agent must obey: a source, a rule, the approved plan, a check.

The test has two parts. Does a written rule pick the winner? Does applying it leave the approved plan and every check unchanged? Yes to both: the agent settles it and records the rule it used. No to either: a person decides.

| Conflict | Who settles | By what rule |
| --- | --- | --- |
| Sources of different rank disagree (spec against a lone ticket) | Agent | The source ranking in the project profile |
| An older version of a source against the pinned one | Agent | The pinned version in the profile |
| Code against an approved scenario | Agent | The scenario wins; fix the code |
| A test against an approved scenario | Agent | The scenario wins; fix the test |
| A core rule against a project rule | Agent | The project rule wins |
| Lint or a standard against the agent's own code | Agent | Fix the code, never the check |
| Two ways to build the same outcome inside one package | Agent | Standards; the choice is noted in the report |
| Spec against design on labels, layout or visible controls | Agent | The design wins on what a person sees |
| Spec against design on behaviour or data rules | Agent | The spec wins on what happens |
| A newer spec against an older page | Agent | The newer release wins; the page to update is listed for product |
| No source states a behaviour, and the product has no such rule | Agent | It is not written as a scenario; code never justifies one |
| Sources disagree and no rule above settles it | Person | None exists; both readings are recorded |
| No source states a behaviour the product already has | Person | Proposed as a team decision; kept only when confirmed, with the date |
| The approved plan against what the code allows | Person | The plan is theirs; execution never rewrites it |
| A package needs a file it does not own, or a locked file | Person | The split or the lock was approved by them |
| A scenario against what the server returns | Person | The server owns its values; no client workaround |
| Two project rules disagree | Person | The project owns its rules |
| A check can pass only by weakening it | Person | Thresholds and assertions are never lowered by an agent |
| The fix needs a new dependency, build setting or CI step | Person | Outside the approved scope |

Most person-side conflicts are found while planning and asked together, once, before the run. One found during a run ends that run early with both sides in the report.
