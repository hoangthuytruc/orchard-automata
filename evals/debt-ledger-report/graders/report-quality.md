---
type: llm
weight: 3
focus:
  source: file
  path: docs/tech-debt/ledger.md
---
You are shown a technical debt report. PASS only if ALL hold:
1. Items are ranked and each carries an impact score, a likelihood score, an effort size, evidence as a
   repo-relative `path:line` (or a command and its count), and a suggested first step.
2. It covers at least five of: the `TransactionStore.shared` singleton with unsynchronized mutable state on a
   DispatchQueue; force unwraps or `try!` on data paths in `TransactionStore`, `LedgerFormatter` or `SyncClient`;
   the auth token in `UserDefaults`; the completion-handler `URLSession` API instead of async/await; `Date()` read
   inside `monthTotalCents`; the single sleep-based test and the missing tests for refunds and the empty store;
   Swift 5 language mode in `Package.swift`.
3. It has a method-and-limits section saying what was scanned and which tools were unavailable.
4. It does not claim that any fix was applied. Suggested first steps, including a one-line code idea, are
   expected.
FAIL if items lack evidence or scores, if fewer than five of the listed debts appear, if it claims fixes were
made, or if it is a prose essay without a ranked list. Table versus bullets and column names do not matter.
