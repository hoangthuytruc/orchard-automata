# iOS review checklist

Used by the reviewer role (`$ORCHARD/roles/reviewer.md`), by the `review` skill and by the review rounds of a run
(`$ORCHARD/references/run-flow.md`). Each line is a question with the cheapest way to answer it. A mechanical hit
is a candidate; a finding needs the breaking input, state or ordering, or the missing evidence, plus a concrete fix.

This file is the only home of the finding labels (part D) and the review output (part E). The bar the code is held
to is `$ORCHARD/references/standards.md`; this file asks whether the change meets it. The project's review rules
(profile key `review_rules`) and guides (profile key `guides`) win over both.

Contents: A General review · B Mechanical scan · C Line review (sections 1–11) · D Labels · E Output

Some rules here are adapted from an MIT-licensed review skill; see `$ORCHARD/THIRD_PARTY_NOTICES.md`.

## How the parts are used

1. **Context first.** Read the plan when there is one, the change's description and linked ticket, the size of the
   diff, the evidence that exists for it (CI checks, a verify evidence file), and the project's guides and review
   rules. Know what the change is for before reading a line.
2. **General review** (part A) on the change as a whole, before any line.
3. **Mechanical scan** (part B) for candidates.
4. **Line review** (part C) of every changed file in full, plus the types it depends on.
5. **Counterexamples.** List the assumptions that make the change look right and try to break each with a concrete
   input, state or ordering: nil, empty, duplicate, stale async result, cancellation, second tap, month boundary,
   time zone, concurrent writer. Keep only what holds up against the intended contract.
6. **Sort and write** with the labels (part D) in the output format (part E).

Not reviewed by hand: formatting, import order and anything the linter enforces. A lint breach is a finding only
when something works around the linter (an inline disable without a reason).

## A. General review (the whole change)

These are judged on the change as a whole. What they turn up is written as open questions to the author, in
plain words, never forced onto one line.

**Fit**
- Does the solution fit the problem, at the size of the problem? Signs of over-engineering: a simple `if` replaced
  by a strategy, a factory and a registry; a protocol with one conformer; a generic with one use; a layer added
  for "later"; a pattern that made the code much longer and no easier to test. A pattern earns its place when it
  solves an extension problem the code actually has.
- The opposite failure: the same technique used for every problem because it is familiar.
- Does everything in the diff serve the stated task? Is it small enough to review well (past roughly 400 changed
  lines, name the split)?

**How it is built**
- Which pattern does the change use for state, navigation, dependency injection and networking, and is it the one
  its neighbours use? A deviation is a decision: it cites a reason or it is a question.
- Is a pattern applied where it pays (a strategy for a growing `switch`, a builder for parameter sprawl), and not
  applied where a plain function would do?
- Responsibilities: one reason to change per type. Can the type be described in one sentence? If requirement X
  changes, which of its methods change, and if Y changes? Signs of trouble: a type that knows the network, the
  storage and the screen; a view model past a few hundred lines; a helper named `Manager` or `Utils`.
- Size signals for triage, never findings on their own: a file past about 300 lines, a function past about 50, a
  type past about 200, more than three parameters, nesting deeper than three levels.

**How it fits the codebase**
- Dependency direction: domain imports no UI or infrastructure framework; features depend on protocols, not on
  concrete infrastructure; composition happens in the root. No cycle between modules. A call to an external
  service goes through a protocol that a test can replace.
- Layer leaks: a persistence, transport or server format type returned across a boundary; a view formatting a
  server value; a use case knowing a screen; a screen calling a repository or the network directly.
- One owner per state; no duplicated source of truth; derived data is computed, not stored. No global mutable
  state shared between modules.
- Coupling and cohesion: does a change here force a change in an unrelated module? Do the things in one type
  change together and work on the same data? Watch for a whole model passed where one field is used, a boolean
  flag that switches what a function does, and code that reaches into another type's internals.
- Extension without edit: will the next variant need a new case in five places? Will this `switch` grow with every
  new type?
- Substitution: does every conformer honour the protocol's contract (no `fatalError("not supported")`, no error
  the protocol does not promise)?
- Interface size: does a protocol make its users depend on methods they do not call? Is the protocol owned by the
  side that uses it?
- Growth: does the change hold up when the data grows (paging, a list of thousands, a cache with no bound)?

**Open questions**
- Everything above that is not a defect on a line becomes a question to the author: a choice of structure that
  differs from its neighbours, a responsibility in a surprising place, a boundary that leaks, something built
  for later.
