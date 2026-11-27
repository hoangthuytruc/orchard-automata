# Principles

The rules every skill, role and workflow obeys. A skill points here; it does not restate them. Words in these rules (claim, evidence, verification, scope, boundary) are defined in [terms](terms.md).

The governing idea is zero trust: an agent's statement is a claim, never a result. Agents run from an approved plan to a finished result without waiting on a person; the skill set's job is to make that result cheap to verify.

1. **A claim is not evidence.** Every claim needs evidence produced in this run on the final change: a test or command record, a network log, a screenshot or screen recording, a code reference, a file hash. A report quotes it or links it; it does not paraphrase it. A claim with no evidence at all is not done, whatever the report says about it.
2. **The person decides at the ends, not in the middle.** A plan becomes `approved`, and work becomes `accepted`, only on the owner's words. Between the two, a run does not wait for anyone.
3. **Gates are scripts and evidence, not prose.** A rule that a script can check is checked by a script (locked files by hash, scenario coverage, exit codes). Prose rules are for what scripts cannot see.
4. **The author never reviews.** The reviewer is a different agent, read-only, and gets the diff and the rules, not the author's reasoning.
5. **Fix the code, never the check.** No lowered coverage threshold, loosened assertion, skipped test or rerun in hope of a pass. A test that passes on rerun is a failure to diagnose.
6. **Say what did not run.** Readiness is claimed only for checks that ran against this change. Missing evidence is named.
7. **Code is never a requirement.** Existing code shows current behaviour; it does not justify a scenario.
8. **Never settle a conflict that no written rule can settle.** When a written rule picks the winner, apply it and record it. When none does, record both readings and ask the owner. [Boundaries](boundaries.md#conflicts) lists which is which.
9. **One home per rule.** A skill points to the rule; it does not restate it.
10. **The smallest change.** Every changed line traces to an approved plan item.

## Evidence is about the final change

Each result is recorded with the state of the change it ran against. A check that runs once per run runs after the last edit, so a fix round cannot leave it describing an earlier version. An earlier result is reused only when the map from files to tests shows that the later edits did not touch what it covers. Where that is not known, the check runs again, or the claim is reported as not verified.

## What counts as evidence

Every claim carries the strongest evidence that can be produced for it, and at least one piece. The forms:

| Form | What it shows | Produced by |
| --- | --- | --- |
| Test or command record | A check ran on this exact change: command, state of the change, exit status, summary | `evidence.py record` |
| Network log | What the app sent and what came back: request shape, status, reply shape; tokens and personal data masked | An integration test, a real-backend check, or the app's network logging during a test |
| Screenshot | A state a person sees, on the running product | The simulator or device, driven to that state by the scenario's test |
| Screen recording | A journey: several steps, navigation, an animation, a timing | The simulator or device, recorded while the scenario's test runs |
| Code reference | Where the change does it: `path:line` in the final diff | The diff of the final change |
| File hash | A file the run must not change stayed the same | `lock_check.py` |

**Visual evidence wherever it can be captured.** A behaviour a screen can show gets a screenshot (a state) or a recording (a journey) whenever the product can run on a simulator or device in this run, beside its test record. When it cannot be captured (no app target, no simulator, a system sheet, hardware), the claim rests on its other evidence and the report says in one line why there is no picture.

**What blocks and what does not.** A claim with no evidence of any form is not delivered. A missing picture alone does not block acceptance: it is a named gap in the report, and the developer decides whether the other evidence is enough. Every screenshot and recording is captured after the last edit, names the scenario, and is listed in the evidence file with the state of the change it shows.

## Two sides of quality

| | Functional suitability | Structural quality |
| --- | --- | --- |
| Question | Does the product do what its owner would refuse to ship without? | Is the code sound, bounded and maintainable? |
| Stated as | Scenarios in the words a person sees, each with a basis | Standards, architecture boundaries, lint rules |
| Proved by | A test bound to the scenario, plus evidence from the running product | Static analysis, independent review, technical-debt report |
| Decided by | The product owner; the developer records the decision | The developer |

Both names are defined in [terms](terms.md).
