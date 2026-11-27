# Test strategy

How a change is proved, cheapest proof first. Used by `plan` (to name the kind of each planned test), `implement`
and `test` (to write it), `verify` (to run it), `review` (to judge it) and `handoff` (to report it). Words such as
unit test, behaviour test, oracle, fixture and affected tests are defined in `$ORCHARD/docs/terms.md`. Commands,
time budgets and which kinds are enabled are project values in the profile (`test.unit`, `test.behaviour`,
`test.visual`, `test.integration`, `lint`, `affected_map`, `backend_environments`).

Contents: 1 The seven checks · 2 Each check, defined · 3 Where iOS code is tested · 4 Choosing a kind ·
5 Stubbed or real backend · 6 Design match is not a visual test · 7 The four axes · 8 Rule for plans ·
9 Rules that save time · 10 Evidence about the final change · 11 Determinism · 12 Test doubles ·
13 Writing a test · 14 Flaky tests · 15 Suite audit · 16 What a test may assert ·
17 A finished test set

## 1. The seven checks

This is the test pyramid applied to a run: each scenario is proved by the cheapest kind of test that can fail for
the right reason, and each kind runs only as often as its cost allows. The seven rows run from cheapest to most
expensive: five kinds of automated check, then the full regression run and manual checks. Those two are not kinds,
but they are scheduled the same way.

| Check | Proves | When it runs | Selection |
| --- | --- | --- | --- |
| Static analysis | Rules a script can see | Every round | Whole change |
| Unit tests | One rule, calculation, mapping or data-layer contract, alone | Every round | Affected tests only |
| Visual tests | How a screen looks: layout, clipping, styling, themes | Once per run, after the last edit, when the profile enables them | Affected tests only |
| Behaviour tests | How the app reacts: state changes, navigation, the outcome of a journey | Every round when in-process; once per run, after the last edit, when through the UI | Affected tests only |
| Integration tests | Every endpoint the app calls works against the real backend | Once per run, after the last edit, only when the plan names endpoints; never as a default every run | The endpoints the plan names only |
| Full regression run | Regressions outside the change | Outside the run: CI or release | All tests, all endpoints |
| Manual checks | What no automated check reaches | After the run | Items the report lists as not automated |

## 2. Each check, defined

| Check | What it does | In scope | Out of scope |
| --- | --- | --- | --- |
| Static analysis | Reads the code without running it | The whole change: lint rules, dependency rules between layers, locked-file hashes, a test traced to every scenario | Anything that needs the code to run |
| Unit tests | Runs one type or function alone; everything it depends on is a test double | One unit: a rule, a calculation, a mapping, a validation, its error paths. In the data layer: decoding, error mapping and repository wiring, on fixtures | Screens, live network, real time; a whole scenario's flow |
| Visual tests | Renders one screen in a fixed state and checks its appearance: a snapshot image, or the element hierarchy | How one screen looks: layout, nothing clipped by the keyboard or a small device, styling, dark mode, text size, element hierarchy, direct response to a touch | What happens after the tap; journeys; logic |
| Behaviour tests | Gives the app an input and checks how it reacts. Runs in-process by default: real units together, with test doubles for network, storage and clock. Runs through the UI in a simulator only when the claim needs real screens | One scenario's flow: the order of states, the side effects asked for, navigation, recovery from an error, the end outcome of a journey | How a screen looks; what the real server returns |
| Integration tests | Calls each endpoint the app uses on the real test backend and checks the reply against what the app expects | Every endpoint: request shape, sign-in, reply shape, values the server decides, error replies | Production; screens, journeys and app logic |
| Full regression run | Re-runs every existing automated test, in random order where the project supports it | The whole app, to catch effects outside the change | New behaviour; the kinds above prove that |
| Manual checks | A person uses the app on a device | What automation cannot reach: payments, push, system extensions, hardware, how it feels | Anything an automated kind can prove |

## 3. Where iOS code is tested