- Also what the reviewer could not decide from the change: an unstated requirement, a behaviour that could be
  intended or a bug, a trade-off that needs the author's reason, a product rule with no source.
- One clear question each, in plain words: what you saw (with its `path:line`), what you would expect, and what
  the answer changes. No pattern names and no jargon ("SOLID", "coupling", "design pattern", "architecture"): say
  what the code does and what it costs. Ask about the code, never the person.
- A question is not a way to soften a defect. What is wrong on a line is an inline finding.

**Against the plan** (when there is one)
- Is the design change of the plan what was built? Does every scenario row have its test, and does the test prove
  it? Did anything outside the plan's packages change? Was any test weakened?

**Against the sources** (with or without a plan)

A test bound to a scenario proves the scenario, not that the scenario is right. The reviewer reads the product
sources itself; how to read each one and what standing it has is `$ORCHARD/references/scenario-gate.md`, section 1.
Where they are comes from the profile (`knowledge_base`, `spec_source`, `design_source`, `tracker`,
`source_ranking`) and from the ticket the change links.
- Which scenarios does the change touch? With a plan, its scenario rows; without one, the scenarios bound to the
  changed tests and those whose steps describe the changed behaviour.
- For each: open the cited basis at its current version and quote the clause or the frame. Do the scenario's Given,
  When, Then and Examples say what the source says? Does the test's assertion say the same (same value, label,
  error surface)? A scenario with no basis, or with only code or a superseded page behind it, is a finding.
- Did a cited source change since the plan was approved, or since the version the feature file cites?
- The other way: does the diff add a behaviour, a rule, a label, an error or a visible state that no scenario and
  no source states? Does the ticket or the spec for this change require something the diff does not do?
- Labels, layout and visible controls: where the evidence holds a screenshot and the design has the frame, compare
  them.
- A mismatch is an inline finding on the line that shows it (the assertion, or the code that implements the
  behaviour), with both readings quoted and their sources. When a decision rule of the scenario gate (section 2)
  settles it, say in words which reading wins and why; when none does, it is an open question for the owner. The
  reviewer never picks a side no rule gives it, and never edits a scenario.
- A source the reviewer could not open (no access, key missing from the profile) is named under "Sources" in the
  output as not checked, with the reason. It is never passed as checked.

**Verification**
- What evidence exists for this exact change (CI checks, the verify evidence file, test kinds touching the changed
  contracts), and what is missing. The reviewer does not run the tests.

## B. Mechanical scan

Grep the diff for each pattern. Each hit is a candidate to confirm in the line review, never a finding by itself.
Add the project smells listed in its review rules.

- `!` after an identifier or `)`, `try!`, `as!`, `.first!`, `[0]`, `var x: T!` outside outlets
- `DispatchQueue`, `DispatchSemaphore`, `static var`, `@unchecked Sendable`, `nonisolated(unsafe)`,
  `Task.detached`, `Task {`, `MainActor.assumeIsolated`
- `Date()`, `UUID()`, `.random`, `Locale.current`, `TimeZone.current` inside the type under test
- `sleep(`, `Task.sleep`, `asyncAfter`, raised timeouts, `.serialized`
- `@ObservedObject var … = …(` (a model created under the wrong wrapper)
- `onAppear` with a `Task` or an `await` inside; `onChange` beside `onAppear`
- `@Published`
- `try?`, an empty `catch {}`, `catch { throw error }`, `_ =` on a throwing or `@discardableResult` call
- `UserDefaults` near `token|secret|password|key`; string-built URLs (`"https://` with `\(`)
- `accessibilityIdentifier("` with a literal
- `print(`, `NSLog(`, `Logger` interpolation without a privacy level
- `TODO|FIXME|HACK`
- `default:` in a `switch` over an app enum
- `XCTSkip`, `.disabled`, `withKnownIssue` without a reference

## C. Line review

### 1. Correctness

- Every new branch has an input that reaches it and a test that proves it. Boundaries: empty, nil, zero, max, one
  element, duplicates, unsorted input, off by one at either end, month or day boundaries, time zones.
- Optionals: what happens when each new `?` is nil? A default from `??` must be a value the product wants, not a
  way to hide a missing one. An implicitly unwrapped property is a hidden force unwrap on every access: inject the
  dependency as a non-optional instead.
- Boolean logic: negated compound conditions (`!(a && b)` is `!a || !b`), inverted guards.
- Sign, unit and rounding: cents versus decimals, percentages, `Int` overflow and underflow, `Double` equality.
- Ordering: does the code depend on dictionary or set order, or on the order async results arrive?
- Check-then-act: a check and the action it guards are separate steps something else can interleave (file
  exists then read, balance read then write, any `await` between the two). Do the action and handle the failure.

