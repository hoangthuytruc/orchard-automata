# Scenario gate: sources, decision rules and re-check

Used by `plan` in every mode: drafting scenarios for new work, and re-checking the existing scenarios of a feature
against their sources. Sections 1 and 2 hold for both; section 3 is the re-check. The reviewer reads sections 1 and 2 to
check a change against its sources (`$ORCHARD/references/review-checklist.md`, part A); it reports and settles nothing. Drafting from scratch is in
`$ORCHARD/references/scenario-draft.md`. Writing the approved result into the knowledge base, the register template
and the checks are in `$ORCHARD/references/scenario-register.md`. The project's guides override anything here.

Scenario, basis, source, requirement and register are defined in `$ORCHARD/docs/terms.md`. Which conflicts an agent
settles and which go to a person is in `$ORCHARD/docs/boundaries.md`, "Conflicts"; the rules in section 2 apply
that table to scenarios.

## 1. Sources

External systems are optional source adapters. Read each source from the system the profile names, or from a file
the developer gives; never assume a particular tool exists. Record for every source what lets someone else open the
same thing: page id or path, version and date for a spec; key and status for a ticket; file, version and frame id
for a design; file and symbol for code.

| Source | Profile keys | How to read it | Standing |
| --- | --- | --- | --- |
| Spec | `spec_source`, `source_ranking` | The full text of each page, not a search excerpt. Start from the pages the feature file and the register cite, then check whether each page's version moved since the cited one. | **Current** specs are a basis. **Legacy** pages (an earlier product or release, pages the profile ranks as superseded) explain intent and are not a basis. |
| Ticket | `tracker`, `source_ranking` | The ticket with its comments when the description is thin. | Supports a spec: acceptance criteria product confirmed, a done bug that fixed a rule. Core default: a ticket alone is not a basis. It is one only when the profile's `source_ranking` says so (`ticket alone is a basis`). |
| Design | `design_source` | The **reference version** the profile pins. Without a pinned version, the live file, and say so. | A basis for labels, layout, visible controls and states. |
| Code and tests | none | Search or a code index. The feature's views, models and use cases; the tests bound to each scenario. | Never a basis. It shows today's behaviour, where tests bind, and who owns a behaviour (client, remote config or server). |
| Decisions | none | The plan files already accepted, and the register's "Team decisions" table. | A dated decision by the owner or product is the basis `Team decision`. |
| Server catalogue or real backend | `backend_environments` | The backend's error-code page first; a recorded fixture next; one probe against a test environment last, and only under the four rules in `$ORCHARD/references/test-strategy.md`, section 5. | Settles what the server does. Never assumed. |

**Reading a design.** Whatever the tool, four things are needed, and a design adapter provides them (for example
`$ORCHARD/scripts/sources/figma_frames.py`, an adapter for one design tool among others; its token comes from the
environment only):

- **List** the frames of a page or section.
- **Text** of each frame, plus the notes that sit outside frames (designers write rules there, sometimes in another
  language: translate and quote them). Hidden layers are skipped.
- **Render** each frame that decides something to a picture and look at it: a back button, a disabled state or
  which button is primary is visible only in the picture, not in the text.
- **Exists:** prove that every cited frame is in the reference version.

When the design source is a folder of exported files, the same four things are read from the files.

Short names used in plan rows: a spec page as a short code (`<ABC>`) defined once in the plan's source line; a
design frame as `D/<frame id>`.

## 2. Decision rules

Apply these alone. Ask the owner only when none settles the case.

1. **A scenario stays only when a current spec or the reference design requires it.** Check each Given, When and
   Then, and each Examples row: remove the unsupported clause or row inside a kept scenario.
2. **No source, but the app already has a sensible rule** (a length limit, a preselection, a safe order of two
   calls): propose it as a team decision. Until the owner confirms, it is "to confirm", not kept. With the
   confirmation it becomes `Team decision` with the date and the spec product must update.
3. **No source and no such rule** (inferred, legacy only, ticket only when tickets are not a basis): remove.
4. **Spec against spec:** the newer release's spec wins over an older page; a spec backed by a done bug and a
   design frame wins over a page nobody updated. Keep the scenario of the winner, retire those whose Given can no
   longer happen, and add "update page X" for product.
5. **Spec against design:** the design wins on labels, layout and visible controls; the spec wins on behaviour and
   data rules. Where the owner already decided otherwise, record that decision instead.
6. **Server-decided values** (lock counts, caps, waits, expiry, send limits) are not conflicts and not app rules.
7. **Owner of a behaviour:** server, client or remote config. A fix goes to its owner. No client copy of a server
   rule, no workaround.