| Code | Proves | Kind | Test doubles | Speed |
| --- | --- | --- | --- | --- |
| Domain and model | Business rules, mapping, state machines, reducers | Unit | In-memory fakes, injected clock and ids | ms |
| Presentation (view model, store) | One intent and the state it produces, an error or empty branch | Unit | Fakes for use cases and services | ms |
| Presentation over a sequence | Intent to state transitions in order, the side effects requested | Behaviour, in-process | Fakes for use cases and services | ms |
| Data layer on fixtures | Response decoding, repository composition, error mapping, persistence round trips | Unit | Fixture transport (`URLProtocol` stub or replay), temporary store | ms–s |
| A scenario through the real assembly | A user story from input to outcome | Behaviour, in-process | Real composition, fixture backend | s |
| Snapshot of one screen state | A look that was already accepted | Visual | Fixtures | s |
| XCUITest journey | A journey that needs real screens; accessibility audit | Behaviour, through the UI | In-app mock or fixture server | min |
| Live contract | The backend still answers as the fixtures say | Integration | None: the real test backend | min |

Data-layer tests on fixtures are unit tests: they run in-process, in milliseconds, every round. The name
"integration test" is kept for tests against the real backend. Apple's "UI tests" (XCUITest) are behaviour tests
run through the UI, not visual tests.

## 4. Choosing a kind

Take the cheapest kind that can observe the claim.

- A claim about a value or a rule is a unit test.
- A claim about how the app reacts (a sequence, a state, a journey) is a behaviour test; it runs in-process unless
  the claim needs real screens.
- A claim about how a screen looks is a visual test.
- A claim about what the server says is an integration test.
- A claim about hardware or a third party is a manual check.

A scenario moves to a dearer kind only when the cheaper one cannot observe the claim, and the plan says why. A
final-state assertion alone does not prove a transition: assert the intermediate state, the side effect requested,
and the outcome.

## 5. Stubbed or real backend

A stubbed or a real backend is an option of a test, not a kind of test. Unit, visual and behaviour tests use test
doubles by default, so they stay fast and repeatable; a behaviour test may be pointed at the real backend when the
profile allows it, and it is still a behaviour test. Integration tests are the one kind that always uses the real
backend, because the backend is what they test.

Any call to the real backend, from a test or a single probe, follows four rules:

1. **Test environments only, never production.** Only the environments in `backend_environments`, with the sign-in
   method the profile gives. With `none`, no call is made.
2. **One targeted call per question, never repeated on failure.** Never a whole suite to answer one question.
3. **It removes the data it created** (`backend_cleanup`). The report lists anything it could not remove. When
   the profile has no `backend_cleanup`, no real-backend call or integration test that creates data runs; each is
   recorded "not run: no clean-up method in the profile".
4. **It records the request shape, the status and the reply shape**, never tokens or personal data unless the result
   cannot be shown without them, and then masked.

A reply that disagrees with the plan is a gap, classified by `$ORCHARD/references/gap-classification.md`, not a
reason to change the plan or the test.

## 6. Design match is not a visual test

Whether a screen matches its design is evidence in the report, not a visual test. A visual test only guards a look
that was already accepted.

The method: render the pinned design frame (the reference version in `design_source`) and screenshot the app in the
same state. Compare zoomed crops, about 2x, one region at a time (art and images, icons, colours, copy, button
style), never whole-screen thumbnails. Read each element's design properties (font, colour, size, icon, effects)
and check them against the code. Every text the design shows must also be what the spec says for that state. The
app picture shows that frame's state and no other: when no app state matches, say so instead of pairing a near one.

A design comparison has a person as oracle: putting two pictures side by side proves nothing until someone looks.
It is listed under manual checks in the report, whatever tool made the pictures, until a snapshot of that screen
has been approved.

## 7. The four axes