### 2. Error handling

- Every thrown error reaches the user or a log as a typed, handled case. No `try?` or empty `catch` on a path
  that matters; no catch-and-rethrow that adds nothing. Catch only to add context or to recover.
- An error is handled once: not logged, wrapped and rethrown at every layer. The layer that decides handles it.
- Error types say what went wrong in the domain's terms and carry the context a reader needs (the operation and
  the key values, never a secret). A transport or storage error is mapped at the module boundary and does not reach
  a view as is; when wrapped, the underlying error is kept.
- Errors are not used for ordinary control flow. Results that matter are not discarded.
- Typed throws only for a closed set of errors; `Result` only where an outcome is stored or passed later.
- Preconditions are checked before the work starts, so a failure cannot leave it half done.
- A failure leaves state consistent: no half-written store, no spinner left on, no flag set before the work
  succeeded.
- What the person sees on failure names the problem in their words and exposes no internals (no stack, no server
  body, no query).

### 3. Concurrency (Swift 6 lens)

- Mutable state shared across tasks or queues without an actor or `@MainActor`: `DispatchQueue`, `static var`,
  `var` on a non-actor class used from async code.
- Isolation of each new type is explicit and correct: UI-facing state on `@MainActor`; `Sendable` conformance of
  anything crossing a boundary, without `@unchecked` or `nonisolated(unsafe)` unless justified; an `@unchecked
  Sendable` type guards every access to its state with one lock.
- Tasks have an owner: a `Task {}` is stored and cancelled with it, or it is a `.task` tied to a view. No
  fire-and-forget work that outlives its screen. Parallel work uses `async let` or a task group, not loose tasks.
- Independent awaits that run one after another where `async let` would run them together.
- A task group over a large input limits how many children run at once. A fast producer feeding an `AsyncStream`
  has a buffering policy.
- No blocking call inside async code: a semaphore wait, synchronous file or network I/O, a lock held across an
  `await`.
- Cancellation is checked in loops and before writes, and reaches every child. Long work can be cancelled or
  times out. Continuations resume exactly once on every path.
- Stale results: a slower earlier request overwriting a newer one (guard with task identity or cancellation).
- Reentrancy: an actor method awaiting mid-way while state changes underneath.
- Locks: taken in one consistent order, never nested without reason, held as briefly as possible.

### 4. Memory and lifecycle

- A closure stored by a longer-lived object captures `[weak self]`, or the ownership is explained. `unowned`
  only where the lifetime is proven: a callback that can fire after the owner is gone crashes with `unowned`.
- Delegates are `weak`, and their protocols are bound to `AnyObject`.
- Observers, notification tokens, timers and `AnyCancellable`s are stored and removed; file handles and streams are
  closed (`defer`).
- Large data (images, decoded payloads) is not held on the main actor longer than needed.

### 5. Types and API design

- Value or reference is a choice: a struct by default; a class for identity or shared mutable state, `final`
  unless designed for subclassing. A reference type inside a struct breaks value semantics without saying so.
- `some` over `any` where one concrete type flows through; a generic constraint over an existential in a hot path;
  `any` only for truly mixed values.
- Names read as phrases at the call site (Swift API Design Guidelines); a method name tells whether it mutates
  (`sort()` against `sorted()`); booleans read as assertions; no needless words; no abbreviations the codebase
  does not use.
- Access control is the narrowest that compiles; `public` and `open` are intentional; `private(set)` exposes state
  read-only.
- Comments follow the project's policy; no narrative comments, no commented-out code, no TODO without an owner or
  ticket where the project requires one.

### 6. SwiftUI and UIKit

**Async work and lifecycle**
- Async work starts in `.task`, never in `.onAppear { Task { await … } }`: SwiftUI cancels a `.task` when the view
  disappears; a loose `Task` keeps running and leaks.
- Work that reruns when a value changes (a search text, a selected id) uses `.task(id:)`, not `.onAppear` plus
  `.onChange` wired by hand.
- `.onAppear` holds only light synchronous work: an analytics event, a simple animation, focusing a field. Nothing
  that blocks the main thread.

**State and view model ownership**
- `@State` for a value the view owns; `@StateObject` for a model the view creates; `@ObservedObject` for a model
  owned elsewhere and passed in (or an `@Observable` type taken directly when the project targets iOS 17 or later);
  `@Binding` for a parent's value the child edits.
- `@ObservedObject var vm = MyViewModel()` is always a finding: the model is rebuilt when the view redraws, and its
  state is lost.

