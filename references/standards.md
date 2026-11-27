# iOS production standards

The bar every skill holds code to. The project's guides (profile key `guides`) and its review rules (profile key
`review_rules`) override anything here when they conflict (`$ORCHARD/docs/boundaries.md`, "Conflicts"); say so
in the report when you deviate from this file because of them. `$ORCHARD` is the root of the skill set.

How a change is judged against these standards is in `$ORCHARD/references/review-checklist.md`. How it is proved is
in `$ORCHARD/references/test-strategy.md`. This file says what good code is; it does not repeat either.

## 1. Language and concurrency

- Target Swift 6 language mode with strict concurrency. In a project still on Swift 5 mode, write new code that
  would compile under Swift 6: every type crossing an isolation boundary is `Sendable`, UI state is `@MainActor`,
  shared mutable state lives in an `actor` or behind `@MainActor`.
- Structured concurrency first: `async let`, `TaskGroup`, cancellation checked in loops and before expensive work.
  No new `DispatchQueue`, `DispatchGroup`, semaphore, or completion-handler API when an async form exists. Wrap a
  legacy callback once with `withCheckedThrowingContinuation` and resume exactly once.
- `@unchecked Sendable`, `nonisolated(unsafe)`, `Task.detached` and `MainActor.assumeIsolated` are exceptions that
  need a stated reason at the use site (follow the project's comment policy for how). `@unchecked Sendable` also
  needs a lock or queue that guards every access to its mutable state.
- No `!` force unwrap, `try!`, `as!` or implicitly unwrapped optional in production code. `fatalError` and
  `precondition` only for programmer-error invariants, never for data or network states.
- Prefer value types; `final class` when identity or reference semantics are required. Errors are typed enums with
  a clear boundary where they are mapped; no `NSError` domains leaking into features. Typed throws only for a closed
  set of errors; plain `throws` for an interface whose errors may grow.
- Access control is the narrowest that compiles; `public` only across module boundaries and documented;
  `private(set)` to expose state read-only.

## 2. Architecture

- Dependency rule: UI depends on domain, infrastructure depends on domain, domain depends on nothing (no UIKit,
  SwiftUI, URLSession, persistence framework). Every crossing goes through a protocol owned by the consumer side.
  No dependency cycle between modules.
- One owner per piece of state; derived state is computed, never duplicated. Side effects (network, persistence,
  clock, randomness, identifiers, OS services) are injected and happen at the boundary, never inside a reducer or
  a view body.
- Choose the smallest pattern that makes state ownership, dependencies, side effects and tests explicit; escalate
  (MVVM, MVI or reducer, TCA, Clean) only for observed pressure. Consistency with the codebase beats textbook
  purity: match the existing pattern unless the approved plan changes it, with its reason.
- Composition happens in one place (composition root, app assembly). No service locator or singleton for mutable
  state; `static let shared` is allowed only for stateless, `Sendable` utilities.
- Navigation has one owner per flow (coordinator, router, `NavigationPath` owner); views request navigation, they do
  not build destinations from other features.
- Feature code is grouped by feature, shared code by responsibility; a shared folder gaining a feature-specific type
  is a smell. Configuration and environment values live in one place, never hard-coded across features.

## 3. SwiftUI and UIKit

- A view is a function of state. Views hold layout and presentation only; formatting and business rules live in
  display models or domain types. Prefer `@Observable` over `ObservableObject` where the deployment target allows.
- Every interactive control has a stable accessibility identifier (constants, not literals) and a meaningful
  accessibility label; Dynamic Type works at the largest accessibility sizes; colour is never the only signal.
- Previews exist for every state of a screen or component (loading, empty, error, populated, long text, right to
  left where relevant).
- No work in `body` beyond cheap derivation; expensive computation is memoised in the model. Watch for views that
  re-render on unrelated state.
- Mind type-checker and runtime pitfalls the project documents (for example computed `some View` properties).
- UIKit bridging through `UIViewRepresentable` with a coordinator; no reaching into the hosting controller.
- A picture in the design is one image in the app: export the frame the person sees, at its own bounds, and show
  it. Never ship a larger source to crop, offset or patch in code. Code draws only what changes at run time (text,
  state, data, theme). Hand-tuned offsets or patches around an image mean the wrong thing was exported.
- Whether a screen matches its design is shown by evidence, not by a visual test. The method is in
  `$ORCHARD/references/test-strategy.md`, section "Design match is not a visual test".
- Every question to the owner about how a screen looks or what it says carries the pinned design frame and the app
  render of that state, both as pictures, plus the case in one line (OS, state, action).
- Before editing a shared UI component, list every other screen that uses it and say what the change does there.
  Then decide: change it directly when every caller is in scope, or extend it with an option whose default keeps
  the other screens unchanged.

## 4. API design

- Swift API Design Guidelines: clarity at the point of use, argument labels that read as a phrase, `-ed`/`-ing`
  for nonmutating pairs (`sorted()` returns, `sort()` mutates), no needless words, booleans read as assertions
  (`isEmpty`, `hasChanges`), protocols named by capability.
- Public surface is documented with `///` where the project documents APIs; otherwise names carry the meaning.

## 5. Testing

The testing rules have one home: `$ORCHARD/references/test-strategy.md` (kinds of check, choosing a kind, test
doubles, determinism, procedure, flaky tests). Two rules from it hold for every line of code written under these
standards:

- Every behaviour change ships its tests in the same change, written first and seen to fail for the right reason.
- Never lower a coverage threshold, loosen an assertion, skip, disable or delete a test to get green.

## 6. Security and privacy

- Secrets, tokens and credentials live in the Keychain (or the project's secure store), never in `UserDefaults`,
  plists, source or logs. No secrets in the repository; sample values only in example files.
- App Transport Security stays on; certificate handling is explicit. Inputs from the network, deep links, the
  pasteboard or files are validated before use.
- Cryptography uses the platform (CryptoKit, Security framework); no hand-written algorithm. Tokens and nonces come
  from a secure random source, never from a seeded or test generator.
- Stored personal data uses file protection that matches its sensitivity, and is removed when the person signs out
  or deletes it.
- `PrivacyInfo.xcprivacy` declares required-reason APIs and collected data truthfully; logs redact personal data
  (`privacy: .private`); tests and fixtures contain no real personal data.

## 7. Performance and reliability

- Nothing blocking on the main thread: I/O, decoding, image work and heavy computation run off `@MainActor`.
- No retain cycles: closures stored by a longer-lived object capture `[weak self]`; tasks are cancelled with their
  owner; observations, timers and subscriptions are removed.
- Launch, hang and memory regressions are measured, not guessed (Instruments, MetricKit, XCTest metrics) before and
  after a change that touches them.
- Background work uses the system schedulers (`BGTaskScheduler`, background `URLSession`) with expiration handled.
- Lists that can grow are paged and shown in lazy containers.

## 8. Delivery hygiene

- Lint is clean with the project's configuration (profile key `lint`); no rule disabled inline without a stated
  reason.
- A change touches only what the task needs; every changed line traces to an approved plan item. Unrelated cleanups
  are reported, not done.
- A draft pull-request body follows the project's template (profile key `pr_template`). No skill commits, pushes,
  branches or opens a pull request. Never attribute code to an AI or a tool in any text a skill produces.
- Report what was verified and what was not, with the exact commands and their results.