A name such as "unit test" does not say what is under test, what is being claimed, how failure is decided, or where
the inputs come from. A test is only described when all four are answered. The seven checks are shorthand for seven
common combinations. The axes follow Alperen Keles's vocabulary for testing
(https://alperenkeles.com/posts/vocab-for-testing/).

| Check | What is under test | State | What is claimed | How failure is decided (the oracle) | Where inputs come from |
| --- | --- | --- | --- | --- | --- |
| Static analysis | The source text of the whole change | None: nothing runs | A rule holds: layering, style, a test traced to every scenario | The rule itself | None: no input is run |
| Unit tests | A function or a type; in the data layer, a small module | Mostly stateless | Functional correctness | Example: a stated input and its stated output | Hand-picked examples; a table of boundary values |
| Visual tests | One screen, rendered | Stateless: one fixed state | Appearance | Snapshot: an image a person approved earlier | Hand-picked states |
| Behaviour tests | A module in-process, or the whole app through the UI | Stateful | Functional correctness | Example, checked at each step of a scenario and not only at its end | Hand-written scenarios; faults injected through the test double |
| Integration tests | The app together with the real backend | Stateful | The contract with the server holds | Compatibility: the live reply against the fixture and the plan | One call per endpoint |
| Full regression run | Everything | Both | Whatever the re-run tests claim | Theirs | Theirs |
| Manual checks | The app on a device | Stateful | Anything | A person | A person |

What the axes show:

- **Two of the seven rows are not kinds of test.** The full regression run is a selection (all tests) at a time
  (outside the run). A manual check is any check whose oracle is a person. Visual tests are named by what they
  claim, appearance, and not by their usual oracle.
- **Only two things are claimed: functional correctness and appearance.** Accessibility is checked in review and
  wherever the project's UI tests audit it. Performance is measured only when a change touches a launch, scrolling
  or memory-heavy path. Security rests on static analysis and review. Resilience to faults goes only as far as the
  test doubles inject errors, offline and slow replies. Each of these is "not covered" in a report unless the plan
  names it.
- **Almost every oracle is an example.** An example proves one input. A property proves a rule for many: a round
  trip (encode, then decode, gives the original), idempotency (applying twice equals applying once), an invariant
  (a balance is never negative; a state is never invalid), compatibility (a new implementation agrees with the old
  one). Properties are the cheaper proof for mappings, codecs and state reducers; prefer one wherever the scenario
  states a rule and not a single case.
- **Every input is hand-picked.** A test then finds only what its author thought of. A property checked over a
  table of boundary values (`@Test(arguments:)`) widens that at almost no cost. Random generation finds more but
  needs a library, and a new dependency is the developer's decision.
- **A design comparison has a human oracle** (section 6).

## 8. Rule for plans

Each planned test names its kind, and also its oracle whenever that is not a plain example. A test whose oracle is
a person is listed as a manual check. The plan template has the columns: `$ORCHARD/templates/plan.md`, section 5.

## 9. Rules that save time

1. **Order by cost.** Fail fast: cheap kinds run first and a failure stops the sequence, so no expensive kind runs
   on a change already known to be wrong.
2. **Run per round, not per edit.** Tests run when a package is finished, not after each changed line.
3. **Affected scope only.** The run never widens to a full suite to feel safe. What it skipped is named in the
   report.
4. **No reruns.** A failed or blocked run is read, not retried. A pass on rerun is a flaky test and is reported as
   a failure to diagnose.
5. **No waits.** Time, ids and randomness are injected, so no test sleeps.
6. **Read the summary.** Read the project's result summary; open raw logs only when the summary is not enough.
7. **Work in parallel where files do not overlap.** Packages run in separate working copies, with the worker limit
   the profile sets (`workers`). Never two test runs on one simulator (`device_policy`).
8. **One kind per scenario.** A scenario proved by a unit test is not proved again through the UI unless the
   journey on screen is itself the claim.

The report states, per scenario, the kind of test that proved it and the time each kind took, so a person can see
where the time went and what was left out (`$ORCHARD/templates/test-report.md`).

## 10. Evidence about the final change

The rule is in `$ORCHARD/docs/principles.md`, "Evidence is about the final change". How it is applied:

- Every check is run through `$ORCHARD/scripts/evidence.py record`, which stores the state of the change it ran
  against (commit plus a hash of the uncommitted diff).
- Before the report, `evidence.py stale` lists results recorded on an earlier state. A stale result is reused only
  when `affected_map` shows the later edits did not touch what it covers; with `affected_map: none`, the check runs
  again, or the claim is reported as not verified.

## 11. Determinism

- **Time:** inject `any Clock<Duration>` or a "now" provider; tests use a manual clock or a fixed `Date`. Never
  `Date()`, `DispatchTime.now()` or `ContinuousClock()` inside the type under test.
- **Identifiers and randomness:** inject an id generator and a `RandomNumberGenerator`; tests use fixed sequences.
- **Network:** a fixture transport keyed by method and path, or a `URLProtocol` subclass registered on an ephemeral
  `URLSessionConfiguration`. No live hosts outside integration tests.
- **Storage:** a temporary directory or an in-memory container per test, removed in teardown.
- **Locale, time zone, calendar:** pass them explicitly; tests pin `en_US_POSIX`, `UTC` and `gregorian` unless the
  behaviour is about locale.
- **Concurrency:** tests await the actual work (`await store.load()`), or use `confirmation` or expectations
  fulfilled by the code under test. No `Task.sleep` to "let things settle". Main-actor state is read on the main
  actor.
- **Shared state:** no `static var` in tests; suites are independent and run in any order and in parallel.

## 12. Test doubles

- Fakes are small and explicit; an unexpected call fails the test.
- Code under test depends on a protocol, so a test can pass a double; a concrete dependency that a test cannot
  replace is a missing seam. `test` may add the smallest seam the test needs.
- Faults are injected through the double: an error, nothing, an offline or slow reply, a cancelled call.
- Fixtures live where the project keeps them, reuse shared replies, and contain no real personal data.
- A fixture that no longer matches the real backend is fixture drift (`$ORCHARD/references/gap-classification.md`);
  it is updated from a recorded reply, never edited by hand to make a test pass.

## 13. Writing a test

1. **Name the behaviour:** `balanceSubtractsRefunds`, `loadShowsErrorWhenRepositoryFails`. The name is the first
   assertion. Bind the test to its scenario id the way the project does.
2. **Arrange** with the smallest real objects plus explicit fakes; put shared arrangement in a helper that returns a
   value, not in stored properties mutated across tests.
3. **Act** once.
4. **Assert** the contract with precise values, not `isNotNil` or "does not throw". Use `#require` (or
   `try XCTUnwrap`) for preconditions so the test stops at the first broken assumption instead of cascading. Assert
   behaviour, not implementation details.
5. **Cover the branches** the change introduces: happy, empty, failure, boundary (zero, max, month or day
   boundary, cancellation, stale result arriving after a newer one). This list is where to look, not a
   quota: a case is written only when it catches a failure the other tests miss (section 17).
6. **Run** the project's command scoped to the suite; confirm a new test fails before the implementation exists,
   red for the right reason: the assertion, not a compile error or a nil crash.

Swift Testing is the default for new unit and behaviour tests unless the project standardises on XCTest:
`@Suite` struct per type under test; `@Test(arguments:)` for tables; `#expect(throws:)` asserting the specific
error; `confirmation` for callbacks; `withKnownIssue` only for a tracked defect, with its reference. Keep XCTest
for XCUITest, performance metrics and existing XCTest suites unless the project is migrating.

XCUITest rules: find elements by accessibility identifier constants; wait with `waitForExistence(timeout:)` or
predicates on element state; launch with arguments that select fixtures; never assert on localised text unless the
test is about content; never widen a run beyond the methods the change touches unless asked.

## 14. Flaky tests

1. **Reproduce:** run the single test repeatedly (the project's runner option, `-test-iterations`, or a shell loop
   of at most 10 runs) and in random order. Record the failure rate and the exact message.
2. **Classify the cause**, in this order of likelihood: wall-clock dependence; unawaited async work or a race
   between two tasks; shared mutable state across tests (static, singleton, disk, `UserDefaults`); order
   dependence; real network or simulator state; timeouts tuned to a fast machine.
3. **Fix the cause** in the code or the test seam (inject the clock, await the work, isolate the state). Never add a
   retry, a sleep, a longer timeout, `.serialized` without a stated reason, or a skip.
4. **Prove it:** the same repetition now passes every time; where possible, an assertion would fail if the race
   came back.

## 15. Suite audit

Signals, cheapest first:

- Tests containing `sleep(`, `Task.sleep`, `asyncAfter`, `XCTWaiter` on time, raised timeouts.
- Tests without assertions, or asserting only `isNotNil` or "does not throw".
- `static var` or singletons touched by tests; disk or `UserDefaults` not isolated; a test that reaches a live
  service.
- Source types with no test naming them (map `Sources/**/<Type>.swift` to `Tests/**/*<Type>*Tests.swift`).
- Slowest tests from the last result bundle or timings report; a unit test over one second is a smell.
- Skipped or disabled tests and the reasons; `withKnownIssue` without a reference.
- Coverage thresholds and diff coverage, if configured, and whether they are gates or warnings. Coverage measures
  execution, not verification.

## 16. What a test may assert

A failing test says the code and an expectation disagree. It helps only when something other than the code can
say which side is wrong. Some rules here are adapted from an MIT-licensed testing skill; see
`$ORCHARD/THIRD_PARTY_NOTICES.md`.

| The expected value may come from | It may not come from |
| --- | --- |
| The approved scenario and its basis (spec, design, team decision) | A constant copied from the code under test |
| A contract someone else consumes: an endpoint, a schema, a stored or wire format, a recorded backend reply | The same calculation written again inside the test |
| A law the code must obey: round trip, idempotency, ordering, an invariant | The code's own output, recorded and never reviewed |
| A snapshot or golden file a person approved | A tuned value read from configuration |

- **A test from the second column is a change detector.** When it fails nobody can tell which side is wrong, so
  the only fix is to make the two agree again. Report it as that, not as proof. An approved snapshot or a fixture
  can go stale too: when one fails, go back to its source before changing either side.
- **Configuration is not behaviour.** A value is configuration when the source names the parameter and not its
  value, and it changes for tuning: a timeout, a retry count, a page size, a feature-flag default, a remote-config
  value, an animation duration. No test asserts it. The test passes in a value of its own and checks the rule
  around it: for "refuse at the limit", a limit `L` chosen by the test, then one below `L`, `L`, and one above.
  Those three stay green when the value is retuned, and each catches a different mistake (`>` for `>=`, `==`, a
  rule that refuses everything).
- **A value the source fixes exactly is a contract** and may be asserted: a legal retention period, a protocol
  constant, a limit the spec states as a number. A value the server decides is neither: the app has no rule to
  test, only its reaction to the reply.
- **What does need a check around configuration:** which value wins when two sources set it (default, remote,
  override) is behaviour, tested with values the test can tell apart; a shipped file that must have a key or a
  range is checked where the app loads it, so the app fails fast too.
- **No source for the expected value** (the rule exists only in the code) means there is nothing to test yet: it
  is an undecided behaviour. Name it for the owner; a test would make it permanent.

## 17. A finished test set

Written tests join a suite other changes wrote and later changes will edit. A test set for a change is finished
when three things hold; then stop writing tests.

**Complete**
- Every behaviour the change must have, with its failure modes, has at least one assertion that fails when the
  behaviour breaks. The behaviours come from the scenario rows, not from the lines changed.
- Every path through the changed code is exercised, or accounted for in words: where it runs, which invariant
  prevents it, or what stops it being verified. A behaviour that could not be verified is reported as open, never
  counted as covered. A coverage percentage is not a goal.

**Minimal**
- Every case catches a failure the rest of the suite would miss, and its author can say which one. Two inputs with
  the same expected result both stay when they catch different mistakes; a case that catches nothing new is merged
  or not written.
- The existing test comes first: keep, extend or correct the test that already covers the behaviour, and add a
  case only for a failure the suite misses. When a test covered the behaviour and still let a defect through, fix
  that test; a second test beside it leaves the weak one in place.
- No test asserts a tuned value, repeats the calculation, or depends on a private symbol, its own setup or the
  wall clock.

**Consistent with the suite**
- An existing test that turns red is evidence first, and its source decides which side changes. The code is wrong:
  fix the code (`$ORCHARD/docs/principles.md`, "Fix the code, never the check"). The approved scenario changed the
  behaviour: the expectation changes, and the change names the scenario row. The old expectation had no source or
  held an incidental detail: correct or remove it and say why. Two sources of equal standing disagree: stop and
  ask. An expectation is never edited until it passes with nothing said.
- An expectation for a behaviour the change removed is removed in the same change; it would keep passing and
  nobody would notice. The assertions in that test for behaviour that stays are kept.
- Tests of behaviour the change did not touch still check what they checked before. A clean-up of the whole suite
  is a task of its own.
- A test is never removed because another one runs the same lines. Equal coverage does not mean the same failures
  are caught; removing one takes an argument about the failures each catches.

**A finding on a test** shows one of these, or it is a question:
- a wrong implementation the test still accepts (the test cannot fail);
- a change the sources allow that the test rejects: a retuned value, a refactor that keeps the behaviour, a
  renamed private symbol (the test holds something it should not);
- a required case that is skipped, never collected, or not deterministic.
