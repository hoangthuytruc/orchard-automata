# Scenario gate: drafting scenarios

Used by `plan` when a feature or an area has no scenarios yet, and for the scenarios a new piece of work adds.
Sources, their standing and the decision rules are those of `$ORCHARD/references/scenario-gate.md`, sections 1 and
2; read those first. The project's guides override anything here.

Contents: 1 Steps · 2 The requirement list · 3 Writing a scenario · 4 Where a draft goes in the plan file · 5 Check

## 1. Steps

1. **Ground, sources and scope**, as in a re-check: the current spec pages and versions, the tickets, the reference
   design version, the decisions already made. Write the feature's scope: the entry points it owns, its pages and
   frames, and what it leaves to another feature, by name. Read the other feature files in the knowledge base, so
   a behaviour that already has a scenario elsewhere is not written twice.
2. **Build the requirement list** (section 2). Finish it before writing any scenario.
3. **Write the scenarios** from the list (section 3), each with its basis and evidence.
4. **Handle what has no source.** A behaviour the app already has but no spec or frame states goes to the owner as
   a team decision to confirm. A behaviour you think is sensible but nothing states is a question, not a scenario.
5. **Read the app** for each scenario: does it do this today? One it does not do yet is still a scenario; mark it
   as a gap with its owner (app, backend).
6. **Write the plan file** (section 4) and run the check (section 5). Ask the open questions together.
7. **Stop.** The knowledge base is written by `update-docs`, after acceptance, from the delivered scenarios only.

## 2. The requirement list

One line per thing the sources require. Walk every spec page top to bottom and every frame of the design pages; do
not sample.

| Kind | What to look for |
| --- | --- |
| Rule | a statement of what is always true ("the balance is purchases minus refunds") |
| Flow step | each step of a main flow, and each alternative flow |
| State | each state a screen or item can be in, and each frame variant (empty, loading, disabled, done) |
| Limit | a length, count, format or time the client enforces |
| Error | each failure the spec or a frame names, and what the person sees |
| Exit | cancel, back, close, leaving the app and coming back |
| Role | a behaviour that differs by role, plan or permission |

Each line carries its source (the page's short name and section, or `D/<frame id>`) and a short quote. Split a
sentence that states two behaviours into two lines. Leave out, with the reason: values the server decides,
behaviour that another feature owns, a shared rule that the owning feature already proves, and anything the
project's scope page puts outside the release.

A line that only says a control, a layout or a text is present is not a behaviour. Fold it into the scenario whose
outcome shows it, or leave it out as `none: design check`. Write a scenario for it only when product would refuse
to ship without that outcome.

## 3. Writing a scenario

Defaults; the project's feature-file format, tags and id scheme win.

- **One behaviour, one scenario:** as many Givens as the starting state needs, then one action (When) and one
  outcome (Then, with And for parts of the same outcome). The limit is on the action and the outcome, not on the
  preconditions. A scenario about a state still has a When: the person opens or looks at the screen. A second
  action or a second outcome is a second scenario. Use an outline with examples when only the values change.
- **Group under the product rule** the scenarios prove, in the product's words.
- **Order:** entry and structure, core journey, variations by role and state, input validation and limits,
  failures and recovery, leaving and exit. Happy path first inside each.
- **The person's words:** what they see and do. Quote on-screen text exactly as the frame or spec gives it. No
  view, model, API or fixture names.
- **A title that states the outcome** ("A refund is returned to the balance"), not the action ("Refund test").
- **Server values:** write "the limit the server sends", not the number.
- **Provisional ids** `N1`, `N2`, … in the plan. `update-docs` assigns the real ids by `scenario_id_pattern`;
  ids are never reused.
- **Basis:** `Spec`, `Design`, `Spec + Design`, or `Team decision` (confirmed, with who and date).
- **Tests:** name the kind of test that will prove each (`$ORCHARD/references/test-strategy.md`, section 4), its
  oracle when it is not a plain example, and which test double it needs. Do not write tests while planning.

## 4. Where a draft goes in the plan file

The draft is part of the plan file (`$ORCHARD/templates/plan.md`); there is no separate report.

| Draft content | Plan section |
| --- | --- |
| Outcome: requirements found in how many pages and frames; scenarios proposed by basis; team decisions to confirm; requirements left out with a reason; questions | Top part, "Scenarios" |
| Scope | 1. Scope |
| The requirement list (coverage) | 2. Requirements: one row per requirement, with the scenario that covers it or `none: <reason>` |
| Proposed scenarios, under their rule and in their order | 5. Scenario changes, Change `Add` |
| Team decisions to confirm | 5. Scenario changes, Change `Team decision (to confirm)`, and a row in 6. Open questions |
| App must change; backend must change | 3. Design change, and 4. Impact |
| Spec updates for product; open questions | 6. Open questions |
| Sources and method | Source line at the top of the working detail |

Example rows:

```markdown
| R1 | A refund is added back to the balance at once | <ABC> v3 | "A refund is added back to the balance at once." | N2 |
| R7 | Five purchases at launch | <ABC> v3 | "5 at launch" | none: the server decides the number |

| Add | N2 — A refund is returned to the balance | Given … · When … · Then … | Spec | <ABC> §2: "…" | unit | example | store with a fake clock |
```

## 5. Check

`python3 -I $ORCHARD/scripts/gate_check.py --coverage <plan file>` fails when:

- a requirement row names no scenario and gives no `none: <reason>`;
- a requirement row names a scenario that section 5 does not define;
- a proposed scenario is in no requirement row (nothing requires it) and is not a team decision to confirm;
- a proposed scenario has no valid basis or no evidence.

It also prints review flags, which do not fail the check: a requirement with three or more scenarios (likely
duplicates) and a scenario that covers four or more requirements (possibly too broad). Look at each and either
merge, split or say in the plan why it stands.

Before finishing, confirm by hand: the requirement list covers every page section and every frame you were given,
each quote is in the page version cited, and each frame id is in the reference version.