**Re-renders**
- `@State` lives in the smallest view that needs it. State that serves one small component, kept high in a large
  parent, redraws the whole parent: move it into its own subview.
- `@Published` only on properties that drive the UI. Raw data and internal bookkeeping stay plain properties, so
  a change to them redraws nothing.
- A subview receives only the values it shows, not a whole model or a large struct: otherwise it redraws when an
  unrelated field changes.
- View identity is stable: `ForEach` over a stable id, no `id:` on an index or a value that changes; no `if` that
  rebuilds a subtree where a modifier would do. `.id(…)` only to reset a view's state on purpose.
- No heavy work, formatting or allocation in `body`.

**Separation and size**
- A view renders and forwards the person's actions to its view model or router. No data manipulation, API call,
  business rule or server format in the view or its `body`.
- A view struct past about 200 lines is split into smaller dedicated `struct` views. Computed view properties
  (`var section: some View`) only where the project allows them; some projects forbid them.
- Navigation goes through the flow's owner.

**Accessibility and previews**
- Every new interactive control has an accessibility identifier from the project's constants and a label; Dynamic
  Type and VoiceOver are not broken (fixed frames on text, images without labels, colour-only state).
- Previews exist for the new states. Project-specific pitfalls are avoided.

### 7. Collections and performance

- No membership test or lookup in a loop over an array where a `Set` or `Dictionary` fits; no nested loop over two
  growing collections; no sort or filter repeated per row.
- No whole collection or file read to use one element; filtering is pushed down to the store or the request
  where it can be; `lazy` for a chain over a large sequence that is cut short.
- `compactMap` over `map` then unwrap; `reduce(into:)` when building a collection; `Dictionary(grouping:)` for
  grouping.
- No blocking I/O, decoding or image work on the main actor; no request per item in a loop; lists use lazy
  containers; list requests are paged and fetch only the fields they show.
- A cache has a bound and an invalidation rule.
- Changes to launch, scrolling or memory-heavy paths come with a measurement or an explicit "not measured".

### 8. Code quality

- Reuse: does a helper, extension or component for this already exist? Search the whole repository, adjacent files
  and shared modules, not the diff.
- Near-duplicates: two blocks that differ by a field name, a string or a constant. One shared function with a
  parameter, not two copies.
- Parameter sprawl: a function gaining one argument per requirement, or more than three; boolean flags that switch
  behaviour, or two flags that exclude each other. Group them in a type or replace the flag with an enum.
- Stringly-typed code: a raw string or number where the codebase has an enum or a constant; event names, status
  values or keys scattered across files; string comparisons that silently depend on case.
- Nesting: an `if` past two levels or a chained ternary; use `guard`, early exits, a `switch` or a lookup table.
- Redundant state: a stored property that could be derived, or a cache with no invalidation; an observer that a
  direct call would replace.
- No-op work: a timer, observer or poll that writes or publishes when nothing changed; set a value only when it
  differs.
- Dead weight: unused code kept "for later", a flag nobody reads.

### 9. Security and privacy

- No secret or token in `UserDefaults`, a plist, source, configuration or a log. Keychain or the project's secure
  store, with an accessibility class that fits.
- Inputs from the network, deep links, the pasteboard, files or a web view bridge are validated; URLs are built
  with `URLComponents`, not string concatenation. Paths from outside are not joined into file paths unchecked.
- A check in the app (a role, an owner, a hidden button) is a convenience; the server must also enforce it. The app
  never relies on an id being hard to guess.
- Cryptography from the platform only; tokens and nonces from a secure random source.
- Personal data at rest uses fitting file protection and is removed on sign-out; data in transit uses HTTPS with
  App Transport Security on.
- Logs redact personal data and never log tokens; log lines built from outside input cannot fake another line;
  analytics events contain no personal data; the privacy manifest is updated for new required-reason APIs or data
  collection.
- A new dependency comes from a trusted source, is pinned in the resolved file, and has no known vulnerability.

### 10. Tests as evidence

- Each changed contract has a test at the cheapest kind that can observe it (`$ORCHARD/references/test-strategy.md`):
  initial state, trigger, transition, side effect, outcome. A test named after the feature is not a test of the
  branch.
- Tests assert behaviour, not implementation details: a refactor that keeps the behaviour keeps the test green.
- Tests are deterministic: injected time, ids and randomness; no sleeps, retries, raised timeouts or `.serialized`
  without a reason; no shared static state. Async tests await a value or a state, never a delay.
- Negative and boundary cases exist for the new branches; an error-path test asserts the specific error; a bug fix
  carries a regression test that fails without the fix.
