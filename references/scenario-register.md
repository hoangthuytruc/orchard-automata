# Scenario gate: writing the knowledge base, register template and checks

Used by `update-docs` after acceptance, and by `plan` and `verify` whenever the gate check runs. The knowledge base
and the register are defined in `$ORCHARD/docs/terms.md`; their paths are the profile keys `knowledge_base` and
`register`. The project's guides override anything here.

## 1. Writing the knowledge base

Only `update-docs` writes the scenario files, only after the developer accepted the run, and only what was
delivered and accepted (`$ORCHARD/docs/boundaries.md`). The source is the accepted plan's section 5 and its "Result"
table, for a re-check the accepted plan alone. Order: confirm the lock, feature file, register, check.

1. **Confirm the lock:** `python3 -I $ORCHARD/scripts/lock_check.py verify <snapshot>`. A locked file that changed
   during the run ends the step: report it to the developer, write nothing.
2. **Feature file:** remove the scenarios and clauses marked `Remove`, apply the `Reword` fixes, add the delivered
   `Add` scenarios and the confirmed team decisions, under their rules and in their order. Replace the provisional
   ids by the project's id rule (`scenario_id_pattern`): ids are never reused; a new scenario takes the next free
   id. Update the header's source list and versions. A scenario that was not delivered is not written.
3. **Tests:** `update-docs` changes no code and no test. A binding in the feature file that names the wrong test is
   corrected. A delivered scenario with no test carries an allowed untested tag (below) and a line in the change
   note. Writing the missing test is separate work (`test` or `implement`): offer it, do not
   start it.
4. **Register:** rewrite it from the template below. A removed scenario leaves the register entirely: the register
   reads as the current gate, and the removal with its reason stays in the accepted plan.
5. **Check** (section 3), then the project's own check (`knowledge_base_check`). Show the developer the diff; they
   commit.

## 2. Register template

Beside the feature file, at the path `register` gives. It explains the scenarios; the feature file is the source of
truth, and when the two disagree the register is corrected.

```markdown
# <Feature> requirements register

## At a glance
| | Scenarios |
|---|---|
| **Total** | **<n>** (<first id> to <last id>) |
| Required by a current spec or the reference design | <n> |
| Required by a spec or design, with one detail set by a team decision | <n> |
| Kept by team decision only, spec to follow | <n> |
| Run by at least one automated test | <n> |

Short names: …

## The gate
(the three or four rules of the project's gate)

## Sources
| Source | Id / version | Decides |

## <n>. <Section> (<count>)
**Rule: <the product rule from the feature file>**
| Scenario | Spec clause | Verified evidence | Basis | Tests |
| <ID> — <title> | <page, step> | <short name › section: "quote"; D/<frame id>> | Spec + Design | behaviour: <Type.method> |

## Team decisions (<n> scenarios, plus <n> details)
| Scenario | Decision | Spec to update | Evidence |

## Open decisions
| # | Question | Owner | Blocks |

## Design notes
| Design frame | Differs from | Needed change |
```

Basis cell: `Spec`, `Design`, `Spec + Design` or `Team decision`. A scenario a source requires but with one detail
the team set reads `Spec · team decision on a detail` (or `Spec + Design · …`) and also has a row in "Team
decisions" that names the detail. The Tests cell names the kind of test (`$ORCHARD/references/test-strategy.md`)
and the test, or carries an allowed untested tag.

**Untested tags.** Core default: `@blocked:<reason>` only, the reason saying what blocks a test. A project may
override it with the profile key `tag_policy_untested`, for example to add its manual tag for what no test can
drive; without that key the default applies.

## 3. Checks

`python3 -I $ORCHARD/scripts/gate_check.py <feature file> <register> [--report <plan file>] [--id-pattern <regex>]`,
with `--id-pattern` set from `scenario_id_pattern`, fails when:

- a scenario of the feature file has no row with a Basis, or more than one;
- a Basis is not one of the allowed values, or a row has no spec clause and no evidence;
- a basis with Design cites no frame id;
- a team decision (whole or on a detail) has no row in "Team decisions", or that row has no date;
- "Team decisions" or a scenario table lists an id the feature file no longer has;
- a row has no test and no allowed untested tag (section 2);
- with `--report`: a scenario id of the feature file is missing from the plan file.

It prints the counts for "At a glance". The coverage mode for a plan file (`--coverage`) is described in
`$ORCHARD/references/scenario-draft.md`, section 5.

Before finishing, also confirm by hand: each quote is in the page version cited, each frame id passed the design
adapter's existence check (`$ORCHARD/references/scenario-gate.md`, section 1), each link is a full URL or a
repository path.