8. **Errors and labels:** use the label and the error surface the spec or design names. Never invent a label; when
   none is named, describe the behaviour without one and list the gap for product.
9. **A scenario lives in the feature that owns its entry point.** Look for a duplicate in the other feature files
   before moving or adding one.
10. **Trust nothing stale.** Compare each scenario's title and steps with the file on disk when you write its row
    (files change during the work). A bound test whose name or body does not match the scenario is a finding.
11. **Product language** comes from the project's glossary or terms page. Scenarios use the words a person sees,
    never view, model, API or fixture names.
12. **A gate scenario is an outcome product would refuse to ship without.** A scenario that only checks that a
    control, a layout or a text is present is a design check or a unit test, even when a frame shows it. Never
    remove one for this reason alone: list it as "not a gate scenario, to confirm" and say where it belongs.
13. **A shared rule is proven once**, in the feature that owns the shared spec (a framework, a permission flow, a
    common component). Another feature gets a scenario only where it changes the rule.
14. **An end-to-end scenario stays whole.** Never split it to keep features apart. It lives where its entry
    point is (rule 9), and its test may use another feature's types to finish the flow.

In anything a person reads, give each reason in words. Never cite a rule of this file by number: the reader does
not have this file.

## 3. Re-check of existing scenarios

A re-check is `plan` with scenario changes only: no code changes, no work packages. A feature with no scenarios yet
is a draft (`$ORCHARD/references/scenario-draft.md`), not a re-check.

1. **Scope and inventory.** Write the feature's scope first: the entry points it owns, its spec pages and design
   pages, and what it leaves to another feature, by name. Then parse the feature file in the knowledge base
   (`knowledge_base`): id (`scenario_id_pattern`), title, rule, tags, bound tests. Read the register rows
   (`register`).
2. **Read the sources** (in parallel where the tools allow): every cited spec page at its current version, the
   tickets, the design pages as text, then renders of the deciding frames. Note what changed since the cited
   versions.
3. **Walk the scenarios.** For each one: find the clause or frame, quote it, set the basis, apply the rules. Keep a
   working table: id · verdict · basis · evidence · app today (file, symbol) · tests bound · note.
4. **Read the app** for each verdict that depends on it: what it does today, and whether a kept scenario is true.
   A kept scenario the app does not satisfy is an app change; a server gap is a backend change.
5. **Walk the sources the other way.** For each step, rule, alternative flow and error in the current specs, and
   each frame and state in the design: is there a scenario? A missing one is a proposed scenario with its basis.
   Note the density on the way: a requirement that three or more scenarios prove (likely duplicates), and a
   scenario that proves several unrelated requirements (too broad). These are flags for the owner, not verdicts.
6. **Write the plan file** from `$ORCHARD/templates/plan.md`, as mapped below, and run the coverage check
   (`$ORCHARD/references/scenario-register.md`, section 3).
7. **Ask** the collected questions together: the team decisions to confirm and the conflicts no rule settles.

### Where a re-check's results go in the plan file

The plan file is the only record of the re-check; there is no separate report. Every scenario id of the feature
file appears in section 5.

| Result | Plan section | How it is written |
| --- | --- | --- |
| Outcome: scenarios checked, confirmed, to remove, team decisions (to confirm), to add; app and backend changes; questions | Top part, "Scenarios" | Counts in one line, then the plain-words list |
| Scope | 1. Scope | This feature owns: entry points, spec pages, design pages. Out of scope: behaviour and the feature that owns it |
| Every requirement the current sources state | 2. Requirements | One line each with its quote, and the scenario or the reason for none |
| App must change; backend must change | 3. Design change, and 4. Impact | Today (file, symbol), change, owner |
| Each scenario's verdict | 5. Scenario changes | Change column: `Keep`, `Reword`, `Remove`, `Add`, `Team decision (decided <date>)`, `Team decision (to confirm)`, `Not a gate scenario (to confirm)`; with basis, evidence, kind and test (bound today, or to add and how) |
| Spec updates for product; conflicts no rule settles; team decisions to confirm | 6. Open questions | Question, options, recommended, what it blocks |
| Sources and method | Source line at the top of the working detail | Pages with id and version, tickets with status, design file, version and pages, backend probes, decisions with dates |

Every link is a full URL or a repository path. A re-check plan goes from `approved` straight to `accepted` once the
developer accepts it; `update-docs` then writes it into the knowledge base.