- Test doubles fail on unexpected calls; no test reaches a live service; fixtures contain no real data; setup is
  small enough to read.
- UI tests use identifiers, not text; they wait on state, not time.
- Nothing was skipped, disabled, deleted or lowered (coverage threshold, precision) to make a run pass.

### 11. Hygiene

- A draft pull-request body follows the project's template (profile key `pr_template`); "not verified" items are
  named.
- No generated files, secrets, personal data, or report or build artefacts in the change.
- Lint passes with the project config; no inline rule disable without a stated reason.

## D. Labels

Every inline finding carries a type and a severity. A Blocker or a Risk is High or Medium; a NOTE is Low, NIT, or has none.

| Type | Meaning | Blocks |
| --- | --- | --- |
| Blocker | The change cannot ship: it is broken, or it breaks something else. | Yes |
| Risk | It works, but a likely input, state or ordering would make it fail. | Yes |
| NOTE | Worth knowing; no change required. | No |

| Severity | Meaning | Blocks |
| --- | --- | --- |
| High | A required or planned behaviour is missing or wrong. | Yes |
| Medium | Correct, but a contract has no test, or a standard is broken. | Yes |
| Low | A small defect with little effect on the person using the app. | No |
| NIT | Style or naming. | No |

**What blocks:** a Blocker or a Risk, whatever its severity, and anything at High or Medium. A NOTE never blocks;
its severity, when it has one, is Low or NIT. In a run, what blocks opens a fix round; what does not block goes to the developer in the test report,
who decides at acceptance. General comments carry no label; when one of them must block, it is also written as an
inline finding on the line that shows it.

A security hole a person could exploit is a Blocker; one that needs unusual conditions is a Risk.

## E. Output

A review has two kinds of comment, and they are never mixed.

**General comments** go in the review's summary: the verdict in one sentence, then the open questions (which
carry everything about how the change is built and how it fits the codebase), verification, and what is good.
They are about the change as a whole.

**Inline comments** are the findings. Each is anchored to one line (or a short range) that the change added or
touched, on the side of the diff where it shows, and carries its type, severity, evidence and fix. Anchor to the
line that causes the problem, not the first line of the function. One problem per comment. A finding about code the
diff does not touch goes to the summary under "Outside the diff", with its `path:line`.

```
## Review: <target>

**Verdict:** <request changes | comment>: <one sentence>. <n> blocking, <n> not blocking.

### Open questions
1. `path:line` <what you saw, in plain words>. <the question>? <what the answer changes>

### Verification
- Evidence: <what ran for this change>
- Gaps: <untested contracts, checks not run, manual sign-off needed>
- Sources: <each source read, with its version or date; "not checked: <source>, <reason>">

### What's good
- <two to four lines the next contributor must not "fix">

### Outside the diff
- `path:line`: <finding about untouched code that the change relies on>

## Inline comments
(most severe first)

### `path/File.swift:42` · Risk · High
**<Short claim.>** <The problem in technical terms; the breaking input, state or ordering, or the missing
evidence.>

Suggested fix: <the concrete change in one or two lines>
```

An inline comment's fix is a suggestion block (` ```suggestion `) only when it replaces exactly the anchored
lines and compiles as written; otherwise it is prose.

Style: exact identifiers; repository-relative paths with line numbers; specific and actionable; no hedging, no
filler, no praise inside a finding, no mention of tools or AI. A section with nothing to say reads "none". The
review never approves.

**Review of fixes.** After a fix round the reviewer gets only the findings that were fixed and the diff since the
last review. It answers per finding: fixed, not fixed, or fixed and broke something (a new finding in the format
above).

**Payload for posting.** For a pull request target the reviewer also writes the same review as JSON, ready for
`POST /repos/{owner}/{repo}/pulls/{n}/reviews`, and names the file on the last line of its message. Posting it is
the developer's decision (`$ORCHARD/scripts/post_review.py`).

```json
{
  "commit_id": "<head sha reviewed>",
  "body": "<the general comments, from Verdict to Outside the diff, as Markdown>",
  "comments": [
    {"path": "Sources/App/File.swift", "line": 42, "side": "RIGHT",
     "body": "**Risk · High. <Short claim.>** <problem>\n\nSuggested fix: <change>"}
  ]
}
```

`line` is a line number in the file at the reviewed head and must lie inside a diff hunk of that file (`side`
`LEFT` and the old line number for a deleted line; `start_line` with `line` for a range in one hunk). A finding
that cannot be anchored this way moves to "Outside the diff". The payload carries no `event`: it is never an
approval.
